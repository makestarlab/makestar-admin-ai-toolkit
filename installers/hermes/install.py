from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_MANIFEST = '.makestar-admin-skills-install.json'


class InstallError(RuntimeError):
    pass


@dataclass(slots=True)
class InstallConfig:
    source_root: Path
    target: Path
    backup_root: Path | None
    overwrite: bool
    backup: bool
    dry_run: bool
    only: list[str] | None
    toolkit_version: str
    source_ref: str
    manifest_digest: str | None
    require_hermes: bool


def default_target() -> Path:
    return Path.home() / '.hermes' / 'skills' / 'makestar'


def default_source_root() -> Path:
    public_root = REPO_ROOT / 'hermes' / 'skills' / 'makestar'
    if public_root.exists():
        return public_root
    return REPO_ROOT / 'dist' / 'hermes' / 'skills' / 'makestar'


def default_backup_root() -> Path:
    return Path.home() / '.hermes' / 'skills-backup'


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def parse_bundle(path: Path) -> list[str]:
    if not path.exists():
        raise InstallError(f'Missing Hermes bundle file: {path}')
    skills: list[str] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line.startswith('- '):
            skills.append(line[2:].strip())
    return skills


def safe_resolve(path: Path, *, must_exist: bool = False) -> Path:
    try:
        return path.expanduser().resolve(strict=must_exist)
    except OSError as exc:
        raise InstallError(f'Invalid path {path}: {exc}') from exc


def reject_symlink_ancestors(path: Path, *, label: str) -> None:
    current = Path(path.expanduser())
    if not current.is_absolute():
        current = Path.cwd() / current
    probe = Path(current.anchor) if current.anchor else Path('.')
    for part in current.parts[1:] if current.anchor else current.parts:
        probe = probe / part
        try:
            st = probe.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(st.st_mode):
            raise InstallError(f'{label} contains forbidden symlink ancestor: {probe}')


def reject_relative_escape(path: Path, *, label: str) -> None:
    if path.is_absolute() or '..' in path.parts:
        raise InstallError(f'Unsafe {label}: {path}')


def safe_skill_name(name: str) -> str:
    if not name or Path(name).name != name or '/' in name or '\\' in name or '..' in Path(name).parts:
        raise InstallError(f'Unsafe skill name: {name}')
    return name


def ensure_contained(path: Path, root: Path, *, label: str) -> None:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError as exc:
        raise InstallError(f'{label} escapes expected root: {path}') from exc


def reject_symlinks(root: Path, *, label: str) -> None:
    if root.is_symlink():
        raise InstallError(f'{label} must not be a symlink: {root}')
    if not root.exists():
        return
    for path in root.rglob('*'):
        if path.is_symlink():
            raise InstallError(f'{label} contains forbidden symlink: {path}')


def ensure_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise InstallError(f'Required tool executable not found on PATH: {name}')


def chmod_tree(root: Path) -> None:
    for directory, dirnames, filenames in os.walk(root):
        Path(directory).chmod(0o700)
        for dirname in dirnames:
            (Path(directory) / dirname).chmod(0o700)
        for filename in filenames:
            (Path(directory) / filename).chmod(0o600)


