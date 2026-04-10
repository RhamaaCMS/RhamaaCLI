"""
Utility functions for RhamaaCLI
"""

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


def _is_within_dir(child: Path, parent: Path) -> bool:
    try:
        child_resolved = child.resolve()
        parent_resolved = parent.resolve()
    except FileNotFoundError:
        child_resolved = child.absolute()
        parent_resolved = parent.absolute()
    return child_resolved == parent_resolved or parent_resolved in child_resolved.parents


def safe_extract_zip(zip_path: str | Path, dest_dir: Path) -> None:
    """
    Safely extract a ZIP into dest_dir, preventing Zip Slip path traversal.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        dest_root = dest_dir.resolve()

        for member in zf.infolist():
            name = member.filename
            if not name or name.endswith("/"):
                continue

            target_path = (dest_dir / name).resolve()
            if not _is_within_dir(target_path, dest_root):
                raise ValueError(f"Unsafe ZIP entry path: {name}")

            target_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member, "r") as src, open(target_path, "wb") as dst:
                shutil.copyfileobj(src, dst)


def _pick_extracted_root(extract_dir: Path) -> Path:
    extract_dir = Path(extract_dir)
    entries = [p for p in extract_dir.iterdir() if p.name not in {".DS_Store"}]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extract_dir


def install_dir_to_apps(
    *,
    app_name: str,
    source_dir: Path,
    force: bool,
    dry_run: bool,
    operation: str = "copy",  # "copy" | "move"
) -> Path | None:
    """
    Install a directory into apps/<app_name> with consistent --force/--dry-run behavior.
    Returns the target app_dir on success, otherwise None.
    """
    apps_dir = Path("apps")
    app_dir = apps_dir / app_name

    if app_dir.exists() and not force:
        return None

    if dry_run:
        return app_dir

    apps_dir.mkdir(exist_ok=True)

    if app_dir.exists():
        if not _is_within_dir(app_dir, apps_dir):
            raise ValueError(f"Refusing to remove path outside apps/: {app_dir}")
        shutil.rmtree(app_dir)

    source_dir = Path(source_dir)
    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    if operation == "move":
        shutil.move(str(source_dir), str(app_dir))
    elif operation == "copy":
        shutil.copytree(source_dir, app_dir)
    else:
        raise ValueError(f"Unknown operation: {operation}")

    return app_dir


def install_zip_to_apps(
    *,
    zip_path: str | Path,
    app_name: str,
    force: bool,
    dry_run: bool,
    operation: str = "move",  # "copy" | "move"
    cleanup_zip: bool = False,
) -> Path | None:
    """
    Extract a ZIP into a temporary directory (Zip Slip-safe) and install its
    content into apps/<app_name> with consistent --force/--dry-run behavior.
    Returns the target app_dir on success, otherwise None.
    """
    zip_path = Path(zip_path)

    if dry_run:
        # No filesystem mutations; keep behavior consistent with install_dir_to_apps.
        return Path("apps") / app_name

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            safe_extract_zip(zip_path, tmp_path)
            extracted_root = _pick_extracted_root(tmp_path)

            return install_dir_to_apps(
                app_name=app_name,
                source_dir=extracted_root,
                force=force,
                dry_run=False,
                operation=operation,
            )
    finally:
        if cleanup_zip:
            try:
                if zip_path.exists():
                    zip_path.unlink()
            except OSError:
                # Best-effort cleanup only; extraction/install may have succeeded.
                pass


def download_github_repo(repo_url, branch="main", progress=None, task_id=None):
    """
    Download a GitHub repository as a ZIP file.

    Args:
        repo_url (str): GitHub repository URL
        branch (str): Branch to download (default: main)
        progress: Rich progress instance
        task_id: Progress task ID

    Returns:
        str: Path to downloaded ZIP file
    """
    # Convert GitHub URL to ZIP download URL
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]

    zip_url = f"{repo_url}/archive/refs/heads/{branch}.zip"

    try:
        if progress and task_id:
            progress.update(
                task_id, description="[cyan]Downloading repository...")

        response = requests.get(zip_url, stream=True)
        response.raise_for_status()

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with temp_file as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress and task_id and total_size > 0:
                        progress.update(
                            task_id, completed=downloaded, total=total_size)

        return temp_file.name

    except requests.RequestException as e:
        console.print(f"[red]Error downloading repository: {e}[/red]")
        return None


def extract_repo_to_apps(zip_path, app_name, progress=None, task_id=None):
    """
    Extract downloaded repository to apps/ directory.

    Args:
        zip_path (str): Path to ZIP file
        app_name (str): Name of the app
        progress: Rich progress instance
        task_id: Progress task ID

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if progress and task_id:
            progress.update(task_id, description="[cyan]Extracting files...")

        installed = install_zip_to_apps(
            zip_path=zip_path,
            app_name=app_name,
            force=True,  # callers already gate overwrite; preserve prior behavior
            dry_run=False,
            operation="move",
            cleanup_zip=True,
        )

        if not installed:
            return False

        if progress and task_id:
            progress.update(task_id, description="[green]Extraction complete!")

        return True

    except Exception as e:
        console.print(f"[red]Error extracting repository: {e}[/red]")
        return False


def check_wagtail_project():
    """
    Check if current directory is a Wagtail project.

    Returns:
        bool: True if it's a Wagtail project, False otherwise
    """
    # Check if manage.py exists (primary indicator of Django project)
    manage_py = Path("manage.py")
    if manage_py.exists():
        return True

    # Check for settings directory or file
    if Path("settings.py").exists() or Path("settings").is_dir():
        return True

    # Check for common Django/Wagtail project structure
    common_files = ["requirements.txt", "setup.py", "pyproject.toml"]
    if any(Path(f).exists() for f in common_files):
        return True

    return False
