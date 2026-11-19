# Python How-To Learning Workspace

Welcome to the **Python How-To** educational curriculum! This repository is designed to take you from your first Python script through to Python's object model, descriptors, memory layout, bytecode inspection, concurrency, C interop (`ctypes`), and complete multi-file capstone programs—using only **modern Python 3.12+ and the Python Standard Library**.

---

## 1. Quickstart & Toolchain Guide

Every standalone **Primer** (`NNN_topic.py`) and multi-file **Lab** (`NNN_topic_lab/`) is runnable out of the box with zero third-party PyPI dependencies. Use either your active `python` executable or `uv run --no-project python` (which runs cleanly without requiring a `pyproject.toml` or virtual environment setup).

### Running a Primer
Execute any standalone **Primer** directly:
```powershell
python 001_first.py
# Or using uv with explicit Python 3.12+:
uv run --no-project --python 3.12 python 001_first.py
```

Useful everyday interpreter flags you will test along the way:
- `python -B file.py`: Skip writing `__pycache__/*.pyc` bytecode files on import.
- `python -O file.py`: Set `__debug__ = False` and strip `assert` statements.
- `python -i file.py`: Run the file and drop straight into the interactive REPL afterward.
- `python -W error file.py`: Turn runtime warnings (such as `DeprecationWarning`) into exceptions.

### Fast Syntax & AST Verification (`-B` / `ast.parse`)
Verify syntax without executing top-level code or creating `__pycache__` directories (note that `ast.parse` and `py_compile` catch `SyntaxError` and `IndentationError`, while static type hints are checked separately by `mypy` or `pyright`):
```powershell
python -B -c "import ast, pathlib; ast.parse(pathlib.Path('001_first.py').read_text(encoding='utf-8'), filename='001_first.py')"
uv run --no-project python -B -c "import ast, pathlib; ast.parse(pathlib.Path('001_first.py').read_text(encoding='utf-8'), filename='001_first.py')"
```

### Running Unit Tests (`195`)
Unit testing **Primers** use Python's built-in `unittest` runner:
```powershell
python -m unittest -v 195_unit_testing_with_unittest.py
uv run --no-project python -m unittest -v 195_unit_testing_with_unittest.py
```

### Running Doctests (`470`)
Executable `>>>` docstring examples in `470` are verified with Python's built-in `doctest` module:
```powershell
python -m doctest -v 470_doctest_and_executable_documentation.py
uv run --no-project python -m doctest -v 470_doctest_and_executable_documentation.py
```

### Running Multi-File Labs (`400`–`980`)
**Labs** live in numbered subdirectories (`400_modules_import_system_and_sys_path/`, `950_ecs_entity_simulation_lab/`, etc.). Run their entry script directly, or use `python -m` for package-relative module invocation inside a **Lab** folder:
```powershell
python 400_modules_import_system_and_sys_path/main.py
# Or using -m on a package inside a Lab directory:
python -m my_package.main
# For the Tkinter capstone (980), pass --headless for automated frame verification:
python 980_arcade_simulation_and_tk_lab/main.py --headless
```

### Batch Verification Loop (PowerShell)
Syntax-check every `.py` file across all **Primers** and **Labs** in `python_how_to/` in one pass without generating `__pycache__` folders (no external test harness or manifest file required):
```powershell
python -B -c "import ast, pathlib; [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in sorted(pathlib.Path('.').rglob('*.py'))]; print('AST OK')"
```

---

## 2. Pedagogical Philosophy

### The ~5–20% Soft Scaffold & Open Drills Model
Most programming tutorials fall into one of two traps:
1. **Passive reading**: Complete reference scripts that look obvious when you read them, but evaporate the moment you open an empty editor.
2. **Blank-canvas paralysis**: An empty file where you aren't sure what structure is idiomatic, and AI coding assistants hallucinate legacy Python 2/3.6 patterns (`typing.List`, `typing.Optional`, `os.path` instead of `pathlib`, or C-style `range(len(x))` loops).

