# python 440_config_env_vars_and_dotenv_patterns.py

from collections.abc import Mapping
from dataclasses import dataclass, field
import os
from typing import Self


def env_var_traps_and_bool_parsing() -> None:

    # Every operating system environment variable stored in os.environ is a
    # plain str (or None when missing from os.getenv). Two everyday bugs follow
    # straight from that fact:
    #
    # - The string boolean trap: bool("false") and bool("0") both evaluate to
    #   True because EVERY non-empty string in Python is truthy! Never cast an
    #   environment variable with bool(os.getenv(...)); always match normalized
    #   lowercase tokens explicitly.
    # - Empty string vs. unset: os.getenv("API_KEY", "fallback") returns
    #   "fallback" ONLY when "API_KEY" is absent from os.environ. If a shell or
    #   container exports API_KEY="", os.getenv returns "" instead of the
    #   fallback!
    #
    #     Suppose os.environ has {"DEBUG": "false", "API_KEY": ""}.
    #     bool(os.getenv("DEBUG", "false")) returns True (bug!).
    #     os.getenv("API_KEY", "fallback") returns "" (bug if you expected fallback!).

    print("Trap check -> bool('false') evaluates to:", bool("false"))
    print("Unset env lookup ->", os.getenv("ODIN_LEARNING_MISSING_KEY", "fallback"))

    # Write def parse_env_bool(raw: str | None, default: bool = False) -> bool:
    # right here (or at module scope above main):
    # - If raw is None or raw.strip() == "": return default.
    # - Normalize with normalized = raw.strip().lower().
    # - Return True if normalized in {"1", "true", "yes", "on"}.
    # - Return False if normalized in {"0", "false", "no", "off"}.
    # - Otherwise raise ValueError(f"Invalid boolean env value: {raw!r}").
    # Test it on "false", "YES", "   ", None, and catch ValueError on "maybe".


    # Write def parse_env_port(raw: str | None, default: int = 8000) -> int:
    # that treats None or blank strings as default, parses int(raw.strip()),
    # and raises ValueError if the string is not an integer or falls outside
    # 1 <= port <= 65535. Test it on "9090", "", and "not-a-port".


def zero_dependency_dotenv_parsing() -> None:

    # Local development often keeps non-committed defaults in a .env file while
    # production injects live environment variables. Writing a clean
    # zero-dependency parser takes ~15 lines once you handle three real-world
    # edge cases:
    #
    # - Values containing "=" (Base64 secrets like "abc=123==" or database URLs
    #   with query strings): plain line.split("=") splits into 3+ pieces and
    #   crashes on unpacking! Always use line.split("=", maxsplit=1).
    # - Optional shell export prefixes (export HOST="0.0.0.0") stripped cleanly
    #   via line.removeprefix("export ").
    # - Matching outer quotes: strip surrounding double quotes ("...") or
    #   single quotes ('...') ONLY when both ends match, preserving quotes
    #   inside the value.
    #
    #     Suppose a .env line reads: export API_KEY="abc=123=="
    #     After removeprefix("export ") and split("=", maxsplit=1), key is
    #     "API_KEY" and value becomes "abc=123==" without truncating "==".

    sample_line = "API_KEY=abc=123=="
    sample_key, sample_val = sample_line.split("=", maxsplit=1)
    print(f"maxsplit=1 keeps trailing '=' -> {sample_key}={sample_val!r}")

    # Write def parse_dotenv_lines(content: str) -> dict[str, str]:
    # - Iterate over content.splitlines(), strip surrounding whitespace, and
    #   skip empty lines or lines starting with "#".
    # - Strip an optional leading "export " prefix via line.removeprefix("export ").
    # - If "=" not in line, raise ValueError(f"Malformed .env line: {line!r}").
    # - Split via key, value = line.split("=", maxsplit=1), strip both, and
    #   remove matching outer '"' or "'" quotes when len(value) >= 2 and
    #   value[0] == value[-1] and value[0] in {'"', "'"}.
    # - Store result[key] = value and return result.


    # Test parse_dotenv_lines on a multi-line sample containing comments, blank
    # lines, an export HOST="127.0.0.1" line, PORT=8080, DEBUG=true, and
    # API_KEY="abc=123==". Print the parsed dictionary and assert
    # parsed["API_KEY"] == "abc=123==".


