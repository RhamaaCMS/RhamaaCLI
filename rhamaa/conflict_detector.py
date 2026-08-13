"""
Conflict Detection for RhamaaCLI App Manifests
Detects and reports configuration conflicts between apps.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path


@dataclass
class Conflict:
    """Base class for configuration conflicts."""
    conflict_type: str
    apps: List[str]
    description: str
    severity: str  # 'warning', 'error', 'info'
    suggestions: List[str]


@dataclass
class SettingConflict(Conflict):
    """Conflict in Django settings."""
    setting_key: str
    values: Dict[str, Any]  # app -> value mapping
    
    def __init__(self, setting_key: str, values: Dict[str, Any], apps: List[str]):
        super().__init__(
            conflict_type='setting',
            apps=apps,
            description=f"Setting '{setting_key}' has different values across apps",
            severity='error',
            suggestions=[
                f"Choose one value for {setting_key}",
                "Consider creating a shared configuration",
                "Use environment variables for different values per environment"
            ]
        )
        self.setting_key = setting_key
        self.values = values


@dataclass
class MiddlewareConflict(Conflict):
    """Conflict in middleware ordering."""
    middleware_class: str
    positions: Dict[str, str]  # app -> position requirement
    
    def __init__(self, middleware_class: str, positions: Dict[str, str], apps: List[str]):
        super().__init__(
            conflict_type='middleware',
            apps=apps,
            description=f"Middleware '{middleware_class}' has conflicting position requirements",
            severity='warning',
            suggestions=[
                "Review middleware documentation for correct ordering",
                "Consider if both middlewares are actually needed",
                "Manual review of middleware order in settings.py"
            ]
        )
        self.middleware_class = middleware_class
        self.positions = positions


@dataclass
class URLConflict(Conflict):
    """Conflict in URL paths."""
    path: str
    includes: Dict[str, str]  # app -> include path
    
    def __init__(self, path: str, includes: Dict[str, str], apps: List[str]):
        super().__init__(
            conflict_type='url',
            apps=apps,
            description=f"URL path '{path}' is used by multiple apps",
            severity='error',
            suggestions=[
                f"Use different path prefixes (e.g., '{path}1/', '{path}2/')",
                "Merge the apps if they provide related functionality",
                "Use URL namespaces to distinguish"
            ]
        )
        self.path = path
        self.includes = includes


@dataclass
class TemplateDirConflict(Conflict):
    """Conflict in template directories."""
    template_dir: str
    apps: List[str]
    
    def __init__(self, template_dir: str, apps: List[str]):
        super().__init__(
            conflict_type='template_dir',
            apps=apps,
            description=f"Template directory '{template_dir}' is defined by multiple apps",
            severity='warning',
            suggestions=[
                "Ensure templates use unique subdirectories per app",
                "Consider template naming conventions"
            ]
        )
        self.template_dir = template_dir


class ConflictDetector:
    """
    Detect configuration conflicts between multiple app manifests.
    """
    
    def __init__(self, manifests: Dict[str, Any]):
        """
        Initialize with app manifests.
        
        Args:
            manifests: Dict of app_key -> AppManifest or dict
        """
        self.manifests = manifests
    
    def detect_all_conflicts(self) -> List[Conflict]:
        """
        Detect all types of conflicts.
        Returns list of Conflict objects.
        """
        conflicts = []
        
        conflicts.extend(self.detect_setting_conflicts())
        conflicts.extend(self.detect_middleware_conflicts())
        conflicts.extend(self.detect_url_conflicts())
        conflicts.extend(self.detect_template_conflicts())
        conflicts.extend(self.detect_installed_apps_conflicts())
        
        return conflicts
    
    def detect_setting_conflicts(self) -> List[SettingConflict]:
        """
        Detect conflicts in Django settings.
        Same setting key with different values across apps.
        """
        conflicts = []
        setting_values: Dict[str, Dict[str, Any]] = {}
        
        for app_key, manifest in self.manifests.items():
            django_config = manifest.get('django', {}) if isinstance(manifest, dict) else getattr(manifest, 'django', None)
            if not django_config:
                continue
            
            settings = django_config.get('settings', {}) if isinstance(django_config, dict) else getattr(django_config, 'settings', {})
            
            for key, value in settings.items():
                if key not in setting_values:
                    setting_values[key] = {}
                setting_values[key][app_key] = value
        
        # Find conflicts (same key, different values)
        for key, values in setting_values.items():
            if len(values) > 1:
                # Check if values are actually different
                unique_values = set(str(v) for v in values.values())
                if len(unique_values) > 1:
                    conflict = SettingConflict(
                        setting_key=key,
                        values=values,
                        apps=list(values.keys())
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def detect_middleware_conflicts(self) -> List[MiddlewareConflict]:
        """
        Detect middleware ordering conflicts.
        Same middleware with different position requirements.
        """
        conflicts = []
        middleware_positions: Dict[str, Dict[str, str]] = {}
        
        for app_key, manifest in self.manifests.items():
            django_config = manifest.get('django', {}) if isinstance(manifest, dict) else getattr(manifest, 'django', None)
            if not django_config:
                continue
            
            middleware_list = django_config.get('middleware', []) if isinstance(django_config, dict) else getattr(django_config, 'middleware', [])
            
            for mw in middleware_list:
                if isinstance(mw, dict):
                    mw_class = mw.get('class', '')
                    position = mw.get('position')
                else:
                    mw_class = str(mw)
                    position = None
                
                if not mw_class:
                    continue
                
                if mw_class not in middleware_positions:
                    middleware_positions[mw_class] = {}
                middleware_positions[mw_class][app_key] = position or 'default'
        
        # Find conflicts (same middleware, different positions)
        for mw_class, positions in middleware_positions.items():
            unique_positions = set(positions.values())
            if len(unique_positions) > 1 and any(p != 'default' for p in unique_positions):
                conflict = MiddlewareConflict(
                    middleware_class=mw_class,
                    positions=positions,
                    apps=list(positions.keys())
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def detect_url_conflicts(self) -> List[URLConflict]:
        """
        Detect URL path conflicts.
        Same URL path used by multiple apps.
        """
        conflicts = []
        path_apps: Dict[str, Dict[str, str]] = {}
        
        for app_key, manifest in self.manifests.items():
            urls = manifest.get('urls', []) if isinstance(manifest, dict) else getattr(manifest, 'urls', [])
            
            for url_config in urls:
                if isinstance(url_config, dict):
                    path = url_config.get('path', '')
                    include = url_config.get('include', '')
                else:
                    path = getattr(url_config, 'path', '')
                    include = getattr(url_config, 'include', '')
                
                if not path:
                    continue
                
                if path not in path_apps:
                    path_apps[path] = {}
                path_apps[path][app_key] = include
        
        # Find conflicts
        for path, includes in path_apps.items():
            if len(includes) > 1:
                conflict = URLConflict(
                    path=path,
                    includes=includes,
                    apps=list(includes.keys())
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def detect_template_conflicts(self) -> List[TemplateDirConflict]:
        """
        Detect template directory conflicts.
        """
        conflicts = []
        dir_apps: Dict[str, Set[str]] = {}
        
        for app_key, manifest in self.manifests.items():
            django_config = manifest.get('django', {}) if isinstance(manifest, dict) else getattr(manifest, 'django', None)
            if not django_config:
                continue
            
            templates = django_config.get('templates', {}) if isinstance(django_config, dict) else getattr(django_config, 'templates', None)
            if not templates:
                continue
            
            dirs = templates.get('dirs', []) if isinstance(templates, dict) else getattr(templates, 'dirs', [])
            
            for dir_path in dirs:
                if dir_path not in dir_apps:
                    dir_apps[dir_path] = set()
                dir_apps[dir_path].add(app_key)
        
        # Find conflicts
        for dir_path, apps in dir_apps.items():
            if len(apps) > 1:
                conflict = TemplateDirConflict(
                    template_dir=dir_path,
                    apps=list(apps)
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def detect_installed_apps_conflicts(self) -> List[Conflict]:
        """
        Detect potential conflicts in INSTALLED_APPS.
        Same third-party app with potentially different versions.
        """
        conflicts = []
        third_party_apps: Dict[str, Set[str]] = {}
        
        for app_key, manifest in self.manifests.items():
            django_config = manifest.get('django', {}) if isinstance(manifest, dict) else getattr(manifest, 'django', None)
            if not django_config:
                continue
            
            installed_apps = django_config.get('installed_apps', []) if isinstance(django_config, dict) else getattr(django_config, 'installed_apps', [])
            
            for app in installed_apps:
                # Skip apps.{name} pattern (local apps)
                if app.startswith('apps.') or app.startswith('.'):
                    continue
                
                # Track third-party apps
                if app not in third_party_apps:
                    third_party_apps[app] = set()
                third_party_apps[app].add(app_key)
        
        # Check for potential version conflicts via dependencies
        for app_key, manifest in self.manifests.items():
            deps = manifest.get('dependencies', {}) if isinstance(manifest, dict) else getattr(manifest, 'dependencies', None)
            if not deps:
                continue
            
            packages = deps.get('packages', []) if isinstance(deps, dict) else getattr(deps, 'packages', [])
            
            # Check for version specifiers in packages
            for package in packages:
                # This is a simplified check - in real scenario, parse semver
                pass
        
        return conflicts
    
    def generate_resolution_report(self, conflicts: List[Conflict]) -> str:
        """
        Generate human-readable conflict report.
        """
        if not conflicts:
            return "✅ No conflicts detected."
        
        lines = [f"⚠️  Found {len(conflicts)} potential conflict(s):\n"]
        
        for i, conflict in enumerate(conflicts, 1):
            lines.append(f"{i}. [{conflict.severity.upper()}] {conflict.conflict_type}")
            lines.append(f"   Apps: {', '.join(conflict.apps)}")
            lines.append(f"   {conflict.description}")
            lines.append("   Suggestions:")
            for suggestion in conflict.suggestions:
                lines.append(f"   - {suggestion}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def get_safe_install_order(self, target_app: str) -> Tuple[bool, List[str], List[Conflict]]:
        """
        Get safe installation order considering conflicts.
        
        Returns:
            Tuple of (is_safe, install_order, critical_conflicts)
        """
        # This is a simplified version - in practice, you'd use DependencyResolver
        conflicts = self.detect_all_conflicts()
        
        # Filter critical conflicts (errors)
        critical = [c for c in conflicts if c.severity == 'error']
        
        if critical:
            return False, [], critical
        
        # For now, return target_app only
        # Full implementation would integrate with DependencyResolver
        return True, [target_app], []


# Example usage
if __name__ == "__main__":
    # Example manifests
    manifests = {
        'app1': {
            'django': {
                'settings': {
                    'AUTH_USER_MODEL': 'users.User'
                },
                'middleware': [
                    {'class': 'X', 'position': 'after:Session'}
                ],
                'templates': {
                    'dirs': ['app1/templates']
                }
            },
            'urls': [{'path': 'api/', 'include': 'app1.urls'}]
        },
        'app2': {
            'django': {
                'settings': {
                    'AUTH_USER_MODEL': 'members.Member'  # CONFLICT!
                },
                'middleware': [
                    {'class': 'X', 'position': 'before:Session'}  # CONFLICT!
                ],
                'templates': {
                    'dirs': ['app1/templates']  # CONFLICT!
                }
            },
            'urls': [{'path': 'api/', 'include': 'app2.urls'}]  # CONFLICT!
        }
    }
    
    detector = ConflictDetector(manifests)
    conflicts = detector.detect_all_conflicts()
    
    print(detector.generate_resolution_report(conflicts))