**Python How-To** uses a deliberate balance modeled on `CodingTemplateExamples/how_to/` (see approved pilots `001_first.py` and `050_for_while_and_loop_else.py`):
- **~5–20% Soft Scaffold**: Required `import` statements, topic section functions (`def ...() -> None:` with 1 blank line immediately after the `def ...:` header), `def main() -> None:` + `if __name__ == "__main__": main()` placed at the **very bottom** of the file so you read top-to-bottom, and tiny working starter lines (1–4 real lines printing or computing a baseline, plus occasional convenience syntax snippets when introducing new constructs). There are **zero** `pass`, `yield`, or dummy `return 0` / `return ""` / `return {}` / `return []` stubs; every unfilled **Primer** and **Lab** passes `ast.parse` and exits `0` out of the box.
- **Conversational `#` Prose & Graduated Drills**: All explanations live in high-contrast `#` comments (never low-contrast `"""..."""` explanatory docstrings). `"""..."""` string literals appear strictly for assigned/printed multi-line string values (`020`), `>>>` doctest targets (`470`), and minimal 1-line `__doc__` inspection targets (`001`, `100`, `140`, `420`). Prose uses causal first-principles explanations, immediate Feynman definitions whenever introducing a new keyword, operator, or stdlib construct, and concrete hypothetical before/body/after scenarios instead of abstract placeholders. Hands-on tasks are written as natural `#` **Drills** (never `# Prompt N:` labels or `Worked anchor` tags) that graduate from explicit convenience hints naming exact identifiers and types, to conversational recall, to open synthesis—sizing **Core Primers** at `~150–300+` lines (`~8–15+` **Drills**) and **Narrow Primers** at `~85–140` lines (`~4–7` **Drills**) while staying out of obscure flag trivia.

### No Pre-Written Solutions Directory
There is **no `solutions/` directory** in this workspace by design:
- Sibling solution files let editor autocomplete peek at answers and bypass active recall.
- Real mastery comes from reading the mental model, typing out each **Drill** by hand, running the file, and inspecting what Python actually does at runtime.

### Inline Error Experiments
Throughout the **Primers**, you will encounter commented-out experiments such as:
```python
# Try uncommenting: text[0] = "B"
```
Uncommenting these lines temporarily lets you observe CPython's exact runtime errors (`TypeError`, `UnboundLocalError`, `OverflowError`, `ValueError`, `RecursionError`) firsthand before commenting them back out.

---

## 3. Curriculum Roadmap (`000`–`999`)

The curriculum spans 10 tiers totaling **112 single-file Primers** and **10 multi-file Labs** (**122 numbered entries**):

