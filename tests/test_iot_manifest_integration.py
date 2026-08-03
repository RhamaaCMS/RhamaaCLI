import json
import sys
import tempfile
import types
import unittest
import zipfile
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
from rhamaa.app_versioning import parse_version, update_registered_app
from rhamaa.manifest_applier import ApplyResult, ManifestApplier


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
        self.assertEqual(registry["iot"]["version"], "2.1.0")
        self.assertIn("influx", registry)
        self.assertIn("whitelabeling", registry)

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


class AppVersioningTests(unittest.TestCase):
    def _manifest(self, version: str) -> dict:
        return {
            "schema_version": "1.0.0",
            "name": "Rhamaa IoT",
            "slug": "iot",
            "version": version,
            "package_name": "IoT",
            "django": {"installed_apps": ["apps.IoT"]},
            "urls": [],
            "dependencies": {"apps": [], "packages": []},
            "post_install": {"migrations": False},
        }

    def test_versions_are_numeric_and_two_part_versions_are_supported(self):
        self.assertEqual(parse_version("0.7"), (0, 7, 0))
        self.assertLess(parse_version("0.5"), parse_version("0.7"))
        with self.assertRaises(ValueError):
            parse_version("latest")

    def test_update_replaces_code_backs_up_old_app_and_records_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / "apps" / "IoT"
            app.mkdir(parents=True)
            (app / "rhamaa-app.json").write_text(
                json.dumps(self._manifest("0.5")), encoding="utf-8"
            )
            (app / "old.py").write_text("old = True\n", encoding="utf-8")
            (root / ".gitignore").write_text(".env\n", encoding="utf-8")

            archive = root / "iot.zip"
            with zipfile.ZipFile(archive, "w") as package:
                package.writestr(
                    "iot-main/rhamaa-app.json", json.dumps(self._manifest("0.7"))
                )
                package.writestr("iot-main/new.py", "new = True\n")

            info = {
                "repository": "https://github.com/rhamaa/iot-apps",
                "branch": "main",
                "version": "0.7",
                "install_name": "IoT",
            }
            with patch(
                "rhamaa.app_versioning.download_github_repo",
                return_value=str(archive),
            ), patch.object(
                ManifestApplier, "apply_all", return_value=ApplyResult(success=True)
            ):
                result = update_registered_app(
                    registry_key="iot", app_info=info, project_path=root
                )

            self.assertTrue(result.success, result.errors)
            self.assertTrue(result.updated)
            self.assertEqual(result.old_version, "0.5")
            self.assertEqual(result.new_version, "0.7")
            self.assertTrue((app / "new.py").exists())
            self.assertFalse((app / "old.py").exists())
            self.assertTrue((result.backup_path / "old.py").exists())
            state = json.loads((root / ".rhamaa" / "apps.json").read_text())
            self.assertEqual(state["apps"]["iot"]["version"], "0.7")
            self.assertIn(
                "/.rhamaa/backups/", (root / ".gitignore").read_text()
            )

    def test_registry_and_downloaded_versions_must_match(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / "apps" / "IoT"
            app.mkdir(parents=True)
            (app / "rhamaa-app.json").write_text(
                json.dumps(self._manifest("0.5")), encoding="utf-8"
            )
            archive = root / "iot.zip"
            with zipfile.ZipFile(archive, "w") as package:
                package.writestr(
                    "iot-main/rhamaa-app.json", json.dumps(self._manifest("0.6"))
                )
            info = {
                "repository": "https://github.com/rhamaa/iot-apps",
                "branch": "main",
                "version": "0.7",
                "install_name": "IoT",
            }
            with patch(
                "rhamaa.app_versioning.download_github_repo",
                return_value=str(archive),
            ):
                result = update_registered_app(
                    registry_key="iot", app_info=info, project_path=root
                )
            self.assertFalse(result.success)
            self.assertTrue(any("Registry says 0.7" in e for e in result.errors))
            self.assertEqual(
                json.loads((app / "rhamaa-app.json").read_text())["version"], "0.5"
            )


if __name__ == "__main__":
    unittest.main()
