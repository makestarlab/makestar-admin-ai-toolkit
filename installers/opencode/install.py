from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALL_MANIFEST = 'makestar-admin-skills-install.json'


class InstallError(RuntimeError):
    pass


@dataclass(slots=True)
class InstallConfig:
    source_root: Path
    project_root: Path
    global_install: bool
    global_target: Path | None
    backup_root: Path | None
    overwrite: bool
    backup: bool
    dry_run: bool
    toolkit_version: str
    source_ref: str
    manifest_digest: str | None
    require_opencode: bool


def default_project_root() -> Path:
    return Path.cwd()


def default_source_root() -> Path:
    public_root = REPO_ROOT / 'opencode' / '.opencode' / 'skills'
    if public_root.exists():
        return public_root
    return REPO_ROOT / 'dist' / 'opencode' / '.opencode' / 'skills'


def default_global_target() -> Path:
    return Path.home() / '.config' / 'opencode' / 'skills'


def default_backup_root(project_root: Path, global_install: bool) -> Path:
    if global_install:
        return Path.home() / '.config' / 'opencode' / 'skills-backup'
    return project_root / '.opencode' / 'skills-backup'


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


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
        if stat_is_symlink(st.st_mode):
            raise InstallError(f'{label} contains forbidden symlink ancestor: {probe}')


def stat_is_symlink(mode: int) -> bool:
    return (mode & 0o170000) == 0o120000


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


def skill_names(source_root: Path) -> list[str]:
    names = [safe_skill_name(path.name) for path in sorted(source_root.iterdir()) if path.is_dir() and (path / 'SKILL.md').exists()]
    if not names:
        raise InstallError(f'No OpenCode skills found in {source_root}')
    return names


def target_root(config: InstallConfig) -> Path:
    if config.global_install:
        unresolved_global_target = config.global_target or default_global_target()
        reject_symlink_ancestors(unresolved_global_target, label='global target')
        return safe_resolve(unresolved_global_target)
    project = safe_resolve(config.project_root, must_exist=True)
    if not project.is_dir():
        raise InstallError(f'Project root must be a directory: {project}')
    return project / '.opencode' / 'skills'


def copy_tree_verified(src: Path, dst: Path) -> list[dict[str, object]]:
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
    suffix = ('opencode', '.opencode', 'skills')
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


