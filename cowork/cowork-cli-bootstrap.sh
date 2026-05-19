#!/bin/sh
set -eu

APP_NAME=makestar-admin
APP_PLATFORM=linux-x86_64
APP_ASSET=makestar-admin-linux-x86_64.zip
APP_ORIGIN=https://github.com/makestarlab/makestar-admin-cli-releases/releases/download
CLI_HOME=${MAKESTAR_ADMIN_CLI_HOME:-$HOME/.makestar-admin/cowork-cli}
VERSION=${MAKESTAR_ADMIN_CLI_VERSION:-}
RELEASE_TAG=${MAKESTAR_ADMIN_CLI_RELEASE_TAG:-}
MANIFEST_URL=${MAKESTAR_ADMIN_CLI_MANIFEST_URL:-}
MODE=${1:-resolve}

fail() {
  printf '%s\n' "cowork_cli_bootstrap_error=$*" >&2
  exit 1
}

evidence() {
  printf '%s\n' "$*" >&2
}

is_abs() { case "$1" in /*) return 0 ;; *) return 1 ;; esac; }

canonical_release_url() {
  case "$1" in
    "$APP_ORIGIN"/*) return 0 ;;
    *) return 1 ;;
  esac
}

plain_public_url() {
  case "$1" in
    *'?'*|*'#'*|*@*) return 1 ;;
    *) return 0 ;;
  esac
}

require_plain_public_url() {
  label=$1
  url=$2
  plain_public_url "$url" || fail "$label URL must not include userinfo, query, or fragment"
}

safe_version() {
  case "$1" in
    ''|.|..|*[!A-Za-z0-9._+-]*) return 1 ;;
    *) return 0 ;;
  esac
}

safe_download_url() {
  case "$1" in
    "$APP_ORIGIN"/*) return 0 ;;
    https://objects.githubusercontent.com/github-production-release-asset-*) return 0 ;;
    https://release-assets.githubusercontent.com/github-production-release-asset/*) return 0 ;;
    *) return 1 ;;
  esac
}

version_from_output() {
  sed -n 's/.*\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' | sed -n '1p'
}

check_executable_version() {
  exe=$1
  expected=${2:-}
  [ -x "$exe" ] || return 1
  out=$("$exe" --version 2>/dev/null) || return 1
  found=$(printf '%s\n' "$out" | version_from_output)
  [ -n "$found" ] || return 1
  if [ -n "$expected" ] && [ "$found" != "$expected" ]; then
    return 2
  fi
  printf '%s' "$found"
}

managed_root_real() {
  mkdir -p "$CLI_HOME" || fail "cannot create MAKESTAR_ADMIN_CLI_HOME: $CLI_HOME"
  (cd "$CLI_HOME" 2>/dev/null && pwd -P) || fail "cannot resolve MAKESTAR_ADMIN_CLI_HOME: $CLI_HOME"
}

is_under_managed_root() {
  p=$1
  root=$(managed_root_real)
  dir=$(dirname "$p")
  real_dir=$(cd "$dir" 2>/dev/null && pwd -P) || return 1
  case "$real_dir/" in "$root"/*) return 0 ;; *) return 1 ;; esac
}

resolve_override() {
  [ -n "${MAKESTAR_ADMIN_CLI_PATH:-}" ] || return 1
  override=$MAKESTAR_ADMIN_CLI_PATH
  is_abs "$override" || fail "MAKESTAR_ADMIN_CLI_PATH must be an absolute trusted operator path"
  [ -f "$override" ] || fail "MAKESTAR_ADMIN_CLI_PATH does not exist: $override"
  version=$(check_executable_version "$override" "${VERSION#v}") || fail "MAKESTAR_ADMIN_CLI_PATH failed --version verification"
  evidence "resolved_cli_path_category=trusted_override"
  evidence "resolved_cli_version=$version"
  evidence "trusted_override_used=true"
  printf '%s\n' "$override"
  exit 0
}

resolve_managed() {
  root=$(managed_root_real)
  current="$root/current/$APP_NAME"
  [ -f "$current" ] || return 1
  mkdir -p "$root/versions" || fail "cannot create managed versions directory: $root/versions"
  versions_root=$(cd "$root/versions" 2>/dev/null && pwd -P) || fail "cannot resolve managed versions directory: $root/versions"
  current_dir=$(dirname "$current")
  real_current_dir=$(cd "$current_dir" 2>/dev/null && pwd -P) || fail "cannot resolve managed current marker: $current_dir"
  case "$real_current_dir/" in "$versions_root"/*) ;; *) fail "managed current marker escapes MAKESTAR_ADMIN_CLI_HOME versions: $real_current_dir" ;; esac
  set +e
  version=$(check_executable_version "$current" "${VERSION#v}")
  code=$?
  set -e
  if [ "$code" -eq 0 ]; then
    evidence "resolved_cli_path_category=managed_sandbox"
    evidence "resolved_cli_version=$version"
    printf '%s\n' "$current"
    exit 0
  fi
  fail "managed sandbox CLI is stale or corrupt; remove $root/current and rerun bootstrap with an approved release manifest"
}

resolve_path() {
  command -v "$APP_NAME" >/dev/null 2>&1 || return 1
  exe=$(command -v "$APP_NAME")
  case "$exe" in */*) ;; *) return 1 ;; esac
  is_abs "$exe" || return 1
  exe=$(cd "$(dirname "$exe")" && pwd -P)/$(basename "$exe")
  cwd=$(pwd -P)
  cwd_logical=${PWD:-$cwd}
  managed=$(managed_root_real)
  exe_dir=$(dirname "$exe")
  case "$exe" in "$cwd"/*|"$cwd_logical"/*)
    case "$exe" in "$managed"/*) ;; *) fail "refusing workspace-controlled PATH executable outside MAKESTAR_ADMIN_CLI_HOME: $exe" ;; esac
  esac
  case "$exe" in "$managed"/*) ;; *) [ ! -w "$exe_dir" ] || return 1 ;; esac
  version=$(check_executable_version "$exe" "${VERSION#v}") || return 1
  evidence "resolved_cli_path_category=path"
  evidence "resolved_cli_version=$version"
  printf '%s\n' "$exe"
  exit 0
}

download() {
  url=$1
  dest=$2
  require_plain_public_url "download" "$url"
  canonical_release_url "$url" || fail "non-canonical release URL rejected"
  case "$url" in *://127.*|*://10.*|*://192.168.*|*://localhost*|file:*) fail "private or local URL rejected" ;; esac
  if command -v curl >/dev/null 2>&1; then
    effective=$(curl -fLSs -o "$dest" -w '%{url_effective}' "$url") || fail "download failed for approved release URL"
    safe_download_url "$effective" || fail "download redirect left approved release boundary"
  else
    fail "network download requires curl in the Cowork sandbox so redirects can be verified"
  fi
}

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | sed 's/ .*//'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | sed 's/ .*//'
  else
    fail "sha256 verification tool missing"
  fi
}

