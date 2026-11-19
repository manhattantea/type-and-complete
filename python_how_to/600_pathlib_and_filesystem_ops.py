# python 600_pathlib_and_filesystem_ops.py

from pathlib import Path
import tempfile


def path_anatomy_and_rewrites() -> None:

    # For decades, Python code manipulated filesystem paths as plain strings
    # with os.path.join and os.path.splitext. Plain strings have a subtle flaw:
    # nothing separates a file path from ordinary text, and every operation
    # requires calling a separate helper function.
    #
    # pathlib.Path models a path as an immutable value object tailored to the
    # host OS (WindowsPath with backslashes on Windows, PosixPath with forward
    # slashes on Linux and macOS). Path overloads the / division operator via
    # __truediv__ to join path segments cleanly regardless of trailing slashes.
    # Notice one quick catch: at least one of the first two operands must
    # already be a Path object, because Python evaluates left to right:
    #
    #     Suppose base = Path("backups") / "2026" / "archive.tar.gz".
    #     Path("backups") / "2026" produces a Path, so chaining / "archive.tar.gz"
    #     keeps producing a Path. Writing "backups" / "2026" tries to divide two
    #     str objects and raises TypeError immediately.
    #
    # Anatomy properties parse the path string in memory without touching disk:
    # - .parent is the enclosing directory as a Path (at a drive root it stays
    #   at the root).
    # - .parents is an immutable sequence of every ancestor (p.parents[0] equals
    #   p.parent, p.parents[1] is the grandparent, and so on).
    # - .name is the final component including all extensions ("archive.tar.gz").
    # - .stem strips only the last extension ("archive.tar"), while .suffix is
    #   only that last extension (".gz"), and .suffixes is the full list
    #   ([".tar", ".gz"]).
    # - .with_name(...), .with_stem(...), and .with_suffix(...) each return a
    #   brand-new Path with that one piece replaced, leaving the original
    #   immutable Path untouched.
    # - .resolve() turns a relative path into an absolute canonical Path,
    #   collapsing .. segments and symlinks.

    sample = Path("backups") / "2026" / "archive.tar.gz"
    print(f"Sample: {sample} | suffixes={sample.suffixes}")

    # Bind script_path = Path(__file__).resolve() and print its .parent.name,
    # .name, .stem, .suffix, and len(script_path.parents).


    # Practice non-destructive path rewrites on sample without mutating sample:
    # - Call sample.with_name("manifest.json") to swap the entire filename.
    # - Call sample.with_stem("archive_v2") to replace only the stem while
    #   keeping ".gz" (observe why ".tar" disappears along with "archive").
    # - Call sample.with_suffix(".bak") to replace only the final ".gz" suffix.
    # Print all three derived paths and print sample to confirm it stayed unchanged.


    # Try uncommenting the line below to see TypeError when dividing two plain str values:
    # _bad = "backups" / "2026"


def text_bytes_and_atomic_writes() -> None:

    # Two everyday filesystem mistakes corrupt real production data:
    # - Always pass encoding="utf-8" to .read_text() and .write_text(). On Linux
    #   and macOS the locale encoding is almost always UTF-8, but on Windows
    #   Python's default text encoding is still a legacy regional codepage such
    #   as cp1252. Writing a Unicode checkmark or emoji without encoding="utf-8"
    #   crashes with UnicodeEncodeError on Windows or writes garbled bytes.
    # - Never overwrite a critical config or save file directly with
    #   target.write_text(...). That truncates target to 0 bytes before writing
    #   the new content; if power drops or the process crashes mid-write, both
    #   old and new versions vanish. Instead, write the complete payload to a
    #   sibling staging file in the same directory and swap it into place with
    #   staging.replace(target). Path.replace() maps to an atomic OS rename and
    #   cleanly overwrites target on both Windows and POSIX (unlike .rename(),
    #   which raises FileExistsError on Windows when target already exists).
    #
    # For raw binary payloads (headers, images, compressed blobs), .write_bytes()
    # and .read_bytes() bypass text encoding entirely and move exact bytes.
    # tempfile.TemporaryDirectory() is a context manager that creates an isolated
    # scratch directory on disk and deletes the entire tree on exit; it yields a
    # str path, so wrapping tmp = Path(tmp_str) unlocks all Path methods.
    #
    #     Suppose tmp = Path(tmp_str) and target = tmp / "settings.json".
    #     Writing staging = target.with_suffix(target.suffix + ".tmp"),
    #     calling staging.write_text('{"ok": true}\n', encoding="utf-8"), and
    #     then staging.replace(target) leaves target complete and staging gone.

    with tempfile.TemporaryDirectory() as probe_dir:
        probe_file = Path(probe_dir) / "probe.txt"
        probe_file.write_text("ready\n", encoding="utf-8")
        print("Starter temp read:", probe_file.read_text(encoding="utf-8").strip())

    # Open with tempfile.TemporaryDirectory() as tmp_str: and bind tmp = Path(tmp_str).
    # Create a nested folder data_dir = tmp / "configs" / "prod" using
    # data_dir.mkdir(parents=True, exist_ok=True) (parents=True creates missing
    # ancestors; exist_ok=True avoids FileExistsError if it already exists).
    # Verify data_dir.exists() and data_dir.is_dir() by printing both booleans.


    # Inside the same TemporaryDirectory block, write an initial UTF-8 file
    # target = data_dir / "settings.json" with '{"theme": "dark"}\n'.
    # Then perform an atomic update: create
    # staging = target.with_suffix(target.suffix + ".tmp"), write
    # '{"theme": "light", "label": "\u2713"}\n' to staging with encoding="utf-8",
    # and call staging.replace(target). Print target.read_text(encoding="utf-8")
    # and staging.exists() (expected: False).


    # Practice raw binary I/O in the same scratch folder:
    # create blob_path = data_dir / "header.bin", write
    # blob_path.write_bytes(b"\x89PNG\r\n\x1a\n"), read it back into
    # raw = blob_path.read_bytes(), and print raw.hex(" ") and len(raw).


    # Practice safe file deletion with .unlink(missing_ok=True):
    # delete blob_path with blob_path.unlink(missing_ok=True), then call
    # blob_path.unlink(missing_ok=True) a second time to verify it does not
    # raise FileNotFoundError when the file is already absent.


