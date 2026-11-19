# python 620_json_csv_and_tomllib.py

import csv
from dataclasses import asdict, dataclass
import io
import json
from pathlib import Path
import tempfile
import tomllib


def json_coercion_and_object_hooks() -> None:

    # Python's stdlib gives you three everyday structured formats: json for
    # nested interchange (APIs, snapshots), csv for flat tables, and tomllib for
    # human-edited config files like pyproject.toml.
    #
    # JSON only knows six types: object (string-keyed map), array, string,
    # number, boolean, and null. Because Python has richer types, json.dumps()
    # silently coerces some values and rejects others:
    # - Tuples become JSON arrays and decode back as lists, not tuples.
    # - Integer dict keys are silently converted to strings!
    #
    #     Suppose original = {1: (2, 3)}.
    #     json.dumps(original) produces '{"1": [2, 3]}'.
    #     json.loads(json.dumps(original)) returns {"1": [2, 3]} with zero
    #     warning—so original == restored is False!
    #
    # Non-JSON types such as @dataclass instances, Path, datetime, or set raise
    # TypeError unless you pass default=fn to json.dumps(). The callback fn(obj)
    # receives any object json cannot natively encode and returns a JSON-safe
    # substitute (such as asdict(obj) or a tagged dict like {"__type__": "PlayerSave", ...}).
    #
    # On the decode side, json.loads(text, object_hook=hook) calls hook(d) on
    # every decoded JSON object dict (bottom-up). If hook recognizes a tag or
    # field shape, it returns a reconstructed Python object; otherwise it returns
    # d unchanged. Useful formatting flags: indent=2 and sort_keys=True for
    # readable diffs, or separators=(",", ":") for compact wire payloads.

    baseline = json.dumps({"ok": True, "count": 3}, sort_keys=True)
    print("Starter compact JSON:", baseline)

    # Prove JSON's silent key and tuple coercion:
    # bind original = {1: (2, 3)}, round-trip it via
    # restored = json.loads(json.dumps(original)), and print original, restored,
    # and original == restored (expected: False, with string key "1" and list [2, 3]).


    # Define @dataclass(slots=True) class PlayerSave: with fields name: str,
    # level: int, and badges: list[str].
    # Instantiate save = PlayerSave(name="Ada", level=12, badges=["scout", "coder"]).
    # Serialize it with payload = json.dumps(save, default=asdict, indent=2, sort_keys=True),
    # print payload, and rebuild direct = PlayerSave(**json.loads(payload)).
    # Print direct == save (expected: True).


    # Now rebuild rich objects automatically using json.loads(..., object_hook=...):
    # write a helper def encode_tagged(obj: object) -> dict[str, object]: that
    # checks isinstance(obj, PlayerSave) and returns {"__kind__": "PlayerSave", **asdict(obj)}
    # (raising TypeError for anything else).
    # Write def decode_tagged(d: dict[str, object]) -> object: that checks
    # d.get("__kind__") == "PlayerSave" and returns a PlayerSave instance from
    # its fields, or returns d unchanged for normal dicts.
    # Round-trip envelope = {"slot": 1, "save": save} through
    # json.dumps(envelope, default=encode_tagged) and
    # json.loads(..., object_hook=decode_tagged), then print type(rebuilt["save"])
    # and rebuilt["save"] == save.


    # Try uncommenting the line below to see TypeError on an unsupported set value:
    # json.dumps({"tags": {"fast", "safe"}})