def copy_tree_verified(src: Path, dst: Path) -> list[dict[str, object]]:
    if not src.exists() or not src.is_dir():
        raise InstallError(f'Missing source skill: {src}')
    ensure_contained(dst, dst.parent, label='staging skill')
    files: list[dict[str, object]] = []
    for path in sorted(src.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(src)
        reject_relative_escape(rel, label='source relative path')
        target = dst / rel
        ensure_contained(target, dst, label='staging file')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        expected = sha256_file(path)
        actual = sha256_file(target)
        if expected != actual:
            raise InstallError(f'Digest verification failed for {rel.as_posix()}')
        files.append({'path': rel.as_posix(), 'sha256': actual, 'size_bytes': target.stat().st_size})
    chmod_tree(dst)
    return files


def public_root_for_source(source_root: Path) -> Path | None:
    parts = source_root.parts
    suffix = ('hermes', 'skills', 'makestar')
    if len(parts) >= len(suffix) and parts[-3:] == suffix:
        return Path(*parts[:-3]) if parts[:-3] else Path(source_root.anchor)
    return None


def load_public_manifest(source_root: Path, manifest_digest: str | None) -> dict[str, dict[str, object]]:
    public_root = public_root_for_source(source_root)
    manifest_path = public_root / '.makestar-toolkit-manifest.json' if public_root else None
    if manifest_digest:
        if not manifest_path or not manifest_path.exists():
            raise InstallError('--manifest-digest was supplied but public toolkit manifest is missing')
        actual = sha256_file(manifest_path)
        if actual != manifest_digest:
            raise InstallError('Public toolkit manifest digest mismatch')
    if not manifest_path or not manifest_path.exists():
        return {}
    payload = json.loads(manifest_path.read_text())
    return {entry['path']: entry for entry in payload.get('files', []) if isinstance(entry, dict) and isinstance(entry.get('path'), str)}


def verify_manifest_surface(source_root: Path, manifest_entries: dict[str, dict[str, object]]) -> None:
    if not manifest_entries:
        return
    public_root = public_root_for_source(source_root)
    if public_root is None:
        return
    prefix = source_root.relative_to(public_root).as_posix().rstrip('/') + '/'
    expected = [rel for rel in manifest_entries if rel.startswith(prefix)]
    if not expected:
        raise InstallError(f'Public manifest has no entries for source root: {prefix}')
    for rel in expected:
        path = public_root / rel
        if not path.exists() or not path.is_file():
            raise InstallError(f'Public manifest source artifact is missing: {rel}')
        entry = manifest_entries[rel]
        if entry.get('sha256') != sha256_file(path):
            raise InstallError(f'Public manifest digest mismatch for source artifact: {rel}')


def verify_source_artifacts(source_root: Path, skills: list[str], manifest_entries: dict[str, dict[str, object]]) -> None:
    if not manifest_entries:
        return
    public_root = public_root_for_source(source_root)
    if public_root is None:
        return
    for skill in skills:
        for path in sorted((source_root / skill).rglob('*')):
            if not path.is_file():
                continue
            rel = path.relative_to(public_root).as_posix()
            entry = manifest_entries.get(rel)
            if not entry:
                raise InstallError(f'Public manifest missing source artifact: {rel}')
            if entry.get('sha256') != sha256_file(path):
                raise InstallError(f'Public manifest digest mismatch for source artifact: {rel}')


def build_manifest(config: InstallConfig, skills: list[str], files_by_skill: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    return {
        'schema_version': 1,
        'installer': 'install_hermes.py',
        'tool': 'hermes',
        'installed_at': datetime.now(timezone.utc).isoformat(),
        'toolkit_version': config.toolkit_version,
        'source_ref': config.source_ref,
        'source_manifest_digest': config.manifest_digest,
        'target_kind': 'hermes-skills-category',
        'skills': [{'name': skill, 'files': files_by_skill[skill]} for skill in skills],
    }


def validate_selection(source_root: Path, only: list[str] | None) -> list[str]:
    skills = [safe_skill_name(name) for name in parse_bundle(source_root / 'bundle.yaml')]
    if only:
        wanted = set(only)
        for name in wanted:
            safe_skill_name(name)
        unknown = sorted(wanted - set(skills))
        if unknown:
            raise InstallError(f'Unknown skill(s): {", ".join(unknown)}')
        skills = [name for name in skills if name in wanted]
    if not skills:
        raise InstallError('No skills selected for installation.')
    return skills


def install(config: InstallConfig) -> dict[str, object] | None:
    if config.require_hermes:
        ensure_tool('hermes')
    reject_symlink_ancestors(config.source_root, label='source root')
    reject_symlink_ancestors(config.target, label='target')
    if config.backup and config.backup_root:
        reject_symlink_ancestors(config.backup_root, label='backup root')
    source_root = safe_resolve(config.source_root, must_exist=True)
    target = safe_resolve(config.target)
    backup_root = safe_resolve(config.backup_root) if config.backup and config.backup_root else None
    reject_symlinks(source_root, label='source root')
    if target.exists() and target.is_symlink():
        raise InstallError(f'target must not be a symlink: {target}')
    manifest_entries = load_public_manifest(source_root, config.manifest_digest)
    verify_manifest_surface(source_root, manifest_entries)
    skills = validate_selection(source_root, config.only)
    verify_source_artifacts(source_root, skills, manifest_entries)

    print('[makestar-admin-skills] Hermes public install' + (' (dry-run)' if config.dry_run else ''))
    print(f'- source: {source_root}')
    print(f'- target: {target}')
    print(f'- skills: {", ".join(skills)}')

    collisions = [skill for skill in skills if (target / skill).exists()]
    if collisions and not (config.overwrite or config.backup):
        raise InstallError('Target skill already exists: ' + ', '.join(str(target / skill) for skill in collisions) + '. Use --overwrite or --backup.')
    for skill in skills:
        ensure_contained(source_root / skill, source_root, label='source skill')
        ensure_contained(target / skill, target, label='target skill')
        reject_symlinks(target / skill, label=f'target skill {skill}')
        reject_symlinks(source_root / skill, label=f'source skill {skill}')

    if config.dry_run:
        for skill in skills:
            print(f'- dry-run install: {source_root / skill} -> {target / skill}')
        print(f'- dry-run manifest: {target / INSTALL_MANIFEST}')
        return None

    target.mkdir(parents=True, exist_ok=True)
    target.chmod(0o700)
    backup_dir = None
    if config.backup and collisions:
        if backup_root is None:
            raise InstallError('--backup requires --backup-root')
        backup_dir = backup_root / datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_dir.chmod(0o700)

    with tempfile.TemporaryDirectory(prefix='makestar-hermes-install.') as temp_dir:
        staging = Path(temp_dir) / 'skills'
        files_by_skill: dict[str, list[dict[str, object]]] = {}
        for skill in skills:
            files_by_skill[skill] = copy_tree_verified(source_root / skill, staging / skill)
        manifest = build_manifest(config, skills, files_by_skill)
        manifest_path = Path(temp_dir) / INSTALL_MANIFEST
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        manifest_path.chmod(0o600)

        rollback_existing = target / f'.makestar-hermes-install-rollback-{Path(temp_dir).name}'
        moved_skills: list[str] = []
        manifest_backup = Path(temp_dir) / 'rollback-manifest'
        manifest_existed = (target / INSTALL_MANIFEST).exists()
        try:
            if manifest_existed:
                shutil.copy2(target / INSTALL_MANIFEST, manifest_backup)
            if collisions:
                rollback_existing.mkdir(mode=0o700)
            for skill in collisions:
                existing = target / skill
                if backup_dir is not None:
                    shutil.copytree(existing, backup_dir / skill)
                    chmod_tree(backup_dir / skill)
                    print(f'- backup: {existing} -> {backup_dir / skill}')
                existing.rename(rollback_existing / skill)
            for skill in skills:
                shutil.move(str(staging / skill), target / skill)
                moved_skills.append(skill)
                print(f'- install: {skill} -> {target / skill}')
            shutil.move(str(manifest_path), target / INSTALL_MANIFEST)
            if rollback_existing.exists():
                shutil.rmtree(rollback_existing)
        except Exception as exc:
            for skill in moved_skills:
                if (target / skill).exists():
                    shutil.rmtree(target / skill)
            for skill in collisions:
                if (rollback_existing / skill).exists() and (target / skill).exists():
                    shutil.rmtree(target / skill)
                if (rollback_existing / skill).exists():
                    shutil.move(str(rollback_existing / skill), target / skill)
            if (target / INSTALL_MANIFEST).exists():
                (target / INSTALL_MANIFEST).unlink()
            if manifest_existed and manifest_backup.exists():
                shutil.copy2(manifest_backup, target / INSTALL_MANIFEST)
            if rollback_existing.exists() and not any(rollback_existing.iterdir()):
                rollback_existing.rmdir()
            raise InstallError(f'Install failed; rolled back target changes: {exc}') from exc
    print('Done.')
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description='Safely install Makestar Hermes skills from a public artifact root.')
    parser.add_argument('--source-root', type=Path, default=None, help='Defaults to the public Hermes skill root when present, otherwise the local generated Hermes root.')
    parser.add_argument('--target', type=Path, default=None, help='Defaults to ~/.hermes/skills/makestar at runtime.')
    parser.add_argument('--backup-root', type=Path, default=None, help='Defaults to ~/.hermes/skills-backup at runtime when --backup is used.')
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--backup', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--only', nargs='*')
    parser.add_argument('--toolkit-version', default='unknown')
    parser.add_argument('--source-ref', default='unknown')
    parser.add_argument('--manifest-digest', default=None)
    parser.add_argument('--require-hermes', action='store_true', help='Fail if the hermes executable is missing.')
    args = parser.parse_args()

    try:
        install(
            InstallConfig(
                source_root=args.source_root or default_source_root(),
                target=args.target or default_target(),
                backup_root=args.backup_root or default_backup_root(),
                overwrite=args.overwrite,
                backup=args.backup,
                dry_run=args.dry_run,
                only=args.only,
                toolkit_version=args.toolkit_version,
                source_ref=args.source_ref,
                manifest_digest=args.manifest_digest,
                require_hermes=args.require_hermes,
            )
        )
    except InstallError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == '__main__':
    main()
