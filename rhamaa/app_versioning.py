"""Current-only version tracking and safe replacement for registered apps."""

from __future__ import annotations

import json
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .manifest import AppManifest, ManifestParser
from .manifest_applier import ManifestApplier
from .utils import _pick_extracted_root, download_github_repo, safe_extract_zip
from .versions import parse_version


STATE_FILE = Path(".rhamaa") / "apps.json"
BACKUP_DIR = Path(".rhamaa") / "backups" / "apps"


def load_install_state(project_path: Path) -> Dict[str, Any]:
    path = project_path / STATE_FILE
    if not path.exists():
        return {"schema_version": 1, "apps": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid Rhamaa app state: {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("apps", {}), dict):
        raise ValueError(f"Invalid Rhamaa app state structure: {path}")
    data.setdefault("schema_version", 1)
    data.setdefault("apps", {})
    return data


def record_install(
    project_path: Path,
    *,
    registry_key: str,
    app_name: str,
    manifest: AppManifest,
    repository: str,
    branch: str,
) -> Path:
    """Persist installation identity only after successful configuration."""
    state = load_install_state(project_path)
    state["apps"][registry_key] = {
        "app_name": app_name,
        "slug": manifest.slug,
        "version": manifest.version,
        "repository": repository,
        "branch": branch,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    path = project_path / STATE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)
    return path


def _ignore_local_backups(project_path: Path) -> None:
    gitignore = project_path / ".gitignore"
    if not gitignore.exists():
        return
    content = gitignore.read_text(encoding="utf-8")
    rule = "/.rhamaa/backups/"
    if rule not in content.splitlines():
        separator = "" if not content or content.endswith("\n") else "\n"
        gitignore.write_text(
            content + separator + "# RhamaaCLI local app backups\n" + rule + "\n",
            encoding="utf-8",
        )


def installed_manifest(
    project_path: Path, registry_key: str, app_info: Dict[str, Any]
) -> tuple[str, Path, Optional[AppManifest], list[str]]:
    """Resolve tracked install, with manifest-based fallback for older projects."""
    state = load_install_state(project_path)
    tracked = state["apps"].get(registry_key, {})
    app_name = tracked.get("app_name") or app_info.get("install_name") or registry_key
    app_dir = project_path / "apps" / app_name
    manifest_path = ManifestParser.find_manifest(app_dir)
    if not manifest_path:
        return app_name, app_dir, None, [f"Installed manifest not found: {app_dir}"]
    manifest, errors = ManifestParser.load(manifest_path)
    return app_name, app_dir, manifest, errors


@dataclass
class UpdateResult:
    success: bool
    registry_key: str
    app_name: str = ""
    old_version: str = ""
    new_version: str = ""
    updated: bool = False
    backup_path: Optional[Path] = None
    changes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def update_registered_app(
    *,
    registry_key: str,
    app_info: Dict[str, Any],
    project_path: Path,
    dry_run: bool = False,
    reinstall: bool = False,
) -> UpdateResult:
    """Replace installed app with registry's only/current release."""
    app_name, app_dir, old_manifest, errors = installed_manifest(
        project_path, registry_key, app_info
    )
    result = UpdateResult(
        success=False,
        registry_key=registry_key,
        app_name=app_name,
        old_version=old_manifest.version if old_manifest else "",
        errors=list(errors),
    )
    if not old_manifest:
        return result

    expected_name = app_info.get("install_name")
    if expected_name and app_name != expected_name:
        result.errors.append(
            f"Registry app '{registry_key}' must be installed as '{expected_name}'."
        )
        return result

    repository = app_info.get("repository", "")
    branch = app_info.get("branch", "main")
    current_version = str(app_info.get("version", ""))
    if not repository or not current_version:
        result.errors.append("Registry entry requires repository and version.")
        return result

    try:
        old_number = parse_version(old_manifest.version)
        current_number = parse_version(current_version)
    except ValueError as exc:
        result.errors.append(str(exc))
        return result

    if old_number > current_number:
        result.errors.append(
            f"Installed {old_manifest.version} is newer than registry {current_version}; downgrade refused."
        )
        return result
    if old_number == current_number and not reinstall:
        result.success = True
        result.new_version = current_version
        result.changes.append("Already current")
        return result

    archive = download_github_repo(repository, branch)
    if not archive:
        result.errors.append("Failed to download current app source.")
        return result

    try:
        with tempfile.TemporaryDirectory(prefix="rhamaa-app-update-") as temp_dir:
            extracted = Path(temp_dir) / "source"
            safe_extract_zip(archive, extracted)
            source_root = _pick_extracted_root(extracted)
            source_manifest_path = ManifestParser.find_manifest(source_root)
            if not source_manifest_path:
                result.errors.append("Downloaded app has no rhamaa-app.json at repository root.")
                return result
            new_manifest, manifest_errors = ManifestParser.load(source_manifest_path)
            if not new_manifest:
                result.errors.extend(manifest_errors)
                return result
            result.new_version = new_manifest.version

            if parse_version(new_manifest.version) != current_number:
                result.errors.append(
                    f"Registry says {current_version}, downloaded manifest says {new_manifest.version}."
                )
                return result
            if new_manifest.slug != old_manifest.slug:
                result.errors.append(
                    f"App identity changed: {old_manifest.slug} -> {new_manifest.slug}."
                )
                return result
            if new_manifest.package_name and new_manifest.package_name != app_name:
                result.errors.append(
                    f"Downloaded app must be installed as '{new_manifest.package_name}'."
                )
                return result

            if dry_run:
                result.success = True
                result.updated = True
                result.changes.append(
                    f"Would replace {app_name} {old_manifest.version} -> {new_manifest.version}"
                )
                return result

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup_path = (
                project_path
                / BACKUP_DIR
                / app_name
                / f"{timestamp}-{old_manifest.version}"
            )
            _ignore_local_backups(project_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(app_dir, backup_path)
            result.backup_path = backup_path

            candidate = app_dir.parent / f".{app_name}.rhamaa-update-{uuid.uuid4().hex}"
            old_stash = app_dir.parent / f".{app_name}.rhamaa-old-{uuid.uuid4().hex}"
            shutil.copytree(source_root, candidate)
            try:
                app_dir.rename(old_stash)
                candidate.rename(app_dir)
            except Exception:
                if not app_dir.exists() and old_stash.exists():
                    old_stash.rename(app_dir)
                if candidate.exists():
                    shutil.rmtree(candidate)
                raise
            finally:
                if old_stash.exists() and app_dir.exists():
                    shutil.rmtree(old_stash)

            applied = ManifestApplier(
                new_manifest.resolve_placeholders(app_name), project_path, app_name
            ).apply_all(dry_run=False, backup=True)
            if not applied.success:
                result.errors.extend(applied.errors)
                result.errors.append(
                    "New code kept because database migration may be partially applied; restore manually from backup after reviewing DB state."
                )
                return result

            record_install(
                project_path,
                registry_key=registry_key,
                app_name=app_name,
                manifest=new_manifest,
                repository=repository,
                branch=branch,
            )
            result.success = True
            result.updated = True
            result.changes.extend(applied.changes)
            result.changes.insert(
                0, f"Replaced {app_name} {old_manifest.version} -> {new_manifest.version}"
            )
            return result
    except (OSError, ValueError) as exc:
        result.errors.append(str(exc))
        return result
    finally:
        try:
            Path(archive).unlink(missing_ok=True)
        except OSError:
            pass