| Tier Range | Tier Focus | Deliverables |
| :--- | :--- | :--- |
| **`000`–`099`** | **Toolchain, Object Model, Name Binding, Core Types & Control Flow** | 18 **Primers** (`000`–`080`) covering CLI flags, `__main__`, `print`/f-strings, names vs. objects, arbitrary-precision ints & floats, truthiness, `str` vs. `bytes`, `//`/`%` & `:=`, type hints, LEGB scopes, `if`/`match`, loops/`loop-else`, `enumerate`/`zip`, unpacking, `try`/`except`/`else`/`finally`, `ExceptionGroup`, `with`, `assert`, `warnings`, and introspection. |
| **`100`–`199`** | **Functions, Signatures, Closures, Decorators, Generators & Testing** | 12 **Primers** (`100`–`195`) covering pass-by-object-reference, mutable default trap, `*args`/`**kwargs`/`/`/`*`, late-binding closures, `@functools.wraps`, decorator factories, `@cache`/`partial`/`@singledispatch`, `operator` helpers, `yield` generators, custom context managers, `Callable`/`Protocol`/`@overload`, and `unittest`. |
| **`200`–`299`** | **Built-in Collections, Mutability, Aliasing, Hashing & Comprehensions** | 16 **Primers** (`200`–`280`) covering `list` growth & 2D list aliasing, slicing & slice assignment, `copy` vs. `deepcopy`, `tuple` & `NamedTuple`, `dict` hash tables & views, `set`/`frozenset`, `__hash__`/`__eq__` contracts, comprehensions, `defaultdict`/`Counter`/`ChainMap`, `deque`/`bisect`, `heapq`, `Enum`/`Flag`, `itertools`, `array`/`memoryview`, Timsort stability, and safe mutation during iteration. |
| **`300`–`399`** | **Object-Oriented Python, Data Model (Dunders), Descriptors & Metaclasses** | 12 **Primers** (`300`–`395`) covering `class` lookup & mutable class attributes, `@property`/`cached_property`, `@classmethod`/`@staticmethod`, C3 MRO & `super()`, `__repr__`/`__format__`/comparisons, operator & container dunders, `@dataclass(slots=True, frozen=True)`, `__slots__` memory layout, `ABC` vs. `Protocol`, descriptor protocol, `__getattr__`/`__getattribute__`, and `__init_subclass__`/metaclasses. |
| **`400`–`499`** | **Modules, Packages, Imports, Packaging & Project Architecture** | 7 **Primers** & 2 **Labs** (`400`–`480`): **Labs** `400_modules_import_system_and_sys_path/` and `410_visibility_all_and_circular_imports/`, plus **Primers** covering `importlib`/`importlib.resources`, `pyproject.toml`/venvs, `.env`/`tomllib` config, `__future__`/warnings, `assert_never`/static hygiene, `doctest`, and `zipapp` `.pyz` bundles. |
| **`500`–`599`** | **Memory Management, Refcounting, GC, Profiling, Bytecode & Performance** | 15 **Primers** & 2 **Labs** (`500`–`598`) covering refcounting & cyclic `gc`, `weakref`, `tracemalloc`, `str`/`bytes` join performance, `sys.intern`, `timeit`/`perf_counter_ns`, `cProfile`/`pstats`, lightweight stdlib zone/lock/`tracemalloc` wrappers (`565`, `568`, Lab `598` — linking to `../tracy_how_to/` for deep Tracy telemetry), `dis` bytecode, interpreter waste (`575`), `mmap`/buffer protocol (`580`), cache locality/IPC/SIMD (`585`), `ParticleSoAPool` (`590`), Amdahl Haversine (`592`), and Lab `595_memory_profiled_pipeline_lab/`. |
| **`600`–`699`** | **Standard Library Essentials: Files, Serialization, Regex, SQLite & CLI** | 11 **Primers** (`600`–`695`) covering `pathlib`, UTF-8 I/O streams, `json`/`csv`/`tomllib`, binary `struct`, `re`, timezone-aware `datetime`/`zoneinfo`, `argparse`, structured `logging`, `sqlite3`, `hashlib`/`hmac`/`secrets`, and `subprocess.run`. |
| **`700`–`799`** | **Advanced Type System, Generics (PEP 695), AST, Inspection & Hooks** | 8 **Primers** (`700`–`770`) covering PEP 695 `[T]` generics, variance/`ParamSpec`/`TypeVarTuple`, `TypedDict`/`NewType`/`TypeIs`, `inspect.signature` & `Annotated`, `ast` visitors/transformers, safe `ast.literal_eval`, `sys.monitoring` `LINE` tracing & `traceback` inspection (`760` — linking to `../tracy_how_to/700_...` for callback distortion), and `sys.meta_path` import hooks. |
| **`800`–`899`** | **Concurrency (`threading`, `multiprocessing`, `asyncio`) & C Interop (`ctypes`)** | 9 **Primers** & 2 **Labs** (`800`–`890`) covering threads/GIL & `Lock`/`RLock`, `queue.Queue`/`ThreadPoolExecutor`, `ProcessPoolExecutor`/`SharedMemory`, `asyncio` event loop, `TaskGroup`/`asyncio.Queue`/`timeout`, Lab `850_concurrent_pipeline_lab/`, `ctypes` C FFI (`860`), zero-copy `ctypes.from_buffer` 1D dot-product offload (`865` — linking to `../tracy_how_to/800_...` for multi-layer FFI trace timelines), Lab `870_native_plugin_hot_reload_lab/`, non-blocking `selectors`, and `atexit`/signals. |
| **`900`–`999`** | **Complete Programs & Multi-File Training Capstones** | 4 **Primers** (`900`–`930`: hex dumper, open-addressing `HashTable[K, V]`, SQLite/JSON task CLI, `asyncio` TCP command server) & 4 **Labs** (`940_log_search_and_word_freq_lab/`, `950_ecs_entity_simulation_lab/`, `960_bytecode_vm_and_compiler_lab/`, `980_arcade_simulation_and_tk_lab/`). |

### Cross-Repo Boundaries (`python_how_to/` vs. `../tracy_how_to/`)
All numbered entries are preserved across workspaces, with strict responsibility boundaries so you never repeat the same **Drill** twice:
- **`python_how_to/` (`550`–`598`, `760`, `865`)** owns Python standard library profiling, VM internals, and FFI pointer mechanics (`timeit`, `cProfile`, `dis`, `PyLongObject`/`PyFloatObject` waste, `mmap`/`memoryview`, `array("d")` cache density, `ParticleSoAPool`, Amdahl Haversine, `sys.monitoring` `LINE` tracing, and `ctypes.from_buffer` 1D dot-product ABI).
- **`565`, `568`, and Lab `598`** stay slimmed down to pure-Python stdlib zone/lock/`tracemalloc` wrappers that link to [`../tracy_how_to/`](../tracy_how_to/) for `TracySourceLocationData` `ctypes` pinning (`tracy_how_to/150`), nested `Self Time` + recursive zones (`tracy_how_to/250`), Gen-0 GC & object churn forensics (`tracy_how_to/350`), GIL/`asyncio` timeline freezes (`tracy_how_to/450`), Chrome `"ph": "C"` / `"ph": "i"` flight-recorder schemas (`tracy_how_to/550`), `sys.monitoring` distortion (`tracy_how_to/700`), hybrid Python+Odin FFI timeline tracing (`tracy_how_to/800` vs `865`), and 5-system Hotspot Hunt capstones (`tracy_how_to/950`).

