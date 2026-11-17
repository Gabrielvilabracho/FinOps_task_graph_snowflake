#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/prepare_cortex_tooling.sh --check|--prepare

  --check    Validate the pinned lock and local prerequisites without network access.
  --prepare  Download pinned public archives to an external TMPDIR cache and copy
             the selected, unactivated skills into project-local .cortex/skills/.

This script never installs or invokes Cortex Code, Snowflake CLI, coding agents,
package managers, connection commands, SQL, or shell-profile changes.
EOF
}

case "${1:-}" in
  --check) mode="check" ;;
  --prepare) mode="prepare" ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

if (( $# != 1 )); then
  usage >&2
  exit 2
fi

script_dir="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(dirname -- "$script_dir")"
lock_path="$repo_root/.cortex/tooling.lock.json"

command -v python3 >/dev/null 2>&1 || {
  printf 'ERROR: python3 is required.\n' >&2
  exit 1
}

MODE="$mode" REPO_ROOT="$repo_root" LOCK_PATH="$lock_path" python3 - <<'PY'
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tarfile
import tempfile
from urllib.request import Request, urlopen

MODE = os.environ["MODE"]
REPO_ROOT = Path(os.environ["REPO_ROOT"]).resolve()
LOCK_PATH = Path(os.environ["LOCK_PATH"]).resolve()
SKILLS_DIR = REPO_ROOT / ".cortex" / "skills"
ALLOWED_REPOSITORIES = {
    "Snowflake-Labs/snowflake-ai-kit",
    "Snowflake-Labs/coco-skills",
}
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def safe_relative(value: str, label: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "." in path.parts:
        fail(f"{label} must be a normalized relative path: {value!r}")
    return path


def load_and_validate_lock() -> dict:
    if not LOCK_PATH.is_file():
        fail(f"lock file not found: {LOCK_PATH}")
    try:
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot read lock file: {error}")

    if set(lock) != {"schema_version", "resolved_at", "sources"}:
        fail("lock file has unexpected top-level fields")
    if lock["schema_version"] != 1:
        fail("unsupported lock schema_version")
    if not isinstance(lock["resolved_at"], str) or not lock["resolved_at"]:
        fail("resolved_at must be a non-empty string")
    if not isinstance(lock["sources"], list) or not lock["sources"]:
        fail("sources must be a non-empty list")

    source_ids = set()
    destinations = set()
    for source in lock["sources"]:
        required = {
            "id", "repository", "revision", "archive_url", "resolved_from",
            "license_paths", "skills",
        }
        if not isinstance(source, dict) or set(source) != required:
            fail("each source must contain only the documented fields")
        source_id = source["id"]
        repository = source["repository"]
        revision = source["revision"]
        if not isinstance(source_id, str) or not NAME_PATTERN.fullmatch(source_id):
            fail(f"invalid source id: {source_id!r}")
        if source_id in source_ids:
            fail(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
        if repository not in ALLOWED_REPOSITORIES:
            fail(f"repository is not allow-listed: {repository!r}")
        if not isinstance(revision, str) or not SHA_PATTERN.fullmatch(revision):
            fail(f"revision must be an exact lowercase 40-character SHA: {source_id}")
        expected_archive = f"https://codeload.github.com/{repository}/tar.gz/{revision}"
        expected_resolution = f"https://api.github.com/repos/{repository}/commits/main"
        if source["archive_url"] != expected_archive:
            fail(f"archive_url is not the pinned codeload URL for {source_id}")
        if source["resolved_from"] != expected_resolution:
            fail(f"resolved_from is not the public GitHub main-commit endpoint for {source_id}")
        if not isinstance(source["license_paths"], list):
            fail(f"license_paths must be a list for {source_id}")
        for license_path in source["license_paths"]:
            if not isinstance(license_path, str):
                fail(f"license path must be a string for {source_id}")
            safe_relative(license_path, "license path")
        if not isinstance(source["skills"], list) or not source["skills"]:
            fail(f"skills must be a non-empty list for {source_id}")
        for skill in source["skills"]:
            if not isinstance(skill, dict) or set(skill) != {"source", "destination"}:
                fail(f"invalid skill entry for {source_id}")
            if not isinstance(skill["source"], str):
                fail(f"skill source must be a string for {source_id}")
            safe_relative(skill["source"], "skill source")
            destination = skill["destination"]
            if not isinstance(destination, str) or not NAME_PATTERN.fullmatch(destination):
                fail(f"invalid skill destination: {destination!r}")
            if destination in destinations:
                fail(f"duplicate skill destination: {destination}")
            destinations.add(destination)
    return lock


def validate_existing_destinations(lock: dict) -> None:
    if not SKILLS_DIR.exists():
        print("Target state: .cortex/skills/ does not exist (nothing is activated).")
        return
    if not SKILLS_DIR.is_dir():
        fail(f"target exists but is not a directory: {SKILLS_DIR}")
    for source in lock["sources"]:
        for skill in source["skills"]:
            target = SKILLS_DIR / skill["destination"]
            if not target.exists():
                continue
            marker = target / ".source-lock.json"
            skill_file = target / "SKILL.md"
            if not target.is_dir() or not marker.is_file() or not skill_file.is_file():
                fail(f"existing destination is unmanaged or incomplete: {target}")
            try:
                metadata = json.loads(marker.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                fail(f"invalid source marker at {marker}: {error}")
            expected = {
                "repository": source["repository"],
                "revision": source["revision"],
                "source": skill["source"],
            }
            if metadata != expected:
                fail(f"existing destination has a different source lock: {target}")


def extract_archive(archive: Path, destination: Path, expected_root: str) -> Path:
    with tarfile.open(archive, mode="r:gz") as bundle:
        members = bundle.getmembers()
        if not members:
            fail(f"downloaded archive is empty: {archive}")
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts:
                fail(f"unsafe archive path: {member.name!r}")
            if not path.parts or path.parts[0] != expected_root:
                fail(f"archive has unexpected root: {member.name!r}")
            if not (member.isfile() or member.isdir()):
                fail(f"archive contains an unsupported entry type: {member.name!r}")
        bundle.extractall(destination, members=members)
    extracted = destination / expected_root
    if not extracted.is_dir():
        fail(f"expected archive root was not extracted: {expected_root}")
    return extracted


def ensure_cache(source: dict, cache_root: Path) -> Path:
    cache = cache_root / f"{source['id']}-{source['revision']}"
    marker = cache / ".pinned-revision"
    if cache.exists():
        if not cache.is_dir() or not marker.is_file():
            fail(f"external cache is incomplete; move it aside and retry: {cache}")
        if marker.read_text(encoding="utf-8").strip() != source["revision"]:
            fail(f"external cache marker does not match its path: {cache}")
        return cache

    cache_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{source['id']}-", dir=cache_root) as temporary:
        temporary_path = Path(temporary)
        archive = temporary_path / "source.tar.gz"
        request = Request(source["archive_url"], headers={"User-Agent": "finops-cortex-tooling/1"})
        print(f"Downloading {source['repository']}@{source['revision']} ...")
        try:
            with urlopen(request, timeout=60) as response, archive.open("wb") as output:
                if response.geturl().split("?", 1)[0] != source["archive_url"]:
                    fail(f"archive request redirected outside the pinned URL: {response.geturl()}")
                shutil.copyfileobj(response, output)
        except OSError as error:
            fail(f"download failed for {source['id']}: {error}")
        owner, repository_name = source["repository"].split("/", 1)
        del owner
        expected_root = f"{repository_name}-{source['revision']}"
        extracted = extract_archive(archive, temporary_path / "extracted", expected_root)
        (extracted / ".pinned-revision").write_text(source["revision"] + "\n", encoding="utf-8")
        extracted.replace(cache)
    return cache


def copy_selected(lock: dict, caches: dict[str, Path]) -> None:
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    # This project-local ignore file is generated only during explicit preparation.
    # Its wildcard also ignores itself, so downloaded artifacts never enter Git status.
    (SKILLS_DIR / ".gitignore").write_text("*\n", encoding="utf-8")

    for source in lock["sources"]:
        cache = caches[source["id"]]
        for skill in source["skills"]:
            source_path = cache.joinpath(*PurePosixPath(skill["source"]).parts)
            target = SKILLS_DIR / skill["destination"]
            if not (source_path / "SKILL.md").is_file():
                fail(f"selected skill has no SKILL.md: {source_path}")
            if target.exists():
                print(f"Already prepared: {target.relative_to(REPO_ROOT)}")
                continue
            shutil.copytree(source_path, target)
            metadata = {
                "repository": source["repository"],
                "revision": source["revision"],
                "source": skill["source"],
            }
            (target / ".source-lock.json").write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(f"Prepared for review: {target.relative_to(REPO_ROOT)}")

        if source["license_paths"]:
            license_target = SKILLS_DIR / "_source-licenses" / source["id"] / source["revision"]
            if not license_target.exists():
                license_target.mkdir(parents=True)
                for relative in source["license_paths"]:
                    source_license = cache.joinpath(*PurePosixPath(relative).parts)
                    if not source_license.is_file():
                        fail(f"declared license file is missing: {source_license}")
                    shutil.copy2(source_license, license_target / source_license.name)


lock = load_and_validate_lock()
validate_existing_destinations(lock)
print(f"Lock valid: {len(lock['sources'])} pinned public sources.")
print(f"Selected skills: {sum(len(source['skills']) for source in lock['sources'])}.")

if MODE == "check":
    print("Check complete: no network, Snowflake, credentials, or files were accessed outside the project lock and target state.")
    sys.exit(0)

tmpdir = Path(os.environ.get("TMPDIR", tempfile.gettempdir())).resolve()
if not tmpdir.is_dir():
    fail(f"TMPDIR is not a directory: {tmpdir}")
cache_root = tmpdir / "finops-cortex-tooling-cache"
caches = {source["id"]: ensure_cache(source, cache_root) for source in lock["sources"]}
copy_selected(lock, caches)
print("Preparation complete. Skills were copied for inspection only; nothing was installed or activated.")
print(f"External cache: {cache_root}")
PY
