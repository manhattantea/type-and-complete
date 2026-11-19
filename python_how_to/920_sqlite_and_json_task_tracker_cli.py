# python 920_sqlite_and_json_task_tracker_cli.py

# This capstone synthesizes five everyday Python standard-library tools into a
# single durable CLI application:
# - @dataclass(slots=True) for compact, fast in-memory domain records.
# - StrEnum (Python 3.11+) for string-compatible enums whose members ARE plain
#   str instances, so TaskCommand.ADD == "add" works directly in argparse, SQLite
#   parameters, and json.dumps without noisy .value conversions.
# - sqlite3 with sqlite3.Row and parameterized '?' queries for durable storage.
# - json export via dataclasses.asdict for portable serialization.
# - argparse subcommands paired with a zero-argument automated self-test inside
#   tempfile.TemporaryDirectory so the script stays verifiable on every run.

from dataclasses import asdict, dataclass
from enum import StrEnum
import json
from pathlib import Path
import sqlite3
import sys


class TaskCommand(StrEnum):
    ADD = "add"
    DONE = "done"
    LIST = "list"
    EXPORT = "export"


@dataclass(slots=True)
class Task:
    id: int
    title: str
    done: bool


def sqlite_task_store_design() -> None:

    # Two classic Python sqlite3 realities trip up almost every first-time author:
    #
    # First, 'with conn:' commits or rolls back a SQL transaction—it does NOT
    # close the database connection!
    #
    #     Suppose a self-test creates db_path = Path(tmpdir) / "tasks.db" inside
    #     with tempfile.TemporaryDirectory() as tmpdir: and runs queries inside
    #     with conn: without calling conn.close().
    #     On Windows, when TemporaryDirectory tries to delete tasks.db on exit,
    #     the open sqlite3.Connection still holds a file lock and raises
    #     PermissionError: [WinError 32].
    #
    # Wrapping TaskStore in contextlib.closing(store) calls store.close()
    # automatically on block exit, releasing the OS handle before TemporaryDirectory
    # removes the folder.
    #
    # Second, always pass SQL values through '?' parameter tuples rather than
    # f-strings, and remember Python's trailing comma for a 1-element tuple:
    # (task_id,) is a 1-item tuple, while (task_id) is just a plain int!
    # Also note SQLite stores booleans as integer 0 or 1, so reconstructing Task
    # rows explicitly converts bool(row["done"]).

    sample = Task(id=1, title="Draft schema", done=False)
    print(f"Starter SQLite {sqlite3.sqlite_version}; sample JSON: {json.dumps(asdict(sample))}")

    # Define class TaskStore: (at module scope or above main) backed by sqlite3
    # with these exact methods and signatures:
    #
    # - __init__(self, db_path: Path | str) -> None:
    #   Open self._conn = sqlite3.connect(db_path) and configure
    #   self._conn.row_factory = sqlite3.Row so rows support named lookup like
    #   row["title"] instead of brittle positional indices like row[1].
    #
    # - close(self) -> None:
    #   Close self._conn so contextlib.closing(store) releases file locks cleanly.
    #
    # - init_schema(self) -> None:
    #   Inside with self._conn:, execute:
    #   CREATE TABLE IF NOT EXISTS tasks (
    #       id INTEGER PRIMARY KEY AUTOINCREMENT,
    #       title TEXT NOT NULL,
    #       done INTEGER NOT NULL DEFAULT 0
    #   )
    #
    # - add_task(self, title: str) -> Task:
    #   Inside with self._conn:, insert (title, 0) using parameterized '?'
    #   placeholders: INSERT INTO tasks (title, done) VALUES (?, ?).
    #   Read task_id = cursor.lastrowid, assert task_id is not None, and return
    #   Task(id=task_id, title=title, done=False).
    #
    # - complete_task(self, task_id: int) -> bool:
    #   Inside with self._conn:, execute UPDATE tasks SET done = 1 WHERE id = ?
    #   with the 1-element tuple (task_id,). Return cursor.rowcount > 0 so callers
    #   know whether a matching task ID actually existed.
    #
    # - list_tasks(self, only_pending: bool = False) -> list[Task]:
    #   Query SELECT id, title, done FROM tasks (adding WHERE done = 0 when
    #   only_pending is True), ordered by id ASC. Convert each sqlite3.Row into
    #   Task(id=row["id"], title=row["title"], done=bool(row["done"])).
    #
    # - export_json(self) -> str:
    #   Call tasks = self.list_tasks() and return
    #   json.dumps([asdict(task) for task in tasks], indent=2).


def cli_subcommands_and_self_test() -> None:

    # argparse.ArgumentParser.add_subparsers(dest="command", required=True) builds
    # Git-style subcommands where each subcommand declares its own flags:
    #
    #     Suppose the user runs:
    #       python 920_sqlite_and_json_task_tracker_cli.py --db demo.db add "Ship CLI"
    #     parser.parse_args(sys.argv[1:]) produces args.db == Path("demo.db"),
    #     args.command == "add", and args.title == "Ship CLI".
    #
    # Branching on len(sys.argv) == 1 lets running the script with zero arguments
    # execute a full end-to-end self-test in an isolated TemporaryDirectory without
    # polluting the workspace with stray tasks.db files.

    mode = "self-test" if len(sys.argv) == 1 else "cli"
    default_db = Path("tasks.db")
    print(f"Starter CLI mode: {mode}, commands={[c.value for c in TaskCommand]}, default_db={default_db}")

    # Import argparse at the top of the file and define:
    # def build_parser() -> argparse.ArgumentParser:
    # Create parser = argparse.ArgumentParser(description="SQLite + JSON Task Tracker"),
    # add optional --db (type=Path, default=Path("tasks.db")), and attach
    # subparsers = parser.add_subparsers(dest="command", required=True).
    # Register four subcommands using TaskCommand members:
    # - TaskCommand.ADD: positional title (str).
    # - TaskCommand.DONE: positional task_id (type=int).
    # - TaskCommand.LIST: optional --pending boolean flag (action="store_true").
    # - TaskCommand.EXPORT: no extra arguments (prints JSON to stdout).


    # Wire both execution branches using from contextlib import closing and
    # import tempfile:
    # - When len(sys.argv) == 1 (automated self-test):
    #   Open with tempfile.TemporaryDirectory() as tmpdir:, set
    #   db_path = Path(tmpdir) / "tasks.db", and wrap
    #   with closing(TaskStore(db_path)) as store:
    #   Call store.init_schema(), add 3 tasks ("Write hex dumper",
    #   "Verify tombstones", "Ship async TCP"), mark task 2 done via
    #   assert store.complete_task(2) is True, verify a nonexistent ID returns
    #   False (assert store.complete_task(999) is False), assert
    #   len(store.list_tasks(only_pending=True)) == 2, export JSON via
    #   payload = store.export_json(), parse decoded = json.loads(payload)
    #   asserting len(decoded) == 3 and decoded[1]["done"] is True, and print
    #   the pending tasks plus formatted JSON payload.
    # - When len(sys.argv) > 1 (interactive CLI dispatch):
    #   Call args = build_parser().parse_args(sys.argv[1:]), open
    #   with closing(TaskStore(args.db)) as store:, call store.init_schema(),
    #   and match args.command against TaskCommand.ADD, TaskCommand.DONE,
    #   TaskCommand.LIST, and TaskCommand.EXPORT to execute and print the result.


def main() -> None:

    print("=== 1. SQLite TaskStore design ===")
    sqlite_task_store_design()

    print("\n=== 2. CLI subcommands and self-test ===")
    cli_subcommands_and_self_test()


if __name__ == "__main__":
    main()
