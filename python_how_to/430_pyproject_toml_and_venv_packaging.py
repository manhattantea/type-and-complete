# python 430_pyproject_toml_and_venv_packaging.py

from pathlib import Path
import sys
import tempfile
import tomllib


def virtual_environments_and_prefixes() -> None:

    # Running python -m venv .venv does NOT duplicate the entire Python
    # standard library. Instead, it creates a lightweight folder holding a
    # pyvenv.cfg file, a small executable shim, and an isolated site-packages
    # directory for third-party wheels.
    #
    # When the Python binary starts up, it checks for pyvenv.cfg beside itself.
    # If found, it points sys.prefix at the virtual environment root while
    # keeping sys.base_prefix pointed at the underlying base Python install:
    #
    #     Suppose base Python lives at C:\Python312 and you activate .venv.
    #     sys.base_prefix stays C:\Python312 while sys.prefix becomes
    #     ...\project\.venv, so sys.prefix != sys.base_prefix evaluates to True.

    print(f"Active executable: {sys.executable}")
    print(f"Inside virtual environment? {sys.prefix != sys.base_prefix}")

    # Compute in_venv: bool = sys.prefix != sys.base_prefix and print in_venv,
    # sys.prefix, and sys.base_prefix side by side.


    # Check whether cfg_path = Path(sys.prefix) / "pyvenv.cfg" exists. If it
    # does, read and print its lines with cfg_path.read_text(encoding="utf-8");
    # otherwise print "Running against base Python (no pyvenv.cfg)".


    # Filter sys.path for any entries containing "site-packages" and print them
    # so you can see exactly where pip/uv installs third-party packages for
    # this interpreter.


def src_layout_and_import_shadowing() -> None:

    # Because Python places the current working directory (or script folder) at
    # sys.path[0], a flat repository layout (my_pkg/__init__.py sitting directly
    # at the project root) hides a nasty packaging bug:
    #
    #     Suppose your repo has my_pkg/ at the root and you forget to include
    #     my_pkg/data.json in pyproject.toml. When you run pytest from the repo
    #     root, import my_pkg hits sys.path[0] (the raw local folder) instead of
    #     the wheel installed inside .venv/site-packages! Tests pass locally,
    #     then crash on your user's machine!
    #
    # Moving packages one level down into src/my_pkg/__init__.py prevents
    # sys.path[0] from accidentally matching my_pkg, forcing tests to import
    # the genuinely installed package from site-packages (including editable
    # installs). Running python -P (or setting PYTHONSAFEPATH=1) also stops
    # Python from auto-inserting the script folder or cwd onto sys.path[0].

    print(f"Current sys.path[0]: {sys.path[0]!r}")

    # Print sys.path[:4] to inspect the highest-priority import roots used by
    # this script, and note in a short comment what changes if you launch this
    # file with python -P 430_pyproject_toml_and_venv_packaging.py.


    # Model both layouts inside with tempfile.TemporaryDirectory() as tmp_dir:
    # - Create a flat tree: flat_root / "acme_tool" / "__init__.py"
    # - Create a src tree: src_root / "src" / "acme_tool" / "__init__.py"
    # Check (flat_root / "acme_tool").is_dir() vs (src_root / "acme_tool").is_dir()
    # to confirm why adding the repository root to sys.path[0] shadows an
    # installed wheel under flat layout but cannot shadow it under src/ layout.


def pyproject_toml_and_tomllib() -> None:

    # Modern Python packaging replaces fragmented setup.py, setup.cfg, and
    # tool-specific dotfiles with a single pyproject.toml file governed by two
    # core standards:
    # - PEP 517 / 518 ([build-system]): declares build backend tools such as
    #   hatchling or setuptools so frontends build wheels in isolation.
    # - PEP 621 ([project]): declares standard package metadata (name, version,
    #   requires-python, dependencies) and CLI console entry points under
    #   [project.scripts] (for example, acme = "acme_tool.cli:main").
    # - Tool tables ([tool.ruff], [tool.mypy]): keep linter and type-checker
    #   settings alongside project metadata.
    #
    # Since Python 3.11, the stdlib includes read-only tomllib. Note one key
    # rule: tomllib.load(fp) requires a binary file opened with "rb" because
    # the TOML spec mandates strict UTF-8 decoding rather than OS locale text
    # defaults (like cp1252 on Windows).

    starter_meta = tomllib.loads('name = "acme-tool"\nversion = "0.1.0"\n')
    print("Starter TOML parse:", starter_meta)

    # Build a realistic pyproject_text: str (using normal strings joined with
    # "\n", not triple-quoted blocks) containing:
    # - [build-system] with requires = ["hatchling"] and
    #   build-backend = "hatchling.build"
    # - [project] with name = "acme-tool", version = "0.1.0",
    #   requires-python = ">=3.12", and dependencies = []
    # - [project.scripts] with acme = "acme_tool.cli:main"
    # - [tool.ruff] with line-length = 100
    # Parse it with data = tomllib.loads(pyproject_text), then print
    # data["project"]["name"], data["project"]["requires-python"],
    # data["project"]["scripts"], and data["tool"]["ruff"]["line-length"].


    # Practice reading pyproject.toml from disk in binary "rb" mode:
    # - Inside with tempfile.TemporaryDirectory() as tmp_dir:, write
    #   pyproject_text to toml_path = Path(tmp_dir) / "pyproject.toml" with
    #   encoding="utf-8".
    # - Open with toml_path.open("rb") as fp: and parse disk_data = tomllib.load(fp).
    # - Assert disk_data == data to verify identical round-trip parsing.
    #
    # Try uncommenting below inside that TemporaryDirectory to see why text
    # mode fails in tomllib.load:
    # with toml_path.open("r", encoding="utf-8") as bad_fp:
    #     tomllib.load(bad_fp)


    # Write a small helper def missing_project_fields(doc: dict[str, object]) -> list[str]:
    # that verifies "build-system" and "project" exist at top level and that
    # "name" and "version" exist inside doc["project"], returning a list of any
    # missing keys. Test it on both your valid data dict and an incomplete
    # {"project": {"name": "partial"}} dict.


def main() -> None:

    print("=== 1. Virtual environments and sys.prefix ===")
    virtual_environments_and_prefixes()

    print("\n=== 2. src/ layout and import shadowing ===")
    src_layout_and_import_shadowing()

    print("\n=== 3. Modern pyproject.toml and tomllib ===")
    pyproject_toml_and_tomllib()


if __name__ == "__main__":
    main()