def typed_config_validation_and_secret_masking() -> None:

    # Scattered os.getenv() calls throughout a codebase fail late and leak
    # secrets in logs. The clean Python pattern loads every setting ONCE at
    # startup into an immutable @dataclass(slots=True, frozen=True) config
    # object with three safeguards:
    #
    # - Explicit precedence: defaults < optional .env file < live os.environ
    #   (so container/CI env vars always override checked-in or local .env).
    # - Fail-fast validation with a dedicated ConfigError(Exception): if a
    #   required setting such as API_KEY is missing or blank ("   "), raise
    #   ConfigError immediately at startup instead of failing deep inside an
    #   API request later.
    # - Secret masking in __repr__: by default, a dataclass auto-generates a
    #   __repr__ that prints EVERY field verbatim, dumping API keys into logs
    #   and tracebacks! Marking api_key: str = field(repr=False) hides it from
    #   the generated repr, or writing a custom __repr__ prints
    #   api_key='<REDACTED>' while keeping all non-secret fields visible.
    #
    #     Suppose cfg = AppConfig(host="127.0.0.1", port=9090, debug=False, api_key="abc=123==").
    #     repr(cfg) prints AppConfig(host='127.0.0.1', port=9090, debug=False, api_key='<REDACTED>')
    #     so "abc=123==" never appears in terminal output or log files.

    print("Starter types ready:", Mapping.__name__, dataclass.__name__, field.__name__, Self)

    # Define a custom configuration exception class ConfigError(Exception):
    # with def __init__(self, key: str, reason: str) -> None: storing
    # self.key = key and calling super().__init__(f"Config error for {key}: {reason}").


    # Define @dataclass(slots=True, frozen=True) class AppConfig: with fields:
    # - host: str
    # - port: int
    # - debug: bool
    # - api_key: str = field(repr=False)
    # Add a custom def __repr__(self) -> str: returning
    # f"AppConfig(host={self.host!r}, port={self.port}, debug={self.debug}, api_key='<REDACTED>')"
    # so logs show clearly that a key is set without exposing its characters.


    # Add @classmethod def from_env(cls, env: Mapping[str, str] | None = None, dotenv_content: str = "") -> Self:
    # onto AppConfig:
    # - Merge merged = parse_dotenv_lines(dotenv_content) | dict(os.environ if env is None else env)
    #   so live env values override .env entries.
    # - Read raw_key = merged.get("API_KEY", "").strip(); if not raw_key, raise
    #   ConfigError("API_KEY", "required setting is missing or blank").
    # - Parse host = merged.get("HOST", "127.0.0.1").strip() or "127.0.0.1",
    #   port via parse_env_port (converting ValueError into ConfigError("PORT", ...)),
    #   and debug via parse_env_bool (converting ValueError into ConfigError("DEBUG", ...)).
    # - Return cls(host=host, port=port, debug=debug, api_key=raw_key).


    # Verify precedence, masking, and fail-fast validation:
    # - Pass a sample .env containing DEBUG=true, PORT=8080, API_KEY="abc=123=="
    #   together with override_env = {"DEBUG": "false", "PORT": "9090"} to
    #   AppConfig.from_env(env=override_env, dotenv_content=sample_dotenv).
    # - Assert cfg.debug is False, cfg.port == 9090, and cfg.api_key == "abc=123==".
    # - Assert "abc=123==" not in repr(cfg) and "<REDACTED>" in repr(cfg), then print(cfg).
    # - Call AppConfig.from_env(env={"API_KEY": "   "}) inside
    #   try ... except ConfigError as err: and print err to verify missing/blank
    #   required keys fail loudly.


def main() -> None:

    print("=== 1. Environment variable traps and typed parsing ===")
    env_var_traps_and_bool_parsing()

    print("\n=== 2. Zero-dependency .env parsing ===")
    zero_dependency_dotenv_parsing()

    print("\n=== 3. Frozen AppConfig, ConfigError, and secret masking ===")
    typed_config_validation_and_secret_masking()


if __name__ == "__main__":
    main()