def directory_traversal_and_globbing() -> None:

    # pathlib gives you four clean ways to inspect directory trees depending on
    # how deep you want to look and whether you need to skip subtrees:
    # - .iterdir() yields every immediate child Path inside one directory
    #   (non-recursive, files and subdirectories mixed in OS order).
    # - .glob("*.txt") matches a wildcard pattern inside that directory only
    #   (shallow, unless you explicitly include ** in the pattern).
    # - .rglob("*.txt") is shorthand for recursive globbing ("**/*.txt"),
    #   yielding every matching Path in the directory and all nested subfolders.
    # - Path.walk() (added in Python 3.12) yields (dirpath, dirnames, filenames)
    #   triples like os.walk(), while keeping dirpath as a Path object. Mutating
    #   dirnames in place (for example dirnames[:] = [d for d in dirnames if d != ".git"])
    #   prunes whole subtrees before Python ever descends into them!
    #
    #     Suppose tmp contains notes.txt, sub/a.txt, and .git/ignored.txt.
    #     sorted(tmp.glob("*.txt")) returns only [tmp / "notes.txt"], whereas
    #     sorted(tmp.rglob("*.txt")) finds all three .txt files across every folder.

    with tempfile.TemporaryDirectory() as tree_str:
        tree_root = Path(tree_str)
        (tree_root / "README.txt").write_text("root", encoding="utf-8")
        print("Starter shallow count:", len(list(tree_root.iterdir())))

    # Open with tempfile.TemporaryDirectory() as tmp_str: and bind tmp = Path(tmp_str).
    # Build this tiny directory tree on disk:
    # - tmp / "top.txt"
    # - tmp / "data.csv"
    # - tmp / "sub" / "nested.txt" (mkdir parents=True first)
    # - tmp / "sub" / "deep" / "leaf.txt"
    # - tmp / ".cache" / "skip.txt"
    # Write short UTF-8 text into each file so all five exist as regular files.


    # Inside that same TemporaryDirectory block, contrast .iterdir(), .glob(),
    # and .rglob() on tmp:
    # - Print sorted([p.name for p in tmp.iterdir()]) to see immediate entries only.
    # - Print sorted([p.relative_to(tmp).as_posix() for p in tmp.glob("*.txt")])
    #   (expected: ["top.txt"]).
    # - Print sorted([p.relative_to(tmp).as_posix() for p in tmp.rglob("*.txt")])
    #   to confirm .rglob() walks every nested directory including ".cache".


    # Walk tmp using Python 3.12's Path.walk() while pruning ".cache":
    # write for dirpath, dirnames, filenames in tmp.walk():
    # Inside the loop, mutate dirnames in place to remove ".cache" (for example
    # if ".cache" in dirnames: dirnames.remove(".cache")), then print each
    # visited dirpath.relative_to(tmp) and sorted(filenames). Confirm skip.txt
    # is never visited.


    # Combine traversal with file inspection: collect every non-hidden .txt file
    # under tmp (excluding any path with ".cache" in p.parts), sum their byte
    # sizes using p.stat().st_size, and print the file count and total bytes.


def main() -> None:

    print("=== 1. Path anatomy and immutable rewrites ===")
    path_anatomy_and_rewrites()

    print("\n=== 2. UTF-8 text, raw bytes, and atomic writes ===")
    text_bytes_and_atomic_writes()

    print("\n=== 3. Directory traversal: iterdir, glob, rglob, and walk ===")
    directory_traversal_and_globbing()


if __name__ == "__main__":
    main()