def csv_tables_and_windows_newline_trap() -> None:

    # The csv module implements RFC 4180 and writes "\r\n" line endings by
    # default. On Windows, that collides badly with TextIOWrapper's default
    # newline translation:
    #
    #     Suppose you open a file on Windows with open(path, "w", encoding="utf-8")
    #     and omit newline="".
    #     csv.writer writes "Ada,95\r\n". TextIOWrapper translates the "\n" into
    #     "\r\n", putting "Ada,95\r\r\n" on disk—creating a blank empty row
    #     between every real row when read back!
    #
    # Always pass newline="" to open() or Path.open() for both reading and
    # writing CSV files so the csv module controls line endings directly. Pass
    # lineterminator="\n" to csv.writer / csv.DictWriter when you want clean
    # Unix LF endings across platforms.
    #
    # csv.DictWriter maps column names (fieldnames) to dict keys, and
    # csv.DictReader yields one dict per row (with every cell decoded as str!).

    preview = list(csv.DictReader(io.StringIO("name,score\nAda,95\n")))
    print("Starter CSV row:", preview)

    # Create csv_buf = io.StringIO() and fieldnames = ["name", "score"].
    # Use writer = csv.DictWriter(csv_buf, fieldnames=fieldnames, lineterminator="\n"),
    # call writer.writeheader(), and write three rows:
    # {"name": "Ada", "score": 95}, {"name": "Grace", "score": 99}, and
    # {"name": "Linus", "score": 91}.
    # Call csv_buf.seek(0) (without seek(0) the cursor sits at EOF and reads 0 rows!),
    # read rows = list(csv.DictReader(csv_buf)), and print rows plus
    # type(rows[0]["score"]) to confirm CSV values always come back as str.


    # Practice real disk CSV I/O with newline="" inside TemporaryDirectory():
    # open with tempfile.TemporaryDirectory() as tmp_str:, bind
    # csv_path = Path(tmp_str) / "scores.csv", and write a row containing a comma
    # inside a quoted field (for example {"name": "Lovelace, Ada", "score": 95})
    # using csv_path.open("w", encoding="utf-8", newline="").
    # Inspect csv_path.read_bytes() to see proper RFC 4180 quoting and zero
    # "\r\r\n" double-CR corruption, then read it back via
    # csv_path.open("r", encoding="utf-8", newline="") and csv.DictReader.


def tomllib_config_and_binary_mode() -> None:

    # tomllib (added in Python 3.11) parses TOML configuration files such as
    # pyproject.toml into native Python dicts, lists, ints, floats, bools, and
    # even datetime/date objects. (tomllib is read-only in the stdlib.)
    #
    # Watch one sharp difference between json.load() and tomllib.load():
    # - tomllib.loads(text) parses a Python str already in memory.
    # - tomllib.load(fp) REQUIRES a binary file opened in "rb" mode—never text
    #   mode "r"! The TOML spec mandates strict UTF-8, so tomllib refuses to
    #   trust a text wrapper that might be using a platform codepage like cp1252.
    #
    #     Suppose cfg_path = tmp / "app.toml".
    #     with cfg_path.open("rb") as fp:
    #         data = tomllib.load(fp)     # works cleanly on every OS
    #     Passing cfg_path.open("r", encoding="utf-8") raises TypeError!

    inline_toml = '[server]\nhost = "127.0.0.1"\nport = 8080\n'
    cfg = tomllib.loads(inline_toml)
    print("Starter TOML config:", cfg)

    # Parse a richer TOML string with tomllib.loads containing:
    # - a [project] table with name = "scanner" and version = "0.2.0"
    # - a [database] table with port = 5432, ssl = true, and hosts = ["db1", "db2"]
    # - a release_date = 2026-11-19 bare TOML date
    # Print the parsed dict and check type(parsed["release_date"]) (datetime.date!).


    # Load a real .toml file from disk in binary "rb" mode:
    # open with tempfile.TemporaryDirectory() as tmp_str:, bind
    # toml_path = Path(tmp_str) / "config.toml", write UTF-8 TOML text using
    # toml_path.write_text('[worker]\nthreads = 4\nlabel = "ok"\n', encoding="utf-8"),
    # then open it with toml_path.open("rb") as fp: and call
    # disk_cfg = tomllib.load(fp). Print disk_cfg["worker"].


    # Verify why text mode fails with tomllib.load:
    # inside a TemporaryDirectory block (or using io.StringIO('[a]\nx = 1\n')),
    # pass a text stream to tomllib.load(...) inside try ... except TypeError as err:
    # and print the error message.
    #
    # Try uncommenting the line below for a direct TypeError without catching:
    # tomllib.load(io.StringIO('[a]\nx = 1\n'))


def main() -> None:

    print("=== 1. JSON coercion, default encoders, and object_hook ===")
    json_coercion_and_object_hooks()

    print("\n=== 2. CSV DictWriter, DictReader, and newline='' ===")
    csv_tables_and_windows_newline_trap()

    print("\n=== 3. TOML parsing with tomllib.loads and binary tomllib.load ===")
    tomllib_config_and_binary_mode()


if __name__ == "__main__":
    main()
