"""
App Manifest System for RhamaaCLI
Parses and applies rhamaa-app.json configuration
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class MiddlewareConfig:
    """Configuration for Django middleware."""
    class_path: str
    priority: int = 50
    position: Optional[str] = None  # "after:X" or "before:X"
    
    @classmethod
    def from_dict(cls, data: dict) -> "MiddlewareConfig":
        if isinstance(data, str):
            return cls(class_path=data)
        return cls(
            class_path=data.get("class", data.get("middleware", "")),
            priority=data.get("priority", 50),
            position=data.get("position")
        )


@dataclass
class URLConfig:
    """Configuration for URL patterns."""
    path: str
    include: str
    namespace: Optional[str] = None
    name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "URLConfig":
        return cls(
            path=data.get("path", ""),
            include=data.get("include", ""),
            namespace=data.get("namespace"),
            name=data.get("name")
        )


@dataclass
class TemplateConfig:
    """Configuration for Django templates."""
    dirs: List[str] = field(default_factory=list)
    context_processors: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "TemplateConfig":
        return cls(
            dirs=data.get("dirs", []),
            context_processors=data.get("context_processors", [])
        )


@dataclass
class Dependencies:
    """App and package dependencies."""
    apps: List[str] = field(default_factory=list)
    packages: List[str] = field(default_factory=list)
    optional_apps: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Dependencies":
        return cls(
            apps=data.get("apps", []),
            packages=data.get("packages", []),
            optional_apps=data.get("optional_apps", []),
            capabilities=data.get("capabilities", []),
        )


@dataclass
class PostInstallConfig:
    """Post-installation tasks."""
    migrations: bool = True
    fixtures: List[str] = field(default_factory=list)
    management_commands: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "PostInstallConfig":
        commands = data.get("management_commands", [])
        # Normalize command format
        normalized_commands = []
        for cmd in commands:
            if isinstance(cmd, str):
                normalized_commands.append({
                    "command": cmd,
                    "args": [],
                    "kwargs": {},
                    "run_on_install": False,
                })
            else:
                normalized_commands.append({
                    "command": cmd.get("command", ""),
                    "args": cmd.get("args", []),
                    "kwargs": cmd.get("kwargs", {}),
                    "run_on_install": cmd.get("run_on_install", False),
                })
        
        return cls(
            migrations=data.get("migrations", True),
            fixtures=data.get("fixtures", []),
            management_commands=normalized_commands,
            messages=data.get("messages", [])
        )


@dataclass
class DjangoConfig:
    """Django-specific configuration."""
    installed_apps: List[str] = field(default_factory=list)
    middleware: List[MiddlewareConfig] = field(default_factory=list)
    templates: Optional[TemplateConfig] = None
    auth_backends: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    app_label: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> "DjangoConfig":
        middleware_data = data.get("middleware", [])
        middleware = [
            MiddlewareConfig.from_dict(m) if isinstance(m, dict) else MiddlewareConfig(class_path=m)
            for m in middleware_data
        ]
        
        templates_data = data.get("templates")
        templates = TemplateConfig.from_dict(templates_data) if templates_data else None
        
        return cls(
            installed_apps=data.get("installed_apps", []),
            middleware=middleware,
            templates=templates,
            auth_backends=data.get("auth_backends", []),
            settings=data.get("settings", {}),
            app_label=data.get("app_label", ""),
        )


@dataclass
class StaticfilesConfig:
    """Static files configuration."""
    dirs: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> "StaticfilesConfig":
        return cls(dirs=data.get("dirs", []))


@dataclass
class EnvironmentVariable:
    key: str
    default: Any = ""
    required: bool = False
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "EnvironmentVariable":
        return cls(
            key=data.get("key", ""),
            default=data.get("default", ""),
            required=data.get("required", False),
            description=data.get("description", ""),
        )


@dataclass
class EnvironmentConfig:
    file: str = ".env.example"
    variables: List[EnvironmentVariable] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "EnvironmentConfig":
        return cls(
            file=data.get("file", ".env.example"),
            variables=[EnvironmentVariable.from_dict(item) for item in data.get("variables", [])],
        )


@dataclass
class AppManifest:
    """
    Complete app manifest for RhamaaCLI.
    
    Placeholders supported:
    - {app_name}: The name given during installation (e.g., "myusers")
    - {app_class}: CamelCase version (e.g., "Myusers")
    - {app_upper}: UPPERCASE version (e.g., "MYUSERS")
    """
    # Metadata
    schema_version: str = "1.0.0"
    name: str = ""
    slug: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    package_name: str = ""
    
    # Configuration sections
    django: DjangoConfig = field(default_factory=DjangoConfig)
    urls: List[URLConfig] = field(default_factory=list)
    dependencies: Dependencies = field(default_factory=Dependencies)
    staticfiles: Optional[StaticfilesConfig] = None
    env: Optional[EnvironmentConfig] = None
    post_install: PostInstallConfig = field(default_factory=PostInstallConfig)
    
    @classmethod
    def from_file(cls, path: Path) -> "AppManifest":
        """Load manifest from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: dict) -> "AppManifest":
        """Create manifest from dictionary."""
        django_data = data.get("django", {})
        urls_data = data.get("urls", [])
        deps_data = data.get("dependencies", {})
        static_data = data.get("staticfiles")
        post_data = data.get("post_install", {})
        env_data = data.get("env")
        
        return cls(
            schema_version=data.get("schema_version", "1.0.0"),
            name=data.get("name", ""),
            slug=data.get("slug", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            package_name=data.get("package_name", ""),
            django=DjangoConfig.from_dict(django_data),
            urls=[URLConfig.from_dict(u) for u in urls_data],
            dependencies=Dependencies.from_dict(deps_data),
            staticfiles=StaticfilesConfig.from_dict(static_data) if static_data else None,
            env=EnvironmentConfig.from_dict(env_data) if env_data else None,
            post_install=PostInstallConfig.from_dict(post_data)
        )
    
    def resolve_placeholders(self, app_name: str) -> "AppManifest":
        """
        Resolve all placeholders in the manifest.
        
        Placeholders:
        - {app_name} -> app_name (e.g., "myusers")
        - {app_class} -> Myusers (CamelCase)
        - {app_upper} -> MYUSERS (UPPERCASE)
        """
        app_class = app_name.title().replace('_', '').replace('-', '')
        app_upper = app_name.upper().replace('-', '_')
        
        placeholders = {
            "{app_name}": app_name,
            "{app_class}": app_class,
            "{app_upper}": app_upper,
        }
        
        # Create a new manifest with resolved values
        resolved_data = self._resolve_dict(self.to_dict(), placeholders)
        return AppManifest.from_dict(resolved_data)
    
    def _resolve_dict(self, data: Any, placeholders: Dict[str, str]) -> Any:
        """Recursively resolve placeholders in data structure."""
        if isinstance(data, str):
            result = data
            for key, value in placeholders.items():
                result = result.replace(key, value)
            return result
        elif isinstance(data, list):
            return [self._resolve_dict(item, placeholders) for item in data]
        elif isinstance(data, dict):
            return {k: self._resolve_dict(v, placeholders) for k, v in data.items()}
        return data
    
    def to_dict(self) -> dict:
        """Convert manifest to dictionary."""
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "slug": self.slug,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "package_name": self.package_name,
            "django": {
                "installed_apps": self.django.installed_apps,
                "middleware": [
                    {
                        "class": m.class_path,
                        "priority": m.priority,
                        "position": m.position
                    } if m.position else m.class_path
                    for m in self.django.middleware
                ],
                "templates": {
                    "dirs": self.django.templates.dirs,
                    "context_processors": self.django.templates.context_processors
                } if self.django.templates else None,
                "auth_backends": self.django.auth_backends,
                "settings": self.django.settings,
                "app_label": self.django.app_label,
            },
            "urls": [
                {
                    "path": u.path,
                    "include": u.include,
                    "namespace": u.namespace,
                    "name": u.name
                }
                for u in self.urls
            ],
            "dependencies": {
                "apps": self.dependencies.apps,
                "packages": self.dependencies.packages,
                "optional_apps": self.dependencies.optional_apps,
                "capabilities": self.dependencies.capabilities,
            },
            "staticfiles": {
                "dirs": self.staticfiles.dirs
            } if self.staticfiles else None,
            "env": {
                "file": self.env.file,
                "variables": [
                    {
                        "key": item.key,
                        "default": item.default,
                        "required": item.required,
                        "description": item.description,
                    }
                    for item in self.env.variables
                ],
            } if self.env else None,
            "post_install": {
                "migrations": self.post_install.migrations,
                "fixtures": self.post_install.fixtures,
                "management_commands": self.post_install.management_commands,
                "messages": self.post_install.messages
            }
        }
    
    def validate(self) -> List[str]:
        """
        Validate the manifest.
        Returns list of validation errors (empty if valid).
        """
        errors = []
        
        # Required fields
        if not self.name:
            errors.append("Missing required field: name")
        if not self.slug:
            errors.append("Missing required field: slug")
        try:
            from .versions import parse_version

            parse_version(self.version)
        except ValueError as exc:
            errors.append(str(exc))
        if self.package_name and not self.package_name.isidentifier():
            errors.append("package_name must be a valid Python identifier")
        
        # Validate URLs
        for i, url in enumerate(self.urls):
            if not url.path:
                errors.append(f"URL[{i}]: missing path")
            if not url.include:
                errors.append(f"URL[{i}]: missing include")
            # Check for path conflicts
            if url.path and not url.path.endswith('/'):
                errors.append(f"URL[{i}]: path should end with / ({url.path})")
        
        # Validate middleware
        for i, mw in enumerate(self.django.middleware):
            if not mw.class_path:
                errors.append(f"Middleware[{i}]: missing class_path")
        
        # Validate installed_apps
        for i, app in enumerate(self.django.installed_apps):
            if not app:
                errors.append(f"installed_apps[{i}]: empty value")
        if self.env:
            env_path = Path(self.env.file)
            if env_path.is_absolute() or ".." in env_path.parts:
                errors.append("env.file must stay inside project directory")
            for i, variable in enumerate(self.env.variables):
                if not variable.key or not variable.key.isidentifier():
                    errors.append(f"env.variables[{i}]: invalid key")
        
        return errors


