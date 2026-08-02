#!/usr/bin/env python3
"""Render Meshing Around's runtime INI file from YAML or legacy INI input.

The application still consumes ConfigParser values internally.  This adapter keeps
that stable interface while allowing Compose users to maintain a small YAML file
and override individual values through environment variables.
"""

from __future__ import annotations

import argparse
import configparser
import os
import re
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

import yaml


ENV_PREFIX = "MESHING_AROUND__"
TRUE_VALUES = {"1", "true", "yes", "on"}
SUPPORTED_INTERFACES = {"serial", "tcp", "ble"}


class ConfigurationError(ValueError):
    """Raised when configuration input cannot produce a safe runtime config."""


def _new_parser() -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    return parser


def _read_ini(path: Path) -> configparser.ConfigParser:
    parser = _new_parser()
    try:
        with path.open("r", encoding="utf-8") as handle:
            parser.read_file(handle)
    except (OSError, configparser.Error) as exc:
        raise ConfigurationError(f"Could not read INI file {path}: {exc}") from exc
    return parser


def _known_template_keys(path: Path) -> set[tuple[str, str]]:
    """Return active and commented section/key pairs from config.template."""
    known: set[tuple[str, str]] = set()
    section = ""
    section_pattern = re.compile(r"^\s*\[([^]]+)]\s*$")
    option_pattern = re.compile(r"^\s*(?:[#;]\s*)?([^#;:=\s][^:=]*?)\s*[:=]")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ConfigurationError(f"Could not read template {path}: {exc}") from exc
    for line in lines:
        section_match = section_pattern.match(line)
        if section_match:
            section = section_match.group(1).strip()
            continue
        option_match = option_pattern.match(line)
        if section and option_match:
            option = option_match.group(1).strip()
            known.add((section.casefold(), option.casefold()))
    return known


def _find_section(parser: configparser.ConfigParser, requested: str) -> str:
    for section in parser.sections():
        if section.casefold() == requested.casefold():
            return section
    return requested


def _find_option(
    parser: configparser.ConfigParser, section: str, requested: str
) -> str:
    if parser.has_section(section):
        for option in parser.options(section):
            if option.casefold() == requested.casefold():
                return option
    return requested


def _stringify(value: Any, location: str) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, (str, int, float)):
        return str(value)
    if isinstance(value, list):
        if any(isinstance(item, (dict, list)) for item in value):
            raise ConfigurationError(f"{location} must be a scalar or flat list")
        return ",".join(_stringify(item, location) for item in value)
    raise ConfigurationError(f"{location} must be a scalar or flat list")


def _set_value(
    parser: configparser.ConfigParser,
    section_name: str,
    option_name: str,
    value: Any,
) -> str:
    section = _find_section(parser, section_name)
    if not parser.has_section(section):
        parser.add_section(section)
    option = _find_option(parser, section, option_name)
    parser.set(section, option, _stringify(value, f"{section_name}.{option_name}"))
    return f"{section}.{option}"


def _overlay_ini(
    destination: configparser.ConfigParser, source: configparser.ConfigParser
) -> None:
    for section in source.sections():
        for option, value in source.items(section, raw=True):
            _set_value(destination, section, option, value)


def _overlay_yaml(
    destination: configparser.ConfigParser,
    path: Path,
    strict: bool,
    known_keys: set[tuple[str, str]],
) -> list[str]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Could not read YAML file {path}: {exc}") from exc

    if payload is None:
        return []
    if not isinstance(payload, Mapping):
        raise ConfigurationError("The YAML document must be a mapping of INI sections")

    changed: list[str] = []
    for section_name, values in payload.items():
        if not isinstance(section_name, str) or not isinstance(values, Mapping):
            raise ConfigurationError(
                "Each YAML section must be a named mapping of configuration keys"
            )
        existing_section = _find_section(destination, section_name)
        if strict and not destination.has_section(existing_section):
            raise ConfigurationError(f"Unknown configuration section: {section_name}")
        for option_name, value in values.items():
            if not isinstance(option_name, str):
                raise ConfigurationError(f"Keys in {section_name} must be strings")
            if strict and (
                existing_section.casefold(), option_name.casefold()
            ) not in known_keys:
                raise ConfigurationError(
                    f"Unknown configuration key: {section_name}.{option_name}"
                )
            changed.append(
                _set_value(destination, section_name, option_name, value)
            )
    return changed


