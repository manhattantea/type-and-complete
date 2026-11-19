# python 480_zipapp_and_single_file_bundles.py

from pathlib import Path
import subprocess
import sys
import tempfile
import zipapp
import zipfile


def zipimport_and_bundle_creation() -> None:

    # Python's built-in zipimport loader can import .py modules directly from
    # inside a .zip archive. If that archive contains a __main__.py file at its
    # root, Python can execute the entire multi-module application directly via
    # python app.pyz!
    #
    # Why does prepending a Unix shebang (#!/usr/bin/env python3\n) to a binary
    # .zip file work without corrupting the archive?
    # Because the ZIP format stores its Central Directory at the END of the
    # file rather than at byte 0:
    #
    #     Suppose app.pyz starts with b"#!/usr/bin/env python3\nPK\x03\x04...".
    #     The OS script loader reads byte 0 and launches python3, while zipfile
    #     and zipimport seek to the tail of app.pyz to locate the Central
    #     Directory and ignore the leading shebang bytes cleanly.
    #
    # Practical boundary: zipapp shines for pure-Python CLI tools and bundled
    # text/data assets (read via importlib.resources). Compiled C-extension
    # wheels (.pyd on Windows, .so on Linux) cannot be loaded by the OS dynamic
    # linker directly from inside a zip archive.

    print(f"zipapp host interpreter: {sys.executable}")

    # Create a tiny multi-module bundle inside with tempfile.TemporaryDirectory() as tmp_dir:
    # - Make app_dir = Path(tmp_dir) / "hello_bundle" (app_dir.mkdir()).
    # - Write app_dir / "helper.py" defining def greet(name: str) -> str:
    #   returning f"Hello from zipapp, {name}!" plus def run() -> None:
    #   printing greet("AutoEntry").
    # - Write app_dir / "__main__.py" importing from helper import greet and
    #   printing greet("Python").


    # Package app_dir into archive_path = Path(tmp_dir) / "app.pyz" using:
    # zipapp.create_archive(app_dir, target=archive_path, interpreter="/usr/bin/env python3", compressed=True)
    # Assert archive_path.exists() and assert
    # zipapp.get_interpreter(archive_path) == "/usr/bin/env python3".


def inspecting_and_running_pyz_bundles() -> None:

    # Because a .pyz file is a standard ZIP archive (optionally prefixed with a
    # shebang line), you can inspect its entries with zipfile.ZipFile, verify
    # its leading shebang bytes directly, and run it in a child interpreter via
    # subprocess.run([sys.executable, str(archive_path)], ...).
    #
    # When your source directory does NOT have a __main__.py file, passing
    # main="module:callable" to zipapp.create_archive() tells Python to
    # auto-generate a tiny __main__.py wrapper inside the archive for you.

    print(
        "Bundle tools ready:",
        Path(sys.executable).name,
        zipapp.create_archive.__name__,
        zipfile.ZipFile.__name__,
        subprocess.run.__name__,
        tempfile.TemporaryDirectory.__name__,
    )

    # Inside the same TemporaryDirectory workflow (or a helper returning the
    # built bundle path inside a TemporaryDirectory context):
    # - Open with zipfile.ZipFile(archive_path) as zf: and print zf.namelist()
    #   to confirm both "__main__.py" and "helper.py" are packed inside.
    # - Print archive_path.read_bytes()[:32] to see the leading
    #   b"#!/usr/bin/env python3\n" shebang followed immediately by b"PK".


    # Execute the .pyz bundle in a clean subprocess:
    # proc = subprocess.run([sys.executable, str(archive_path)], capture_output=True, text=True, check=True)
    # Print proc.stdout.strip() and assert
    # proc.stdout.strip() == "Hello from zipapp, Python!".


    # Test auto-generated entry points with main="helper:run":
    # - Create a second folder auto_dir = Path(tmp_dir) / "auto_bundle" holding
    #   ONLY helper.py (no __main__.py).
    # - Call zipapp.create_archive(auto_dir, target=auto_pyz, main="helper:run", compressed=True).
    # - Open auto_pyz with zipfile.ZipFile and print
    #   zf.read("__main__.py").decode("utf-8") to inspect the generated stub,
    #   then execute auto_pyz with subprocess.run and verify "Hello from zipapp, AutoEntry!".


def main() -> None:

    print("=== 1. zipimport mechanics and creating .pyz bundles ===")
    zipimport_and_bundle_creation()

    print("\n=== 2. Inspecting and executing .pyz bundles ===")
    inspecting_and_running_pyz_bundles()


if __name__ == "__main__":
    main()