def build_manifest(config: InstallConfig, target_kind: str, skills: list[str], files_by_skill: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    return {
        'schema_version': 1,
        'installer': 'install_opencode.py',
        'tool': 'opencode',
        'installed_at': datetime.now(timezone.utc).isoformat(),
        'toolkit_version': config.toolkit_version,
        'source_ref': config.source_ref,
        'source_manifest_digest': config.manifest_digest,
        'target_kind': target_kind,
        'skills': [{'name': skill, 'files': files_by_skill[skill]} for skill in skills],
    }


def install(config: InstallConfig) -> dict[str, object] | None:
    if config.require_opencode:
        ensure_tool('opencode')
    reject_symlink_ancestors(config.source_root, label='source root')
    reject_symlink_ancestors(config.project_root, label='project root')
    if config.global_install:
        reject_symlink_ancestors(config.global_target or default_global_target(), label='global target')
    if config.backup and config.backup_root:
        reject_symlink_ancestors(config.backup_root, label='backup root')
    source_root = safe_resolve(config.source_root, must_exist=True)
    reject_symlinks(source_root, label='source root')
    manifest_entries = load_public_manifest(source_root, config.manifest_digest)
    verify_manifest_surface(source_root, manifest_entries)
    target = target_root(config)
    reject_symlink_ancestors(target, label='target')
    target_kind = 'opencode-global-skills' if config.global_install else 'opencode-project-skills'
    if target.exists() and target.is_symlink():
        raise InstallError(f'target skills directory must not be a symlink: {target}')
    if target.parent.is_symlink():
        raise InstallError(f'managed .opencode directory must not be a symlink: {target.parent}')
    skills = skill_names(source_root)
    verify_source_artifacts(source_root, skills, manifest_entries)

    print('[makestar-admin-skills] OpenCode public install' + (' (dry-run)' if config.dry_run else ''))
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

    manifest_target = target.parent / INSTALL_MANIFEST
    if config.dry_run:
        for skill in skills:
            print(f'- dry-run install: {source_root / skill} -> {target / skill}')
        print(f'- dry-run manifest: {manifest_target}')
        return None

    target.mkdir(parents=True, exist_ok=True)
    target.chmod(0o700)
    backup_dir = None
    if config.backup and collisions:
        chosen_backup_root = config.backup_root or default_backup_root(safe_resolve(config.project_root), config.global_install)
        reject_symlink_ancestors(chosen_backup_root, label='backup root')
        backup_root = safe_resolve(chosen_backup_root)
        backup_dir = backup_root / datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_dir.chmod(0o700)

    with tempfile.TemporaryDirectory(prefix='makestar-opencode-install.') as temp_dir:
        staging = Path(temp_dir) / 'skills'
        files_by_skill: dict[str, list[dict[str, object]]] = {}
        for skill in skills:
            files_by_skill[skill] = copy_tree_verified(source_root / skill, staging / skill)
        manifest = build_manifest(config, target_kind, skills, files_by_skill)
        manifest_path = Path(temp_dir) / INSTALL_MANIFEST
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        manifest_path.chmod(0o600)

        rollback_existing = target / f'.makestar-opencode-install-rollback-{Path(temp_dir).name}'
        moved_skills: list[str] = []
        manifest_backup = Path(temp_dir) / 'rollback-manifest'
        manifest_existed = manifest_target.exists()
        try:
            if manifest_existed:
                shutil.copy2(manifest_target, manifest_backup)
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
            shutil.move(str(manifest_path), manifest_target)
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
            if manifest_target.exists():
                manifest_target.unlink()
            if manifest_existed and manifest_backup.exists():
                shutil.copy2(manifest_backup, manifest_target)
            if rollback_existing.exists() and not any(rollback_existing.iterdir()):
                rollback_existing.rmdir()
            raise InstallError(f'Install failed; rolled back target changes: {exc}') from exc
    print('Done.')
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description='Safely install Makestar OpenCode skills into project-local .opencode/skills by default.')
    parser.add_argument('--source-root', type=Path, default=None, help='Defaults to the public OpenCode skills root when present, otherwise the local generated OpenCode skills root.')
    parser.add_argument('--project-root', type=Path, default=None, help='Defaults to the current working directory at runtime.')
    parser.add_argument('--target', type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument('--global', dest='global_install', action='store_true', help='Install to ~/.config/opencode/skills (experimental).')
    parser.add_argument('--global-target', type=Path, default=None)
    parser.add_argument('--backup-root', type=Path, default=None)
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--backup', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--toolkit-version', default='unknown')
    parser.add_argument('--source-ref', default='unknown')
    parser.add_argument('--manifest-digest', default=None)
    parser.add_argument('--require-opencode', action='store_true', help='Fail if the opencode executable is missing.')
    args = parser.parse_args()
    if args.target is not None and args.project_root is not None:
        raise SystemExit('--target is deprecated; use --project-root and do not pass both')

    try:
        install(
            InstallConfig(
                source_root=args.source_root or default_source_root(),
                project_root=args.project_root or args.target or default_project_root(),
                global_install=args.global_install,
                global_target=args.global_target,
                backup_root=args.backup_root,
                overwrite=args.overwrite,
                backup=args.backup,
                dry_run=args.dry_run,
                toolkit_version=args.toolkit_version,
                source_ref=args.source_ref,
                manifest_digest=args.manifest_digest,
                require_opencode=args.require_opencode,
            )
        )
    except InstallError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == '__main__':
    main()