def _apply_shortcuts(
    parser: configparser.ConfigParser, environ: Mapping[str, str]
) -> list[str]:
    changed: list[str] = []
    if "MESHTASTIC_TYPE" in environ:
        changed.append(
            _set_value(parser, "interface", "type", environ["MESHTASTIC_TYPE"])
        )

    if "MESHTASTIC_HOST" in environ or "MESHTASTIC_PORT" in environ:
        section = _find_section(parser, "interface")
        current = parser.get(section, "hostname", fallback="meshtastic.local")
        host = environ.get("MESHTASTIC_HOST", current)
        if ":" in host:
            host, current_port = host.rsplit(":", 1)
        else:
            current_port = "4403"
        port = environ.get("MESHTASTIC_PORT", current_port)
        changed.append(_set_value(parser, "interface", "hostname", f"{host}:{port}"))

    if "LOG_LEVEL" in environ:
        changed.append(
            _set_value(parser, "general", "sysloglevel", environ["LOG_LEVEL"])
        )
    return changed


def _apply_environment(
    parser: configparser.ConfigParser, environ: Mapping[str, str]
) -> list[str]:
    changed = _apply_shortcuts(parser, environ)
    for name in sorted(environ):
        if not name.startswith(ENV_PREFIX):
            continue
        path = name[len(ENV_PREFIX) :].split("__")
        if len(path) != 2 or not all(path):
            raise ConfigurationError(
                f"{name} must use MESHING_AROUND__SECTION__KEY"
            )
        changed.append(_set_value(parser, path[0], path[1], environ[name]))
    return changed


def _validate(parser: configparser.ConfigParser) -> None:
    section = _find_section(parser, "interface")
    if not parser.has_section(section):
        raise ConfigurationError("Configuration is missing the interface section")

    interface_type = parser.get(section, "type", fallback="").strip().casefold()
    if interface_type not in SUPPORTED_INTERFACES:
        expected = ", ".join(sorted(SUPPORTED_INTERFACES))
        raise ConfigurationError(f"interface.type must be one of: {expected}")
    if interface_type == "tcp" and not parser.get(
        section, "hostname", fallback=""
    ).strip():
        raise ConfigurationError("interface.hostname is required for a TCP interface")


def render(
    template: Path,
    source: Path,
    output: Path,
    environ: Mapping[str, str],
    strict: bool = False,
) -> tuple[list[str], list[str]]:
    parser = _read_ini(template)
    suffix = source.suffix.casefold()
    if suffix in {".yaml", ".yml"}:
        file_changes = _overlay_yaml(
            parser, source, strict, _known_template_keys(template)
        )
    elif suffix in {".ini", ".conf", ".cfg"}:
        source_parser = _read_ini(source)
        _overlay_ini(parser, source_parser)
        file_changes = [
            f"{section}.{option}"
            for section in source_parser.sections()
            for option in source_parser.options(section)
        ]
    else:
        raise ConfigurationError(
            f"Unsupported configuration extension {suffix!r}; use .yaml, .yml, or .ini"
        )

    environment_changes = _apply_environment(parser, environ)
    _validate(parser)

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", dir=output.parent, text=True
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            parser.write(handle)
        os.chmod(temporary_name, stat.S_IRUSR | stat.S_IWUSR)
        os.replace(temporary_name, output)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return file_changes, environment_changes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--strict",
        action="store_true",
        default=os.getenv("MESHING_AROUND_CONFIG_STRICT", "").casefold()
        in TRUE_VALUES,
        help="Reject YAML keys that are not present in config.template",
    )
    args = parser.parse_args(argv)

    try:
        file_changes, environment_changes = render(
            args.template, args.source, args.output, os.environ, args.strict
        )
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    print(
        f"Rendered {args.output} from {args.source} "
        f"({len(file_changes)} file overrides, "
        f"{len(environment_changes)} environment overrides)."
    )
    if environment_changes:
        print("Environment overrides: " + ", ".join(environment_changes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
