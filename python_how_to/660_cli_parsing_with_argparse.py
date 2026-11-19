# python 660_cli_parsing_with_argparse.py

import argparse
from collections.abc import Sequence
from pathlib import Path


def decoupled_parser_and_basic_flags() -> None:

    # Parsing sys.argv[1:] by hand breaks down as soon as flags take typed values,
    # bundle together (-vv), or branch into subcommands. argparse builds a
    # self-documenting parser that validates types (type=int, type=Path),
    # restricts choices (choices=...), generates --help, and exits with usage
    # diagnostics on invalid input.
    #
    # The best architectural habit for CLI tools is decoupling parser creation
    # from sys.argv:
    # - Build the parser in a helper like def build_parser() -> argparse.ArgumentParser:
    # - Pass argv: Sequence[str] | None = None into parser.parse_args(argv).
    #   When argv is None, argparse reads sys.argv[1:]; when tests or demos pass
    #   ["-vv", "build"], argparse runs 100% in memory without touching sys.argv.
    #
    #     Suppose parser.add_argument("-v", "--verbose", action="count", default=0).
    #     Passing ["-vv"] sets ns.verbose == 2.
    #     Gotcha: omit default=0 on action="count" and missing -v yields None!
    #
    # Other everyday argument options:
    # - action="store_true" sets False when omitted, True when present.
    # - action="append" collects repeated flags (--tag a --tag b) into ["a", "b"].
    # - nargs="+" (one or more) or nargs="*" (zero or more) collects a list.
    # - type=Path converts each string argument directly into a pathlib.Path.

    probe = argparse.ArgumentParser(prog="probe")
    probe.add_argument("--dry-run", action="store_true")
    print("Starter Namespace:", probe.parse_args(["--dry-run"]))

    # Build a small parser accepting positional files with nargs="+" and type=Path,
    # plus -v / --verbose with action="count" and default=0, and --tag with
    # action="append". Parse ["-vv", "--tag", "fast", "--tag", "ci", "a.py", "b.py"]
    # and print the resulting Namespace.


    # Verify the action="count" default=0 rule: create a parser with
    # --verbose (action="count") WITHOUT default=0 and compare parse_args([])
    # against a second flag with default=0.


    # Try uncommenting the lines below to see argparse raise SystemExit(2) on bad flags:
    # try:
    #     probe.parse_args(["--unknown"])
    # except SystemExit as exc:
    #     print("argparse exited with code:", exc.code)


def mutually_exclusive_groups_and_validation() -> None:

    # Many CLI flags cannot meaningfully coexist, such as --quiet and --verbose
    # or --json and --csv. Calling group = parser.add_mutually_exclusive_group()
    # tells argparse to reject any invocation that supplies more than one flag
    # from that group and report a clear usage error:
    #
    #     Suppose group = parser.add_mutually_exclusive_group(required=True).
    #     Adding --quiet and --verbose to group means ["--quiet"] succeeds,
    #     ["--verbose"] succeeds, while ["--quiet", "--verbose"] or [] raises
    #     SystemExit(2).
    #
    # In unit tests, you can verify rejection in memory by wrapping
    # parser.parse_args(...) in try ... except SystemExit as exc: and checking
    # exc.code == 2.

    starter = argparse.ArgumentParser(prog="modes")
    mode_group = starter.add_mutually_exclusive_group()
    mode_group.add_argument("--quiet", action="store_true")
    mode_group.add_argument("--verbose", action="store_true")
    print("Starter exclusive group:", starter.parse_args(["--quiet"]))

    # Create a parser with group = parser.add_mutually_exclusive_group(required=True)
    # containing --fast and --thorough (both action="store_true"). Parse
    # ["--fast"] cleanly, then test both ["--fast", "--thorough"] and [] inside
    # try ... except SystemExit as exc: to confirm both exit with code 2.


    # Combine choices=("json", "csv", "toml") on an optional --format flag with
    # a mutually exclusive --compact / --pretty pair, parse valid arguments, and
    # test an invalid --format xml call inside try ... except SystemExit as exc:.


def subcommands_and_handler_dispatch() -> None:

    # Git-style CLIs (tool run ..., tool export ...) use
    # subparsers = parser.add_subparsers(dest="command", required=True).
    # Always pass required=True: without it, running the CLI with zero
    # subcommand silently returns Namespace(command=None) instead of printing
    # usage help.
    #
    # To avoid sprawling if/elif command dispatch chains, attach a callback
    # directly onto each subparser via subparser.set_defaults(handler=handle_run)
    # and invoke ns.handler(ns) after parsing:
    #
    #     Suppose run_p.set_defaults(handler=handle_run).
    #     Parsing ["run", "--workers", "8"] sets ns.handler to handle_run, so
    #     ns.handler(ns) dispatches directly without checking ns.command strings.
    #
    # Watch out for parent-option placement: global flags registered on the
    # parent parser (like -v) must appear BEFORE the subcommand (tool -vv run),
    # not after it (tool run -vv), unless shared via parents=[...].

    def handle_ping(ns: argparse.Namespace) -> str:

        return f"ping count={ns.count}"

    mini = argparse.ArgumentParser(prog="mini")
    subs = mini.add_subparsers(dest="command", required=True)
    ping_p = subs.add_parser("ping")
    ping_p.add_argument("--count", type=int, default=1)
    ping_p.set_defaults(handler=handle_ping)
    parsed = mini.parse_args(["ping", "--count", "3"])
    print("Starter dispatch:", parsed.handler(parsed))

    # Define def build_tool_parser() -> argparse.ArgumentParser: (inside this
    # function or at module level) with:
    # - A global mutually exclusive group on the parent parser for -v / --verbose
    #   (action="count", default=0) and -q / --quiet (action="store_true").
    # - subparsers = parser.add_subparsers(dest="command", required=True).
    # - Subcommand "run": takes --workers (type=int, default=4) and attaches
    #   set_defaults(handler=handle_run).
    # - Subcommand "export": takes --format (choices=("json", "csv"), required=True)
    #   and positional targets (type=Path, nargs="+"), attaching
    #   set_defaults(handler=handle_export).


    # Parse three simulated argv lists through build_tool_parser():
    # ["-vv", "run", "--workers", "8"],
    # ["-q", "export", "--format", "json", "out/a.json", "out/b.json"],
    # and test placing -vv AFTER "run" (["run", "-vv"]) inside try ... except
    # SystemExit as exc: to observe the parent-option placement rule.


    # Call ns.handler(ns) on both valid parsed Namespaces to verify clean
    # callback dispatch without any if/elif command branching.


def main() -> None:

    print("=== 1. Decoupled parser and basic flags ===")
    decoupled_parser_and_basic_flags()

    print("\n=== 2. Mutually exclusive groups and validation ===")
    mutually_exclusive_groups_and_validation()

    print("\n=== 3. Subcommands and set_defaults(handler=...) ===")
    subcommands_and_handler_dispatch()


if __name__ == "__main__":
    main()
