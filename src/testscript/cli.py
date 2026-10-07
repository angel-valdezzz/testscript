"""Installable tscr entrypoint. Exit codes: 0 pass, 1 failure, 2 invalid, 5 no tests."""

import argparse
import sys
import tomllib
from pathlib import Path

from testscript import __version__
from testscript.analysis import Analyzer
from testscript.configuration import BROWSERS, validate_config
from testscript.parser import ScriptError
from testscript.reporting import write_reports
from testscript.runtime import Runtime


def discover(paths):
    files = set()
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            raise ScriptError(f"Path does not exist: {path}", str(path))
        if path.is_dir():
            files.update(
                p.resolve()
                for p in path.rglob("*.tscr")
                if not any(
                    part.startswith(".") or part in {"site", "build", "dist", "node_modules"}
                    for part in p.relative_to(path).parts
                )
            )
        elif path.suffix == ".tscr":
            files.add(path.resolve())
        else:
            raise ScriptError("Expected .tscr file or directory", str(path))
    return sorted(files)


def read_config(path):
    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    config = data.get("testscript", {})
    if not isinstance(config, dict):
        raise ValueError("[testscript] must be a table")
    return config


def build_parser():
    parser = argparse.ArgumentParser(prog="tscr", description="TestScript • Web + API testing language")
    parser.add_argument("--version", action="version", version=f"TestScript {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "lint", "run", "list"):
        child = commands.add_parser(command)
        child.add_argument("paths", nargs="*", default=["tests"])
        child.add_argument("--config", type=Path, default=Path("testscript.toml"))
        if command in {"run", "list"}:
            child.add_argument("--tag", action="append", default=[])
            child.add_argument("--exclude-tag", action="append", default=[])
            child.add_argument("--name")
        if command == "run":
            child.add_argument("--provider", choices=["playwright", "selenium"])
            child.add_argument("--browser", choices=sorted(set.union(*BROWSERS.values())))
            visibility = child.add_mutually_exclusive_group()
            visibility.add_argument("--headed", dest="headless", action="store_false", default=None)
            visibility.add_argument("--headless", dest="headless", action="store_true")
            child.add_argument("--incognito", action=argparse.BooleanOptionalAction, default=None)
            child.add_argument("--viewport-width", type=int)
            child.add_argument("--viewport-height", type=int)
            child.add_argument("--maximize", action=argparse.BooleanOptionalAction, default=None)
            child.add_argument("--output", type=Path)
        if command == "lint":
            child.add_argument("--flows-only", action="store_true")
            child.add_argument("--strict", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        config = read_config(args.config)
        if getattr(args, "provider", None):
            config["provider"] = args.provider
        for key in ("browser", "headless", "incognito", "viewport_width", "viewport_height", "maximize"):
            value = getattr(args, key, None)
            if value is not None:
                config[key] = value
        validate_config(config)
        output = getattr(args, "output", None) or Path(config.get("output", "testscript-results"))
        runtime = Runtime(config, output)
        paths = discover(args.paths)
        if not paths:
            print("No .tscr files found", file=sys.stderr)
            return 5
        runtime.entry_paths = set(paths)
        for path in paths:
            runtime.load_module(path)
        diagnostics = Analyzer(
            runtime,
            args.command == "lint",
            getattr(args, "flows_only", False) or config.get("tests_use_flows_only", False),
        ).analyze()
        for diagnostic in diagnostics:
            print(diagnostic, file=sys.stderr)
        if any(d.severity == "error" for d in diagnostics):
            return 2
        if args.command in {"check", "lint"}:
            print(f"Checked {len(paths)} file(s) • {len(diagnostics)} diagnostic(s)")
            return 2 if diagnostics and getattr(args, "strict", False) else 0
        selected = [
            t
            for t in runtime.tests
            if t.path in runtime.entry_paths
            and (not args.tag or set(args.tag) & set(t.tags))
            and (not args.exclude_tag or not set(args.exclude_tag) & set(t.tags))
            and (not args.name or args.name in t.name)
        ]
        if not selected:
            print("No tests selected", file=sys.stderr)
            return 5
        runtime.tests = selected
        if args.command == "list":
            for test in selected:
                print(f"{test.path.name} :: {test.name} [{', '.join(test.tags)}]")
            return 0
        results = runtime.run()
        report = write_reports(results, output)
        for result in results:
            print(f"{result.status.upper():7} {result.name} ({result.duration:.3f}s)")
        print(f"Report: {report.resolve()}")
        return 1 if any(r.status == "failed" for r in results) else 0
    except (ScriptError, OSError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