manifest_field() {
  file=$1
  field=$2
  sed -n "s/.*\"$field\"[ ]*:[ ]*\"\([^\"]*\)\".*/\1/p" "$file" | sed -n '1p'
}

manifest_number() {
  file=$1
  field=$2
  sed -n "s/.*\"$field\"[ ]*:[ ]*\([0-9][0-9]*\).*/\1/p" "$file" | sed -n '1p'
}

asset_block() {
  awk '
    /\"assets\"[ ]*:[ ]*\[/ {in_assets=1}
    in_assets && !in_obj && /{/ {in_obj=1; depth=0; obj=""; found=0}
    in_obj {
      obj = obj $0 "\n"
      line = $0
      opens = gsub(/{/, "{", line)
      line = $0
      closes = gsub(/}/, "}", line)
      depth += opens - closes
      if ($0 ~ /\"name\"[ ]*:[ ]*\"makestar-admin-linux-x86_64.zip\"/) found=1
      if (depth <= 0) {
        if (found) {printf "%s", obj; exit}
        in_obj=0; obj=""; found=0
      }
    }
  ' "$1"
}

validate_archive_listing() {
  archive=$1
  tmp=$2
  command -v unzip >/dev/null 2>&1 || fail "unzip is required to extract the approved Linux CLI artifact"
  unzip -Z -1 "$archive" > "$tmp/list" || fail "cannot inspect artifact archive"
  [ -s "$tmp/list" ] || fail "artifact archive is empty"
  if duplicate=$(sort "$tmp/list" | uniq -d | sed -n '1p') && [ -n "$duplicate" ]; then
    fail "artifact archive contains duplicate entries"
  fi
  while IFS= read -r name; do
    case "$name" in
      /*|*'/../'*|../*|*'/..'|.) fail "unsafe archive path rejected: $name" ;;
      makestar-admin/*) ;;
      *) fail "unexpected archive layout rejected: $name" ;;
    esac
  done < "$tmp/list"
  grep '^makestar-admin/makestar-admin$' "$tmp/list" >/dev/null 2>&1 || fail "artifact archive missing expected executable layout"
  perms=$(unzip -Z -l "$archive" 2>/dev/null | sed -n '3,$p' || true)
  if printf '%s\n' "$perms" | grep '^[lcbps]' >/dev/null 2>&1; then
    fail "artifact archive contains symlink, device, or special entries"
  fi
}

install_cli() {
  os=$(uname -s 2>/dev/null || true)
  arch=$(uname -m 2>/dev/null || true)
  [ "$os" = Linux ] || fail "unsupported OS for Cowork bootstrap: $os"
  case "$arch" in x86_64|amd64) ;; *) fail "unsupported architecture for Cowork bootstrap: $arch" ;; esac
  if [ -z "$MANIFEST_URL" ]; then
    [ -n "$RELEASE_TAG" ] || fail "set MAKESTAR_ADMIN_CLI_RELEASE_TAG or MAKESTAR_ADMIN_CLI_MANIFEST_URL for a canonical public release"
    safe_version "$RELEASE_TAG" || fail "unsafe MAKESTAR_ADMIN_CLI_RELEASE_TAG"
    MANIFEST_URL="$APP_ORIGIN/$RELEASE_TAG/release-manifest.json"
  fi
  require_plain_public_url "manifest" "$MANIFEST_URL"
  canonical_release_url "$MANIFEST_URL" || fail "manifest URL must be the approved public release origin"
  release_dir=${MANIFEST_URL%/release-manifest.json}
  [ "$release_dir" != "$MANIFEST_URL" ] || fail "manifest URL must end with release-manifest.json"

  root=$(managed_root_real)
  tmp=$(mktemp -d "$root/.bootstrap.XXXXXX") || fail "cannot create bootstrap temp directory"
  trap 'rm -rf "$tmp"' EXIT HUP INT TERM
  manifest="$tmp/release-manifest.json"
  download "$MANIFEST_URL" "$manifest"
  block="$tmp/asset.json"
  asset_block "$manifest" > "$block"
  [ -s "$block" ] || fail "manifest is missing Linux x86_64 CLI asset"
  name=$(manifest_field "$block" name)
  platform=$(manifest_field "$block" platform)
  sha=$(manifest_field "$block" sha256)
  size=$(manifest_number "$block" size_bytes)
  version=$(manifest_field "$block" version)
  url=$(manifest_field "$block" canonical_asset_url)
  [ -n "$url" ] || url=$(manifest_field "$block" url)
  [ "$name" = "$APP_ASSET" ] || fail "manifest selected unexpected asset: $name"
  [ "$platform" = "$APP_PLATFORM" ] || fail "manifest selected unsupported platform: $platform"
  printf '%s' "$sha" | grep '^[0-9a-f][0-9a-f]*$' >/dev/null 2>&1 || fail "manifest sha256 missing or invalid"
  [ ${#sha} -eq 64 ] || fail "manifest sha256 must be 64 hex characters"
  [ -n "$size" ] && [ "$size" -gt 0 ] || fail "manifest size_bytes missing or invalid"
  [ -n "$version" ] || version=$(manifest_field "$manifest" cli_version)
  [ -n "$version" ] || version=$(manifest_field "$manifest" version)
  [ -n "$version" ] || fail "manifest version missing"
  safe_version "$version" || fail "manifest version is unsafe for managed install path"
  [ -z "$VERSION" ] || [ "${VERSION#v}" = "$version" ] || [ "$VERSION" = "$version" ] || fail "manifest version does not match requested version"
  [ -n "$url" ] || url="$release_dir/$APP_ASSET"
  require_plain_public_url "artifact" "$url"
  case "$url" in "$release_dir/$APP_ASSET") ;; *) fail "artifact URL leaves approved release boundary" ;; esac

  archive="$tmp/$APP_ASSET"
  download "$url" "$archive"
  actual_size=$(wc -c < "$archive" | tr -d ' ')
  [ "$actual_size" = "$size" ] || fail "artifact size mismatch"
  actual_sha=$(sha256_of "$archive")
  [ "$actual_sha" = "$sha" ] || fail "artifact checksum mismatch"
  validate_archive_listing "$archive" "$tmp"

  mkdir -p "$root/versions"
  versions_root=$(cd "$root/versions" 2>/dev/null && pwd -P) || fail "cannot resolve managed versions directory: $root/versions"
  install_root="$versions_root/$version"
  new_root="$root/.new-$version-$$"
  case "$install_root/" in "$versions_root"/*) ;; *) fail "managed install path escapes versions root" ;; esac
  case "$new_root" in "$root"/.new-*) ;; *) fail "managed staging path escapes MAKESTAR_ADMIN_CLI_HOME" ;; esac
  rm -rf "$new_root"
  mkdir -p "$new_root"
  unzip -q "$archive" -d "$new_root" || fail "artifact extraction failed"
  exe="$new_root/makestar-admin/makestar-admin"
  [ -f "$exe" ] || fail "extracted executable missing"
  chmod 755 "$exe" || fail "cannot mark executable usable"
  found=$(check_executable_version "$exe" "$version") || fail "post-install --version verification failed"
  rm -rf "$install_root.tmp"
  mv "$new_root/makestar-admin" "$install_root.tmp" || fail "cannot stage verified install"
  rm -rf "$install_root"
  mv "$install_root.tmp" "$install_root" || fail "cannot publish verified install"
  rm -rf "$root/current.new"
  ln -s "versions/$version" "$root/current.new" || fail "cannot create current marker"
  rm -rf "$root/current"
  mv -f "$root/current.new" "$root/current" || fail "cannot update current marker"
  evidence "resolved_cli_path_category=managed_sandbox"
  evidence "resolved_cli_version=$found"
  evidence "approved_artifact_source=$url"
  evidence "approved_artifact_sha256=$sha"
  printf '%s\n' "$root/current/$APP_NAME"
}

case "$MODE" in
  resolve)
    resolve_override || true
    resolve_managed || true
    resolve_path || true
    install_cli
    ;;
  install)
    install_cli
    ;;
  *) fail "usage: $0 [resolve|install]" ;;
esac
