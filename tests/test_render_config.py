from __future__ import annotations

import configparser
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "script" / "docker" / "render_config.py"
SPEC = importlib.util.spec_from_file_location("render_config", MODULE_PATH)
assert SPEC and SPEC.loader
render_config = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_config)


class RenderConfigTests(unittest.TestCase):
    def read_output(self, path: Path) -> configparser.ConfigParser:
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(path, encoding="utf-8")
        return parser

    def test_yaml_overlays_template_and_preserves_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            source = temp / "config.yaml"
            output = temp / "config.ini"
            source.write_text(
                "interface:\n"
                "  type: tcp\n"
                "  hostname: mesh.local:4403\n"
                "general:\n"
                "  respond_by_dm_only: false\n",
                encoding="utf-8",
            )

            render_config.render(
                ROOT / "config.template", source, output, {}, strict=True
            )
            parser = self.read_output(output)

            self.assertEqual(parser.get("interface", "type"), "tcp")
            self.assertEqual(parser.get("interface", "hostname"), "mesh.local:4403")
            self.assertFalse(parser.getboolean("general", "respond_by_dm_only"))
            self.assertTrue(parser.has_section("bbs"))

    def test_generic_environment_override_has_highest_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            source = temp / "config.yaml"
            output = temp / "config.ini"
            source.write_text(
                "interface:\n  type: tcp\n  hostname: from-file:4403\n",
                encoding="utf-8",
            )

            render_config.render(
                ROOT / "config.template",
                source,
                output,
                {
                    "MESHTASTIC_HOST": "shortcut-host",
                    "MESHING_AROUND__INTERFACE__HOSTNAME": "generic-host:5555",
                },
            )
            parser = self.read_output(output)

            self.assertEqual(
                parser.get("interface", "hostname"), "generic-host:5555"
            )

    def test_shortcut_host_and_port_are_combined(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            source = temp / "config.yaml"
            output = temp / "config.ini"
            source.write_text(
                "interface:\n  type: tcp\n  hostname: from-file:4403\n",
                encoding="utf-8",
            )

            render_config.render(
                ROOT / "config.template",
                source,
                output,
                {"MESHTASTIC_HOST": "10.0.0.25", "MESHTASTIC_PORT": "5500"},
            )
            parser = self.read_output(output)

            self.assertEqual(parser.get("interface", "hostname"), "10.0.0.25:5500")

    def test_legacy_ini_input_remains_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            source = temp / "config.ini"
            output = temp / "rendered.ini"
            source.write_text(
                "[interface]\ntype = serial\nport = /dev/ttyUSB9\n",
                encoding="utf-8",
            )

            render_config.render(ROOT / "config.template", source, output, {})
            parser = self.read_output(output)

            self.assertEqual(parser.get("interface", "type"), "serial")
            self.assertEqual(parser.get("interface", "port"), "/dev/ttyUSB9")
            self.assertTrue(parser.has_section("general"))

    def test_strict_mode_rejects_unknown_yaml_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            source = temp / "config.yaml"
            source.write_text(
                "interface:\n  type: tcp\n  hostname: mesh.local\n  typo: value\n",
                encoding="utf-8",
            )

            with self.assertRaises(render_config.ConfigurationError):
                render_config.render(
                    ROOT / "config.template",
                    source,
                    temp / "config.ini",
                    {},
                    strict=True,
                )

    def test_invalid_interface_type_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            source = temp / "config.yaml"
            source.write_text("interface:\n  type: carrier-pigeon\n", encoding="utf-8")

            with self.assertRaises(render_config.ConfigurationError):
                render_config.render(
                    ROOT / "config.template", source, temp / "config.ini", {}
                )

    def test_runtime_file_permissions_are_private(self) -> None:
        if os.name == "nt":
            self.skipTest("Windows does not expose POSIX permission bits consistently")
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            source = temp / "config.yaml"
            output = temp / "config.ini"
            source.write_text(
                "interface:\n  type: tcp\n  hostname: mesh.local\n",
                encoding="utf-8",
            )

            render_config.render(ROOT / "config.template", source, output, {})

            self.assertEqual(output.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