---

## 4. Python Mental Model & Anti-Gotcha Cheat Sheet

Coming from C, C++, Rust, Odin, Go, or Java? Internalize these core Python runtime semantics early to avoid the most common bugs:

### 1. Names Are Labels Bound to Objects (Not Typed Memory Boxes)
Assigning `b = a` never copies a value into a stack slot—it binds another name in the current namespace to the exact same heap-allocated `PyObject` (refcount + type pointer + value).
- **Rebinding** (`items = []` or `x = x + 1`) detaches the local label and points it at a different object; other aliases are untouched.
- **Mutating in place** (`items.append(4)` or `items[:] = []`) modifies the underlying object, so every alias sees the change.

### 2. Identity (`is`) vs. Equality (`==`)
- Use `is` and `is not` **only** for singletons (`None`, `True`, `False`, `Ellipsis`, `Enum` members, or custom sentinels like `MISSING = object()`).
- **Never** compare numbers or strings with `is` for equality! CPython pre-allocates small integers (`-5` through `256`) and interns some strings, making `a is b` appear to work on `200` and suddenly fail on `int("5000")`. Always use `==` for value equality.

### 3. Mutable Default Arguments
Default parameter expressions are evaluated **once at `def` time**, not on each call:
```python
# Bug: every call without `buf` shares and mutates the same default list
def bad_append(val: int, buf: list[int] = []) -> list[int]:
    buf.append(val)
    return buf

# Fix: use None as the default and allocate a fresh list inside the call
def good_append(val: int, buf: list[int] | None = None) -> list[int]:
    if buf is None:
        buf = []
    buf.append(val)
    return buf
```

### 4. Late-Binding Loop Closures
Functions inside loops capture the **variable cell**, not its value at the iteration where the function was created:
```python
# Bug: all 5 lambdas look up `i` when called later and return 4
funcs = [lambda: i for i in range(5)]

# Fix: bind the current iteration's value via a default argument
funcs = [lambda i=i: i for i in range(5)]
```

### 5. 2D List Multiplication Aliasing
Multiplying a list copies **references**, not independent inner lists:
```python
# Bug: all 3 rows point to the exact same inner list object
grid = [[0] * 3] * 3

# Fix: allocate a fresh inner list per row
grid = [[0] * 3 for _ in range(3)]
```

### 6. No Block Scope (`if` / `for` / `while` / `with` / `try`)
Compound blocks like `if`, `for`, and `with` do **not** create a new lexical scope in Python—variables assigned inside them live in the enclosing function (only `def`, `class`, modules, and comprehensions have their own scope). Also, any assignment `x = ...` anywhere in a `def` marks `x` local to that entire function at compile time, causing `UnboundLocalError` if `x` is read before that line.

### 7. Single-Pass Generator & Iterator Exhaustion
Generators, generator expressions `(x for x in items)`, `zip()`, `map()`, and `filter()` are single-pass iterators. Once consumed by a `for` loop, `list()`, or `sum()`, they are permanently exhausted and yield zero items on a second pass.

### 8. `list.sort()` Mutates In Place and Returns `None`
`items.sort()` modifies `items` in place and returns `None` explicitly so you never mistake an in-place mutation for a copy (`x = items.sort()` sets `x` to `None`!). When you want a new sorted list and need to preserve the original, call `sorted(items)`.

### 9. Truthiness Traps & Modern Annotations
- **`0`, `0.0`, `""`, `[]` are falsy**: Write `if count is not None:` rather than `if count:` whenever `0` is a valid non-missing value.
- **Mutable class attributes**: Declaring `tags: list[str] = []` directly in a `class` body shares one list across all instances; assign instance data in `__init__` or use `@dataclass` with `field(default_factory=list)`.
- **Modern type hints (3.12+)**: Prefer `list[int]`, `dict[str, float]`, `X | None`, `collections.abc` (`Sequence`, `Mapping`, `Iterable`, `Callable`), and PEP 695 (`def f[T](x: T) -> T:`) over legacy `typing.List`, `typing.Optional`, or `TypeVar`.

Happy coding in Python!