class ManifestParser:
    """Parser for rhamaa-app.json files."""
    
    @staticmethod
    def load(manifest_path: Path) -> Tuple[Optional[AppManifest], List[str]]:
        """
        Load and validate a manifest file.
        
        Returns:
            Tuple of (manifest or None, validation errors)
        """
        try:
            manifest = AppManifest.from_file(manifest_path)
            errors = manifest.validate()
            if errors:
                return None, errors
            return manifest, []
        except json.JSONDecodeError as e:
            return None, [f"Invalid JSON: {e}"]
        except FileNotFoundError:
            return None, [f"Manifest file not found: {manifest_path}"]
        except Exception as e:
            return None, [f"Error loading manifest: {e}"]
    
    @staticmethod
    def find_manifest(app_dir: Path) -> Optional[Path]:
        """Find manifest file in app directory."""
        candidates = [
            app_dir / "rhamaa-app.json",
            app_dir / "manifest.json",
            app_dir / ".rhamaa" / "manifest.json"
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        return None


# Example usage / test
if __name__ == "__main__":
    # Create example manifest
    manifest = AppManifest(
        name="User Management",
        slug="users",
        description="Complete user management system",
        django=DjangoConfig(
            installed_apps=["apps.{app_name}", "allauth"],
            middleware=[MiddlewareConfig(
                class_path="apps.{app_name}.middleware.ActivityMiddleware"
            )],
            settings={
                "AUTH_USER_MODEL": "{app_name}.User"
            }
        ),
        urls=[URLConfig(path="accounts/", include="apps.{app_name}.urls")]
    )
    
    # Resolve placeholders
    resolved = manifest.resolve_placeholders("myusers")
    print(json.dumps(resolved.to_dict(), indent=2))
