"""
Dependency Resolver for RhamaaCLI App Manifests
Handles app dependencies, circular dependency detection, and installation ordering.
"""

from typing import List, Dict, Set, Optional, Tuple
from collections import deque
from dataclasses import dataclass


@dataclass
class DependencyNode:
    """Represents an app in the dependency graph."""
    app_key: str
    dependencies: List[str]
    manifest: Optional[dict] = None


class DependencyResolver:
    """
    Resolve dependencies between Rhamaa apps.
    
    Uses topological sort (Kahn's algorithm) for dependency ordering.
    """
    
    def __init__(self, available_apps: Dict[str, dict], installed_apps: List[str] = None):
        """
        Initialize resolver.
        
        Args:
            available_apps: Dict of app_key -> manifest dict (from registry)
            installed_apps: List of already installed app keys
        """
        self.available_apps = available_apps
        self.installed_apps = set(installed_apps or [])
        self.dependency_graph: Dict[str, DependencyNode] = {}
        self._build_graph()
    
    def _build_graph(self) -> None:
        """Build dependency graph from available apps."""
        for app_key, manifest in self.available_apps.items():
            deps_data = manifest.get('dependencies', {})
            deps = deps_data.get('apps', []) if isinstance(deps_data, dict) else []
            
            self.dependency_graph[app_key] = DependencyNode(
                app_key=app_key,
                dependencies=deps,
                manifest=manifest
            )
    
    def get_missing_dependencies(self, target_app: str) -> List[str]:
        """
        Get list of dependencies that need to be installed for target_app.
        Returns empty list if all dependencies are satisfied.
        """
        if target_app not in self.dependency_graph:
            return []
        
        node = self.dependency_graph[target_app]
        missing = []
        
        for dep in node.dependencies:
            if dep not in self.installed_apps:
                missing.append(dep)
                # Recursively check sub-dependencies
                sub_missing = self.get_missing_dependencies(dep)
                for sub_dep in sub_missing:
                    if sub_dep not in missing:
                        missing.append(sub_dep)
        
        return missing
    
    def resolve_dependencies(self, target_app: str) -> List[str]:
        """
        Resolve installation order for target_app and its dependencies.
        
        Returns list of apps in installation order (dependencies first).
        Uses topological sort (Kahn's algorithm).
        """
        if target_app not in self.dependency_graph:
            # Target app not in registry, return just the target
            return [target_app]
        
        # Collect all apps involved (target + missing dependencies)
        involved_apps = set()
        queue = deque([target_app])
        
        while queue:
            app = queue.popleft()
            if app in involved_apps:
                continue
            involved_apps.add(app)
            
            if app in self.dependency_graph:
                node = self.dependency_graph[app]
                for dep in node.dependencies:
                    if dep not in self.installed_apps:
                        queue.append(dep)
        
        # Build adjacency list for topological sort
        # Edge from A -> B means A depends on B (B must be installed before A)
        adjacency: Dict[str, Set[str]] = {app: set() for app in involved_apps}
        in_degree: Dict[str, int] = {app: 0 for app in involved_apps}
        
        for app in involved_apps:
            if app in self.dependency_graph:
                node = self.dependency_graph[app]
                for dep in node.dependencies:
                    if dep in involved_apps and dep not in self.installed_apps:
                        # App depends on dep, so edge dep -> app
                        if dep not in adjacency:
                            adjacency[dep] = set()
                        adjacency[dep].add(app)
                        in_degree[app] = in_degree.get(app, 0) + 1
        
        # Kahn's algorithm
        queue = deque([app for app in involved_apps if in_degree.get(app, 0) == 0])
        result = []
        
        while queue:
            app = queue.popleft()
            result.append(app)
            
            for dependent in adjacency.get(app, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check for circular dependencies
        if len(result) != len(involved_apps):
            raise CircularDependencyError(
                f"Circular dependency detected involving: {involved_apps - set(result)}"
            )
        
        return result
    
    def check_circular_dependencies(self) -> Optional[List[str]]:
        """
        Check for circular dependencies in the entire graph.
        Returns the circular chain if found, None otherwise.
        """
        visited = set()
        recursion_stack = set()
        
        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            visited.add(node)
            recursion_stack.add(node)
            
            if node in self.dependency_graph:
                for dep in self.dependency_graph[node].dependencies:
                    if dep not in visited:
                        result = dfs(dep, path + [dep])
                        if result:
                            return result
                    elif dep in recursion_stack:
                        # Found cycle
                        cycle_start = path.index(dep)
                        return path[cycle_start:] + [dep]
            
            recursion_stack.remove(node)
            return None
        
        for app in self.dependency_graph:
            if app not in visited:
                cycle = dfs(app, [app])
                if cycle:
                    return cycle
        
        return None
    
    def is_installable(self, target_app: str) -> Tuple[bool, str]:
        """
        Check if target_app can be installed.
        Returns (is_installable, reason).
        """
        # Check if app exists in registry
        if target_app not in self.dependency_graph:
            return False, f"App '{target_app}' not found in registry"
        
        # Check for circular dependencies
        cycle = self.check_circular_dependencies()
        if cycle:
            return False, f"Circular dependency detected: {' -> '.join(cycle)}"
        
        # Check if all dependencies are available
        try:
            install_order = self.resolve_dependencies(target_app)
        except CircularDependencyError as e:
            return False, str(e)
        
        missing_in_registry = []
        for app in install_order:
            if app != target_app and app not in self.dependency_graph:
                missing_in_registry.append(app)
        
        if missing_in_registry:
            return False, f"Missing dependencies in registry: {', '.join(missing_in_registry)}"
        
        return True, "Installable"
    
    def get_installation_plan(self, target_app: str) -> List[dict]:
        """
        Get detailed installation plan for target_app.
        Returns list of dicts with app_key and manifest info.
        """
        try:
            install_order = self.resolve_dependencies(target_app)
        except CircularDependencyError:
            return []
        
        plan = []
        for app in install_order:
            if app in self.installed_apps:
                continue  # Skip already installed
            
            node = self.dependency_graph.get(app)
            if node:
                plan.append({
                    'app_key': app,
                    'manifest': node.manifest,
                    'dependencies': node.dependencies
                })
            else:
                plan.append({
                    'app_key': app,
                    'manifest': None,
                    'dependencies': []
                })
        
        return plan


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected."""
    pass


# Example usage
if __name__ == "__main__":
    # Example registry
    available = {
        'users': {
            'dependencies': {'apps': ['notifications']}
        },
        'notifications': {
            'dependencies': {'apps': []}
        },
        'articles': {
            'dependencies': {'apps': ['users']}
        }
    }
    
    resolver = DependencyResolver(available, installed_apps=[])
    
    # Check articles dependencies
    missing = resolver.get_missing_dependencies('articles')
    print(f"Missing for articles: {missing}")
    
    # Get install order
    order = resolver.resolve_dependencies('articles')
    print(f"Install order: {order}")
    
    # Get plan
    plan = resolver.get_installation_plan('articles')
    for step in plan:
        print(f"  - {step['app_key']} (deps: {step['dependencies']})")
