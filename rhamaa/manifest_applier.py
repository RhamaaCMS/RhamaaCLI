"""
Manifest Applier for RhamaaCLI
Orchestrates the application of AppManifest configurations to a Django project.
"""

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .manifest import AppManifest, ManifestParser
from .config_utils import (
    SettingsParser, URLParser, 
    find_settings_file, find_urls_file, create_app_urls_py
)
from .utils import is_github_repo_url
from .dependency_resolver import DependencyResolver
from .conflict_detector import ConflictDetector, Conflict


console = Console()


@dataclass
class ApplyResult:
    """Result of applying a manifest."""
    success: bool
    changes: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    backup_files: List[Path] = field(default_factory=list)
    
    def __bool__(self):
        return self.success


class ManifestApplier:
    """
    Applies an AppManifest to a Django project.
    
    Handles:
    - Settings modifications (apps, middleware, templates, auth, custom settings)
    - URL configuration
    - Post-install hooks (migrations, fixtures, commands)
    - Backup creation
    - Dry-run mode
    """
    
    def __init__(self, manifest: AppManifest, project_path: Path, app_name: str):
        """
        Initialize applier.
        
        Args:
            manifest: The parsed and resolved AppManifest
            project_path: Path to Django project root
            app_name: The name given during installation
        """
        self.manifest = manifest
        self.project_path = project_path
        self.app_name = app_name
        self.changes: List[str] = []
        self.backup_files: List[Path] = []
        self.modified_files: List[Path] = []
        
        # Find project files
        self.settings_file = find_settings_file(project_path)
        self.urls_file = find_urls_file(project_path)
        self.app_dir = project_path / "apps" / app_name
    
    def apply_all(self, dry_run: bool = False, backup: bool = False) -> ApplyResult:
        """
        Apply all manifest configurations.
        
        Args:
            dry_run: If True, preview changes without applying
            backup: If True, create .bak files before modifications
        
        Returns:
            ApplyResult with status and details
        """
        errors = []
        warnings = []
        
        try:
            compatibility_errors = self._check_project_compatibility()
            if compatibility_errors:
                return ApplyResult(success=False, errors=compatibility_errors)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # 1. Apply Django settings
                task = progress.add_task("Applying settings...", total=None)
                if self.settings_file:
                    result = self._apply_settings(dry_run, backup)
                    if result:
                        self.changes.append(f"Modified settings: {self.settings_file.name}")
                else:
                    warnings.append("Could not find settings file")
                progress.remove_task(task)

                task = progress.add_task("Applying environment defaults...", total=None)
                if self._apply_env(dry_run, backup):
                    self.changes.append(f"Modified environment template: {self.manifest.env.file}")
                progress.remove_task(task)
                
                # 2. Apply URL configuration
                task = progress.add_task("Applying URLs...", total=None)
                if self.urls_file:
                    result = self._apply_urls(dry_run, backup)
                    if result:
                        self.changes.append(f"Modified URLs: {self.urls_file.name}")
                else:
                    warnings.append("Could not find urls.py")
                progress.remove_task(task)
                
                # 3. Create app urls.py if needed
                task = progress.add_task("Creating app URLs...", total=None)
                if not dry_run and self.app_dir.exists():
                    urls_path = create_app_urls_py(self.app_dir, self.app_name)
                    self.changes.append(f"Created app urls.py: apps/{self.app_name}/urls.py")
                progress.remove_task(task)
                
                # 4. Run post-install if not dry_run
                if not dry_run:
                    task = progress.add_task("Running post-install...", total=None)
                    post_changes = self._run_post_install()
                    self.changes.extend(post_changes)
                    progress.remove_task(task)
            
            return ApplyResult(
                success=len(errors) == 0,
                changes=self.changes,
                errors=errors,
                warnings=warnings,
                backup_files=self.backup_files
            )
            
        except Exception as e:
            errors.append(f"Error applying manifest: {e}")
            return ApplyResult(
                success=False,
                changes=self.changes,
                errors=errors,
                warnings=warnings,
                backup_files=self.backup_files
            )
    
    def _apply_settings(self, dry_run: bool, backup: bool) -> bool:
        """Apply Django settings from manifest."""
        if not self.settings_file:
            return False
        
        parser = SettingsParser(self.settings_file)
        modified = False
        
        # 1. Add INSTALLED_APPS
        for app in self.manifest.django.installed_apps:
            if parser.add_installed_app(app):
                modified = True
                self.changes.append(f"  + Added '{app}' to INSTALLED_APPS")
        
        # 2. Add middleware
        for mw in self.manifest.django.middleware:
            position = mw.position if hasattr(mw, 'position') else None
            if parser.add_middleware(mw.class_path, position):
                modified = True
                self.changes.append(f"  + Added middleware: {mw.class_path}")
        
        # 3. Add template directories
        if self.manifest.django.templates:
            if parser.add_template_dirs(self.manifest.django.templates.dirs):
                modified = True
                for d in self.manifest.django.templates.dirs:
                    self.changes.append(f"  + Added template dir: {d}")
            
            # Add context processors
            if parser.add_context_processors(self.manifest.django.templates.context_processors):
                modified = True
                for cp in self.manifest.django.templates.context_processors:
                    self.changes.append(f"  + Added context processor: {cp}")
        
        # 4. Add auth backends
        if self.manifest.django.auth_backends:
            if parser.add_auth_backends(self.manifest.django.auth_backends):
                modified = True
                for backend in self.manifest.django.auth_backends:
                    self.changes.append(f"  + Added auth backend: {backend}")
        
        # 5. Set custom settings
        for key, value in self.manifest.django.settings.items():
            setting_value = value.get("default") if isinstance(value, dict) and "default" in value else value
            if parser.set_setting(key, setting_value):
                modified = True
                self.changes.append(f"  + Set {key} = {setting_value}")
        
        # 6. Add staticfiles dirs
        if self.manifest.staticfiles and self.manifest.staticfiles.dirs:
            if parser.add_staticfiles_dirs(self.manifest.staticfiles.dirs):
                modified = True
                for d in self.manifest.staticfiles.dirs:
                    self.changes.append(f"  + Added staticfiles dir: {d}")
        
        # Write changes if not dry_run
        if modified and not dry_run:
            if backup:
                backup_path = self.settings_file.with_suffix('.py.bak')
                self.backup_files.append(backup_path)
            parser.write(backup=backup)
        
        return modified

    def _check_project_compatibility(self) -> List[str]:
        """Validate host-app requirements before changing project files."""
        errors = []
        if self.manifest.django.installed_apps and not self.settings_file:
            errors.append("Could not find Django settings file.")
            return errors

        settings_content = self.settings_file.read_text(encoding="utf-8") if self.settings_file else ""
        for dependency in self.manifest.dependencies.apps:
            # Dotted dependencies are host Django apps, not registry keys.
            if "." in dependency and dependency not in settings_content:
                errors.append(
                    f"Required Django app '{dependency}' is missing. "
                    "Install this app on a compatible RhamaaCMS template."
                )
        for capability in self.manifest.dependencies.capabilities:
            if capability not in settings_content:
                errors.append(
                    f"Project capability '{capability}' is missing. "
                    "Use the required RhamaaCMS project template/branch."
                )
        return errors
    
    def _apply_urls(self, dry_run: bool, backup: bool) -> bool:
        """Apply URL configurations from manifest."""
        if not self.urls_file or not self.manifest.urls:
            return False
        
        parser = URLParser(self.urls_file)
        modified = False
        
        for url_config in self.manifest.urls:
            url_dict = {
                'path': url_config.path,
                'include': url_config.include,
                'namespace': url_config.namespace,
                'name': url_config.name
            }
            
            if parser.add_url_config(url_dict):
                modified = True
                ns_str = f" (namespace={url_config.namespace})" if url_config.namespace else ""
                self.changes.append(f"  + Added URL: {url_config.path} -> {url_config.include}{ns_str}")
        
        # Write changes if not dry_run
        if modified and not dry_run:
            if backup:
                backup_path = self.urls_file.with_suffix('.py.bak')
                self.backup_files.append(backup_path)
            parser.write(backup=backup)
        
        return modified

    def _apply_env(self, dry_run: bool, backup: bool) -> bool:
        if not self.manifest.env or not self.manifest.env.variables:
            return False
        project_root = self.project_path.resolve()
        env_path = (project_root / self.manifest.env.file).resolve()
        if env_path != project_root and project_root not in env_path.parents:
            raise RuntimeError("Environment template path escapes project directory.")
        content = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
        additions = []
        for variable in self.manifest.env.variables:
            if any(line.split("=", 1)[0].strip() == variable.key for line in content.splitlines() if "=" in line):
                continue
            if variable.description:
                additions.append(f"# {variable.description}")
            value = "" if variable.default is None else str(variable.default)
            additions.append(f"{variable.key}={value}")
        if not additions:
            return False
        if not dry_run:
            if backup and env_path.exists():
                backup_path = env_path.with_suffix(env_path.suffix + ".bak")
                backup_path.write_text(content, encoding="utf-8")
                self.backup_files.append(backup_path)
            separator = "\n" if content.endswith("\n") or not content else "\n\n"
            env_path.write_text(content + separator + "\n".join(additions) + "\n", encoding="utf-8")
        return True
    
    def _run_post_install(self) -> List[str]:
        """Run post-installation tasks."""
        changes = []
        post = self.manifest.post_install
        
        if not post:
            return changes
        
        # 1. Apply migrations shipped by the prebuilt app. Schema ownership
        # stays in app repository; installer must never generate migrations.
        if post.migrations:
            app_label = self.manifest.django.app_label
            command = [sys.executable, "manage.py", "migrate"]
            if app_label:
                command.append(app_label)
            result = subprocess.run(
                command,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip()
                raise RuntimeError(f"Migration failed: {detail}")
            suffix = f" for {app_label}" if app_label else ""
            changes.append(f"  ✓ Applied migrations{suffix}")
        
        # 2. Load fixtures
        for fixture_path in post.fixtures:
            try:
                # Resolve placeholder in fixture path
                fixture_full = fixture_path.replace('{app_name}', self.app_name)
                fixture_full = fixture_full.replace('{app_class}', self.app_name.title().replace('_', ''))
                
                result = subprocess.run(
                    [sys.executable, "manage.py", "loaddata", fixture_full],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    changes.append(f"  ✓ Loaded fixture: {fixture_full}")
                else:
                    changes.append(f"  ⚠ Fixture not found: {fixture_full}")
            except Exception as e:
                changes.append(f"  ⚠ Fixture error: {e}")
        
        # 3. Run management commands
        for cmd_config in post.management_commands:
            if not cmd_config.get('run_on_install', False):
                continue
            try:
                cmd = cmd_config.get('command', '')
                args = cmd_config.get('args', [])
                kwargs = cmd_config.get('kwargs', {})
                
                if not cmd:
                    continue
                
                # Build command
                cmd_parts = [sys.executable, "manage.py", cmd] + args
                for key, value in kwargs.items():
                    cmd_parts.extend([f"--{key}", str(value)])
                
                result = subprocess.run(
                    cmd_parts,
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    changes.append(f"  ✓ Ran command: {cmd}")
                else:
                    detail = (result.stderr or result.stdout).strip()
                    raise RuntimeError(f"Command failed: {cmd}: {detail}")
            except Exception as e:
                raise RuntimeError(f"Post-install command error: {e}") from e
        
        # 4. Show messages
        if post.messages:
            changes.append("  📋 Post-install messages:")
            for msg in post.messages:
                changes.append(f"    - {msg}")
        
        return changes
    
    def preview_changes(self) -> List[str]:
        """
        Preview all changes that would be made (dry-run).
        """
        result = self.apply_all(dry_run=True, backup=False)
        return result.changes
    
    def rollback(self) -> bool:
        """
        Rollback changes by restoring from backup files.
        Returns True if successful.
        """
        if not self.backup_files:
            return False
        
        success = True
        for backup_file in self.backup_files:
            if backup_file.exists():
                try:
                    original = backup_file.with_suffix('')
                    original.write_text(backup_file.read_text(), encoding='utf-8')
                    backup_file.unlink()
                except Exception as e:
                    console.print(f"[red]Failed to rollback {backup_file}: {e}[/red]")
                    success = False
        
        return success


def install_app_with_manifest(
    app_name: str,
    prebuild_key: str,
    force: bool = False,
    dry_run: bool = False,
    backup: bool = False,
    resolve_deps: bool = True,
    ignore_conflicts: bool = False,
    branch: Optional[str] = None
) -> ApplyResult:
    """
    High-level function to install an app with its manifest.
    
    This function:
    1. Downloads the prebuilt app
    2. Finds and parses the manifest
    3. Resolves dependencies
    4. Detects conflicts
    5. Applies the configuration
    """
    from .utils import download_github_repo, extract_repo_to_apps
    from .commands.cms.startapp import load_app_registry
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    project_path = Path.cwd()
    app_dir = project_path / "apps" / app_name
    
    # Check if app already exists
    if app_dir.exists() and not force:
        return ApplyResult(
            success=False,
            errors=[f"App '{app_name}' already exists. Use --force to overwrite."]
        )
    
    custom_repo = is_github_repo_url(prebuild_key)
    app_info = None
    if custom_repo:
        app_info = {'repository': prebuild_key, 'name': app_name}
    else:
        registry = load_app_registry()
        app_info = registry.get(prebuild_key)
        if not app_info:
            return ApplyResult(
                success=False,
                errors=[f"Prebuilt app '{prebuild_key}' not found in registry."]
            )
    
    # Download the app
    console.print(f"[cyan]Installing {app_info['name']}...[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Downloading...", total=None)
        
        # Download
        selected_branch = branch or app_info.get('branch') or 'main'
        zip_path = download_github_repo(app_info['repository'], selected_branch)
        
        if not zip_path:
            return ApplyResult(
                success=False,
                errors=["Failed to download app"]
            )
        
        progress.update(task, description="Extracting...")
        
        # Extract
        success = extract_repo_to_apps(zip_path, app_name, progress, task)
        if not success:
            return ApplyResult(
                success=False,
                errors=["Failed to extract app"]
            )
        
        progress.remove_task(task)
    
    # Find and parse manifest
    manifest_path = ManifestParser.find_manifest(app_dir)
    
    if not manifest_path:
        if custom_repo:
            return ApplyResult(
                success=False,
                errors=["Missing rhamaa-app.json manifest in repository. Custom GitHub app installs require a rhamaa-app.json manifest at repo root."]
            )
        # No manifest, use basic auto-config
        from .config_utils import auto_configure_app
        changes = auto_configure_app(app_name, project_path, dry_run, backup)
        return ApplyResult(
            success=True,
            changes=changes,
            warnings=["No manifest found, using basic auto-configuration"]
        )
    
    # Parse manifest
    manifest, errors = ManifestParser.load(manifest_path)
    
    if not manifest:
        return ApplyResult(
            success=False,
            errors=errors
        )

    if manifest.package_name and manifest.package_name != app_name:
        return ApplyResult(
            success=False,
            errors=[
                f"This app must be installed as '{manifest.package_name}' "
                f"(received '{app_name}')."
            ],
        )
    
    # Resolve placeholders
    manifest = manifest.resolve_placeholders(app_name)
    
    # Check for conflicts if not ignored
    if not ignore_conflicts:
        detector = ConflictDetector({app_name: manifest.to_dict()})
        conflicts = detector.detect_all_conflicts()
        
        if conflicts:
            report = detector.generate_resolution_report(conflicts)
            console.print(report)
            
            critical = [c for c in conflicts if c.severity == 'error']
            if critical:
                return ApplyResult(
                    success=False,
                    errors=[f"{len(critical)} critical conflict(s) found. Use --ignore-conflicts to proceed."],
                    warnings=[report]
                )
    
    # Apply manifest
    applier = ManifestApplier(manifest, project_path, app_name)
    result = applier.apply_all(dry_run, backup)
    
    if result.success:
        console.print(f"[green]✓[/green] Successfully installed '{app_name}'")
        for change in result.changes:
            console.print(f"  {change}")
    else:
        console.print(f"[red]✗[/red] Installation failed")
        for error in result.errors:
            console.print(f"  [red]{error}[/red]")
    
    return result
