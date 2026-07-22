import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

# Keep contract tests runnable in minimal Python environments where optional
# CLI presentation dependency Rich is not installed.
if "rich" not in sys.modules:
    rich = types.ModuleType("rich")
    console_module = types.ModuleType("rich.console")
    progress_module = types.ModuleType("rich.progress")

    class Console:
        def print(self, *args, **kwargs):
            return None

    class Progress:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def add_task(self, *args, **kwargs):
            return 1

        def remove_task(self, *args, **kwargs):
            return None

    console_module.Console = Console
    progress_module.Progress = Progress
    progress_module.SpinnerColumn = lambda *args, **kwargs: None
    progress_module.TextColumn = lambda *args, **kwargs: None
    progress_module.BarColumn = lambda *args, **kwargs: None
    progress_module.TaskProgressColumn = lambda *args, **kwargs: None
    sys.modules.update(
        {"rich": rich, "rich.console": console_module, "rich.progress": progress_module}
    )

if "requests" not in sys.modules:
    sys.modules["requests"] = types.ModuleType("requests")

from rhamaa.manifest import ManifestParser
from rhamaa.manifest_applier import ManifestApplier


class IoTManifestIntegrationTests(unittest.TestCase):
    def _project(self, root: Path) -> None:
        (root / "apps" / "IoT").mkdir(parents=True)
        package = root / "demo"
        (package / "settings").mkdir(parents=True)
        (package / "settings" / "base.py").write_text(
            'RHAMAA_CAPABILITIES = {"mqtt-worker-v1"}\n'
            'INSTALLED_APPS = ["apps.mqtt", "wagtail.snippets"]\n',
            encoding="utf-8",
        )
        (package / "urls.py").write_text(
            "from django.urls import include, path\nurlpatterns = []\n",
            encoding="utf-8",
        )
        (root / "manage.py").write_text("", encoding="utf-8")
        (root / ".env.example").write_text("MQTT_BROKER_HOST=localhost\n", encoding="utf-8")

    def test_manifest_contract_and_install_plan(self):
        manifest_path = Path(__file__).parents[2] / "Apps" / "IoT" / "rhamaa-app.json"
        if not manifest_path.exists():
            self.skipTest("Ecosystem sibling Apps/IoT is unavailable")
        manifest, errors = ManifestParser.load(manifest_path)
        self.assertEqual(errors, [])
        self.assertEqual(manifest.package_name, "IoT")
        self.assertEqual(manifest.django.app_label, "iot")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._project(root)
            completed = type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()
            with patch("rhamaa.manifest_applier.subprocess.run", return_value=completed) as run:
                result = ManifestApplier(manifest, root, "IoT").apply_all()
            self.assertTrue(result.success, result.errors)
            command = run.call_args.args[0]
            self.assertEqual(command[-3:], ["manage.py", "migrate", "iot"])
            settings = (root / "demo" / "settings" / "base.py").read_text(encoding="utf-8")
            urls = (root / "demo" / "urls.py").read_text(encoding="utf-8")
            environment = (root / ".env.example").read_text(encoding="utf-8")
            self.assertIn("apps.IoT", settings)
            self.assertIn("apps.IoT.urls", urls)
            self.assertIn("apps.IoT.ota_urls", urls)
            self.assertIn("IOT_OTA_PUBLIC_BASE=", environment)
            self.assertIn("IOT_PROVISION_RATE_LIMIT=10", environment)
            self.assertEqual(environment.count("MQTT_BROKER_HOST="), 1)

    def test_registry_uses_fixed_package_name(self):
        registry_path = Path(__file__).parents[1] / "rhamaa" / "templates" / "cms" / "app_list.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertNotIn("mqtt", registry)
        self.assertEqual(registry["iot"]["install_name"], "IoT")

    def test_incompatible_template_is_rejected_before_changes(self):
        manifest_path = Path(__file__).parents[2] / "Apps" / "IoT" / "rhamaa-app.json"
        if not manifest_path.exists():
            self.skipTest("Ecosystem sibling Apps/IoT is unavailable")
        manifest, _ = ManifestParser.load(manifest_path)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._project(root)
            settings_path = root / "demo" / "settings" / "base.py"
            settings_path.write_text('INSTALLED_APPS = ["wagtail.snippets"]\n', encoding="utf-8")
            result = ManifestApplier(manifest, root, "IoT").apply_all(dry_run=True)
            self.assertFalse(result.success)
            self.assertTrue(any("apps.mqtt" in error for error in result.errors))
            self.assertNotIn("apps.IoT", settings_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
