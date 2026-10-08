from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


TOOL = Path(__file__).resolve().parents[1] / "scripts" / "optimizer_api.py"
SPEC = importlib.util.spec_from_file_location("optimizer_api", TOOL)
assert SPEC and SPEC.loader
optimizer_api = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = optimizer_api
SPEC.loader.exec_module(optimizer_api)


class OptimizerApiTests(unittest.TestCase):
    def resolver(self, root: Path) -> Path:
        target = root / "registry" / "optimizer_registry.py"
        target.parent.mkdir(parents=True)
        target.write_text(
            "import json, sys\n"
            "print(json.dumps({'path': '/runtime', 'environment': 'optimizer', 'route': sys.argv[2]}))\n",
            encoding="utf-8",
        )
        return target

    def test_exact_registry_environment_variable_has_priority(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.resolver(Path(temporary))
            with mock.patch.dict(os.environ, {"OPTIMIZER_REGISTRY": str(target)}, clear=True):
                self.assertEqual(target.resolve(), optimizer_api.resolver_path())

    def test_optimizer_home_resolves_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.resolver(root)
            with mock.patch.dict(os.environ, {"OPTIMIZER_HOME": str(root)}, clear=True):
                self.assertEqual(target.resolve(), optimizer_api.resolver_path())

    def test_explicit_resolver_runs_without_a_machine_specific_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.resolver(Path(temporary))
            route = optimizer_api.resolve("stable", target)
            self.assertEqual("stable", route["route"])
            self.assertEqual("optimizer", route["environment"])

    def test_missing_resolver_explains_all_configuration_options(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            missing_home = Path(temporary)
            with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
                optimizer_api.Path, "home", return_value=missing_home
            ):
                with self.assertRaisesRegex(ValueError, "OPTIMIZER_REGISTRY"):
                    optimizer_api.resolver_path()


if __name__ == "__main__":
    unittest.main()
