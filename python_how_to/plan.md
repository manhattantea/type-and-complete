# Python How-To — Exhaustive Per-File Training Outline, Concept Index & Keyword Breakdown (`plan.md`)

This document is the authoritative per-file blueprint for `python_how_to/`, aligned with [`.scratch/curriculum-alignment/spec.md`](../.scratch/curriculum-alignment/spec.md), [`GLOSSARY.md`](../GLOSSARY.md), [`ADR-0001`](../docs/adr/0001-single-folder-file-flag-and-labs.md), and [`ADR-0002`](../docs/adr/0002-conversational-prose-hash-comments-and-convenience-scaffold.md), and modeled on `CodingTemplateExamples/how_to/` and the approved Python pilots (`001_first.py`, `050_for_while_and_loop_else.py`). Every implementing agent **must** cover every listed defining concept, friction point, keyword/API breakdown, **Scaffold**, and graduated **Drill** sequence when authoring each standalone **Primer** (`NNN_topic.py`) or multi-file **Lab** (`NNN_topic_lab/`).

---

## 1. Global Rules, Pedagogical Style & Python Gotchas Checklist (Read Before Writing Any `.py` File)

1. **Target Python Version & Modern Idioms (Python 3.12+ / 3.13+ Standard Library Only)**:
   - Target modern **Python 3.12+** (with 3.13+ notes where relevant, such as free-threaded GIL status and `TypeIs`).
   - **Zero third-party PyPI dependencies**: Every **Primer** and **Lab** must run using only Python's standard library (`sys`, `os`, `pathlib`, `dataclasses`, `typing`, `collections`, `itertools`, `functools`, `contextlib`, `concurrent.futures`, `asyncio`, `sqlite3`, `tomllib`, `unittest`, `ctypes`, `ast`, `dis`, `tracemalloc`, `tkinter`, etc.).
   - **Modern Type Annotations**:
     - Use built-in generic types (`list[int]`, `dict[str, float]`, `tuple[int, ...]`, `set[str]`) — **never** legacy `typing.List`, `typing.Dict`, `typing.Tuple`, or `typing.Set`.
     - Use `X | Y` and `X | None` union syntax (PEP 604) — **never** legacy `typing.Union` or `typing.Optional` (except when briefly contrasting legacy code in `030`).
     - Use `collections.abc` (`Sequence`, `Mapping`, `Iterable`, `Iterator`, `Callable`) for parameter annotations rather than `typing.Sequence` / `typing.Callable`.
     - Teach PEP 695 `type Alias = ...`, `def func[T](...):`, and `class Box[T]:` syntax in the generics tier (`700`+).
2. **Core Python Mental Model & Anti-Hallucination Rules**:
   - **Names Are Labels Bound to Objects (Not Typed Memory Boxes)**:
     - Assigning `x = 42` or `b = a` never copies a value into a stack slot; it binds a name (reference) to a heap-allocated `PyObject` with a reference count, type pointer, and value.
     - Always distinguish **rebinding a name** (`x = x + 1` or `items = []`) from **mutating an object in place** (`items.append(1)` or `items[:] = []`).
   - **Identity (`is`) vs. Equality (`==`)**:
     - Use `is` and `is not` **only** for singletons (`None`, `True`, `False`, `Ellipsis`, `enum` members, or custom sentinel objects `MISSING = object()`) or when explicitly checking memory identity (`id(a) == id(b)`).
     - **Never** use `is` to compare integers or strings for value equality (explain CPython's `-5..256` small-int cache and string interning trap).
   - **High-Friction Python Gotchas Every Agent Must Emphasize Where Relevant**:
     - **Mutable default arguments** (`def f(items=[]):` evaluates `[]` *once* at `def` time, sharing one list across all calls).
     - **Late-binding loop closures** (`[lambda: i for i in range(5)]` captures the variable `i`, not its current value, so all functions return `4`).
     - **2D list multiplication aliasing** (`[[0] * 3] * 3` creates 3 references to the *same* inner list).
     - **Function-scoped variables (No block scope)** (`if`, `for`, `while`, `with`, and `try` blocks do **not** introduce a new lexical scope; loop variables and block variables leak into the enclosing function).
     - **Generator single-pass exhaustion** (iterating a generator or `map`/`filter`/`zip` iterator once drains it permanently; a second `for` loop sees zero items).
     - **`list.sort()` returns `None`** (mutates in place and returns `None` to prevent accidental aliasing confusion, vs. `sorted(iterable)` which allocates a new `list`).
     - **Truthiness traps with `0`, `0.0`, `""`, `[]`** (writing `if count:` instead of `if count is not None:` silently treats `0` as missing).
     - **Class attributes vs. instance attributes** (declaring a mutable list `items = []` on a `class` body without `@dataclass` shares that single list across every instance).
3. **File Structure, `#` Prose & `~5–20%` Soft Scaffold (`spec.md` & `ADR-0002`)**:
   - **Quiet line-1 run hint**: `# python NNN_name.py` (or `# python -m unittest -v 195_unit_testing_with_unittest.py` for `195`, `# python -m doctest -v 470_doctest_and_executable_documentation.py` for `470`, `# python NNN_lab_name/main.py` plus `--headless` where supported for **Lab** entry files).
   - **Multi-section structure with `main()` at the bottom**: Group multi-concept **Primers** into 3–4 focused topic functions called sequentially from `def main() -> None:` with clean section print banners (`=== 1. ... ===`), placing `def main() -> None:` and `if __name__ == "__main__": main()` at the **very bottom** of the file.
   - **1 blank line after `def ...:`**: Leave 1 empty line immediately after every `def <name>(...) -> ...:` header (or immediately after the 1-line `"""..."""` docstring in the scoped `__doc__` targets below).
   - **`#` comment prose everywhere (scoped `"""..."""` exceptions only)**: Write **all** explanatory prose in `#` comments so it renders cleanly without low-contrast string highlighting or runtime `__doc__` bloat. `"""..."""` string literals are strictly restricted to:
     1. Assigned/printed multi-line string values in `020_strings_unicode_and_bytes.py`.
     2. Target functions carrying `>>>` doctests in `470_doctest_and_executable_documentation.py`.
     3. Minimal 1-line `__doc__` inspection targets in `001_first.py`, `100_functions_and_return_semantics.py`, `140_decorators_and_functools_wraps.py`, and `420_dynamic_imports_and_importlib.py`.
   - **Voice, Feynman Rule & Hypothetical Scenarios**: Use `CodingTemplateExamples/how_to/` causal prose explaining *why* CPython or the machine behaves that way from first principles. Whenever introducing a new keyword, directive, operator, or stdlib construct, immediately explain what it means in plain conversational words (Feynman rule). Pair syntax illustrations with tiny concrete hypothetical before/body/after examples (never ambiguous `{ ... }` or `...` placeholders), and never split an inline code expression across a comment line wrap.
   - **Banned comment noise**: Zero `"Prompt"`, `"Step N (Prompt)"`, `"Worked anchor"`, `"Suggested task"`, `"Signature:"`, `"Syntax:"`, `"cue:"`, `"exercise:"`, ALL-CAPS headers (`CONCEPT:`, `FRICTION:`), `**bold**`, `*italics*`, single backticks `` ` ``, `reST` double-backticks `` `` ``, fenced code blocks ```` ``` ````, `---` or `===` comment underlines (`===` allowed only inside runtime `print` banner string literals in `main()`), `$...$` LaTeX, or `1. / 2.` numbered **Drill** checklists.
   - **~5–20% Soft Scaffold & Zero `pass`/Dummy Stubs**:
     - Pre-write only required `import` statements, topic section function definitions, `def main() -> None:` + `if __name__ == "__main__": main()`, and tiny real working starter **Scaffold** lines (1–4 lines printing or computing a baseline, plus convenience syntax illustrations where helpful).
     - **Never** emit `pass`, `yield`, `_ = x` silencers, or dummy `return 0` / `return ""` / `return {}` / `return []` stubs. Unimplemented helper functions, classes, and class methods live as `#` **Drills** specifying exact names, parameter types, and return types.
     - Graduate **Drills** smoothly in prose from explicit convenience hints (exact variable/function/class names and Python 3.12+ types) -> conversational recall -> open synthesis (including `# Try uncommenting:` error experiments).
   - **Primer Sizing, Lab Boundaries & Flag-Trivia Guardrails**:
     - **Core Primers**: Target `~150–300+` lines with `~8–15+` **Drills** (soft guideline).
     - **Narrow Primers** (`000`, `025`, `040`, `170`, `210`, `250`, `270`, `320`, `370`, `450`–`480`, `530`–`560`, `580`, `630`, `690`, `695`, `750`–`770`, `865`, `890`): Target `~85–140` lines with `~4–7` **Drills** (soft guideline).
     - **Multi-file Labs**: Judge by topical coverage and clean module boundaries; keep shared domain/ABI contracts and OS/setup boilerplate as **Scaffold**, convert domain logic, dispatch branches (`980/main.py`), and helpers into open **Drills**, and keep visibility **Labs** (`400`, `410`) minimal with 1–2 anchor constants/exports.
     - **Flag-Trivia & Scope-Creep Guardrails**: Focus on everyday fluency—skip `-I`/`-s`/`-E`/`-X`/`-OO`/`-v` and full `sys.flags` dissection (`000`), `!a`/locale `n`/`g`/`G` edge flags (`001`), `decimal.Context` trap tables/`sys.int_info` limb math (`010`), PEP 393 UCS-1/2/4 internals and `swapcase`/`expandtabs`/`zfill` (`020`), PEP-508 marker minutiae (`430`), `buffering=0/1` quirks (`610`), rare `struct` codes `P`/`e`/`n`/`p` (`630`), `re.LOCALE`/`re.DEBUG` (`640`), `argparse` `SUPPRESS`/`prefix_chars`/`conflict_handler` (`660`), `Popen` `close_fds`/`creationflags` (`695`), all 18 `sys.monitoring.events` masks (`760`), and `TCP_NODELAY`/`SO_LINGER` (`880`).
   - **Cross-Repo Boundaries (`python_how_to/` vs. `../tracy_how_to/`)**:
     - `python_how_to/` (`550`–`598`, `760`, `865`) owns Python stdlib profiling, VM internals, and FFI pointer mechanics (`timeit`, `cProfile`, `dis`, `PyLongObject`/`PyFloatObject` waste, `mmap`/`memoryview`, `array("d")` cache density, `ParticleSoAPool`, Amdahl Haversine, `sys.monitoring` `LINE` tracing, and `ctypes.from_buffer` 1D dot-product ABI).
     - Slim `565`, `568`, and Lab `598` to Python stdlib zone/lock/`tracemalloc` wrappers linking to `../tracy_how_to/`—do NOT duplicate `TracySourceLocationData` `ctypes` pinning (`tracy_how_to/150`), recursive zone / nested `Self Time` (`tracy_how_to/250`), Gen-0 GC churn (`tracy_how_to/350`), `asyncio` blocking freezes (`tracy_how_to/450`), Chrome `"ph": "C"` / `"ph": "i"` flight-recorder schemas (`tracy_how_to/550`), `sys.monitoring` callback distortion (`tracy_how_to/700`), hybrid FFI timelines (`tracy_how_to/800`), or 5-system Hotspot Hunt capstones (`tracy_how_to/950`).
   - **No `solutions/` Directory & Verification Gate (`Write-First, Verify-Once`)**:
     - Keep zero `solutions/` folders and zero `.ps1` test harnesses or manifest JSONs (`tests/` is retired).
     - Every unfilled **Primer** and **Lab** must pass `python -B` `ast.parse` with zero `SyntaxError`/`IndentationError` (and zero `__pycache__` writes) and exit `0` when executed cleanly.

---

## 2. Tier Overview (`000`–`999`)

| Range | Tier Focus | Count |
| :--- | :--- | :--- |
| **`000`–`099`** | **Toolchain, Object Model, Name Binding, Core Types & Control Flow** | 18 Primers |
| **`100`–`199`** | **Functions, Signatures, Closures, Decorators, Generators & Testing** | 12 Primers |
| **`200`–`299`** | **Built-in Collections, Mutability, Aliasing, Hashing & Comprehensions** | 16 Primers |
| **`300`–`399`** | **Object-Oriented Python, Data Model (Dunders), Descriptors & Metaclasses** | 12 Primers |
| **`400`–`499`** | **Modules, Packages, Imports, Packaging & Project Architecture** | 7 Primers, 2 Labs |
| **`500`–`599`** | **Memory Management, Refcounting, GC, Profiling, Bytecode & Performance** | 15 **Primers**, 2 **Labs** |
| **`600`–`699`** | **Standard Library Essentials: Files, Serialization, Regex, SQLite & CLI** | 11 Primers |
| **`700`–`799`** | **Advanced Type System, Generics (PEP 695), AST, Inspection & Hooks** | 8 Primers |
| **`800`–`899`** | **Concurrency (`threading`, `multiprocessing`, `asyncio`) & C Interop (`ctypes`)** | 9 Primers, 2 Labs |
| **`900`–`999`** | **Complete Programs & Multi-File Training Capstones** | 4 Primers, 4 Labs |

**Total Curriculum**: **112 Single-File Primers + 10 Multi-File Labs (122 numbered entries)**

---

## 3. Master Concept Index of All `xxx_yyy.py` Primers & `xxx_yyy_lab/` Subfolders

Before the per-file keyword breakdowns in Section 4, here is the complete high-level concept and friction map for all 122 curriculum units:

### Tier `000`–`099`: Toolchain, Object Model, Name Binding, Core Types & Control Flow
1. **`000_running_and_inspecting_python.py`** *(Primer)* — Python CLI execution modes (`python file.py`, `-m`, `-c`, `-i`, `-O`, `-B`), `__name__ == "__main__"`, `sys.version_info`, and `.pyc` bytecode caching.
2. **`001_first.py`** *(Primer)* — `print()` mechanics (`sep`, `end`, `flush`), comments vs. runtime `__doc__` docstrings, and modern f-strings (`f"{expr=}"`, format specifiers, `!r`/`!s`).
3. **`005_names_objects_and_binding.py`** *(Primer)* — Names as labels bound to heap `PyObject`s (not memory boxes), `id()`, `is` vs. `==`, `None`, `del`, and CPython's small-integer caching friction.
4. **`010_numbers_arbitrary_precision_and_math.py`** *(Primer)* — Arbitrary-precision `int`, IEEE-754 `float` representation error (`0.1 + 0.2 != 0.3`), `math.isclose`, `Decimal`, `Fraction`, and `complex`.
5. **`015_booleans_truthiness_and_short_circuit.py`** *(Primer)* — `bool` as an `int` subclass (`True == 1`), container truthiness, short-circuit value-returning `and`/`or` vs. the falsy-zero trap (`x or default` when `x = 0`), and chained comparisons.
6. **`020_strings_unicode_and_bytes.py`** *(Primer)* — Immutable Unicode code-point `str` vs. raw `bytes` (`b"..."`) vs. mutable `bytearray`, UTF-8 `.encode()`/`.decode()`, and indexing differences (`str[0]` -> `str`, `bytes[0]` -> `int`).
7. **`025_operators_floor_div_and_walrus.py`** *(Primer)* — True division `/` vs. floor division `//` (rounding toward -infinity), floored modulo `%`, `divmod()`, bitwise operators, and assignment expressions (`:=` walrus operator).
8. **`030_type_annotations_and_static_checking.py`** *(Primer)* — Modern type hints (`int | None`, `list[str]`, `Final`, `Literal`), runtime non-enforcement friction, `__annotations__`, and `isinstance()` type narrowing.
9. **`035_scopes_legb_and_closures_preview.py`** *(Primer)* — LEGB lookup rule, why `if`/`for`/`with` blocks do NOT create a new scope (variable leaking), `UnboundLocalError` friction, `global`, and `nonlocal`.
10. **`040_if_elif_else_and_conditional_expr.py`** *(Primer)* — `if / elif / else`, `pass` vs. `...` (`Ellipsis`), inline conditional expressions (`a if cond else b`), and explicit `is not None` guards.
11. **`045_structural_pattern_matching.py`** *(Primer)* — `match / case` structural pattern matching: sequence/mapping/class unpacking, guards, OR patterns, and the bare-identifier capture vs. dotted-constant trap.
12. **`050_for_while_and_loop_else.py`** *(Primer)* — Iterator-driven `for`, `range()`, `while`, `break`, `continue`, and the `for ... else:` clause (runs only when the loop completes without `break`).
13. **`055_iteration_helpers_enumerate_zip_reversed.py`** *(Primer)* — `enumerate()`, `zip(..., strict=True)` (preventing silent truncation on mismatched lengths), `reversed()`, `sorted()`, `any()`, and `all()`.
14. **`060_unpacking_and_starred_expressions.py`** *(Primer)* — Sequence unpacking, starred catch-all targets (`first, *mid, last = seq`), nested unpacking, and `*` / `**` splatting inside collection literals.
15. **`065_exceptions_try_except_else_finally.py`** *(Primer)* — `try / except / else / finally`, exception hierarchy (`BaseException` vs. `Exception` — why bare `except:` is a bug), and `finally` return-override pitfalls.
16. **`070_raising_chaining_and_exception_groups.py`** *(Primer)* — Custom exceptions, explicit exception chaining (`raise ... from err` vs. `from None`), `add_note()`, and `ExceptionGroup` / `except*`.
17. **`075_with_context_managers_basics.py`** *(Primer)* — Deterministic `with` block resource management vs. non-deterministic GC, multi-resource `with`, and `contextlib.suppress` / `nullcontext`.
18. **`080_assertions_warnings_and_introspection.py`** *(Primer)* — `assert` (and why `-O` strips assertions in production), `warnings.warn`, and runtime object introspection (`dir`, `vars`, `getattr`, `hasattr`, `callable`).

### Tier `100`–`199`: Functions, Signatures, Closures, Decorators, Generators & Testing
19. **`100_functions_and_return_semantics.py`** *(Primer)* — `def`, implicit `return None`, tuple return unpacking, first-class function attributes, and pass-by-object-reference (mutating vs. rebinding parameters).
20. **`110_positional_keyword_and_default_args.py`** *(Primer)* — Positional and keyword arguments, and the **Mutable Default Argument trap** (`def f(x, buf=[]):` sharing state across calls via `__defaults__`).
21. **`120_varargs_kwargs_and_signature_markers.py`** *(Primer)* — `*args`, `**kwargs`, call-site unpacking, positional-only `/` parameters, and keyword-only `*` parameters for clean API design.
22. **`130_lambda_and_late_binding_closures.py`** *(Primer)* — `lambda`, enclosing cell variables (`__closure__`), and the **Late-Binding Loop Closure trap** (`[lambda: i for i in range(5)]` returning `[4, 4, 4, 4, 4]`).
23. **`140_decorators_and_functools_wraps.py`** *(Primer)* — Higher-order function wrappers, `@decorator` syntax, why `@functools.wraps` is mandatory to preserve metadata and `__wrapped__`, and decorator stacking order.
24. **`150_parameterized_and_class_decorators.py`** *(Primer)* — 3-level decorator factories (`@retry(times=3)`), optional-arg decorators (`@trace` or `@trace(level="INFO")`), callable class decorators, and class decorators.
25. **`160_functools_lru_cache_partial_and_singledispatch.py`** *(Primer)* — Memoization with `@cache` and `@lru_cache` (hashable argument constraint), `partial` application, `reduce`, and `@singledispatch` type-based overloading.
26. **`170_operator_module_and_key_functions.py`** *(Primer)* — Fast C-backed `itemgetter`, `attrgetter`, `methodcaller`, operator functions, and `cmp_to_key` for legacy comparison functions.
27. **`180_generators_and_yield.py`** *(Primer)* — Lazy generator functions (`yield`), `next()` / `StopIteration`, `yield from` delegation, `.send()` / `.close()`, and single-pass iterator exhaustion friction.
28. **`185_custom_context_managers_contextlib.py`** *(Primer)* — Writing `__enter__` / `__exit__` classes (exception suppression semantics) vs. `@contextlib.contextmanager` generators and dynamic `ExitStack`.
29. **`190_callable_types_and_callbacks.py`** *(Primer)* — Typing callbacks with `Callable[[...], R]`, callback `Protocol`s for keyword/variadic signatures, and `@typing.overload` for input-dependent return types.
30. **`195_unit_testing_with_unittest.py`** *(Primer)* — Built-in `unittest.TestCase`, assertions, `assertRaises`, `subTest()` parameterized loops, and `unittest.mock.patch` / `MagicMock`.

### Tier `200`–`299`: Built-in Collections, Mutability, Aliasing, Hashing & Comprehensions
31. **`200_lists_dynamic_arrays_and_aliasing.py`** *(Primer)* — `list` over-allocation growth (O(1) append vs. O(N) front insert/pop), reference aliasing, and the **2D list multiplication trap** (`[[0]*3]*3`).
32. **`205_slicing_slice_assignment_and_stride.py`** *(Primer)* — Slice syntax `a[start:stop:step]`, `slice` objects, why `list` slicing allocates a shallow copy (not a view), and in-place slice assignment `a[:] = ...`.
33. **`210_shallow_vs_deep_copy.py`** *(Primer)* — Shallow copies (`list.copy()`, `dict.copy()`, `copy.copy()`) sharing nested mutable children vs. recursive `copy.deepcopy()` with cycle memoization.
34. **`215_tuples_immutability_and_namedtuple.py`** *(Primer)* — `tuple` records, 1-tuple trailing comma `(x,)`, mutating a `list` inside an "immutable" `tuple` (`t[1] += [4]` raises `TypeError` *and* still mutates!), and `typing.NamedTuple`.
35. **`220_dicts_insertion_order_and_views.py`** *(Primer)* — Hash table mechanics, insertion order guarantee, `.get()`, `.setdefault()`, `|` and `|=` merge operators, live set-like dict views, and `RuntimeError` on resize during iteration.
36. **`225_sets_and_frozensets.py`** *(Primer)* — `set` vs. hashable `frozenset`, why `{}` is a `dict`, O(1) membership lookups, set algebra (`|`, `&`, `-`, `^`, `<=`), and order-preserving deduplication.
37. **`230_hashability_and_equality_contracts.py`** *(Primer)* — `hash()`, `__hash__` and `__eq__` invariant (`a == b => hash(a) == hash(b)`), why mutable objects are unhashable, and key corruption if a custom key is mutated in place.
38. **`235_comprehensions_and_generator_expressions.py`** *(Primer)* — List, dict, and set comprehensions, multi-clause ordering, filtering + transforming in one pass with `:=`, and zero-allocation generator expressions.
39. **`240_collections_defaultdict_counter_chainmap.py`** *(Primer)* — `defaultdict` (`__missing__` factory), `Counter` (top-N frequencies and multiset math), and `ChainMap` (multi-layer dictionary views).
40. **`245_collections_deque_and_bisect.py`** *(Primer)* — Double-ended `deque` (O(1) ends and bounded `maxlen` ring buffers) and sorted-sequence binary search with `bisect_left` / `insort`.
41. **`250_heapq_and_priority_queues.py`** *(Primer)* — In-place min-heap operations (`heapify`, `heappush`, `heappop`, `nlargest`), max-heap negation, and `(priority, tie_breaker, task)` tuples to avoid comparison crashes.
42. **`255_enum_intenum_and_flag.py`** *(Primer)* — `Enum`, `IntEnum`, `StrEnum`, `Flag` / `IntFlag` bitwise combinations, `auto()`, `@unique`, and identity matching.
43. **`260_itertools_combinatorics_and_streams.py`** *(Primer)* — Lazy stream pipelines (`islice`, `chain`, `batched`, `pairwise`, `accumulate`), `groupby` (pre-sorting requirement!), and combinatorics (`product`, `permutations`, `combinations`).
44. **`265_array_bytearray_and_memoryview.py`** *(Primer)* — Unboxed C-typed `array.array`, `bytearray`, and zero-copy slicing / type reinterpretation with `memoryview` (`.cast()`).
45. **`270_sorting_timsort_and_stability.py`** *(Primer)* — In-place `.sort()` vs. `sorted()`, Timsort stability for multi-pass sorts, multi-key tuple keys, and handling mixed/nullable sort keys.
46. **`280_mutation_during_iteration_and_defensive_copies.py`** *(Primer)* — The silent index-skipping bug when calling `list.remove()` inside `for x in items:`, and safe filtering/in-place compaction idioms.

### Tier `300`–`399`: Object-Oriented Python, Data Model (Dunders), Descriptors & Metaclasses
47. **`300_classes_instances_and_attributes.py`** *(Primer)* — `class`, `__init__` vs. `__new__`, `self`, `instance.__dict__` -> `cls.__dict__` lookup, and the **Mutable Class Attribute trap**.
48. **`310_properties_getters_and_computed_attrs.py`** *(Primer)* — `@property` getter/setter/deleter (Pythonic attribute access without `get_`/`set_` boilerplate) and `@functools.cached_property`.
49. **`320_classmethods_staticmethods_and_constructors.py`** *(Primer)* — `@classmethod` factory methods (`from_dict`, `from_json` that instantiate `cls` for subclass safety) vs. `@staticmethod`.
50. **`330_inheritance_super_and_mro.py`** *(Primer)* — Inheritance, `isinstance`/`issubclass`, C3 linearization Method Resolution Order (`__mro__`), cooperative `super()`, and Mixins.
51. **`340_dunder_repr_format_and_comparisons.py`** *(Primer)* — `__repr__` vs. `__str__`, custom f-string `__format__`, `__eq__` returning `NotImplemented`, and `@functools.total_ordering`.
52. **`350_dunder_arithmetic_and_containers.py`** *(Primer)* — Operator overloading (`__add__`, `__radd__`, `__iadd__`), sequence/mapping protocols (`__len__`, `__getitem__`, `__contains__`, `__iter__`), and `__call__`.
53. **`360_dataclasses_slots_and_frozen.py`** *(Primer)* — `@dataclass(slots=True, frozen=True, kw_only=True)`, `field(default_factory=...)`, `__post_init__`, and `dataclasses.replace`.
54. **`370_slots_and_object_memory_layout.py`** *(Primer)* — `__slots__`: eliminating per-instance `__dict__` overhead, preventing accidental attribute typos, and slot inheritance rules.
55. **`380_abstract_base_classes_and_protocols.py`** *(Primer)* — Nominal interfaces (`abc.ABC`, `@abstractmethod`) vs. structural duck-typed interfaces (`typing.Protocol`, `@runtime_checkable`).
56. **`385_descriptor_protocol_deep_dive.py`** *(Primer)* — Reusable attribute validators via the Descriptor Protocol (`__set_name__`, `__get__`, `__set__`) and data vs. non-data descriptor lookup priority.
57. **`390_getattr_getattribute_and_proxies.py`** *(Primer)* — Fallback `__getattr__` vs. universal `__getattribute__` (and avoiding infinite `RecursionError` via `super().__getattribute__`), `__setattr__`, and proxy objects.
58. **`395_init_subclass_and_metaclasses.py`** *(Primer)* — Subclass registration and validation with `__init_subclass__` vs. custom metaclasses (`class Meta(type):`, `__new__`, `__prepare__`).

### Tier `400`–`499`: Modules, Packages, Imports, Packaging & Project Architecture
59. **`400_modules_import_system_and_sys_path/`** *(Multi-File Lab)* — Package directory structure (`__init__.py`, sibling modules, subpackages), absolute vs. relative imports, `sys.modules` singleton cache, and running with `python -m`.
60. **`410_visibility_all_and_circular_imports/`** *(Multi-File Lab)* — `_private` conventions, `__mangled` attributes, `__all__`, and diagnosing + breaking **Circular Imports** using `TYPE_CHECKING` and architectural inversion.
61. **`420_dynamic_imports_and_importlib.py`** *(Primer)* — `importlib.import_module`, loading modules from arbitrary file paths, and inspecting package metadata (`importlib.metadata` & `importlib.resources`).
62. **`430_pyproject_toml_and_venv_packaging.py`** *(Primer)* — Modern `pyproject.toml` (PEP 621), virtual environment isolation (`sys.prefix` vs. `sys.base_prefix`), `src/` layout, and console script entry points.
63. **`440_config_env_vars_and_dotenv_patterns.py`** *(Primer)* — `os.environ`, zero-dependency `.env` parsing, `tomllib` config loading, and immutable typed configuration objects.
64. **`450_warnings_deprecation_and_future_flags.py`** *(Primer)* — `from __future__ import annotations`, `warnings.warn` with `stacklevel=2`, `catch_warnings()`, and `@warnings.deprecated`.
65. **`460_code_quality_typecheck_and_linter_hygiene.py`** *(Primer)* — Exhaustiveness checking with `typing.assert_never`, `assert_type`, `ast.parse`/`py_compile`, and idiomatic patterns for clean `mypy`/`pyright`/`ruff` passes.
66. **`470_doctest_and_executable_documentation.py`** *(Primer)* — Writing self-testing `>>>` docstring examples and running `doctest.testmod()` programmatically.
67. **`480_zipapp_and_single_file_bundles.py`** *(Primer)* — Bundling multi-module Python packages into a single executable `.pyz` archive with `zipapp.create_archive()`.

### Tier `500`–`599`: Memory Management, Refcounting, GC, Profiling, Bytecode & Performance
68. **`500_refcounting_and_garbage_collection.py`** *(Primer)* — CPython reference counting (`sys.getrefcount`) vs. cyclic `gc` (`gc.collect`, reference cycle creation and collection).
69. **`510_weakref_and_caches_without_leaks.py`** *(Primer)* — Non-owning references (`weakref.ref`, `WeakValueDictionary`, `WeakKeyDictionary`, `weakref.finalize`) to cache objects and break parent-child cycles without memory leaks.
70. **`520_tracemalloc_and_memory_leak_hunting.py`** *(Primer)* — Tracking heap allocations by file and line number with `tracemalloc` (`start`, `take_snapshot`, `compare_to`, `get_traced_memory`).
71. **`530_string_and_bytes_concatenation_perf.py`** *(Primer)* — Why repeated concatenation can cause quadratic copying vs. `"".join()`, `b"".join()`, `io.StringIO`, and `io.BytesIO`.
72. **`540_object_interning_and_flyweight_pools.py`** *(Primer)* — `sys.intern()` for deduplicating repeated strings and O(1) pointer comparison, plus interned flyweight instances.
73. **`550_timing_and_benchmarking_timeit.py`** *(Primer)* — Monotonic nanosecond timing (`time.perf_counter_ns`, `time.monotonic`, `time.process_time`) and statistically sound microbenchmarks with `timeit`.
74. **`560_profiling_with_cprofile_and_pstats.py`** *(Primer)* — Deterministic call-graph profiling with `cProfile.Profile` and programmatic bottleneck analysis with `pstats.Stats`.
75. **`565_profiling_with_tracy_zones_and_frames.py`** *(Primer — Slimmed Wrapper Linking to `../tracy_how_to/`)* — Lightweight Python stdlib zone/frame/plot timing wrapper (`time.perf_counter_ns()` + optional `ctypes` hook), linking to `tracy_how_to/` (`150`, `250`, `550`) for `TracySourceLocationData` pinning, recursive zones, and Chrome flight-recorder schemas.
76. **`568_tracy_memory_and_gil_thread_profiling.py`** *(Primer — Slimmed Wrapper Linking to `../tracy_how_to/`)* — Lightweight stdlib `tracemalloc` zone delta & `threading.Lock` wait/hold wrapper, linking to `tracy_how_to/` (`350`, `450`) for Gen-0 GC churn forensics and `asyncio` GIL timeline freezes.
77. **`570_bytecode_disassembly_with_dis.py`** *(Primer)* — Inspecting CPython stack-machine bytecode (`dis.dis`, `dis.Bytecode`, `fn.__code__`), local vs. global lookup speeds (`LOAD_FAST` vs. `LOAD_GLOBAL`), and 3.11+ adaptive instructions.
78. **`575_interpreter_waste_and_bytecode_cost.py`** *(Primer — Computer, Enhance! Multiplier #1: Waste)* — Why `a += b` in Python is NOT one CPU `ADD` instruction (tracing the CPython eval loop, `PyObject` boxing, type slot dispatch, and refcount traffic) and how to eliminate interpreter loop waste on profiled hotspots.
79. **`580_buffer_protocol_and_mmap.py`** *(Primer)* — OS virtual-memory file mapping with `mmap.mmap` and zero-copy `memoryview` manipulation.
80. **`585_cache_locality_ipc_and_simd_in_python.py`** *(Primer — Computer, Enhance! Multipliers #2, #3, #4)* — Pointer-chasing cache misses in `list[float]` vs. 64-byte cache-line packing in `array.array('d')`/`memoryview`, why pure-Python loops stall CPU IPC and SIMD, and delegating inner loops to C-backed vectorized builtins.
81. **`590_arena_and_object_pool_patterns.py`** *(Primer)* — Object pooling and flat Structure-of-Arrays (`array('f')`) tables in Python to eliminate per-item `PyObject` allocation overhead.
82. **`592_hotspot_optimization_workflow.py`** *(Primer — Computer, Enhance! Part 2)* — The pragmatic **Profile First -> Isolate Hotspot -> Diagnose Multiplier -> Optimize Only the 5% Hotspot** workflow (referencing **Tracy** `tracy_how_to/` and `cProfile`).
83. **`595_memory_profiled_pipeline_lab/`** *(Multi-File Lab)* — Multi-file **Lab** (`main.py`, `pool.py`, `processor.py`) using `tracemalloc`, `__slots__`, and `WeakValueDictionary` to process records with bounded peak memory and zero leaks.
84. **`598_tracy_hotspot_profiler_lab/`** *(Multi-File Lab — Slimmed Stdlib Profiler Linking to `../tracy_how_to/950_python_hotspot_hunt_five_multipliers_lab/`)* — Multi-file stdlib zone & `tracemalloc` pipeline **Lab** (`main.py`, `tracy_prof.py`, `workload.py`) isolating a single transform hotspot; links to `tracy_how_to/950` for full 5-system cold-herring Hotspot Hunt capstones.

### Tier `600`–`699`: Standard Library Essentials: Files, Serialization, Regex, SQLite & CLI
85. **`600_pathlib_and_filesystem_ops.py`** *(Primer)* — Object-oriented paths with `pathlib.Path`, atomic file replacement (`replace`), globbing, and `tempfile.TemporaryDirectory`.
86. **`610_io_streams_buffering_and_encodings.py`** *(Primer)* — Explicit `encoding="utf-8"` discipline, `io.StringIO`/`BytesIO`, and zero-allocation binary reads with `readinto(bytearray)`.
87. **`620_json_csv_and_tomllib.py`** *(Primer)* — Custom `json` encoders/hooks for dataclasses, `csv.DictReader`/`DictWriter` (`newline=""`), and `tomllib`.
88. **`630_binary_packing_with_struct.py`** *(Primer)* — Packing and unpacking C binary wire headers with `struct.Struct` (`<`, `>`, `!` endianness) and `int.to_bytes`/`from_bytes`.
89. **`640_regular_expressions_re.py`** *(Primer)* — Compiled regexes, named groups `(?P<name>...)`, non-greedy quantifiers, callback `re.sub`, and `re.VERBOSE`.
90. **`650_datetime_timezones_and_zoneinfo.py`** *(Primer)* — Timezone-aware UTC datetimes (`datetime.now(timezone.utc)`), `zoneinfo.ZoneInfo`, `timedelta`, and ISO-8601 parsing.
91. **`660_cli_parsing_with_argparse.py`** *(Primer)* — `argparse` flags, types, choices, mutually exclusive flags, and Git-style subcommands (`add_subparsers`).
92. **`670_structured_logging_and_handlers.py`** *(Primer)* — Hierarchical loggers, handlers, formatters, custom context filters, and exception traceback logging.
93. **`680_sqlite3_embedded_database.py`** *(Primer)* — In-memory and file-backed `sqlite3`, transactional `with conn:` blocks, parameterized SQL queries, and `sqlite3.Row`.
94. **`690_hashlib_hmac_and_secrets.py`** *(Primer)* — Streaming SHA-256 / BLAKE2b digests, constant-time `hmac.compare_digest`, and CSPRNG token generation with `secrets`.
95. **`695_subprocess_and_os_processes.py`** *(Primer)* — Safe child process execution with `subprocess.run` (argument lists without `shell=True`), timeouts, pipes, and exit-code handling.

### Tier `700`–`799`: Advanced Type System, Generics (PEP 695), AST, Inspection & Hooks
96. **`700_modern_generics_and_type_params.py`** *(Primer)* — PEP 695 generic functions `def f[T](...):`, generic classes `class Stack[T]:`, generic `type` aliases, and type bounds.
97. **`710_variance_paramspec_and_typevartuple.py`** *(Primer)* — Invariance vs. covariance (`list[T]` vs. `Sequence[T]`), `ParamSpec` (`**P`) for signature-preserving decorators, and `TypeVarTuple` (`*Ts`).
98. **`720_typeddict_literal_newtype_and_typeguard.py`** *(Primer)* — `TypedDict` (`NotRequired`, `ReadOnly`), `NewType` nominal wrappers, `Literal`, and `TypeIs` / `TypeGuard` narrowing functions.
99. **`730_runtime_inspection_and_signatures.py`** *(Primer)* — `inspect.signature`, `sig.bind`, and reading `typing.Annotated` metadata via `get_type_hints(..., include_extras=True)` for runtime validation.
100. **`740_ast_parsing_walking_and_transforming.py`** *(Primer)* — Parsing source into ASTs (`ast.parse`), `NodeVisitor` static checks, `NodeTransformer` code rewriting, `ast.unparse`, and `compile()`.
101. **`750_dynamic_code_exec_and_safe_literal_eval.py`** *(Primer)* — Why `eval()` is unsafe, parsing untrusted data with `ast.literal_eval()`, and writing a safe AST-based math expression evaluator.
102. **`760_sys_monitoring_and_trace_hooks.py`** *(Primer)* — Tracing execution events with `sys.monitoring` (`LINE`, `PY_START`, `PY_RETURN`, `DISABLE`) and inspecting structured tracebacks with `traceback.extract_tb` (linking to `../tracy_how_to/700_python_tracy_zones_and_sys_monitoring.py` for callback distortion & `PY_UNWIND`).
103. **`770_import_hooks_and_custom_loaders.py`** *(Primer)* — Customizing `sys.meta_path` with `importlib.abc.MetaPathFinder` and `Loader` to synthesize or instrument modules on import.

### Tier `800`–`899`: Concurrency (`threading`, `multiprocessing`, `asyncio`) & C Interop (`ctypes`)
104. **`800_threads_gil_and_synchronization.py`** *(Primer)* — OS threads (`threading.Thread`), GIL vs. free-threading (`sys._is_gil_enabled`), `Lock`, `RLock`, `Event`, `Condition`, `Barrier`, and `threading.local`.
105. **`810_thread_safe_queues_and_worker_pools.py`** *(Primer)* — Producer-consumer synchronization with `queue.Queue` and concurrent I/O fan-out with `ThreadPoolExecutor` (`submit`, `as_completed`).
106. **`820_multiprocessing_and_shared_memory.py`** *(Primer)* — Multi-core CPU parallelism with `ProcessPoolExecutor` and zero-copy cross-process buffers with `multiprocessing.shared_memory.SharedMemory`.
107. **`830_asyncio_coroutines_and_event_loop.py`** *(Primer)* — Single-threaded event loop mechanics (`async def`, `await`, `create_task`, `gather`), non-blocking sleep, and `asyncio.to_thread`.
108. **`840_asyncio_taskgroups_queues_and_timeouts.py`** *(Primer)* — Structured concurrency with `asyncio.TaskGroup`, `asyncio.timeout`, `asyncio.Queue`, `asyncio.Semaphore`, and `async for` / `async with`.
109. **`850_concurrent_pipeline_lab/`** *(Multi-File Lab)* — Multi-stage bounded async/threaded work pipeline (`main.py`, `pipeline.py`) with backpressure, retries, and clean cancellation.
110. **`860_ctypes_foreign_c_interop.py`** *(Primer)* — Calling native C functions (`ctypes.CDLL`, `c_int`, `c_double`, `Structure`, `byref`, `argtypes`/`restype` safety) and passing Python callbacks via `CFUNCTYPE`.
111. **`865_ctypes_simd_hotspot_offload.py`** *(Primer — Computer, Enhance! "Python Revisited")* — Passing zero-copy contiguous `array.array('f')` buffers across `ctypes.from_buffer` over a 1D dot-product ABI with pure-Python fallback (linking to `../tracy_how_to/800_hybrid_python_odin_tracy_offload_lab/` for multi-layer FFI timeline tracing & crossover forensics).
112. **`870_native_plugin_hot_reload_lab/`** *(Multi-File Lab)* — Live plugin hot-reloading engine (`host.py`, `shared_state.py`, `plugins/rules_plugin.py`) that detects file changes, reloads logic dynamically via `importlib`, preserves state, and survives broken plugin edits.
113. **`880_sockets_and_selectors_nonblocking_io.py`** *(Primer)* — Raw non-blocking loopback TCP sockets, partial `sock.send()` backpressure handling, and event-driven readiness multiplexing with `selectors.DefaultSelector`.
114. **`890_signals_atexit_and_graceful_shutdown.py`** *(Primer)* — Registering `atexit` hooks and handling `SIGINT`/`SIGTERM` signals for deterministic shutdown cleanup.

### Tier `900`–`999`: Complete Programs & Multi-File Training Capstones
115. **`900_binary_hex_dumper.py`** *(Primer)* — CLI hex + ASCII file inspector using `pathlib` and zero-copy 16-byte `memoryview` slices.
116. **`910_custom_open_addressing_hash_table.py`** *(Primer)* — Generic `HashTable[K, V]` implementing linear probing, tombstones, load-factor resizing, and the `MutableMapping` dunder protocol.
117. **`920_sqlite_and_json_task_tracker_cli.py`** *(Primer)* — End-to-end CLI task manager combining `argparse`, `@dataclass(slots=True)`, `sqlite3` transactions, and JSON import/export.
118. **`930_async_tcp_command_server.py`** *(Primer)* — Self-testing loopback `asyncio` TCP command server and client handling `PING`, `ADD`, `STATS`, and `QUIT`.
119. **`940_log_search_and_word_freq_lab/`** *(Multi-File Lab)* — Multi-file directory log search & word-frequency analyzer (`main.py`, `indexer.py`, `report.py`).
120. **`950_ecs_entity_simulation_lab/`** *(Multi-File Lab)* — Data-oriented Entity-Component-System simulation (`main.py`, `world.py`, `systems.py`) using generational handles, `IntFlag` masks, and `array('f')` SoA storage.
121. **`960_bytecode_vm_and_compiler_lab/`** *(Multi-File Lab)* — Stack/register bytecode virtual machine & text assembler (`main.py`, `isa.py`, `assembler.py`, `vm.py`).
122. **`980_arcade_simulation_and_tk_lab/`** *(Multi-File Lab)* — 60-FPS 2D Space Invaders arcade game (`main.py`, `game.py`, `renderer.py`) using stdlib `tkinter.Canvas` with a `--headless` 10-frame automated verification mode.

---

## 4. Exhaustive Per-File Training Outline, Keywords & Concept Breakdown (`000`–`999`)

## `000`–`099`: Toolchain, Object Model, Name Binding, Core Types & Control Flow

### `000_running_and_inspecting_python.py` *(Narrow Primer — ~100–140 lines, 6–8 Drills; reset user edits)*
- **Defining Concept & Friction Point**: Understanding how the Python interpreter compiles source to bytecode and executes scripts versus modules (`python file.py` vs. `python -m module`), and why top-level code executes immediately on import unless guarded by `if __name__ == "__main__":`. *(Reset partial user-edited solution lines in `000` back to a clean unfilled Scaffold.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `if __name__ == "__main__":` — Runtime check that is `True` only when the file is executed directly as the entry-point script, and equals the module's import name when imported by another file.
  - `sys.version_info` — Named tuple `(major, minor, micro, releaselevel, serial)` used to check Python version programmatically (`sys.version_info >= (3, 12)`).
  - `sys.platform` & `sys.executable` — Identifies the host OS (`"win32"`, `"linux"`, `"darwin"`) and the exact path of the running `python` binary.
  - `sys.flags.optimize` — Inspects active optimization flag (`0`, `1` under `-O`).
  - `py_compile.compile(file, doraise=True)` — Compiles a `.py` source file to bytecode (`.pyc` inside `__pycache__/`) to verify syntax without executing top-level code.
  - Everyday CLI Flags (`-m`, `-c`, `-i`, `-O`, `-B`, `-W error`) — `-m` runs a library module as a script; `-c` executes a command string; `-i` drops into the interactive REPL after running; `-O` strips `assert` statements and sets `__debug__ = False`; `-B` suppresses writing `__pycache__/*.pyc` files; `-W error` escalates warnings. *(Guardrail: skip `-I`, `-s`, `-E`, `-X`, `-OO`, `-v` and full `sys.flags` dissection.)*
- **Scaffold**: `#` prose comments, `import py_compile`, `import sys`, and a tiny starter `print(sys.version.split()[0])` line (leave `def main() -> None:` and the `if __name__ == "__main__":` guard to be written by the learner as their first entry point).
- **Ordered Outline**:
  1. Explain in `#` comments how CPython first compiles `.py` source into bytecode instructions (cached in `__pycache__/*.pyc`) and then runs them on the CPython virtual machine, plus how `python -B` `ast.parse` / `python -m py_compile` checks syntax across all files in `python_how_to/`.
  2. Explain why every runnable Python file should put its execution logic inside `def main() -> None:` at the bottom guarded by `if __name__ == "__main__":`.
  3. **Drill 1**: Define `def main() -> None:` (leaving 1 blank line after `def main() -> None:`) and print `__name__`, `sys.version_info[:3]`, `sys.platform`, `sys.executable`, `sys.flags.optimize`, and `__debug__`.
  4. **Drill 2**: Inside `main()`, call `py_compile.compile(__file__, doraise=True)` and print the resulting `.pyc` path (plus a brief `python -c` / `-m` check).
  5. **Drill 3**: Add the `if __name__ == "__main__": main()` guard at the bottom of the file, and re-run with `python -O 000_running_and_inspecting_python.py` and `python -B` to observe `__debug__` flip from `True` to `False`.

### `001_first.py` *(Approved Pilot Primer — Core, 158 lines)*
- **Defining Concept & Friction Point**: Mastering `print()` formatting, f-string debugging (`f"{expr=}"`), and distinguishing `#` comments (stripped by the lexer) from `"""..."""` docstrings (retained at runtime as `__doc__`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `#` line comment — Ignored completely by the parser; Python has no `/* ... */` block comment syntax.
  - `"""..."""` docstring & `__doc__` — Scoped exception: minimal 1-line module `__doc__`, `main.__doc__`, and a local `greet.__doc__` inspection target; anywhere else, bare `"""..."""` is a useless runtime string constant.
  - `print(*objects, sep=" ", end="\n", file=sys.stdout, flush=False)` — Built-in output function supporting mixed types (`str`, `int`, `float`, `bool`, `None`, containers), `file=sys.stderr`, and `flush=True`.
  - `f"..."` formatted string literals (f-strings) & PEP 701 (Python 3.12+) nested quote reuse (`f"HP: {stats["hp"]}"`).
  - `f"{expr=}"` self-documenting debug specifier & `!s` / `!r` conversion flags.
  - Format specifiers (`:.2f`, `:.1%`, `:,`, `:<12`, `:>8.2f`, `:^10`) and the retained clean `#` hex formatting guide (`:x`, `:X`, `:#x`, `:08x`, `:_x`, plus `>`/`<`/`^`/`=`/`*>` alignment). *(Guardrail: skip `!a`, locale `n`, and `g`/`G` edge flags.)*
- **Scaffold**: Approved 3-section layout (`console_printing`, `fstrings_and_hex_formatting`, `debug_fstrings_and_docstrings`, bottom `def main() -> None:` + `if __name__ == "__main__": main()`), 1 blank line after `def ...:`, tiny starter `print` lines per section, and `#` prose comments.
- **Ordered Outline**:
  1. **Section 1 (`console_printing`)**: Mixed-type `print(..., sep=" | ", end="!\n")`, inline `flush=True` progress dots, and `file=sys.stderr` warnings.
  2. **Section 2 (`fstrings_and_hex_formatting`)**: Comma/percent formatting (`:,`, `:.1%`), two-row price table (`:<12`, `:>8.2f`), PEP 701 nested quotes, and hex formatting drills using the `#` hex guide.
  3. **Section 3 (`debug_fstrings_and_docstrings`)**: `!s` vs `!r` and `f"{expr=}"` inspection, module + `main.__doc__` inspection, and a local `greet` function proving `#` comments never enter `__doc__`.

### `005_names_objects_and_binding.py` *(Core Primer — reset user edits)*
- **Defining Concept & Friction Point**: Breaking the C/Odin/Java mental model of "variables are typed boxes in memory". In Python, variables are **untyped names (labels)** in a namespace dictionary that point to heap-allocated `PyObject` structs (`refcount`, `type*`, `value`). Rebinding a name moves the label; it never overwrites the target memory slot. *(Reset user-pasted `sys.monitoring`/`dis`/`estimate_native` experiment back to pure name-binding **Drills**; those topics belong in `570`/`575`/`760`.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `=` (name binding) vs. in-place mutation vs. `+=` rebinding (`int`/`str`) vs. mutating (`list`).
  - `id(obj)`, `type(obj)`, `is` / `is not` (object identity) vs. `==` / `!=` (value equality).
  - `None` — Always check with `x is None` or `x is not None` (never `x == None`, because a custom `__eq__` can return `True` for `None`).
  - `del name` — Removes the name binding from the namespace without freeing objects still referenced by aliases.
  - CPython Small-Integer (`-5..256`) & String Interning Friction — `int("200") is int("200")` vs. `int("5000") is int("5000")`.
- **Scaffold**: Multi-section structure (`labels_and_rebinding`, `identity_vs_equality_and_none`, `aliasing_del_and_plus_equals`, bottom `main()`), `#` prose comments, tiny starter `x = 42` line.
- **Ordered Outline**:
  1. **Drill 1**: Immutable `int`/`str` rebinding (`a = 10; b = a; a = 20`) vs. mutable aliasing (`first_label = [1, 2, 3]; second_label = first_label; first_label.append(4)`), plus rebinding `first_label = [99, 100]` to detach the alias.
  2. **Drill 2**: Integer identity trap comparing `int("200")` vs. `int("5000")` with `==` and `is`, plus a custom class with a broken `__eq__` proving why `is None` is mandatory.
  3. **Drill 3**: Parallel swap `width, height = height, width`, `del alias` unbinding without freeing the underlying list, and `+=` rebinding an `int`/`tuple` vs. mutating a `list` in place.

### `010_numbers_arbitrary_precision_and_math.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Python `int` has arbitrary precision (never overflows like 32/64-bit C/Odin ints), whereas `float` is a 64-bit IEEE-754 double that suffers from binary fraction rounding (`0.1 + 0.2 == 0.30000000000000004`) and has a maximum range (~1.8e308). *(Guardrail: skip `decimal.Context` trap tables and `sys.int_info` limb math.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `int` — Arbitrary-length signed integer; `_` visual separators (`1_000_000`), hex (`0xDEAD_BEEF`), binary (`0b1010_0101`), octal (`0o755`), `int(str_val, base)`, `.bit_length()`, `.bit_count()`.
  - `float` — 64-bit IEEE-754 floating point; `float("inf")`, `float("-inf")`, `float("nan")` (where `nan != nan` is always `True`).
  - `math.isclose(a, b, *, rel_tol=1e-09, abs_tol=0.0)`, `math.isnan()`, `math.isinf()`, `math.isfinite()`.
  - `decimal.Decimal` — Exact base-10 arithmetic (`Decimal("0.1") + Decimal("0.2") == Decimal("0.3")`; warn against passing a `float` `Decimal(0.1)` instead of a `str`).
  - `fractions.Fraction(numerator, denominator)` & `complex(real, imag)` / `j` literal.
  - `round(val, ndigits)` — Round-half-to-even (banker's rounding: `round(2.5) == 2`, `round(3.5) == 4`).
- **Scaffold**: `import math`, `from decimal import Decimal`, `from fractions import Fraction`, section functions, bottom `main()`.
- **Ordered Outline**:
  1. Explain unbounded `int` arithmetic vs. `float` binary rounding and banker's `round()`.
  2. **Drill 1**: Compute `huge_power = 2 ** 128`, inspect `.bit_length()` and `.bit_count()`, and parse `"0xFF_00"` with `int("0xFF_00", 16)`.
  3. **Drill 2**: Show `0.1 + 0.2 == 0.3` is `False`, compare with `math.isclose(0.1 + 0.2, 0.3)` and `Decimal("0.1") + Decimal("0.2") == Decimal("0.3")`, and test `Decimal(0.1)` vs. `Decimal("0.1")`.
  4. **Drill 3**: Demonstrate banker's rounding on `round(2.5)` and `round(3.5)`, `Fraction(1, 3) + Fraction(1, 6)`, `abs(3 + 4j)`, and `nan != nan`, plus `# Try uncommenting: float(10 ** 400)` (`OverflowError`).

### `015_booleans_truthiness_and_short_circuit.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Every Python object has an inherent truthiness (`bool(x)`), and `and`/`or` do **not** return `True`/`False`—they return the **actual operand object** that decided the expression, which causes subtle bugs when `0` or `""` is a valid non-missing value!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `bool`, `True`, `False` — `bool` is a subclass of `int` (`issubclass(bool, int)` is `True`, `True == 1`, `False == 0`, so `sum([True, False, True]) == 2`).
  - Truthiness & Falsiness (`bool(x)`) — Falsy values are `None`, `False`, numeric zero (`0`, `0.0`, `0j`, `Decimal(0)`, `Fraction(0, 1)`), and empty containers (`""`, `b""`, `()`, `[]`, `{}`, `set()`, `range(0)`).
  - `and` / `or` value-returning short-circuit semantics & the Falsy-Zero Trap (`configured_timeout or 30` replacing `0` with `30` vs. `30 if configured_timeout is None else configured_timeout`).
  - `not x` (always returns `bool`) & chained comparisons (`0 <= temperature < 100`, `a == b == c`).
- **Scaffold**: Section functions, `#` prose comments, tiny starter check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Verify `isinstance(True, int)`, `True + True == 2`, and count positives in `[-3, 0, 4, 7, -1, 9]` via `sum(n > 0 for n in nums)`.
  2. **Drill 2**: Demonstrate the `or` default trap with `configured_timeout: int | None = 0`, contrasting `configured_timeout or 30` with `30 if configured_timeout is None else configured_timeout`, plus short-circuit side-effect proof.
  3. **Drill 3**: Practice chained comparisons (`0 <= temperature < 100`) and contrast `not x` returning `bool` with `a and b` / `a or b` returning operand objects.

### `020_strings_unicode_and_bytes.py` *(Core Primer — scoped `"""..."""` string literal exception)*
- **Defining Concept & Friction Point**: The strict wall between `str` (immutable sequence of Unicode code points) and `bytes` (immutable sequence of raw `0..255` integers), plus everyday text cleaning and UTF-8 boundary handling. Indexing `str[0]` returns a 1-character `str`, whereas indexing `bytes[0]` returns an `int`! *(Scoped exception: module prose stays in `#` comments; `"""..."""` is used strictly for assigned/printed multi-line string literal values. Guardrail: skip PEP 393 UCS-1/2/4 internals and obscure methods `swapcase`, `expandtabs`, `zfill`.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - String literals: single `'...'`, double `"..."`, triple-quoted `"""..."""` multi-line literals, escapes (`\n`, `\t`, `\\`, `\"`), and `r"..."` raw literals (plus trailing-backslash gotcha).
  - `str` immutability, `ord()` / `chr()`, `len(s)` code points vs. `len(s.encode("utf-8"))` bytes.
  - `bytes` (`b"..."`) & `bytearray` — `.encode("utf-8")`, `.decode("utf-8", errors="replace")`, `.hex()`, `bytes.fromhex(...)`.
  - Everyday text pipelines: `.strip()`, `.splitlines()`, `.split(maxsplit=1)`, `",".join()`, `.replace()`, `.find()` vs `.index()`, `.partition()`, `.removeprefix()`, `.removesuffix()`, `.casefold()` vs `.lower()`.
- **Scaffold**: Multi-section layout (`literals_escapes_and_raw`, `cleaning_and_splitting_pipelines`, `unicode_bytes_and_bytearray`, bottom `main()`), tiny starter `text = "Aα🚀"`.
- **Ordered Outline**:
  1. **Drill 1**: Practice single/double/triple-quoted `"""..."""` multi-line string values, escape sequences (`\n`, `\t`, `\\`), and `r"C:\new\test"` raw string literals.
  2. **Drill 2**: Build an everyday cleaning pipeline over messy log/CSV text using `.strip()`, `.splitlines()`, `.split(maxsplit=1)`, `",".join()`, `.replace()`, `.removeprefix()`, `.partition()`, `.find()` vs. `.index()`, and `.casefold()` vs. `.lower()`.
  3. **Drill 3**: Encode `"Aα🚀"` to UTF-8 `bytes`, compare `len(text)` vs. `len(raw_utf8)` and `text[0]` (`str`) vs. `raw_utf8[0]` (`int`), decode malformed `b"ok-\xff-end"` with `errors="replace"`, mutate a `bytearray`, and include `# Try uncommenting: text[0] = "B"` (`TypeError`).

### `025_operators_floor_div_and_walrus.py` *(Narrow Primer — ~85–140 lines, 4–7 Drills)*
- **Defining Concept & Friction Point**: Python's `/` always produces a `float` (even `4 / 2 == 2.0`), while `//` and `%` use **floored division toward -infinity** (unlike C's truncated-toward-zero division!), and `:=` binds variables inside expressions.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `/` (true division) vs. `//` (floor division: `-7 // 3 == -3`, since floor(-2.333) = -3).
  - `%` (floored modulo) & `divmod(a, b)` — Satisfies `(a // b) * b + (a % b) == a`, so `-7 % 3 == 2` and ring-buffer index wrapping `(idx - 1) % cap` works cleanly on negative numbers.
  - `**` & 3-arg `pow(base, exp, mod)` (modular exponentiation in O(log exp) time without huge intermediates).
  - Bitwise operators (`&`, `|`, `^`, `~` where `~x == -(x + 1)`, `<<`, `>>`) & `:=` (Walrus operator, PEP 572).
- **Scaffold**: `#` prose comments, tiny starter division print, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Compute and print `8 / 2`, `8 // 2`, `-7 // 3`, `-7 % 3`, `divmod(-7, 3)`, and verify negative wraparound `(0 - 1) % 8`.
  2. **Drill 2**: Compute `pow(7, 10_000, 1_000_007)` and manipulate bit flags using `|`, `&`, `^`, and `& ~mask`.
  3. **Drill 3**: Use `:=` inside `if (n := len(payload)) > 5:` and compare with `~0 == -1`.

### `030_type_annotations_and_static_checking.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Python is **dynamically typed at runtime** (type hints are stored as metadata in `__annotations__` and are *not* enforced by the interpreter when you call a function!) alongside **gradual static typing** checked by tools like `mypy` and `pyright`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - Built-in container & alias hints (`list[int]`, `dict[str, float]`, `tuple[int, str]`, `tuple[int, ...]`, PEP 695 `type UserMap = dict[str, int]`).
  - `X | Y` and `X | None` (PEP 604 union types) vs. `typing.Any` (disables checking) vs. `object` (safe top type requiring `isinstance` narrowing).
  - `typing.Final`, `typing.Literal`, `__annotations__`, `inspect.get_annotations()`, and `isinstance` type narrowing.
- **Scaffold**: `from typing import Any, Final, Literal`, `#` prose comments, section functions, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Define `type ScoreBoard = dict[str, float]`, `MAX_CONNECTIONS: Final[int] = 100`, and `format_id(raw_id: int | str, prefix: Literal["USR", "ORD"] = "USR") -> str` using `isinstance` narrowing.
  2. **Drill 2**: Write container-typed functions using `list[int]`, `dict[str, float]`, `tuple[int, str]`, and `tuple[int, ...]`, and inspect `.__annotations__`.
  3. **Drill 3**: Prove runtime non-enforcement (`x: int = "not an int"` executes without `TypeError`), contrast `Any` vs. `object`, and include `# Try running mypy on: format_id(42, prefix="BAD")`.

### `035_scopes_legb_and_closures_preview.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Two major Python scope surprises: (1) `if`, `for`, `while`, `with`, and `try` blocks **do not have their own scope**—variables declared inside them live in the enclosing function; and (2) **any assignment `x = ...` anywhere inside a function makes `x` local to that entire function at compile time**, causing `UnboundLocalError` if you read `x` before the assignment line!
- **Keywords, Built-ins & Concepts Breakdown**:
  - LEGB Rule (**L**ocal -> **E**nclosing -> **G**lobal -> **B**uilt-in) & built-in shadowing trap (assigning `sum = 0` or `list = []` hides the built-in!).
  - Block scope absence across `if`, `for`, `with`, and `try` (vs. isolated comprehension scope).
  - `UnboundLocalError`, `global name`, and `nonlocal name`.
- **Scaffold**: `GLOBAL_LIMIT = 500`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Demonstrate full LEGB lookup (local, enclosing, module global, built-in `len`) and show the built-in shadowing trap (`sum = 0` breaking a subsequent `sum([1, 2])` unless kept isolated).
  2. **Drill 2**: Verify variables assigned inside `for`, `if`, `with`, and `try` leak into the enclosing function, contrasting with a list comprehension whose loop variable stays isolated.
  3. **Drill 3**: Write a nested `make_counter(start: int)` using `nonlocal count`, mutate a module flag safely with `global`, and include an `UnboundLocalError` `# Try uncommenting:` experiment.

### `040_if_elif_else_and_conditional_expr.py` *(Narrow Primer — ~85–140 lines, 4–7 Drills)*
- **Defining Concept & Friction Point**: Clean conditional branching with `if / elif / else`, inline conditional expressions (`a if cond else b`), and explicit `is None` / `is not None` checks instead of ambiguous truthiness.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `if`, `elif`, `else` (colon-and-indentation branching).
  - `a if cond else b` (ternary conditional expression — lazy branch evaluation).
  - `pass` vs. `...` (`Ellipsis` singleton) in empty blocks vs. type stubs (`tuple[int, ...]`, `Callable[..., int]`) — note we avoid `pass` stubs in Drills themselves.
  - Explicit `is None` / `is not None` guards so `0` or `0.0` is never confused with missing `None`.
- **Scaffold**: `#` prose comments, tiny starter latency check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Write `classify_latency(ms: float | None) -> str` checking `if ms is None:` first, then `< 20.0`, `< 100.0`, and `else`.
  2. **Drill 2**: Use conditional expressions `a if cond else b` (including proving the non-selected branch is not evaluated) and test `0.0` vs. `None`.

### `045_structural_pattern_matching.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Structural Pattern Matching (`match / case`, PEP 634) is **not** a C `switch` statement—it unpacks and binds structure! The #1 gotcha: a bare identifier in `case HTTP_OK:` does **not** compare against the variable `HTTP_OK`; it **captures any value into a new variable named `HTTP_OK`**! Constant value matching requires a dotted name (`case HttpStatus.OK:`) or a literal (`case 200:`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `match subject:` & `case pattern:` (no fallthrough).
  - Literal & OR patterns (`case 200 | 201:`), `as` sub-pattern bindings (`case [cmd, ("fast" | "safe") as mode]:`).
  - Capture pattern vs. Dotted Value pattern (`case x:` vs. `case HttpStatus.OK:`).
  - Sequence patterns (`case [cmd, *args]:`), partial mapping patterns (`case {"event": "move", "x": int(x), "y": int(y)}:`), class patterns (`case Point(x=0, y=y):`), `_` wildcard, and `if` guards.
- **Scaffold**: `from dataclasses import dataclass`, `from enum import IntEnum`, `@dataclass class Point: x: int; y: int`, `class HttpStatus(IntEnum): ...`, section functions, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Write `classify_status(code: int) -> str` using dotted enum constants (`case HttpStatus.OK | HttpStatus.CREATED:`), `case 400 | 404 as err_code:`, and contrast with a deliberate bare-name capture demonstration.
  2. **Drill 2**: Write `handle_event(event: object) -> str` matching `Point(x=0, y=0)`, guarded `Point(x=x, y=y) if x == y`, partial dict `{"type": "cmd", "args": [first, *rest]}`, `("move", int(dx), int(dy))`, and `_` across extra dict keys.

### `050_for_while_and_loop_else.py` *(Approved Pilot Primer — Core, 211 lines)*
- **Defining Concept & Friction Point**: Python's `for` loop always iterates over an **iterable** via the iterator protocol (`iter()` + `next()`), and Python's `for ... else:` / `while ... else:` block runs **only if the loop finished normally without hitting `break`** (think of `else:` on a loop as `nobreak:`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `for item in iterable:` — Iterates `range()`, `str`, `dict.items()`, and `set` directly without `range(len(...))`.
  - `range(start, stop, step)` — Lazy O(1)-memory immutable integer sequence supporting `len()`, `r[-1]`, and O(1) `x in r`.
  - `while cond:`, `while True:` + `break`, `continue`-before-increment infinite-loop trap, and sentinel loops (`while (cmd := next_cmd()) != "QUIT":` and `iter(callable, "QUIT")`).
  - `for ... else:` / `while ... else:` (including empty-iterable behavior) & nested 2D loop early `return` from a helper function (`enumerate`).
  - Mutation-during-iteration trap preview (`list.remove` silent skip vs. `dict` `RuntimeError`).
- **Scaffold**: Approved 4-section layout (`for_loops_and_lazy_ranges`, `while_sentinels_and_continue_traps`, `loop_else_and_nested_early_returns`, `iteration_mutation_trap_preview`, bottom `def main() -> None:` + `if __name__ == "__main__": main()`), 1 blank line after `def ...:`, `#` prose comments, and tiny starter loops.
- **Ordered Outline**:
  1. **Section 1 (`for_loops_and_lazy_ranges`)**: Backward `range(10, 0, -2)`, `sys.getsizeof(range(0, 10_000_000, 5))` O(1) proof, and direct loops over `str`, `dict.items()`, and `set`.
  2. **Section 2 (`while_sentinels_and_continue_traps`)**: Queue draining with `while True:`, safe `while` + `continue` increment-before-check, walrus `:=` sentinel loop, and 2-arg `iter(callable, sentinel)`.
  3. **Section 3 (`loop_else_and_nested_early_returns`)**: Prime check with `for ... else:` (29 vs 28), empty-iterable `for ... else:`, 2D grid cell scan, and `find_target` helper exiting nested loops via early `return`.
  4. **Section 4 (`iteration_mutation_trap_preview`)**: Reproducing `list.remove` skipping `[4, 5]` + shallow-copy/comprehension fix, and `dict` `list(counts)` snapshot + `# Try uncommenting:` `RuntimeError` experiment.

### `055_iteration_helpers_enumerate_zip_reversed.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Writing `for i in range(len(items)):` in Python is an anti-pattern; use `enumerate()`, `zip(..., strict=True)`, and `reversed()`. The friction point: `zip(a, b)` without `strict=True` **silently drops trailing elements** if `a` and `b` have different lengths!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `enumerate(iterable, start=0)`, `zip(*iterables, strict=True)`, `zip(*matrix)` (transposing / unzipping `zip(*pairs)`), `reversed(seq)` (lazy reverse iterator), `sorted()`, `any(iterable)`, and `all(iterable)` (short-circuiting + vacuous `all([]) == True` / `any([]) == False`).
- **Scaffold**: Section functions, `#` prose comments, tiny starter `enumerate` loop, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Iterate `names` and `scores` in parallel using `enumerate(zip(names, scores, strict=True), start=1)`, plus an unzipping drill `names_out, scores_out = zip(*pairs)`.
  2. **Drill 2**: Transpose a `2x3` matrix with `list(zip(*rows, strict=True))` and reverse a sequence lazily with `reversed(names)`.
  3. **Drill 3**: Prove `any()` / `all()` short-circuiting with a side-effect generator, verify `all([]) is True`, and include `# Try uncommenting: list(zip([1, 2], [10], strict=True))` (`ValueError`).

### `060_unpacking_and_starred_expressions.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Python's unpacking grammar lets you destructure arbitrary iterables on the left-hand side of `=` and splat iterables/mappings inside literals and calls with `*` and `**`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - Exact unpacking, starred target unpacking (`head, *body, tail = items`, where `*body` is always a `list`), nested unpacking, `_` / `*_` throwaways, and literal splatting (`[*part_a, 0, *part_b]`, `{**defaults, **overrides}`).
- **Scaffold**: Section functions, `#` prose comments, tiny starter swap/unpack, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Unpack `header, *payload, checksum = b"\xAA\x10\x20\x30\xFF"` (plus edge case when `*payload` receives `[]`).
  2. **Drill 2**: Unpack nested records `for city, (lat, lon) in records:` and discard middle items with `first, *_, last = ...`.
  3. **Drill 3**: Merge lists with `[*a, 0, *b]` and config dicts with `{**base_cfg, **env_cfg}` vs. `base_cfg | env_cfg`, plus `# Try uncommenting:` mismatched-length `ValueError`.

### `065_exceptions_try_except_else_finally.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Understanding all four clauses of `try / except / else / finally`, why bare `except:` is an anti-pattern (`BaseException` vs. `Exception`), exception subclass ordering (`except Exception:` before `except ValueError:` masks `ValueError`!), and the subtle danger of putting `return` inside a `finally:` block (which silently swallows any active exception!).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `try:` / `except SomeError as err:` / `else:` (runs only if `try` succeeded; not caught by preceding `except:`) / `finally:` (always runs).
  - `BaseException` vs. `Exception` (`SystemExit`, `KeyboardInterrupt`, `GeneratorExit`), subclass ordering (`OSError`/`FileNotFoundError` before `Exception`), and the `return`-in-`finally` swallowing trap.
- **Scaffold**: Section functions, `#` prose comments, tiny starter `try/except`, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `parse_ratio(raw: str) -> float | None` keeping only conversion/division in `try:`, catching `(ValueError, ZeroDivisionError)`, using `else:` and `finally:`, and testing valid/zero/bad inputs.
  2. **Drill 2**: Demonstrate exception hierarchy ordering (`FileNotFoundError` / `OSError` before `Exception`) and why `except BaseException:` traps `KeyboardInterrupt`.
  3. **Drill 3**: Demonstrate the `return`-in-`finally` trap swallowing an exception vs. clean `finally:` cleanup.

### `070_raising_chaining_and_exception_groups.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Preserving vs. suppressing diagnostic root causes with explicit exception chaining (`raise NewError(...) from err` vs. `raise NewError(...) from None`), enriching exceptions in transit with `.add_note()`, and handling concurrent failures with `ExceptionGroup` and `except*` (PEP 654).
- **Keywords, Built-ins & Concepts Breakdown**:
  - Custom `Exception` subclasses, bare `raise`, `raise ... from err` (`__cause__`), `raise ... from None` (`__suppress_context__`), `err.add_note("...")`, and `ExceptionGroup` / `except*`.
- **Scaffold**: Section functions, `#` prose comments, tiny starter custom exception check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Define `ConfigError(Exception)` (unimplemented class/methods specified in `#` **Drill** or tiny working `__init__` **Scaffold** with zero `pass` stubs) and write `load_port` raising `ConfigError(...) from err` vs. `from None`, inspecting `err.__cause__`.
  2. **Drill 2**: Attach context via `err.add_note(...)` and inspect `err.__notes__`.
  3. **Drill 3**: Handle an `ExceptionGroup` with `except* ValueError as vg:` and `except* TypeError as tg:`.

### `075_with_context_managers_basics.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Why relying on garbage collection (`__del__`) to close files, sockets, or locks is a bug, and how `with` guarantees deterministic teardown at block exit—including multi-resource parenthesized `with (cm1, cm2):` blocks.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `with expr as var:`, parenthesized multi-manager `with (cm1 as a, cm2 as b):`, `contextlib.suppress`, `contextlib.nullcontext`, and `contextlib.redirect_stdout`.
- **Scaffold**: `import io`, `from contextlib import nullcontext, redirect_stdout, suppress`, `#` prose comments, section functions, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Capture stdout with `io.StringIO()` and `with redirect_stdout(buf):`.
  2. **Drill 2**: Combine multiple context managers inside one parenthesized `with (redirect_stdout(out_a), redirect_stdout(out_b)):` or `TemporaryDirectory` + file handle.
  3. **Drill 3**: Use `with suppress(KeyError):` and `with (cm if enabled else nullcontext()):`.

### `080_assertions_warnings_and_introspection.py` *(Core Primer)*
- **Defining Concept & Friction Point**: The critical distinction between **internal invariants** (`assert`, which disappears completely when Python runs with `-O`!) and **runtime validation** (`if not valid: raise ValueError(...)`), plus Python's runtime introspection built-ins (`dir`, `vars`, `getattr`, `hasattr`, `callable`) and `warnings.warn`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `assert condition, message`, the `assert(False, "msg")` tuple syntax trap, `warnings.warn`, `isinstance`/`issubclass`, `hasattr`/`getattr`/`setattr`/`delattr`, `dir` vs. `vars`, and `callable`.
- **Scaffold**: `import warnings`, `#` prose comments, section functions, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Contrast an internal invariant `assert` (plus `# Try uncommenting:` parenthesized-tuple warning) with a real `if amount < 0: raise ValueError(...)` check and `warnings.warn(...)`.
  2. **Drill 2**: Inspect a small instance and function using `getattr(..., "fallback")`, `hasattr`, `callable`, `vars`, and `dir`.

---

## `100`–`199`: Functions, Signatures, Closures, Decorators, Generators & Testing

### `100_functions_and_return_semantics.py` *(Core Primer — scoped 1-line `__doc__` target)*
- **Defining Concept & Friction Point**: Python parameter passing is **pass-by-object-reference** (also called *call-by-sharing*): a function receives a new local label bound to the *exact same object* the caller passed. Mutating that object (`items.append(99)`)—or mutating a nested mutable item inside it—is visible to the caller, whereas rebinding the parameter name (`items = [99]`) only moves the local label!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `def name(params) -> ReturnType:`, implicit `return None`, multiple return tuple unpacking (`q, r = ...`), pass-by-object-reference (in-place mutation vs. nested mutable mutation vs. shallow rebinding), and first-class function attributes (`__name__`, `__qualname__`, `__doc__` on a scoped 1-line target like `square`/`add`, `__annotations__`, `__code__`, dispatch dicts).
- **Scaffold**: Section functions, `#` prose comments, tiny starter `def square(x: int) -> int:` with 1-line `__doc__` inspection target, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Write `mutate_in_place(data: list[int]) -> None` vs. `rebind_local(data: list[int]) -> list[int]` plus a nested-mutable-argument drill (`nested = [[1], [2]]`, mutating `nested[0].append(9)` vs. shallow rebinding), printing `original` after each call.
  2. **Drill 2**: Write `min_max_sum(nums: list[int]) -> tuple[int, int, int]` and unpack all three return values.
  3. **Drill 3**: Build a dispatch dictionary `ops: dict[str, Callable[[int, int], int]]` mapping `"add"` and `"mul"` to functions, invoke them dynamically, and inspect `square.__doc__`.

### `110_positional_keyword_and_default_args.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Default argument expressions (`def add_tag(tag: str, tags: list[str] = []):` or `cache: dict[str, int] = {}`) are evaluated **once when the `def` statement executes**, NOT each time the function is called! That single container lives in `fn.__defaults__` and accumulates state across every call that omits it.
- **Keywords, Built-ins & Concepts Breakdown**:
  - Positional vs. keyword arguments, default evaluation timing (`__defaults__` / `__kwdefaults__`), mutable `[]` and `{}` default traps, canonical `None` sentinel fix, and `MISSING = object()` sentinel when `None` is a valid explicit argument.
- **Scaffold**: `MISSING = object()`, section functions, `#` prose comments, tiny starter default inspection, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Demonstrate both the mutable `[]` default list trap (`buggy_append`) and the mutable `{}` default dict trap (`buggy_cache`), inspecting `.__defaults__` after repeated calls.
  2. **Drill 2**: Write `safe_append` and `safe_cache` using `| None = None` with fresh container allocation inside the body.
  3. **Drill 3**: Write `update_setting(val: int | None | object = MISSING)` distinguishing explicit `None` from omitted `val`.

### `120_varargs_kwargs_and_signature_markers.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Designing resilient library signatures using `*args`, `**kwargs`, positional-only parameters (`/`), and keyword-only parameters (`*`) so callers cannot break when you rename internal positional parameters or add new options.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `*args: int`, `**kwargs: Any`, `/` (PEP 570 positional-only marker), `*` (PEP 3102 keyword-only marker), and call-site unpacking (`fn(*seq, **mapping)`).
- **Scaffold**: Section functions, `#` prose comments, tiny starter signature print, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Write `send_request(method: str, url: str, /, *, timeout: float = 5.0, follow_redirects: bool = True, **headers: str) -> str` combining `/`, `*`, and `**headers`.
  2. **Drill 2**: Call `send_request` with positional/keyword args and `fn(*args, **kwargs)` unpacking, plus `# Try uncommenting:` experiments for passing `/` args by keyword and `*` args positionally (`TypeError`).

### `130_lambda_and_late_binding_closures.py` *(Core Primer)*
- **Defining Concept & Friction Point**: The **Late-Binding Closure Trap**: when a nested function or `lambda` references a loop variable `i`, Python captures the **cell reference** to `i`, not the value `i` had when the function was created! When called after the loop ends, every closure reads the final value of `i`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `lambda params: expr`, closures & cell objects (`__closure__`, `cell.cell_contents`, `co_freevars`), the late-binding loop trap, default-argument early binding (`lambda x, i=i: ...`), and helper factory / `functools.partial`.
- **Scaffold**: `from functools import partial`, section functions, `#` prose comments, tiny starter closure, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Create `buggy_multipliers = [lambda x: x * i for i in range(4)]`, observe `[30, 30, 30, 30]`, and inspect `buggy_multipliers[0].__closure__[0].cell_contents`.
  2. **Drill 2**: Fix the loop closure via default-argument capture (`lambda x, i=i: x * i`) AND via a `make_multiplier(factor: int)` factory / `partial`, verifying `[0, 10, 20, 30]`.

### `140_decorators_and_functools_wraps.py` *(Core Primer — scoped 1-line `__doc__` target)*
- **Defining Concept & Friction Point**: A decorator `@deco` is just `fn = deco(fn)` executed at definition time. Without `@functools.wraps(fn)`, a naive wrapper destroys `fn.__name__`, `fn.__doc__`, `fn.__annotations__`, and `fn.__wrapped__`!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `@decorator` desugaring, `@functools.wraps(fn)`, `__wrapped__`, and decorator stacking order (`@outer` above `@inner` applies bottom-up, runs top-down).
- **Scaffold**: `from collections.abc import Callable`, `from functools import wraps`, section functions, `#` prose comments, tiny starter decorator, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Write a broken decorator *without* `@wraps` and decorate a target function carrying a 1-line `"""..."""` docstring (`compute_tax`), printing `__name__` and `__doc__` to observe metadata loss (`"wrapper"` / `None`).
  2. **Drill 2**: Fix it with `@functools.wraps(fn)`, verify `compute_tax.__name__`, `compute_tax.__doc__`, and call the unwrapped original via `compute_tax.__wrapped__(100.0, 0.08)`.
  3. **Drill 3**: Stack two decorators (`@outer` above `@inner`) and verify execution order.

### `150_parameterized_and_class_decorators.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Writing decorators that accept configuration arguments (`@retry(max_attempts=3)`) requires a 3-level **decorator factory**—or a dual-mode decorator using `functools.partial` that works both bare `@tag` and parameterized `@tag(category="math")`!
- **Keywords, Built-ins & Concepts Breakdown**:
  - 3-layer Decorator Factory, dual-mode decorator (`if fn is None: return partial(...)`), stateful class decorator (`CallCounter` + `functools.update_wrapper`), and decorating a `class` (`register_command`).
- **Scaffold**: `from functools import partial, update_wrapper, wraps`, section functions, `#` prose comments, tiny starter wrapper, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Write a parameterized `@retry(max_attempts: int = 3)` decorator factory retrying on `ValueError`.
  2. **Drill 2**: Write a dual-mode `@tag` decorator working both as `@tag` and `@tag(category="math")`, plus a class-based `CallCounter` or class-registration decorator.

### `160_functools_lru_cache_partial_and_singledispatch.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Using `functools` for automatic memoization (`@cache`, `@lru_cache`), partial application (`partial`), and type-dispatched function overloading (`@singledispatch`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `@functools.cache` & `@functools.lru_cache(maxsize=128, typed=False)` (hashable argument constraint & mutated-cached-return trap), `.cache_info()` / `.cache_clear()`, `functools.partial`, `functools.reduce`, and `@functools.singledispatch` + `@fn.register`.
- **Scaffold**: `from functools import cache, lru_cache, partial, singledispatch`, section functions, `#` prose comments, tiny starter cache call, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Write `@lru_cache(maxsize=64) def count_ways(steps: int) -> int:`, compute `count_ways(30)`, print `count_ways.cache_info()`, and test the unhashable `list` `TypeError` + `cache_clear()`.
  2. **Drill 2**: Define `@singledispatch def serialize(val: object) -> str:` with registered overloads for `int`, `float`, and `list`, plus `functools.partial`.

### `170_operator_module_and_key_functions.py` *(Narrow Primer — ~110–130 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Replacing verbose `lambda x: x["score"]` or `lambda x: x.name` callbacks with fast, self-documenting C-level callables from `operator` (`itemgetter`, `attrgetter`, `methodcaller`) and `functools.cmp_to_key`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `operator.itemgetter(*items)`, `operator.attrgetter(*attrs)` (dotted attribute paths), `operator.methodcaller(name, *args, **kwargs)`, and `functools.cmp_to_key(cmp_fn)`.
- **Scaffold**: `from functools import cmp_to_key`, `from operator import attrgetter, itemgetter, methodcaller`, `#` prose comments, tiny starter sort, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Sort dicts by `itemgetter("department", "level")` and project fields with `map(itemgetter("name", "level"), employees)`.
  2. **Drill 2**: Use `attrgetter` on nested objects, `methodcaller("split", ",")`, and `cmp_to_key` to sort `["3", "30", "34", "5", "9"]` into `"9534330"`.

### `180_generators_and_yield.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Any function containing `yield` compiles into a **generator factory**: calling it returns a lazy generator iterator (`gi_frame`) that pauses at each `yield` and resumes on `next()`. Generators are **single-use iterators**, and breaking out early triggers `GeneratorExit` so cleanup belongs inside `try ... finally:`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `yield expr`, `next(gen, default)`, `StopIteration.value` (capturing a generator's `return` value!), `yield from sub_iterable`, `.send(val)` / `.close()`, `try ... finally:` cleanup on early `break` / `GeneratorExit`, generator expression vs. list comprehension memory (`sys.getsizeof`), and single-pass exhaustion vs. re-iterable class (`__iter__`).
- **Scaffold**: `from collections.abc import Iterator`, `from itertools import islice`, `import sys`, section functions, `#` prose comments, tiny starter generator, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Build an everyday streaming log pipeline (generate lines -> filter `"ERROR"` -> take first 3 with `islice`), and contrast `sys.getsizeof` of a generator expression vs. a list comprehension.
  2. **Drill 2**: Write a recursive `flatten_nested` using `yield from`, inspect `StopIteration.value` from a generator that `return`s a summary, and prove `try ... finally:` runs cleanup on early `break` / `.close()`.
  3. **Drill 3**: Demonstrate single-pass generator exhaustion and wrap a generator factory in a tiny re-iterable class with `__iter__`.

### `185_custom_context_managers_contextlib.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Authoring custom `with` context managers via `__enter__`/`__exit__` or `@contextlib.contextmanager` (where cleanup must sit inside `try: yield ... finally:` because exceptions inside the `with` body are re-raised at the `yield` line!), plus dynamic `ExitStack`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `__enter__(self) -> T`, `__exit__(self, exc_type, exc_val, exc_tb) -> bool | None` (exception suppression when returning `True`), `@contextlib.contextmanager`, and `contextlib.ExitStack` (`enter_context`, `callback` LIFO cleanup).
- **Scaffold**: `from collections.abc import Iterator`, `from contextlib import ExitStack, contextmanager`, `import time`, section functions, `#` prose comments, tiny starter context usage, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `StopwatchTimer` (`__enter__`/`__exit__`) using `time.perf_counter_ns()`.
  2. **Drill 2**: Implement `@contextmanager def temp_config_override(...)` restoring the original key inside `finally:` even when an exception occurs.
  3. **Drill 3**: Use `with ExitStack() as stack:` and `stack.callback(...)` to verify LIFO teardown order.

### `190_callable_types_and_callbacks.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Expressing rich function signatures in Python's type system: `collections.abc.Callable[[P1, P2], R]`, callback `Protocol` (`def __call__`) for keyword/default/variadic arguments, and `@typing.overload` for input-dependent return types.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `collections.abc.Callable[[Param1, Param2], ReturnType]`, `Callable[..., ReturnType]`, callback `Protocol`, and `@typing.overload` stubs above one runtime implementation.
- **Scaffold**: `from collections.abc import Callable`, `from typing import Literal, Protocol, overload`, section functions, `#` prose comments, tiny starter callback, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Define `ValidatorProtocol(Protocol)` with `def __call__(self, value: str, *, strict: bool = False) -> bool:` (exact signature inside `#` **Drill** or working starter class) and pass a matching callable to `run_validation`.
  2. **Drill 2**: Write two `@overload` declarations for `parse_data(raw: str, *, as_bytes: Literal[False] = False) -> str` and `as_bytes: Literal[True] -> bytes` above the single runtime implementation, and call both.

### `195_unit_testing_with_unittest.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Writing deterministic, isolated unit tests using Python's built-in `unittest` and `unittest.mock` modules (`python -m unittest -v 195_unit_testing_with_unittest.py`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `unittest.TestCase`, `setUp(self)` / `tearDown(self)` per-test isolation, `assertEqual`, `assertAlmostEqual`, `assertRaises`, `assertWarns`, `subTest()`, `MagicMock`, and `unittest.mock.patch.object` against a concrete helper object.
- **Scaffold**: `import unittest`, `from unittest.mock import MagicMock, patch`, `import warnings`, starter `clamp_and_scale` baseline, bottom `main()` calling `unittest.main(exit=False)`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `clamp_and_scale(val: float, lo: float, hi: float, scale: float = 1.0) -> float` (raising `ValueError` if `lo > hi` and emitting a `UserWarning` on overflow clamping if desired).
  2. **Drill 2**: Write `TestClampAndScale(unittest.TestCase)` with `setUp()` / `tearDown()` per-test state isolation, parameterized `self.subTest(...)`, `self.assertRaises(ValueError)`, and `self.assertWarns(...)`.
  3. **Drill 3**: Define a tiny `Notifier` service class and test it with `MagicMock` and concrete `patch.object(Notifier, "send", ...)` verifying `.assert_called_once_with(...)`.

---

## `200`–`299`: Built-in Collections, Mutability, Aliasing, Hashing & Comprehensions

*(Note: Strip all legacy `reST` double-backticks `` `` `` and expand thin Primers in `200`–`280` into `#`-prose multi-section walkthroughs.)*

### `200_lists_dynamic_arrays_and_aliasing.py` *(Core Primer)*
- **Defining Concept & Friction Point**: A Python `list` is a contiguous dynamically resized C array of `PyObject*` pointers (`O(1)` amortized `.append`/`.pop`, `O(N)` front `.insert(0, x)`/`.pop(0)`), and `[[0] * 3] * 3` / `[{}] * 3` copy references to the **exact same inner mutable object**!
- **Keywords, Built-ins & Concepts Breakdown**:
  - Over-allocation growth observed via `sys.getsizeof`, `.append`, `.extend`, `.insert`, `.pop`, `.remove`, `.clear`, `.index()` (`ValueError` when absent), `a += b` in-place vs. `a + b` new list, and 2D `[[0] * 3] * 3` / `[{}] * 3` aliasing vs. `[[0] * 3 for _ in range(3)]`.
- **Scaffold**: `import sys`, section functions, `#` prose comments, tiny starter list growth check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Measure `sys.getsizeof` jumps as a list grows from `0` to `32` items, and practice `.append`, `.extend`, `.insert`, `.pop`, `.remove`, `.clear`, and `.index()` (catching `ValueError`).
  2. **Drill 2**: Reproduce both `bad_grid = [[0] * 3] * 3` and `bad_buckets = [{}] * 3` aliasing traps (inspecting `[id(row) for row in bad_grid]`), then fix both with list comprehensions.
  3. **Drill 3**: Contrast `a += [3]` (mutates aliases in place) with `a = a + [4]` (allocates new list).

### `205_slicing_slice_assignment_and_stride.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Unlike Odin/Go/Rust slices (zero-copy views), slicing a Python `list` (`sub = items[1:4]`) **allocates a shallow copy** (sharing nested mutable items!), while left-hand-side slice assignment (`items[1:4] = [99]`, `del a[1:3]`) mutates the list in place without changing `id(items)`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `seq[start:stop:step]`, negative-step bounds (`a[3:1:-1]`, `a[::-1]`), `slice(start, stop, step)` objects, shallow slice aliasing on nested lists (`nested_copy = nested[:]` still shares inner lists!), in-place slice assignment (`items[:] = ...`), `del items[1:3]`, and equal-length requirement on extended stride assignment (`step != 1`).
- **Scaffold**: Section functions, `#` prose comments, tiny starter slice, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Prove flat list slicing copies (`middle[0] = 999` leaves `nums` unchanged) AND prove nested list slicing shares inner lists (`sub = matrix[:]; sub[0].append(99)` mutates `matrix[0]`).
  2. **Drill 2**: Practice negative-step bounds (`a[3:1:-1]`, `a[::-1]`) and named `slice` objects (`MAGIC = slice(0, 2)`).
  3. **Drill 3**: Mutate in place with `nums[1:4] = [200, 300]`, `del nums[1:3]`, `nums[:] = [1, 2, 3]` (preserving `id(nums)`), and extended stride slice assignment.

### `210_shallow_vs_deep_copy.py` *(Narrow Primer — ~110–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Knowing when a shallow copy (`list.copy()`, `dict.copy()`, `copy.copy()`) shares nested mutable children vs. when `copy.deepcopy()` (with `memo` cycle detection) is required.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `copy.copy(x)` / `.copy()`, `copy.deepcopy(x)` (recursive + `memo` dict for self-referential cycles), and `__copy__` / `__deepcopy__`.
- **Scaffold**: `import copy`, `#` prose comments, tiny starter shallow check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Mutate `shallow_state["inventory"]` and observe `state["inventory"]` change; contrast with `copy.deepcopy(state)`.
  2. **Drill 2**: Create a self-referential cyclic list `cycle.append(cycle)` and verify `copy.deepcopy(cycle)` preserves the cycle without `RecursionError`.

### `215_tuples_immutability_and_namedtuple.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Two classic `tuple` traps: (1) `(42)` is `int`, whereas `(42,)` is a 1-tuple; and (2) tuple immutability only locks its array of object references—so `t = (1, [10, 20]); t[1] += [30]` **raises `TypeError` AND mutates `t[1]` anyway**!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `()` / `(x,)` literals, shallow reference lock, the `t[1] += [30]` bytecode puzzle, and `typing.NamedTuple` (`_asdict()`, `_replace()`, `_fields`).
- **Scaffold**: `from typing import NamedTuple`, section functions, `#` prose comments, tiny starter tuple check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Contrast `type((42))` vs. `type((42,))` and unpack multi-field records.
  2. **Drill 2**: Wrap `record[1] += ["admin"]` in `try / except TypeError:` and inspect `record` afterward to prove `"admin"` was appended before item assignment failed.
  3. **Drill 3**: Define `Color(NamedTuple)` (`r, g, b, a=255`), unpack it, and build a variant with `._replace(a=128)` / `._asdict()`.

### `220_dicts_insertion_order_and_views.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Compact insertion-ordered hash tables, live set-like views (`.keys()`, `.items()`), `dict.fromkeys(keys, [])` shared-list bug, `setdefault` eager evaluation waste, and `RuntimeError` on resizing during iteration.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `d.get(k, default)`, counting/grouping (`d.get(k, 0) + 1`), `d.pop(k, default)` vs. `d.popitem()`, `d.setdefault(k, default)` (warns that `default` is evaluated eagerly on every call even when `k` exists!), `dict.fromkeys(keys, [])` shared-reference bug, `d1 | d2` / `d1 |= d2`, set algebra on `.keys()`, and `for k in list(d):`.
- **Scaffold**: Section functions, `#` prose comments, tiny starter dict check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Practice counting (`counts[w] = counts.get(w, 0) + 1`), `pop(k, default)`, `popitem()`, and `scores | bonus`.
  2. **Drill 2**: Reproduce the `dict.fromkeys(["a", "b"], [])` shared-list bug and fix it with `{k: [] for k in keys}`, plus contrast `setdefault` eager evaluation with `if k not in d:`.
  3. **Drill 3**: Use `scores.keys() & bonus.keys()` / `bonus.keys() - scores.keys()` and delete keys safely via `list(merged.keys())`.

### `225_sets_and_frozensets.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Using `set` and hashable `frozenset` for O(1) membership and set algebra (`|`, `&`, `-`, `^`, `<=`), while remembering `{}` is an empty `dict` (not a `set`) and sets do not preserve insertion order.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `set()` vs. `{}` vs. `frozenset`, O(1) membership vs. O(N) list scan, set operators vs. `.union()`/`.intersection()`/`.isdisjoint()` (which accept any iterable), `.add()` / `.discard()` vs. `.remove()`, and order-preserving deduplication (`list(dict.fromkeys(items))`).
- **Scaffold**: Section functions, `#` prose comments, tiny starter set check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Check `required_perms <= user_perms`, compute `-` and `^`, and contrast `.discard()` vs. `.remove()`.
  2. **Drill 2**: Deduplicate `raw_events` preserving first-seen order via `list(dict.fromkeys(raw_events))` and contrast with scrambled `list(set(raw_events))`.
  3. **Drill 3**: Use `frozenset[str]` as keys in a `dict[frozenset[str], str]`.

### `230_hashability_and_equality_contracts.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Python hash tables probe `hash(key) & mask` then compare `==`. Therefore: (1) `a == b` must imply `hash(a) == hash(b)`; (2) defining `__eq__` sets `__hash__ = None` (`TypeError: unhashable type`); and (3) mutating hashed fields after insertion strands the key in the wrong bucket.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `hash()`, `__hash__` / `__eq__` invariant, `{1: "int", True: "bool", 1.0: "float"}` collision puzzle (`hash(1) == hash(1.0) == hash(True) == 1`), tuple-based hashing `hash((self.x, self.y))`, and mutable-key corruption.
- **Scaffold**: Section functions, `#` prose comments, tiny starter hash check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Inspect `{1: "int", True: "bool", 1.0: "float"}` (`len == 1`, key stays `1`, value becomes `"float"`).
  2. **Drill 2**: Implement immutable `GridCoord` with `__eq__` and `__hash__`, use it as `dict`/`set` keys, and show a mutable-key corruption experiment.

### `235_comprehensions_and_generator_expressions.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Declarative data pipelines with list/dict/set comprehensions and lazy generator expressions, avoiding conditional-output vs. trailing-`if` syntax confusion, dict-comprehension key collisions, and two-pass generator exhaustion.
- **Keywords, Built-ins & Concepts Breakdown**:
  - List/dict/set comprehensions, conditional output expression (`["even" if n % 2 == 0 else "odd" for n in nums]`) vs. trailing filter (`[n for n in nums if n % 2 == 0]`), dict key-collision overwrites, nested `for` flattening order, `:=` walrus filtering, two-pass generator exhaustion trap (`sum(g)` then `max(g)`), and readability limits.
- **Scaffold**: Section functions, `#` prose comments, tiny starter comprehension, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Contrast conditional output expression (`a if cond else b for ...`) with trailing `if` filter, flatten `matrix`, and use `:=` inside a comprehension filter.
  2. **Drill 2**: Demonstrate dict-comprehension key collision (last value wins) and invert a unique mapping.
  3. **Drill 3**: Prove generator expressions allocate O(1) memory and trigger the two-pass exhaustion trap (`sum(g)` then `max(g)` raises `ValueError: max() iterable argument is empty`).

### `240_collections_defaultdict_counter_chainmap.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Eliminating key-boilerplate with `defaultdict`, `Counter` (including `.update()` / `.subtract()`), and layered `ChainMap`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `defaultdict(factory)` (`__missing__` on `d[k]`, not `d.get(k)`), `Counter` (`.most_common(n)`, `.total()`, `.update()`, `.subtract()` keeping zero/negative counts vs. `+`/`-` dropping them), and `ChainMap(*maps)` (`.new_child()`, writes go to `maps[0]`).
- **Scaffold**: `from collections import ChainMap, Counter, defaultdict`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Group pairs into `defaultdict(list)` and verify `d.get("missing")` does not insert a key while `d["missing"]` does.
  2. **Drill 2**: Count words with `Counter`, inspect `.most_common(2)` and `.total()`, and contrast `c1 - c2` (drops `<= 0`) with `c1.subtract(c2)` (retains `<= 0`) + `.update()`.
  3. **Drill 3**: Layer `cli_args`, `env_vars`, and `defaults` into a `ChainMap` and test `.new_child()`.

### `245_collections_deque_and_bisect.py` *(Core Primer)*
- **Defining Concept & Friction Point**: O(1) FIFO queues and `maxlen` ring buffers with `collections.deque` (where middle indexing `d[n // 2]` is O(N)), and O(log N) binary search on sorted sequences with `bisect`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `deque(iterable, maxlen=None)` (`.append`, `.appendleft`, `.pop`, `.popleft`, `.rotate`), `bisect.bisect_left`, `bisect.bisect_right`, and `bisect.insort`.
- **Scaffold**: `import bisect`, `from collections import deque`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Build a FIFO queue with `deque`, rotate elements, and verify bounded `deque(maxlen=3)` evicts the oldest items automatically.
  2. **Drill 2**: Map numeric scores to letter grades using `bisect.bisect_right([60, 70, 80, 90], score)` and keep a sorted leaderboard with `bisect.insort`.

### `250_heapq_and_priority_queues.py` *(Narrow Primer — ~110–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: In-place min-heaps on plain `list`s (`heapq`), negating keys for max-heaps, and `(priority, tie_breaker, item)` tuples to prevent `TypeError` on equal-priority unorderable tasks.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `heapq.heapify` (O(N)), `heappush`/`heappop` (O(log N)), `heappushpop`/`heapreplace`, `nlargest`/`nsmallest`/`merge`, and `itertools.count()` tie-breakers.
- **Scaffold**: `import heapq`, `from itertools import count`, `#` prose comments, tiny starter heap, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: `heapify(nums)`, push `2`, pop smallest 3 items, and test `nlargest` / `nsmallest`.
  2. **Drill 2**: Build a priority scheduler using `(priority, next(tie_breaker), {"job": name})` with equal-priority dicts so tie-breaking never compares `dict < dict`.

### `255_enum_intenum_and_flag.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Replacing magic strings/ints with `Enum`, `StrEnum`, `IntEnum`, and bitmask `Flag`/`IntFlag`—understanding why pure `Enum` does not equal raw ints (`Color.RED == 1` is `False`), whereas `StrEnum`/`IntEnum`/`IntFlag` interoperate cleanly with JSON and C/bitmask APIs.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `Enum`, `auto()`, `@unique`, `StrEnum` (JSON serialization & string equality), `IntEnum`, `Flag` (`|`, `&`, `^`, `~`, `in`, iterating set bits), and `IntFlag` (bitwise int interop).
- **Scaffold**: `from enum import Enum, Flag, IntEnum, IntFlag, StrEnum, auto, unique`, `import json`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Define `@unique class OrderStatus(StrEnum):` with `auto()`, verify `OrderStatus.PAID == "paid"`, and round-trip it cleanly through `json.dumps`.
  2. **Drill 2**: Contrast pure `Enum` (`!= 1`) with `IntEnum` (`== 1`).
  3. **Drill 3**: Define `Flag` and `IntFlag` permission masks (`Permission.READ | Permission.WRITE`), test `in` and `list(rw)`, and combine `IntFlag` with integer masks.

### `260_itertools_combinatorics_and_streams.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Zero-allocation iterator pipelines (`itertools`), and the classic `groupby` trap: `itertools.groupby` only groups **consecutive identical keys**, so unsorted inputs must be sorted by the same key first and inner group iterators must be consumed before advancing!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `chain.from_iterable`, `islice`, `pairwise`, `batched` (3.12+), `accumulate`, `zip_longest`, `takewhile`, `groupby`, and `product`/`permutations`/`combinations`.
- **Scaffold**: `import itertools`, section functions, `#` prose comments, tiny starter `batched`/`pairwise`, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Build lazy pipelines with `batched`, `pairwise`, `accumulate`, `chain.from_iterable`, `zip_longest`, and `takewhile`.
  2. **Drill 2**: Pre-sort `(category, item)` tuples and group with `itertools.groupby`, contrasting against unsorted input to prove why pre-sorting is required.
  3. **Drill 3**: Generate Cartesian coordinates with `itertools.product` and pairs with `combinations`.

### `265_array_bytearray_and_memoryview.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Unboxed contiguous C arrays (`array.array`) shrink per-element memory from ~36 bytes per boxed `int` down to 4–8 bytes, and `memoryview` gives zero-copy slices and type reinterpretation (`.cast()`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `array.array(typecode, init)`, `sys.getsizeof`, `memoryview` zero-copy slicing (`sub = mv[4:8]`), and `mv.cast("I")` in-place type reinterpretation.
- **Scaffold**: `import array`, `import sys`, section functions, `#` prose comments, tiny starter `array`, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Compare `sys.getsizeof` on a 1,000-element `list[int]` (plus elements) vs. `array.array("i", range(1000))`.
  2. **Drill 2**: Mutate `bytearray` through a `memoryview` slice (`sub[:] = b"1234"`) to prove zero-copy in-place mutation.
  3. **Drill 3**: Cast a 16-byte `bytearray(16)` with `.cast("I")`, write 4 `u32` values, and inspect `buf.hex()`.

### `270_sorting_timsort_and_stability.py` *(Narrow Primer — ~110–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Timsort stability (preserving relative order on equal keys), avoiding `x = items.sort()` (`None` return trap), and sorting lists containing `None` (`None < 5` raises `TypeError` in Python 3).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `list.sort()` (returns `None`) vs. `sorted()`, Timsort stability for multi-pass sorts, and `(x is None, x)` tuple keys for nullable sorting.
- **Scaffold**: `#` prose comments, tiny starter sort check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Show `items.sort()` returns `None` while `sorted(items)` returns a new list, and sort `[42, None, 7, None, 19, 0]` with `None` last via `(x is None, x)`.
  2. **Drill 2**: Sort player records alphabetically by name ascending and by score descending using both a single tuple key and two stable `.sort()` passes.

### `280_mutation_during_iteration_and_defensive_copies.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Mutating a `list` inside `for x in items:` shifts elements left while the internal index advances, **silently skipping elements**, whereas mutating a `dict` or `set` mid-loop raises `RuntimeError` immediately!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `list` silent index-skipping bug (`items.remove(x)`), `dict` / `set` `RuntimeError: ... changed size during iteration`, slice-assignment filtering (`items[:] = [...]`), shallow-copy iteration (`for x in items[:]:`, `for k in list(d):`), and reverse-index deletion.
- **Scaffold**: Section functions, `#` prose comments, tiny starter list/dict copy, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Reproduce the silent list-skip bug on `[2, 4, 5, 6]` (observing `[4, 5]`), then fix in place via `items[:] = [...]`, `for x in items[:]:`, and reverse-index `del`, verifying `id(items)` is preserved.
  2. **Drill 2**: Trigger and catch `RuntimeError` when deleting from a `dict` and a `set` during direct iteration, then fix both using `list(d)` and `list(s)` snapshots.

---

## `300`–`399`: Object-Oriented Python, Data Model (Dunders), Descriptors & Metaclasses

### `300_classes_instances_and_attributes.py` *(Core Primer)*
- **Defining Concept & Friction Point**: How Python's attribute lookup chain works (`instance.__dict__` -> `Class.__dict__` -> base classes) and the **Class Attribute vs. Instance Attribute Trap**: declaring `inventory: list[str] = []` directly in a regular `class` body creates a **single class-level list shared by every instance**, whereas setting `self.inventory = []` inside `__init__` creates a per-instance list!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `class Name:`, `__init__(self, ...)` (must return `None`), `__new__(cls, ...)`, and attribute lookup vs. assignment asymmetry (`vars(obj)` vs. `Class.__dict__`).
- **Scaffold**: Section functions, `#` prose comments, tiny starter class inspection, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Demonstrate the mutable class attribute bug with `BuggyPlayer` (`bag: list[str] = []` at class scope) so `p1.bag.append("gem")` appears in `p2.bag`.
  2. **Drill 2**: Implement fixed `Player` initializing `self.bag: list[str] = []` in `__init__`, and inspect `vars(p1)`, `vars(p2)`, and `Player.__dict__`.

### `310_properties_getters_and_computed_attrs.py` *(Core Primer)*
- **Defining Concept & Friction Point**: `@property` lets you upgrade any public attribute (`temp.celsius`) into a validated/computed getter/setter later with zero breaking changes to callers, while `@functools.cached_property` writes the result into `self.__dict__` on first access.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `@property`, `@attr.setter` / `@attr.deleter` (storing backing state in `self._attr` to avoid `RecursionError`), read-only properties, and `@functools.cached_property`.
- **Scaffold**: `from functools import cached_property`, section functions, `#` prose comments, tiny starter property, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `Temperature` backed by `self._kelvin: float` with validated `@property def kelvin` (rejecting `< 0`) and read/write `@property def celsius`.
  2. **Drill 2**: Add `@cached_property def calibration_table(self) -> list[float]:`, access it twice to verify one-time computation, and test read-only property `AttributeError`.

### `320_classmethods_staticmethods_and_constructors.py` *(Narrow Primer — ~110–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Alternative constructors (`from_json`, `from_milliseconds`) via `@classmethod` receive `cls` (the actual calling subclass) and return `cls(...)`, whereas hardcoding `MyClass(...)` inside a `@staticmethod` breaks inheritance!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `@classmethod`, `typing.Self` (3.11+), and `@staticmethod`.
- **Scaffold**: `from typing import Self`, `#` prose comments, tiny starter class, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Define `Timestamp` with `__init__(self, seconds: float)`, `@classmethod def from_milliseconds(cls, ms: float) -> Self:`, and `@staticmethod def is_valid_epoch(sec: float) -> bool:`.
  2. **Drill 2**: Subclass `HighResTimestamp(Timestamp)` and verify `HighResTimestamp.from_milliseconds(1500)` returns a `HighResTimestamp` instance (contrasting with a broken `@staticmethod` returning `Timestamp`).

### `330_inheritance_super_and_mro.py` *(Core Primer)*
- **Defining Concept & Friction Point**: `super()` does **not** mean "call my parent class"—it means **"call the next class in `type(self).__mro__`"** computed by C3 linearization! Cooperative multiple inheritance requires forwarding `**kwargs` through `super().__init__(**kwargs)` so every mixin in a diamond receives its own arguments exactly once.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `class Sub(Base):`, zero-arg `super()`, `Cls.__mro__` / C3 linearization, and cooperative `super().__init__(**kwargs)` across diamond/mixin hierarchies with distinct init parameters.
- **Scaffold**: Section functions, `#` prose comments, tiny starter MRO print, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Build `Serializer`, `JsonMixin`, `CompressionMixin`, and `CompressedJsonSerializer(CompressionMixin, JsonMixin, Serializer)` where each `process()` calls `super().process(data)` and print `__mro__`.
  2. **Drill 2**: Build a diamond hierarchy (`BaseDevice`, `NetworkMixin(host=...)`, `AuthMixin(token=...)`, `ManagedClient`) using cooperative `super().__init__(**kwargs)` so distinct keyword parameters reach every mixin exactly once.

### `340_dunder_repr_format_and_comparisons.py` *(Core Primer)*
- **Defining Concept & Friction Point**: `__repr__` vs. `__str__`, custom f-string `__format__`, returning `NotImplemented` (not raising `NotImplementedError`) in comparisons, and the rule that defining `__eq__` on a class automatically sets `__hash__ = None` (`TypeError: unhashable type` in `set`/`dict`)!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `__repr__` vs. `__str__`, `__format__(self, format_spec)`, `NotImplemented` singleton, `@functools.total_ordering`, and `__eq__` disabling `__hash__`.
- **Scaffold**: `from functools import total_ordering`, section functions, `#` prose comments, tiny starter `repr`, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `@total_ordering class Version:` (`major, minor, patch`) with `__repr__`, `__str__`, `__format__` (`"short"`), `__eq__`, and `__lt__` returning `NotImplemented` for non-`Version`.
  2. **Drill 2**: Sort `Version` instances, format `f"{v:short}"`, verify `v == "1.2.0"` returns `False`, and prove `Version` cannot be placed in a `set` or `dict` (`TypeError: unhashable type`) because defining `__eq__` set `__hash__ = None` (plus `# Try uncommenting:` experiment).

### `350_dunder_arithmetic_and_containers.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Supporting operator overloading (`v1 + v2`, `3 * v1`, `v1 += v2` where `__iadd__` must return `self` or `v1` becomes `None`!), container indexing (`__len__`, `__getitem__`, `__setitem__`), truthiness (`__bool__` vs. `__len__`), and `__call__`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `__add__`, `__sub__`, `__mul__`, `__rmul__`, `__iadd__` (returning `self` vs. the `return None` trap), `__len__`, `__bool__`, `__getitem__`, `__setitem__`, `__contains__`, `__iter__`, and `__call__`.
- **Scaffold**: Section functions, `#` prose comments, tiny starter vector check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `Vec2` with `__add__`, `__sub__`, `__mul__`, `__rmul__` (so `2.0 * v` works), `__iadd__` (returning `self` and contrasting a broken `return None` example), and `__bool__`.
  2. **Drill 2**: Implement `RingSlice` with `__len__`, `__getitem__`, `__setitem__` (wrapping indices via `% len`), and a callable counter/scaler with `__call__`.

### `360_dataclasses_slots_and_frozen.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Synthesizing boilerplate with `@dataclass(slots=True, frozen=True, order=True, kw_only=True)`, avoiding mutable default errors via `field(default_factory=...)`, hiding/excluding fields with `compare=False` / `repr=False`, and knowing inheritance caveats (`slots=True` subclassing or non-default-after-default field order).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `@dataclass(slots=True, frozen=True, order=True, kw_only=True)`, `field(default_factory=..., compare=False, repr=False)`, `__post_init__` (`object.__setattr__` when frozen), `InitVar`, `replace`, `asdict`, and inheritance caveats.
- **Scaffold**: `from dataclasses import InitVar, asdict, dataclass, field, replace`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Define `@dataclass(slots=True, frozen=True, order=True) class ServerEndpoint:` with `compare=False` metadata, `kw_only=True` option, and `__post_init__` port validation.
  2. **Drill 2**: Define mutable `@dataclass(slots=True) class JobQueue:` with `field(default_factory=list)` and `secret_token: str = field(repr=False, compare=False)`, plus demonstrate `dataclasses.replace`, `set` hashing, and dataclass inheritance caveats.

### `370_slots_and_object_memory_layout.py` *(Narrow Primer — ~110–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Standard instances carry a per-instance `__dict__` hash table (~104+ bytes overhead). `__slots__ = ("x", "y")` replaces `__dict__` with fixed C struct offsets, saving memory and raising `AttributeError` on typos—unless a subclass forgets `__slots__ = ()`!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `__slots__`, typo protection (`AttributeError`), subclass `__slots__ = ()` inheritance gotcha, and `"__weakref__"`.
- **Scaffold**: `import sys`, `#` prose comments, tiny starter size check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Define `DictParticle` and `SlottedParticle` (`__slots__ = ("x", "y", "vx", "vy")`) and compare `sys.getsizeof(p) + sys.getsizeof(p.__dict__)` vs. `sys.getsizeof(sp)`.
  2. **Drill 2**: Verify `hasattr(sp, "__dict__")` is `False`, test typo protection (`sp.mass = 1.0` -> `AttributeError`), and contrast a subclass with vs. without `__slots__ = ()`.

### `380_abstract_base_classes_and_protocols.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Nominal subtyping (`abc.ABC` + `@abstractmethod`, checked at instantiation) vs. structural duck typing (`typing.Protocol`, `@runtime_checkable`, checked without inheritance).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `abc.ABC`, `@abstractmethod`, `typing.Protocol`, and `@runtime_checkable`.
- **Scaffold**: `from abc import ABC, abstractmethod`, `from typing import Protocol, runtime_checkable`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `StorageBackend(ABC)` (`load`, `save` specified in `#` **Drill** or clean concrete `MemoryStorage(StorageBackend)`) and include `# Try uncommenting: StorageBackend()`.
  2. **Drill 2**: Define `@runtime_checkable class Renderable(Protocol)` and pass an unrelated `Banner` class (not inheriting `Renderable`) to `draw_item(item: Renderable)`, verifying `isinstance(Banner(), Renderable)`.

### `385_descriptor_protocol_deep_dive.py` *(Core Primer)*
- **Defining Concept & Friction Point**: The Descriptor Protocol (`__set_name__`, `__get__`, `__set__`) powers `@property`, methods, and `__slots__`. Lookup precedence is **Data Descriptor > `instance.__dict__` > Non-Data Descriptor**, and storing state on `self` inside a descriptor shares it across every instance!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `__set_name__`, `__get__(self, instance, owner)`, `__set__(self, instance, value)`, data vs. non-data descriptors, and per-instance storage (`setattr(instance, self.private_name, ...)`).
- **Scaffold**: `from typing import Any`, section functions, `#` prose comments, tiny starter lookup note, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `BoundedFloat(min_val, max_val)` with `__set_name__`, `__get__`, and `__set__`, and attach it to `SensorReading` (`voltage`, `temp_c`).
  2. **Drill 2**: Test valid/invalid assignments across two independent `SensorReading` instances (proving zero cross-instance leakage) and contrast a non-data descriptor (`__get__` only) overridden by `instance.__dict__`.

### `390_getattr_getattribute_and_proxies.py` *(Core Primer)*
- **Defining Concept & Friction Point**: `__getattr__` runs **only** as a fallback on missing attributes (and must raise `AttributeError`, never `KeyError`, so `hasattr()` works), whereas `__getattribute__` intercepts **every** attribute read and triggers `RecursionError` unless you delegate via `super().__getattribute__(name)`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `__getattr__`, `__getattribute__` + `super().__getattribute__`, and `__setattr__` + `super().__setattr__`.
- **Scaffold**: `from typing import Any`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `LazyConfigProxy` wrapping a `dict[str, Any]` via `__getattr__` (raising `AttributeError` on missing keys so `getattr(proxy, "missing", "default")` works) and blocking writes via `__setattr__`.
  2. **Drill 2**: Implement an access-auditing wrapper using `__getattribute__` and `super().__getattribute__`.

### `395_init_subclass_and_metaclasses.py` *(Core Primer)*
- **Defining Concept & Friction Point**: 95% of class customization (plugin auto-registration, enforcing subclass invariants, class kwargs) needs only 5 lines with `__init_subclass__`; reserve custom metaclasses (`class Meta(type):`) for altering namespaces via `__prepare__` or replacing class construction in `__new__`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `__init_subclass__(cls, **kwargs)` (PEP 487), 3-argument `type(name, bases, namespace)`, and `class Meta(type):` (`__new__`, `__prepare__`).
- **Scaffold**: `from typing import Any`, section functions, `#` prose comments, tiny starter `type(...)` check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `CommandPlugin` with `REGISTRY: dict[str, type[CommandPlugin]] = {}` and `__init_subclass__`, define `PingPlugin` and `StatusPlugin`, and verify `REGISTRY` populates at class-definition time.
  2. **Drill 2**: Implement `EnforceSnakeCaseMeta(type)` rejecting uppercase public method names in `__new__` (plus `# Try uncommenting:` bad method test).

---

## `400`–`499`: Modules, Packages, Imports, Packaging & Project Architecture

### `400_modules_import_system_and_sys_path/` *(Multi-File Lab)*
- **Files**: `main.py`, `sibling_helper.py`, `geometry/__init__.py`, `geometry/shapes.py`, `geometry/transforms.py`
- **Defining Concept & Friction Point**: Every `.py` file is an isolated module (unlike Odin/Go single-package folders), cached as a singleton in `sys.modules`. `from pkg.mod import value` binds a local reference at import time, whereas `import pkg.mod` reads live updates. Relative imports (`from .shapes import Circle`) require package context (`python -m`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `import`, `from ... import ...`, relative imports, `__init__.py`, `sys.modules`, and `sys.path`.
- **Scaffold**: `#` prose comments, minimal 1–2 anchor constants/exports in `geometry/__init__.py` & `sibling_helper.py`, bottom `def main() -> None:` in `main.py` (zero `pass`/dummy stubs).
- **Ordered Outline**:
  1. In `sibling_helper.py`: **Drill** to define `MODULE_VERSION = "1.0.0"` and `format_banner(title: str) -> str`.
  2. In `geometry/shapes.py`: **Drill** to define `@dataclass(slots=True, frozen=True) class Circle:` and `circle_area(c: Circle) -> float`.
  3. In `geometry/transforms.py`: **Drill** to use `from .shapes import Circle` and define `scale_circle(c: Circle, factor: float) -> Circle`.
  4. In `geometry/__init__.py`: **Drill** to re-export public symbols and define `__all__`.
  5. In `main.py`: **Drill** to exercise `sibling_helper` and `geometry`, and verify `sys.modules["geometry.shapes"] is geometry.shapes`.

### `410_visibility_all_and_circular_imports/` *(Multi-File Lab)*
- **Files**: `main.py`, `vault/__init__.py`, `vault/public_api.py`, `vault/_internal.py`, `vault/models.py`
- **Defining Concept & Friction Point**: `_private` convention, `__mangled` class attributes (`_ClassName__attr`), `__all__`, and breaking **Circular Imports** (`from __future__ import annotations` + `if TYPE_CHECKING:`, leaf `models.py` extraction, or local imports).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `_name`, `__name` mangling, `__all__`, `TYPE_CHECKING`, and circular import resolution.
- **Scaffold**: `#` prose comments, minimal 1–2 anchor exports in `vault/__init__.py`, bottom `def main() -> None:` in `main.py` (zero `pass`/dummy stubs).
- **Ordered Outline**:
  1. In `vault/_internal.py`: **Drill** to define `_SECRET_SALT = 0x9E3779B9` and `_hash_pin(pin: int) -> int`.
  2. In `vault/models.py` & `vault/public_api.py`: **Drill** to resolve a bidirectional type reference cleanly via `from __future__ import annotations` and `if TYPE_CHECKING:`, and define `__all__` in `vault/__init__.py`.
  3. In `main.py`: **Drill** to exercise `vault.verify_pin(1234)`, inspect `vault.__all__`, and inspect `_VaultAccount__master_key` mangling.

### `420_dynamic_imports_and_importlib.py` *(Core Primer — scoped 1-line `__doc__` target)*
- **Defining Concept & Friction Point**: Loading modules/plugins dynamically at runtime (`importlib`), reading bundled package data cleanly without fragile relative file paths (`importlib.resources`), and inspecting distribution metadata (`importlib.metadata`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `importlib.import_module(name, package=None)` (vs. `__import__`), `importlib.util.find_spec`, `spec_from_file_location` / `module_from_spec` / `exec_module` (with scoped 1-line `__doc__` inspection target in the temporary plugin), `importlib.reload`, `importlib.metadata` (`version`, `entry_points`), and `importlib.resources` (`files("package").joinpath(...).read_text(encoding="utf-8")` / reading bundled package data cleanly without `__file__` hacks).
- **Scaffold**: `import importlib`, `import importlib.metadata`, `import importlib.resources`, `import importlib.util`, `from pathlib import Path`, `import sys`, `import tempfile`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Dynamically import `"math"` and `"statistics"` via `importlib.import_module`, invoke functions via `getattr`, and probe modules without importing using `importlib.util.find_spec`.
  2. **Drill 2**: Load a standalone plugin `.py` file (carrying a 1-line `"""..."""` docstring) from a `TemporaryDirectory` via `spec_from_file_location`, inspect `plugin_mod.__doc__` and invoke its hook, and test `importlib.reload`.
  3. **Drill 3**: Create a tiny temporary package containing a data file (`data/banner.txt`) on `sys.path`, read it cleanly using `importlib.resources.files(pkg).joinpath("data/banner.txt").read_text(encoding="utf-8")`, and query `importlib.metadata` safely.

### `430_pyproject_toml_and_venv_packaging.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Modern PEP 517/621 `pyproject.toml`, `venv` isolation (`sys.prefix != sys.base_prefix`), and why the `src/` layout prevents tests from accidentally importing the un-installed local folder. *(Guardrail: skip PEP-508 environment marker minutiae.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `venv` detection (`sys.prefix != sys.base_prefix`), `src/` vs. flat layout, `[build-system]`, `[project]`, `[project.scripts]`, and `tomllib.loads()`.
- **Scaffold**: `import sys`, `import tomllib`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Check `in_venv = sys.prefix != sys.base_prefix` and inspect `sys.prefix`, `sys.base_prefix`, and `sys.executable`.
  2. **Drill 2**: Parse a sample PEP 621 `pyproject.toml` string with `tomllib.loads` and extract `name`, `requires-python`, and `[project.scripts]`.

### `440_config_env_vars_and_dotenv_patterns.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Environment variables are always `str` (`bool("false") == True` trap!), required settings must fail loudly with a clear `ConfigError`, and secret values (`api_key`, `token`) must be masked in `__repr__` so logs never leak credentials!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `os.environ` / `os.getenv`, `parse_env_bool`, zero-dependency `.env` parsing, required-setting validation (`ConfigError`), and secret masking (`field(repr=False)` or custom `__repr__`) on a frozen `AppConfig` dataclass.
- **Scaffold**: `from dataclasses import dataclass, field`, `import os`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `parse_env_bool(raw: str | None, default: bool = False) -> bool` and `parse_dotenv_lines(content: str) -> dict[str, str]`.
  2. **Drill 2**: Define `ConfigError(Exception)` and `@dataclass(slots=True, frozen=True) class AppConfig:` with a `@classmethod def from_env(...)` that raises `ConfigError` when required keys like `API_KEY` are missing and masks `api_key` in `__repr__` / logs (`"***"`).

### `450_warnings_deprecation_and_future_flags.py` *(Narrow Primer — ~100–130 lines, 5–7 Drills)*
- **Defining Concept & Friction Point**: Evolving APIs with `warnings.warn(..., DeprecationWarning, stacklevel=2)` so warnings point to the caller's line, `warnings.catch_warnings(record=True)`, and `from __future__ import annotations`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `from __future__ import annotations`, `warnings.warn(..., stacklevel=2)`, `warnings.catch_warnings(record=True)`, and `warnings.simplefilter`.
- **Scaffold**: `from __future__ import annotations`, `import warnings`, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Write deprecated `legacy_connect` emitting `DeprecationWarning` with `stacklevel=2`.
  2. **Drill 2**: Capture the warning with `catch_warnings(record=True)` + `simplefilter("always")` and verify `recorded[0].lineno` points at the caller line in `main()`.

### `460_code_quality_typecheck_and_linter_hygiene.py` *(Narrow Primer — ~100–130 lines, 5–7 Drills)*
- **Defining Concept & Friction Point**: Compile-time exhaustiveness checking across `Enum` / Union branches using `typing.assert_never`, `typing.assert_type`, and clean static hygiene.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `typing.assert_never`, `typing.Never`, and `typing.assert_type`.
- **Scaffold**: `from enum import Enum, auto`, `from typing import Never, assert_never, assert_type`, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Define `TrafficLight(Enum)` and `next_light(light: TrafficLight) -> TrafficLight` with `case _ as unreachable: assert_never(unreachable)`.
  2. **Drill 2**: Use `assert_type` on inferred values and test `next_light`.

### `470_doctest_and_executable_documentation.py` *(Narrow Primer — ~100–130 lines, 5–7 Drills; scoped `>>>` doctest exception)*
- **Defining Concept & Friction Point**: Keeping docstring examples verifiable with `doctest.testmod()` (`python -m doctest -v 470_doctest_and_executable_documentation.py`). *(Scoped exception: move module prose to `#` comments; keep `"""..."""` strictly on target functions carrying `>>>` doctests such as `slugify` and `make_marker`.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `doctest.testmod()`, `doctest.ELLIPSIS`, `<BLANKLINE>`, and `Traceback (most recent call last):` exception doctests.
- **Scaffold**: `import doctest`, `#` prose comments, tiny starter target, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `slugify(title: str) -> str` and `make_marker(label: str) -> str` with `>>>` docstring examples covering normal calls, blank lines / ellipsis, and `ValueError` tracebacks.
  2. **Drill 2**: Run `results = doctest.testmod()` in `main()`, print counts, and assert `results.failed == 0`.

### `480_zipapp_and_single_file_bundles.py` *(Narrow Primer — ~100–130 lines, 5–7 Drills)*
- **Defining Concept & Friction Point**: Bundling multi-module Python packages into a single executable `.pyz` archive with `zipapp.create_archive()`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `zipapp.create_archive`, `zipapp.get_interpreter`, and `zipfile.ZipFile` inspection.
- **Scaffold**: `from pathlib import Path`, `import tempfile`, `import zipapp`, `import zipfile`, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Inside `TemporaryDirectory()`, create `helper.py` and `__main__.py`, bundle into `app.pyz` with `zipapp.create_archive`, and inspect entries via `zipfile.ZipFile` (and execute or verify entry point).

---

## `500`–`599`: Memory Management, Refcounting, GC, Profiling, Bytecode & Performance

### `500_refcounting_and_garbage_collection.py` *(Core Primer)*
- **Defining Concept & Friction Point**: CPython uses **two** memory management mechanisms simultaneously: (1) **Reference Counting** (`ob_refcnt`), freeing objects immediately when refcount hits `0`; and (2) a **Generational Cyclic Garbage Collector** (`gc` module), which breaks isolated reference cycles (`a.peer = b; b.peer = a`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `sys.getrefcount(obj)` (always >= +1 for call argument), reference cycles, `gc.collect(generation=2)`, `gc.get_threshold()`, `gc.get_count()`, and `gc.disable()` / `gc.enable()`.
- **Scaffold**: `import gc`, `import sys`, `import weakref`, section functions, `#` prose comments, tiny starter refcount check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Track `sys.getrefcount` as references are added/removed in a list, and verify `weakref.ref` dies immediately when the last strong reference vanishes (without `gc.collect()`).
  2. **Drill 2**: Create cyclic `CycleNode` objects, call `gc.disable()`, delete `n1` and `n2`, verify weak references stay alive, then run `gc.collect()` (and `gc.enable()`) to reclaim them.

### `510_weakref_and_caches_without_leaks.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Strong-reference caches and parent-child back-pointers keep objects alive forever; `weakref.ref`, `WeakValueDictionary`, `WeakKeyDictionary`, and `weakref.finalize` break cycles and prune caches automatically without leaking.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `weakref.ref(obj)`, `WeakValueDictionary`, `WeakKeyDictionary`, parent-child cycle breaking with `weakref.ref(parent)`, and `weakref.finalize` (never pass `obj` inside `*args`!).
- **Scaffold**: `import gc`, `import weakref`, section functions, `#` prose comments, tiny starter weakref check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Build a `WeakValueDictionary` cache and watch keys disappear automatically as strong local references are deleted.
  2. **Drill 2**: Break a parent-child cycle using `self.parent = weakref.ref(parent)` so deleting the parent frees both immediately without relying on cyclic GC, and attach `weakref.finalize` cleanup.

### `520_tracemalloc_and_memory_leak_hunting.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Using `tracemalloc` (Python's equivalent of Odin's `mem.Tracking_Allocator`) to measure `(current_bytes, peak_bytes)` and diff snapshots (`compare_to(..., "lineno")`) before and after fixing a leak.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `tracemalloc.start()` / `stop()`, `get_traced_memory()`, `reset_peak()`, `take_snapshot()`, and `snap2.compare_to(snap1, "lineno")` for before/after leak-fix verification.
- **Scaffold**: `import tracemalloc`, section functions, `#` prose comments, tiny starter trace check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Take `snap_before` and `snap_after` around a leaking cache helper, inspect `get_traced_memory()`, and print the top `compare_to(snap_before, "lineno")` offenders.
  2. **Drill 2**: Fix the unbounded cache leak (bounded/weak cache), take a new snapshot diff, and verify retained bytes drop back near `0`.

### `530_string_and_bytes_concatenation_perf.py` *(Narrow Primer — ~100–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Repeatedly appending immutable `str` or `bytes` via `+=` can degrade to O(N^2) copying (especially for `bytes +=` or aliased `str`); use `"".join()`, `b"".join()`, `io.StringIO`/`BytesIO`, or `bytearray.extend()`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `"".join(parts)`, `b"".join(parts)`, `io.StringIO`, `io.BytesIO`, `bytearray.extend()`, and `bytes +=` vs. `bytearray`/`BytesIO` allocation contrast (verified via `tracemalloc` or `time.perf_counter_ns`).
- **Scaffold**: `import io`, `import tracemalloc`, `#` prose comments, tiny starter join, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Build a multi-line CSV report via `"\n".join(parts)` and `io.StringIO`.
  2. **Drill 2**: Contrast `bytes += chunk` against `bytearray` + `.extend()` / `io.BytesIO` using `tracemalloc` or timing to observe O(N) vs. O(N^2) allocation behavior.

### `540_object_interning_and_flyweight_pools.py` *(Narrow Primer — ~100–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: `sys.intern(s)` deduplicates repeated dynamic strings to one canonical instance (turning O(K) comparisons into O(1) pointer checks), and `__new__` + `WeakValueDictionary` implements memory-safe flyweight pools.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `sys.intern(s)`, compile-time vs. runtime interning, and flyweight `__new__` + `WeakValueDictionary`.
- **Scaffold**: `import sys`, `import weakref`, `#` prose comments, tiny starter intern check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Build two dynamic strings `"".join(...)` (`s1 is s2` is `False`), intern both with `sys.intern()`, and verify `s1 is s2` is `True`.
  2. **Drill 2**: Implement `InternedSymbol` (`__slots__ = ("name", "__weakref__")`) returning existing instances from `__new__`.

### `550_timing_and_benchmarking_timeit.py` *(Narrow Primer — ~100–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Never use `time.time()` for elapsed durations (it jumps with NTP); use `time.perf_counter_ns()` for benchmarks, `time.monotonic()` for timeouts, `time.process_time()` for CPU-only time, and `min(timeit.repeat(...))`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `time.perf_counter_ns()`, `time.monotonic()`, `time.process_time()`, and `timeit.Timer(...).repeat(...)` (`min` vs. mean).
- **Scaffold**: `import time`, `import timeit`, `#` prose comments, tiny starter `perf_counter_ns`, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Contrast `perf_counter` vs. `process_time` across a `time.sleep(0.01)` call.
  2. **Drill 2**: Use `timeit.repeat` (small `number=1000, repeat=3`) to compare membership lookup in a 100-item `list` vs. `set`.

### `560_profiling_with_cprofile_and_pstats.py` *(Narrow Primer — ~100–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Deterministic call-graph profiling with `cProfile` + `pstats`, separating `tottime` (self time inside the function) from `cumtime` (inclusive time with callees) and inspecting call relationships with `.print_callers()` / `.print_callees()`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `cProfile.Profile()`, `pstats.Stats(pr, stream=buf)`, `SortKey.TIME` / `SortKey.CUMULATIVE`, `.print_stats()`, `.print_callers()`, and `.print_callees()`.
- **Scaffold**: `import cProfile`, `import io`, `import pstats`, `#` prose comments, tiny starter profile, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Profile a multi-function workload inside `with cProfile.Profile() as pr:`, print top functions sorted by `SortKey.TIME` and `SortKey.CUMULATIVE` into `io.StringIO`.
  2. **Drill 2**: Inspect caller/callee attribution using `stats.print_callers(...)` and `stats.print_callees(...)`.

### `565_profiling_with_tracy_zones_and_frames.py` *(Primer — Slimmed Python Stdlib Wrapper Linking to `../tracy_how_to/`)*
- **Defining Concept & Friction Point**: Building a lightweight pure-Python stdlib zone/frame/plot timing wrapper (`time.perf_counter_ns()` + optional `ctypes` hook) to spot single-frame latency spikes that `cProfile` averages away—and keeping loops wrapped from the *outside* so instrumentation does not dominate runtime. *(Cross-repo boundary: keep `565` focused on a clean Python stdlib zone/frame/plot wrapper; link to `../tracy_how_to/150_python_tracy_ctypes_api_and_zero_cost_gates.py`, `250_python_frame_marks_and_scoped_zones.py`, and `550_python_plots_messages_and_frame_budgets.py` for `TracySourceLocationData` `ctypes` pinning, recursive zone `self_ns` accounting, and Chrome `"ph": "C"` / `"ph": "i"` flight-recorder schemas.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - Lightweight `ZoneTimer` context manager / decorator, `frame_mark()`, `plot()` scalar series, and coarse outer-loop instrumentation.
- **Scaffold**: `from collections.abc import Callable, Iterator`, `from contextlib import contextmanager`, `from dataclasses import dataclass`, `import time`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement a compact stdlib `FrameZoneRecorder` (`zone(name)`, `frame_mark()`, `plot(series, val)`) tracking per-frame durations and zone totals.
  2. **Drill 2**: Simulate 4 frames with a 10x batch spike on Frame #3, print the per-frame table highlighting the spike, and note how `../tracy_how_to/` extends this to native `TracyClient.dll` `Srcloc` pinning and Chrome Trace export.

### `568_tracy_memory_and_gil_thread_profiling.py` *(Primer — Slimmed Python Stdlib Wrapper Linking to `../tracy_how_to/`)*
- **Defining Concept & Friction Point**: Correlating per-zone `tracemalloc` heap deltas with `threading.Lock` wait vs. hold timing using pure stdlib Python (`tracemalloc`, `threading.get_native_id()`). *(Cross-repo boundary: keep `568` focused on stdlib `tracemalloc` zone wrappers and `TracyMonitoredLock`; link to `../tracy_how_to/350_python_tracy_memory_and_object_churn.py` and `450_python_threads_gil_and_asyncio_traces.py` for Gen-0 GC churn forensics, GIL vs. native-release isolation, and `asyncio` blocking freezes.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `tracemalloc.get_traced_memory()` + `reset_peak()` inside `@contextmanager def mem_zone(...)`, `threading.get_native_id()`, and `MonitoredLock` (`wait_ns` vs. `hold_ns`).
- **Scaffold**: `from array import array`, `from collections.abc import Iterator`, `from contextlib import contextmanager`, `import sys`, `import threading`, `import time`, `import tracemalloc`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `mem_zone` measuring retained and peak spike bytes, comparing an in-place `array("d")` loop against boxed dict churn.
  2. **Drill 2**: Implement `MonitoredLock` recording `wait_ns` / `hold_ns` per `threading.get_native_id()` across 3 worker threads, linking to `../tracy_how_to/450` for full GIL and `asyncio` timeline traces.

### `570_bytecode_disassembly_with_dis.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Peeking into the CPython stack-machine VM using `dis`: comparing `LOAD_FAST` (indexed local array) vs. `LOAD_GLOBAL` (dict lookup) and observing Python 3.11+ adaptive specialization (`BINARY_OP_ADD_INT`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `dis.Bytecode(fn, adaptive=True)`, `dis.dis(fn)`, `fn.__code__` (`co_varnames`, `co_consts`, `co_names`, `co_stacksize`), and `LOAD_FAST` vs. `LOAD_GLOBAL`.
- **Scaffold**: `import dis`, section functions, `#` prose comments, tiny starter bytecode inspection, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Inspect `dis.Bytecode(compute_poly)` alongside `co_varnames`, `co_consts`, and `co_names`.
  2. **Drill 2**: Compare bytecode for global `math.sin` lookup inside a loop vs. local hoisted `sin = math.sin` (`LOAD_GLOBAL` vs. `LOAD_FAST`), and inspect adaptive specialization after warmup calls.

### `575_interpreter_waste_and_bytecode_cost.py` *(Core Primer — Computer, Enhance! Multiplier #1: Waste)*
- **Defining Concept & Friction Point**: Tracing why `a += b` inside a Python loop executes 50–150+ CPU instructions instead of one hardware `ADD`: opcode dispatch, adaptive type guards, immutable 28-byte `PyLongObject` heap allocation, and `Py_INCREF`/`Py_DECREF` traffic—and pushing hot inner loops into C-backed bulk stdlib primitives. *(Keep prose focused on CPython eval-loop and boxing mechanics without pasting redundant 4-bullet Five-Multipliers summaries.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `dis.Bytecode(fn, adaptive=True)` opcode count per iteration, `sys.getsizeof(1)` (`28` bytes) / `sys.getsizeof(1.0)` (`24` bytes), and bulk C-loop replacements (`sum()`, `itertools.accumulate`, `array`).
- **Scaffold**: `import dis`, `import sys`, `import time`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Measure `PyLongObject` / `PyFloatObject` object sizes and count adaptive loop-body bytecodes executed for `add_loop_python(values)` over `10_000` integers.
  2. **Drill 2**: Benchmark `add_loop_python(values)` vs. C-loop `sum(values)` with `min` over 5 runs (`time.perf_counter_ns()`).

### `580_buffer_protocol_and_mmap.py` *(Narrow Primer — ~100–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Mapping files or anonymous OS virtual memory pages with `mmap.mmap` and overlaying zero-copy `memoryview` slices without reading entire files into RAM.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `mmap.mmap(fileno, length, access=...)`, `ACCESS_WRITE` / `ACCESS_READ` / `ACCESS_COPY`, `mm.find()`, and `memoryview(mm)`.
- **Scaffold**: `import mmap`, `from pathlib import Path`, `import tempfile`, `#` prose comments, tiny starter `mmap`, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Map a temp binary file with `mmap.mmap`, locate a byte pattern via `mm.find(...)`, overwrite via `memoryview(mm)`, flush, and verify disk contents.
  2. **Drill 2**: Demonstrate copy-on-write `ACCESS_COPY` edits staying invisible on disk.

### `585_cache_locality_ipc_and_simd_in_python.py` *(Core Primer — Cache Density & Pointer-Chasing)*
- **Defining Concept & Friction Point**: Why `list[float]` scatters 24-byte `PyFloatObject` allocations across RAM (chasing pointers across cache lines), whereas `array.array("d")` / `memoryview` packs 8 raw 8-byte doubles into every single 64-byte CPU cache line—and why pure-Python loops prevent C-level vectorization. *(Keep prose focused on `list[float]` pointer-chasing vs. `array("d")` cache density, avoiding boilerplate multi-bullet taxonomy dumps.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `list[float]` total memory (`sys.getsizeof(lst) + sum(...)`) vs. contiguous `array("d")` (`arr.buffer_info()`, `itemsize`), 64-byte cache-line packing, and AoS vs. SoA column layout.
- **Scaffold**: `from array import array`, `import sys`, `import time`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Compare total memory bytes and cache-line count (`(4096 * 8) // 64`) of a 4,096-element `list[float]` vs. `array("d")`, inspecting contiguous addresses via `arr.buffer_info()`.
  2. **Drill 2**: Compare AoS `list[tuple[...]]` vs. SoA `array("d")` columns and benchmark C-backed `sum(arr)` / `memoryview` slicing.

### `590_arena_and_object_pool_patterns.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Replacing per-frame `PyObject` heap churn with reusable `__slots__` object pools and flat Structure-of-Arrays (`array("f")`) tables indexed by generational handles `(index, generation)` (paralleling `odin_how_to/490_pool_and_handle_allocations.odin`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - Object pool (`acquire` / `release`), `ParticleSoAPool` (`array("f")` parallel columns + free-list + `generations`), and stale-handle rejection.
- **Scaffold**: `from array import array`, `from typing import NamedTuple`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `ParticleSoAPool` (`spawn`, `despawn`, `is_alive`, `generations` check) over contiguous `array("f")` columns.
  2. **Drill 2**: Spawn `"Goblin"`, despawn it, spawn `"Dragon"` (reusing slot 0), and verify the stale `"Goblin"` handle is rejected.

### `592_hotspot_optimization_workflow.py` *(Core Primer — Amdahl Haversine Workflow)*
- **Defining Concept & Friction Point**: Never optimize blindly or optimize cold code: profile first to isolate the >90% hotspot, verify Amdahl's Law (`1 / ((1 - p) + p / s)`), and optimize *only* the hotspot while verifying checksum parity.
- **Keywords, Built-ins & Concepts Breakdown**:
  - Amdahl's Law, lightweight `@contextmanager def profile_zone(name, timings)`, hoisting `math.sin`/`cos`/`sqrt`/`asin` (`LOAD_FAST`), and contiguous `array("d")` inputs.
- **Scaffold**: `from array import array`, `from contextlib import contextmanager`, `import math`, `import time`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `profile_zone` and instrument a 3-stage pipeline (`load_config`, `compute_haversine_hotspot`, `format_summary`) proving >90% time sits in `compute_haversine_hotspot`.
  2. **Drill 2**: Optimize *only* `compute_haversine_hotspot` (hoisted locals + `array("d")`), assert checksum match within `1e-9`, and print before/after speedup vs. Amdahl prediction (linking to `../tracy_how_to/` for deep trace forensics).

### `595_memory_profiled_pipeline_lab/` *(Multi-File Lab)*
- **Files**: `main.py`, `pool.py`, `processor.py`
- **Defining Concept & Friction Point**: Combining `tracemalloc`, `__slots__`, `WeakValueDictionary` / object pooling (`pool.py`), and generator streaming (`processor.py`) so processing 1,000+ events runs in bounded O(1) scratch memory with zero leaks.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `__slots__`, `PacketPool` (`acquire`/`release`), `try ... finally:` buffer return in generators, and `tracemalloc.get_traced_memory()`.
- **Scaffold**: `#` prose comments, domain dataclasses/contracts (`PacketBuffer` slots), bottom `main()` (zero `pass`/dummy stubs).
- **Ordered Outline**:
  1. In `pool.py`: **Drill** to implement `PacketBuffer` and `PacketPool` (`acquire`, `release`, `in_use_count`, `free_count`).
  2. In `processor.py`: **Drill** to implement `process_packets(raw_chunks, pool)` borrowing and returning buffers inside `try ... finally:`.
  3. In `main.py`: **Drill** to run 1,000 chunks under `tracemalloc.start()`, assert `pool.in_use_count == 0`, and report peak bytes.

### `598_tracy_hotspot_profiler_lab/` *(Multi-File Lab — Slimmed Stdlib Profiler Linking to `../tracy_how_to/950_python_hotspot_hunt_five_multipliers_lab/`)*
- **Files**: `main.py`, `tracy_prof.py`, `workload.py`
- **Defining Concept & Friction Point**: Building a lightweight stdlib zone & `tracemalloc` profiler (`tracy_prof.py`) and applying it to a 4-stage pipeline (`workload.py`) to isolate the >90% transform hotspot and optimize *only* that function while leaving cold stages untouched. *(Cross-repo boundary: keep `598` focused on stdlib `ZoneStats` + `tracemalloc` hotspot isolation over one pipeline; link to `../tracy_how_to/950_python_hotspot_hunt_five_multipliers_lab/` for the full 5-system cold-herring Hotspot Hunt capstone and Chrome Trace JSON telemetry.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - Nested zone stack (`self_ns = total_ns - child_ns`), `tracemalloc` byte deltas, and before/after checksum parity.
- **Scaffold**: `#` prose comments, `ZoneStats` dataclass + `generate_sensor_batch` data setup **Scaffold**, bottom `main()` (zero `pass`/dummy stubs).
- **Ordered Outline**:
  1. In `tracy_prof.py`: **Drill** to implement `TracySession` (`zone(name)` tracking `self_ns` and `tracemalloc` deltas, plus `format_hotspot_table()`).
  2. In `workload.py`: **Drill** to instrument the cold stages and implement naive `transform_records_hotspot` vs. `array("d")` / hoisted `transform_records_optimized`.
  3. In `main.py`: **Drill** to run baseline vs. hotspot-only optimized passes, assert `abs(opt_checksum - base_checksum) < 1e-9`, and print the before/after report.

---

## `600`–`699`: Standard Library Essentials: Files, Serialization, Regex, SQLite & CLI

*(Note: Heavy-expand `600`–`620` and `640`–`680` to `~160–250` lines / `8–12` Drills; keep `630`, `690`, `695` focused at `~110–140` lines / `6–8` Drills.)*

### `600_pathlib_and_filesystem_ops.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Object-oriented filesystem paths with `pathlib.Path`, explicit `encoding="utf-8"`, and atomic writes (`temp.replace(target)`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `Path` `/` joining, `.parent`/`.parents`/`.name`/`.stem`/`.suffix`/`.suffixes`, `.with_name()`/`.with_stem()`/`.with_suffix()`, `.iterdir()`, `.glob()` vs. `.rglob()`, `.read_text(encoding="utf-8")` / `.write_text()`, `.read_bytes()` / `.write_bytes()`, `.replace()`, `.unlink(missing_ok=True)`, and `tempfile.TemporaryDirectory()`.
- **Scaffold**: `from pathlib import Path`, `import tempfile`, section functions, `#` prose comments, tiny starter path check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Inspect `Path(__file__).resolve()` properties (`.parent`, `.name`, `.stem`, `.suffix`, `.with_name()`, `.with_stem()`).
  2. **Drill 2**: Inside `TemporaryDirectory()`, create nested folders with `.mkdir(parents=True, exist_ok=True)`, write/read both UTF-8 text and binary `.read_bytes()`/`.write_bytes()`, and perform an atomic `.tmp` -> `.replace()` update.
  3. **Drill 3**: Compare `.iterdir()`, `.glob("*.txt")` (shallow), and `.rglob("*.txt")` (recursive).

### `610_io_streams_buffering_and_encodings.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Python's 3-layer I/O stack, why omitting `encoding="utf-8"` on Windows falls back to `cp1252` and crashes on Unicode, why `newline=""` prevents `\r\n` corruption, and zero-allocation binary streaming with `readinto(bytearray)`. *(Guardrail: skip `buffering=0/1` quirks.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `Path.open(..., encoding="utf-8", newline="")`, `"x"` exclusive create (`FileExistsError`), `errors="strict"` / `"replace"` / `"ignore"`, `readinto(bytearray)` + `memoryview`, and `io.StringIO` / `io.BytesIO`.
- **Scaffold**: `import io`, `from pathlib import Path`, `import tempfile`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Write and read real disk files via `Path.open(..., encoding="utf-8", newline="")` inside `TemporaryDirectory()`, test `"x"` exclusive-create catching `FileExistsError`, and verify `\n` preservation.
  2. **Drill 2**: Stream `io.BytesIO(b"0123456789ABCDEF")` in 4-byte chunks into a single reusable `bytearray(4)` using `readinto` + `memoryview[:n]`.
  3. **Drill 3**: Decode malformed bytes `b"Hello \xff World"` with `errors="replace"` vs. `errors="strict"`.

### `620_json_csv_and_tomllib.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Serialization traps in `json`, `csv`, and `tomllib`: (1) `json` silently coerces int dict keys `{1: (2, 3)}` into `{"1": [2, 3]}`; (2) `json.dumps` needs `default=` and `json.loads` uses `object_hook=` for custom types; (3) CSV files on Windows need `newline=""`; and (4) `tomllib.load(fp)` requires binary `"rb"` mode!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `json.dumps(..., default=..., indent=2, sort_keys=True)`, `json.loads(..., object_hook=...)`, `{1: (2, 3)}` round-trip coercion, `csv.DictReader` / `csv.DictWriter` (`newline=""`), `tomllib.loads(s)`, and `tomllib.load(binary_fp)` (`"rb"` mode).
- **Scaffold**: `import csv`, `from dataclasses import asdict, dataclass`, `import io`, `import json`, `from pathlib import Path`, `import tempfile`, `import tomllib`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Verify the `{1: (2, 3)}` JSON round-trip coercion (`{"1": [2, 3]}`), then serialize a `@dataclass` with `default=asdict` and reconstruct rich objects cleanly using `json.loads(..., object_hook=...)`.
  2. **Drill 2**: Write and read CSV rows in `io.StringIO` (and disk with `newline=""`) via `csv.DictWriter` / `csv.DictReader`.
  3. **Drill 3**: Parse TOML via `tomllib.loads` AND write a temporary `.toml` file inside `TemporaryDirectory()` to load it with `tomllib.load(fp)` opened in `"rb"` binary mode (plus `# Try uncommenting:` text-mode `"r"` `TypeError` experiment).

### `630_binary_packing_with_struct.py` *(Narrow Primer — ~110–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Exact binary wire layouts with `struct.Struct`: prefixes `<`, `>`, `!`, `=` disable C alignment padding, whereas native `@` includes C padding. *(Guardrail: skip rare format codes `P`, `e`, `n`, `p`.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `struct.Struct("<HBI")`, `@` vs. `<`/`>`/`!`, `.pack`, `.unpack`, `.pack_into`, `.iter_unpack`, and `int.to_bytes` / `int.from_bytes`.
- **Scaffold**: `import struct`, `#` prose comments, tiny starter size comparison, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Compare `struct.calcsize("@HBI")` vs. `struct.calcsize("<HBI")`, pack `(0xCAFE, 1, 1024)`, and unpack back.
  2. **Drill 2**: Pack multiple records into a `bytearray` via `pack_into`, iterate with `iter_unpack`, and test `int.to_bytes` / `int.from_bytes`.

### `640_regular_expressions_re.py` *(Core Primer)*
- **Defining Concept & Friction Point**: `re.match()` only anchors at index 0 (passing `"123abc"` for `r"\d+"`!), whereas `re.fullmatch()` validates the entire string; greedy `<.*>` over-matches compared to lazy `<.*?>`; and `re.VERBOSE` keeps complex patterns readable. *(Guardrail: skip `re.LOCALE` and `re.DEBUG`.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `re.compile`, `re.search` vs. `re.match` vs. `re.fullmatch`, named groups `(?P<name>...)` / `.groupdict()`, greedy `*` vs. lazy `*?`, `re.finditer` spans (`.span()`, `.start()`, `.end()`), callback `re.sub`, and `re.VERBOSE`.
- **Scaffold**: `import re`, section functions, `#` prose comments, tiny starter match check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Contrast `re.match` vs. `re.fullmatch` on `"123abc"`, and contrast greedy `r"<.*>"` vs. lazy `r"<.*?>"` on `"<b>hi</b>"`.
  2. **Drill 2**: Compile a `re.VERBOSE` log-line regex with named groups and inspect `.groupdict()`, then collect `(text, span)` tuples via `re.finditer`.
  3. **Drill 3**: Transform integers inside text using `re.sub` with a callback function.

### `650_datetime_timezones_and_zoneinfo.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Naive datetimes (`datetime.now()` without `tz`) vs. timezone-aware `datetime.now(UTC)` (`TypeError` when subtracting or comparing naive and aware!), `ZoneInfo`, and `strptime` / `strftime` vs. `fromisoformat`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `datetime.now(UTC)`, `timedelta`, `.isoformat()` / `datetime.fromisoformat()`, `strptime` / `strftime`, `zoneinfo.ZoneInfo`, `.astimezone()`, and naive-vs-aware `TypeError`.
- **Scaffold**: `from datetime import UTC, datetime, timedelta, timezone`, `from zoneinfo import ZoneInfo`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Create `now_utc = datetime.now(UTC)`, add `timedelta(hours=2, minutes=30)`, round-trip via `.isoformat()` / `fromisoformat()`, and parse/format custom strings with `strptime` / `strftime`.
  2. **Drill 2**: Convert across timezones via `.astimezone(ZoneInfo("America/New_York"))` (or fixed `timezone(...)` fallback) and verify instant equality `==`.
  3. **Drill 3**: Trigger and catch `TypeError` when subtracting a naive `datetime.now()` from aware `now_utc`.

### `660_cli_parsing_with_argparse.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Building testable CLIs by returning an `ArgumentParser` and calling `parser.parse_args(argv)` with explicit `argv`, supporting `type=Path`, `nargs="+"`, mutually exclusive groups, and `set_defaults(handler=...)` subcommand dispatch. *(Guardrail: skip `argparse.SUPPRESS`, `prefix_chars`, and `conflict_handler`.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `ArgumentParser`, `type=Path`, `nargs="+"`, `action="store_true"` / `"count"`, `choices=...`, `.add_mutually_exclusive_group()`, `.add_subparsers(dest="command", required=True)`, and `subparser.set_defaults(handler=...)`.
- **Scaffold**: `import argparse`, `from collections.abc import Sequence`, `from pathlib import Path`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Build a parser with `--verbose` (`action="count"`), a mutually exclusive `--quiet` / `--debug` group, and `type=Path` / `nargs="+"` file arguments.
  2. **Drill 2**: Add `run` and `export` subcommands wired with `set_defaults(handler=...)` and invoke the resolved handler on simulated `argv` lists in `main()`.

### `670_structured_logging_and_handlers.py` *(Core Primer — expanded from 1 Drill to 8–12 Drills)*
- **Defining Concept & Friction Point**: Hierarchical loggers (`logging.getLogger(__name__)`), why libraries never call `logging.basicConfig()` or root `logging.info()`, two-stage threshold filtering (Logger level + Handler level), parent/child `propagate=True` double-logging traps, and `logger.exception()`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `logging.getLogger(__name__)`, module logger isolation, dual Logger vs. Handler level thresholds, parent/child propagation (`logger.propagate = True` double-logging trap vs. `False`), `StreamHandler`, `Formatter`, custom `logging.Filter`, lazy `%s` formatting, and `logger.exception()`.
- **Scaffold**: `import io`, `import logging`, section functions, `#` prose comments, tiny starter logger inspection, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Demonstrate two-stage threshold filtering (handler set to `DEBUG` prints nothing while logger stays at `WARNING` until `logger.setLevel(logging.DEBUG)`).
  2. **Drill 2**: Reproduce the parent/child propagation double-logging trap (`"app"` and `"app.db"` both having handlers with `propagate=True`), then fix it with `child.propagate = False`.
  3. **Drill 3**: Configure `"demo.service"` writing to `io.StringIO` with a custom `Formatter`, emit lazy `%s` logs (`debug`/`info`/`warning`), attach a context filter, and capture a `ZeroDivisionError` traceback via `logger.exception(...)`.

### `680_sqlite3_embedded_database.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Using stdlib `sqlite3`: (1) `with conn:` commits/rolls back **transactions**, whereas `contextlib.closing(sqlite3.connect(...))` **closes** the connection; (2) always use `?` `(val,)` 1-tuples or `:key` named placeholders (never f-strings!); and (3) SQLite disables foreign-key enforcement by default unless you run `PRAGMA foreign_keys = ON;`!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `closing(sqlite3.connect(":memory:"))`, `with conn:` transaction rollback/commit, `PRAGMA foreign_keys = ON`, positional `?` (`(100,)` 1-tuple) vs. named `:key` placeholders, `executemany`, and `sqlite3.Row`.
- **Scaffold**: `from contextlib import closing`, `import sqlite3`, section functions, `#` prose comments, tiny starter version print, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Create `users`, batch-insert with `executemany`, query with positional `(100,)` 1-tuple AND named `:min_credits` placeholders, and read `sqlite3.Row` fields.
  2. **Drill 2**: Enable `PRAGMA foreign_keys = ON`, create a child `orders(user_id REFERENCES users(id))` table, verify inserting an invalid `user_id` raises `sqlite3.IntegrityError` (contrasting with `PRAGMA foreign_keys = OFF` silently accepting orphans!).
  3. **Drill 3**: Prove automatic transaction rollback when an `IntegrityError` escapes `with conn:`.

### `690_hashlib_hmac_and_secrets.py` *(Narrow Primer — ~110–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Using `secrets` (CSPRNG) instead of `random` for tokens/keys, `hmac.compare_digest` for constant-time MAC verification, and streaming `hashlib.file_digest`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `hashlib.sha256` / `blake2b` / `file_digest`, `hmac.new`, `hmac.compare_digest`, and `secrets.token_hex` / `token_urlsafe` / `token_bytes`.
- **Scaffold**: `import hashlib`, `import hmac`, `import io`, `import secrets`, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Digest an `io.BytesIO` stream with `hashlib.file_digest(..., "sha256")`, plus incremental `.update()` hashing.
  2. **Drill 2**: Generate a key with `secrets.token_bytes(32)`, sign a payload with `hmac.new`, verify valid vs. tampered signatures with `hmac.compare_digest`, and generate `secrets.token_urlsafe`.

### `695_subprocess_and_os_processes.py` *(Narrow Primer — ~110–140 lines, 6–8 Drills)*
- **Defining Concept & Friction Point**: Safe child execution via `subprocess.run` with argument lists (`shell=False`), `check=True`, `timeout=`, custom `env`/`cwd`, and inspecting `stderr` on failure. *(Guardrail: skip `Popen` `close_fds` and `creationflags`.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `subprocess.run([sys.executable, ...], capture_output=True, text=True, check=True, timeout=..., env=..., cwd=...)`, `CalledProcessError` (`.returncode`, `.stderr`), and `TimeoutExpired`.
- **Scaffold**: `from pathlib import Path`, `import subprocess`, `import sys`, `import tempfile`, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Run `[sys.executable, "-c", ...]` with `input=`, custom `env={...}`, and `cwd=...` inside `TemporaryDirectory()`, reading `result.stdout`.
  2. **Drill 2**: Catch `subprocess.CalledProcessError` on a failing child command and inspect `.returncode` and `.stderr`.

---

## `700`–`799`: Advanced Type System, Generics (PEP 695), AST, Inspection & Hooks

### `700_modern_generics_and_type_params.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Python 3.12+ (PEP 695) native generic syntax (`def first[T](items: Sequence[T]) -> T:`, `class RingBuffer[T]:`, `type Pair[T] = tuple[T, T]`) with upper bounds (`[T: Bound]`) and constrained types (`[T: (int, float)]`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - PEP 695 generic functions, generic classes (`__type_params__`), lazy `type` aliases (including recursive `type Tree[T] = ...`), constrained `[T: (int, float)]`, and explicit upper-bound `[T: SupportsArea]` / `[T: BaseModel]` **Drills**.
- **Scaffold**: `from collections.abc import Sequence`, `from typing import Protocol`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Define a recursive `type Tree[T] = T | list[Tree[T]]`, generic `first_item[T]`, and an upper-bounded generic helper `def total_area[T: HasArea](items: Sequence[T]) -> float:`.
  2. **Drill 2**: Implement generic `BoundedStack[T]` (`push`, `pop`, `peek`) and instantiate `BoundedStack[int](capacity=4)`.

### `710_variance_paramspec_and_typevartuple.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Mutable containers (`list[T]`) are **invariant** (`list[Dog]` is not a `list[Animal]`), whereas read-only `Sequence[T]` is **covariant**; `ParamSpec` (`**P`) preserves wrapped function parameter names/types in decorators.
- **Keywords, Built-ins & Concepts Breakdown**:
  - Invariance vs. covariance vs. contravariance, PEP 695 `[**P, R]` `ParamSpec`, `Concatenate`, and `TypeVarTuple` (`*Ts`).
- **Scaffold**: `from collections.abc import Callable, Sequence`, `from functools import wraps`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Write `sum_numbers(nums: Sequence[int | float]) -> float` accepting both `list[int]` and `tuple[float, ...]`.
  2. **Drill 2**: Write `with_audit[**P, R](fn: Callable[P, R]) -> Callable[P, R]` preserving full parameter types via `P.args` / `P.kwargs`, plus a `TypeVarTuple` variadic tuple helper.

### `720_typeddict_literal_newtype_and_typeguard.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Typing JSON/API dicts (`TypedDict` with `ReadOnly`, `total=False`, `Required`, `NotRequired`), zero-cost nominal wrappers (`NewType`), and narrowing predicates (`TypeGuard` vs. Python 3.13 `TypeIs`).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `TypedDict` (`total=False`, `Required[T]`, `NotRequired[T]`, `ReadOnly[T]` PEP 705), `NewType("UserId", int)`, `Literal`, and `TypeGuard[T]` (noting Python 3.13 `TypeIs[T]` narrowing both `if` and `else` branches).
- **Scaffold**: `from typing import Literal, NewType, NotRequired, ReadOnly, Required, TypedDict, TypeGuard`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Define `UserId = NewType(...)`, `OrderId = NewType(...)`, a `ReadOnly` `OrderPayload(TypedDict)`, and a `total=False` patch dict using `Required[OrderId]`.
  2. **Drill 2**: Write `is_non_empty_str_list(val: list[object]) -> TypeGuard[list[str]]` and document Python 3.13 `TypeIs` narrowing differences.

### `730_runtime_inspection_and_signatures.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Combining `inspect.signature(fn)`, `inspect.Parameter.empty` vs. `default=None`, `sig.bind(*args, **kwargs)`, and `get_type_hints(..., include_extras=True)` with `Annotated[T, metadata]` for runtime validation.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `inspect.signature`, `inspect.Parameter.empty` (distinguishing an omitted default from `default=None`), `sig.bind` / `apply_defaults`, `Annotated`, and `get_type_hints(..., include_extras=True)`.
- **Scaffold**: `from dataclasses import dataclass`, `import inspect`, `from typing import Annotated, Any, get_args, get_origin, get_type_hints`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Inspect parameter defaults distinguishing `param.default is inspect.Parameter.empty` from `param.default is None`.
  2. **Drill 2**: Implement `@validate_ranges` using `sig.bind` + `get_type_hints(..., include_extras=True)` over `Annotated[int, ValueRange(0, 100)]` and test valid (`75`) vs. out-of-range (`150` -> `ValueError`) calls.

### `740_ast_parsing_walking_and_transforming.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Parsing source into an AST (`ast.parse`), inspecting with `NodeVisitor` (always calling `self.generic_visit(node)`), rewriting with `NodeTransformer` + `ast.fix_missing_locations`, `ast.unparse`, and `compile()`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `ast.parse`, `ast.dump`, `ast.NodeVisitor`, `ast.NodeTransformer`, `ast.fix_missing_locations`, `ast.unparse`, and `compile`.
- **Scaffold**: `import ast`, section functions, `#` prose comments, tiny starter AST dump, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `PrintCallFinder(ast.NodeVisitor)` recording line numbers of `print(...)` calls.
  2. **Drill 2**: Implement `ConstantFolder(ast.NodeTransformer)`, transform an expression tree, call `fix_missing_locations`, print `ast.unparse`, and evaluate `compile(...)`.

### `750_dynamic_code_exec_and_safe_literal_eval.py` *(Narrow Primer — ~110–140 lines, 5–7 Drills)*
- **Defining Concept & Friction Point**: Why `eval()` on untrusted strings is unsafe, parsing data literals safely with `ast.literal_eval()`, and evaluating whitelisted math expressions over `ast.parse(..., mode="eval")`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `ast.literal_eval` and whitelisted AST math evaluator (`Expression`, `Constant`, `BinOp`, `UnaryOp`).
- **Scaffold**: `import ast`, `import operator`, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Parse literal config strings with `ast.literal_eval` and verify `ast.literal_eval("__import__('os').system('echo pwned')")` raises `ValueError`.
  2. **Drill 2**: Implement `safe_calc(expr_str: str) -> float` over `ast.parse(..., mode="eval").body` and evaluate `"2 * (10 + 5) - 3"`.

### `760_sys_monitoring_and_trace_hooks.py` *(Narrow Primer — ~110–140 lines, 5–7 Drills; Links to `../tracy_how_to/700_python_tracy_zones_and_sys_monitoring.py`)*
- **Defining Concept & Friction Point**: Hooking CPython 3.12+ VM events per code object with `sys.monitoring` (`LINE`, `PY_START`, `PY_RETURN`, and returning `sys.monitoring.DISABLE` to zero out future overhead after first hit) alongside `traceback.extract_tb`. *(Cross-repo boundary: keep `760` focused on `sys.monitoring` `LINE` / `PY_START` / `PY_RETURN` / `DISABLE` and `traceback.extract_tb`; link to `../tracy_how_to/700_python_tracy_zones_and_sys_monitoring.py` for callback overhead distortion measurements and `PY_UNWIND` exception-zone cleanup. Guardrail: skip enumerating all 18 `sys.monitoring.events` masks.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `sys.monitoring` (`use_tool_id`, `register_callback`, `set_local_events`, `events.LINE` / `PY_START` / `PY_RETURN`, `sys.monitoring.DISABLE`, `free_tool_id`), and `traceback.extract_tb` / `format_exception`.
- **Scaffold**: `import sys`, `import traceback`, `#` prose comments, tiny starter `events.LINE` mask check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Instrument `compute_sum.__code__` with `LINE`, `PY_START`, and `PY_RETURN` callbacks, verify `sys.monitoring.DISABLE` disables repeated triggers on subsequent hits, and clean up inside `finally:`.
  2. **Drill 2**: Catch a nested `ZeroDivisionError` and extract `[f"{f.name}:{f.lineno}" for f in traceback.extract_tb(err.__traceback__)]`.

### `770_import_hooks_and_custom_loaders.py` *(Narrow Primer — ~110–140 lines, 5–7 Drills)*
- **Defining Concept & Friction Point**: Intercepting `import` via `sys.meta_path` using `MetaPathFinder` (`find_spec`) + `Loader` (`exec_module`) and cleaning up `sys.meta_path` / `sys.modules` in `finally:`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `MetaPathFinder`, `Loader`, `ModuleSpec`, and `sys.meta_path` cleanup.
- **Scaffold**: `from importlib.abc import Loader, MetaPathFinder`, `from importlib.machinery import ModuleSpec`, `import importlib`, `import sys`, `from types import ModuleType`, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Implement `VirtualConfigFinder(MetaPathFinder, Loader)` synthesizing `"virtual_cfg_*"` modules.
  2. **Drill 2**: Register in `sys.meta_path`, import `"virtual_cfg_alpha"`, inspect attributes, and clean up `sys.meta_path` and `sys.modules` in `finally:`.

---

## `800`–`899`: Concurrency (`threading`, `multiprocessing`, `asyncio`) & C Interop (`ctypes`)

### `800_threads_gil_and_synchronization.py` *(Core Primer)*
- **Defining Concept & Friction Point**: OS threads (`threading.Thread`) vs. CPython's GIL (`sys._is_gil_enabled()`), why shared increments still race under the GIL without a `Lock`, and how `threading.RLock` lets the *same* thread re-enter nested locked methods without deadlocking!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `threading.Thread`, `sys._is_gil_enabled()` (3.13+ with 3.12 fallback), unprotected race contrast vs. `threading.Lock`, re-entrant `threading.RLock`, `Event`, `Barrier`, and `threading.local`.
- **Scaffold**: `import sys`, `import threading`, section functions, `#` prose comments, tiny starter GIL check, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Contrast an unprotected shared counter race against `SharedCounter` guarded by `threading.Lock()` across 4 threads (`4000`).
  2. **Drill 2**: Build a recursive/re-entrant method pair protected by `threading.RLock()` proving the same thread acquires it twice without deadlocking (contrasting with a standard `Lock`), plus `Barrier(3)` and `Event`.

### `810_thread_safe_queues_and_worker_pools.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Bounded `queue.Queue` producer-consumer pipelines and `ThreadPoolExecutor` fan-out—where `future.result()` propagates worker exceptions back to the main thread!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `queue.Queue(maxsize=...)` (`.put`, `.get`, `.task_done`, `.join`, `None` sentinel), `ThreadPoolExecutor`, `pool.submit` + `as_completed` vs. `pool.map`, and `try / except` around `future.result()`.
- **Scaffold**: `from concurrent.futures import ThreadPoolExecutor, as_completed`, `import queue`, `import threading`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Fan out tasks via `pool.submit` + `as_completed` AND contrast with `pool.map` (which preserves input order), wrapping `future.result()` in `try / except ValueError:` to handle a failing worker task cleanly.
  2. **Drill 2**: Build a bounded `queue.Queue(maxsize=4)` producer-consumer loop with `None` shutdown sentinel.

### `820_multiprocessing_and_shared_memory.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Multi-core parallelism with `ProcessPoolExecutor` (requiring `if __name__ == "__main__":` on Windows `spawn` and pickleable top-level functions) and zero-copy `SharedMemory` buffers.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `ProcessPoolExecutor`, `spawn` guard, `SharedMemory(create=True, size=N)`, `.buf` (`memoryview`), `.close()`, and `.unlink()`.
- **Scaffold**: `from concurrent.futures import ProcessPoolExecutor`, `from multiprocessing.shared_memory import SharedMemory`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Create `SharedMemory`, cast `.buf` via `.cast("i")`, attach a second `SharedMemory(name=shm.name)` view, mutate zero-copy, and `.close()` + `.unlink()` in `finally:`.
  2. **Drill 2**: Run a top-level CPU function through `ProcessPoolExecutor(max_workers=2)`.

### `830_asyncio_coroutines_and_event_loop.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Single-threaded cooperative `asyncio`: sequential `await a(); await b()` takes `T_a + T_b`, whereas `create_task` / `gather` takes `max(T_a, T_b)`; background tasks need a strong reference set (`add_done_callback(tasks.discard)`); `task.cancel()` raises `CancelledError` for `finally:` cleanup; and blocking calls must use `asyncio.to_thread()`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `async def` / `await`, `asyncio.run`, `create_task` + strong-ref `tasks: set[asyncio.Task[Any]]` with `add_done_callback(tasks.discard)`, sequential vs. concurrent timing contrast (`T_a + T_b` vs. `max(T_a, T_b)`), `task.cancel()` / `CancelledError` cleanup, `asyncio.gather`, and `asyncio.to_thread`.
- **Scaffold**: `import asyncio`, `import time`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Measure sequential `await` vs. concurrent `create_task` / `gather` timing (`perf_counter_ns`), keeping strong references in a `set` via `add_done_callback(bg_tasks.discard)`.
  2. **Drill 2**: Cancel an in-flight task with `task.cancel()`, handle `asyncio.CancelledError` inside `try ... finally:` cleanup, and offload a blocking synchronous call via `await asyncio.to_thread(...)`.

### `840_asyncio_taskgroups_queues_and_timeouts.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Structured concurrency in Python 3.11+: `TaskGroup` cancels sibling tasks and raises `ExceptionGroup` (`except*`); `asyncio.timeout` enforces deadlines; `asyncio.Queue` provides async backpressure; and `async with` / `async for` implement async resource and stream protocols.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `asyncio.TaskGroup`, live sibling cancellation + `except* ExceptionGroup`, `asyncio.timeout(seconds)`, `asyncio.Semaphore`, `asyncio.Queue(maxsize=N)` (`put`, `get`, `task_done`, `join`), `async for` (`__aiter__`/`__anext__`), and `async with` (`__aenter__`/`__aexit__`).
- **Scaffold**: `import asyncio`, `from collections.abc import AsyncIterator`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Fan out bounded jobs with `TaskGroup` + `Semaphore(2)`, AND run a second `TaskGroup` where one task fails to prove live sibling cancellation caught via `try ... except* RuntimeError as eg:`.
  2. **Drill 2**: Build a producer-consumer `asyncio.Queue(maxsize=2)` pipeline with backpressure and `await q.join()`.
  3. **Drill 3**: Test `asyncio.timeout`, an async generator `ticker` (`async for`), and a tiny async context manager (`__aenter__` / `__aexit__`) used with `async with`.

### `850_concurrent_pipeline_lab/` *(Multi-File Lab)*
- **Files**: `main.py`, `pipeline.py`
- **Defining Concept & Friction Point**: Multi-stage concurrent worker pipeline (`Producer -> Bounded asyncio.Queue -> N Workers -> Aggregator`) with `asyncio.TaskGroup`, `asyncio.timeout`, and clean shutdown.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `asyncio.Queue(maxsize=4)`, `asyncio.TaskGroup`, `asyncio.timeout`, `@dataclass(slots=True, frozen=True)` contracts (`WorkItem`, `WorkResult`, `PipelineStats`).
- **Scaffold**: `#` prose comments, shared dataclasses in `pipeline.py`, bottom `main()` in `main.py` (zero `pass`/dummy stubs).
- **Ordered Outline**:
  1. In `pipeline.py`: **Drill** to implement `producer`, `worker`, and `run_pipeline`.
  2. In `main.py`: **Drill** to generate 16 `WorkItem`s, run `run_pipeline(..., worker_count=4)`, verify all 16 results, and print stats.

### `860_ctypes_foreign_c_interop.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Calling native C dynamic libraries via `ctypes`: always set `fn.argtypes` and `fn.restype` or 64-bit pointers/doubles silently truncate to 32-bit `c_int`, and keep a live Python reference to `CFUNCTYPE` callbacks so GC does not free the C trampoline!
- **Keywords, Built-ins & Concepts Breakdown**:
  - `ctypes.CDLL`, `c_int`/`c_double`/`c_size_t`/`c_char_p`/`POINTER`, `argtypes`/`restype`, `ctypes.Structure` + `byref`, and `CFUNCTYPE` (e.g. `qsort`).
- **Scaffold**: `import ctypes`, `import sys`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Load the platform C library (`msvcrt` / `libc`), configure `argtypes`/`restype` on `abs` and `strlen`, and invoke both.
  2. **Drill 2**: Sort a `(ctypes.c_int * 6)` array with C `qsort` using a live `CFUNCTYPE` comparator reference, plus inspect a `ctypes.Structure`.

### `865_ctypes_simd_hotspot_offload.py` *(Narrow Primer — ~132 lines; Links to `../tracy_how_to/800_hybrid_python_odin_tracy_offload_lab/`)*
- **Defining Concept & Friction Point**: Passing zero-copy contiguous `array.array("f")` buffers across `(ctypes.c_float * n).from_buffer(arr)` over a 1D dot-product ABI to an optional native Odin/C `.dll` with graceful pure-Python fallback. *(Cross-repo boundary: `865` owns `ctypes.from_buffer` zero-copy pointer-aliasing mechanics and optional native dot-product fallback; link to `../tracy_how_to/800_hybrid_python_odin_tracy_offload_lab/` for multi-layer Python+Odin FFI timeline tracing and `N`-size crossover forensics.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `(ctypes.c_float * len(arr)).from_buffer(arr)` (and `BufferError`/`TypeError` protection on immutable `bytes`), `argtypes`/`restype`, and pure-Python fallback (`sum(map(operator.mul, a, b))`).
- **Scaffold**: `from array import array`, `import ctypes`, `import operator`, `from pathlib import Path`, `import sys`, `#` prose comments, tiny kernel-path probe, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Create zero-copy `CFloatArray.from_buffer(a)` views over `array("f")` buffers, verify `a.buffer_info()[0] == ctypes.addressof(c_a)` and in-place mutation, plus `# Try uncommenting:` immutable `bytes` safety check.
  2. **Drill 2**: Implement `DotProductKernel` (`argtypes`, `restype`, native DLL vs. bulk `operator.mul` fallback) and verify `abs(result - 6400.0) < 1e-3`.

### `870_native_plugin_hot_reload_lab/` *(Multi-File Lab)*
- **Files**: `host.py`, `shared_state.py`, `plugins/rules_plugin.py`
- **Defining Concept & Friction Point**: Separating persistent `HostState` (`shared_state.py`) from reloadable `step_simulation(state)` logic (`plugins/rules_plugin.py`) and staging candidate reloads via `importlib.util.spec_from_file_location` so broken edits keep the previous plugin running.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `spec_from_file_location` / `module_from_spec` / `exec_module`, persistent state separation, and atomic swap with error fallback.
- **Scaffold**: `#` prose comments, `HostState` dataclass in `shared_state.py`, starter v1 plugin + `PluginHost` boilerplate, bottom `main()` (zero `pass`/dummy stubs).
- **Ordered Outline**:
  1. In `shared_state.py`: **Drill** to define `HostState` (`tick`, `player_x`, `score`, `version_tag`).
  2. In `plugins/rules_plugin.py`: **Drill** to implement `PLUGIN_VERSION` and `step_simulation(state)`.
  3. In `host.py`: **Drill** to implement `PluginLoader` testing v1 -> v2 live reload with preserved state -> broken edit fallback preserving v2.

### `880_sockets_and_selectors_nonblocking_io.py` *(Core Primer)*
- **Defining Concept & Friction Point**: Non-blocking TCP sockets (`setblocking(False)`), OS readiness multiplexing (`selectors.DefaultSelector`), TCP byte-stream framing (`\n` buffering), and **partial `sock.send()` handling** under non-blocking backpressure (retaining unsent tail slices `view[sent:]` and registering `EVENT_WRITE` until drained!). *(Guardrail: skip `TCP_NODELAY` and `SO_LINGER`.)*
- **Keywords, Built-ins & Concepts Breakdown**:
  - `socket.socket`, `.bind(("127.0.0.1", 0))`, `.setblocking(False)`, `selectors.DefaultSelector` (`EVENT_READ` / `EVENT_WRITE`, `modify`), partial `sock.send()` / `BlockingIOError` tail buffering, and `\n` message framing.
- **Scaffold**: `import selectors`, `import socket`, section functions, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Bind a non-blocking loopback server on `("127.0.0.1", 0)`, register with `DefaultSelector`, handle partial `recv()` buffering up to `\n`, and handle partial `send()` / `BlockingIOError` write-buffer draining via `EVENT_WRITE`.
  2. **Drill 2**: Exchange newline-framed requests and responses from a non-blocking loopback client in the same selector loop and close all sockets cleanly.

### `890_signals_atexit_and_graceful_shutdown.py` *(Narrow Primer — ~110–130 lines, 4–7 Drills)*
- **Defining Concept & Friction Point**: LIFO cleanup hooks with `atexit.register` and main-thread signal handlers (`signal.signal`) that only flip a cooperative `stop_requested` flag / `Event` (never acquiring locks inside the signal handler!).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `atexit.register` / `unregister`, `signal.signal` / `getsignal`, and restoring previous handlers in `finally:`.
- **Scaffold**: `import atexit`, `import signal`, `#` prose comments, bottom `main()`.
- **Ordered Outline**:
  1. **Drill 1**: Register and test LIFO `atexit` hooks and install a temporary `SIGINT` handler (restored in `finally:`) flipping `ShutdownController.stop_requested`.

---

## `900`–`999`: Complete Programs & Multi-File Training Capstones

### `900_binary_hex_dumper.py` *(Primer — ~120–140 lines; Parallels `odin_how_to/900_binary_file_dumper.odin`)*
- **Defining Concept & Friction Point**: Building a fast CLI hex + ASCII gutter inspector that reads a file, slices it into 16-byte rows using zero-copy `memoryview`, aligns partial final rows cleanly, and formats printable ASCII (`0x20 <= b <= 0x7E`) vs. `.` placeholders.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `pathlib.Path.read_bytes()`, `memoryview(data)` 16-byte stride slicing, `f"{offset:08x}"`, 8-byte mid-row gap, fixed-width partial-row padding, printable ASCII comprehension, and `sys.argv`.
- **Scaffold**: `from pathlib import Path`, `import sys`, `#` prose comments, tiny starter byte-slice check, bottom `main()` (describe `dump_bytes(data: bytes | memoryview, max_rows: int = 16) -> list[str]` in a `#` **Drill** with zero `...`/`pass` stubs).
- **Ordered Outline**:
  1. **Drill 1**: Implement `dump_bytes(data: bytes | memoryview, max_rows: int = 16) -> list[str]` wrapping `data` in `memoryview`, formatting 8-digit hex offsets, 16 padded hex columns, and `|...|` printable ASCII gutters.
  2. **Drill 2**: In `main()`, read `sys.argv[1]` (defaulting to `Path(__file__)`), call `dump_bytes(raw_bytes, max_rows=12)`, and print each formatted line.

### `910_custom_open_addressing_hash_table.py` *(Primer — Parallels `odin_how_to/910_custom_hash_table.odin`)*
- **Defining Concept & Friction Point**: Implementing a generic open-addressed hash table (`class HashTable[K, V](MutableMapping[K, V]):`) with power-of-2 capacity, linear probing, **Tombstone** deletion markers (so deletions never break later probe chains!), 70% load-factor resizing, and Python's `MutableMapping` interface.
- **Keywords, Built-ins & Concepts Breakdown**:
  - PEP 695 `class HashTable[K, V](MutableMapping[K, V]):`, `SlotState(IntEnum)` (`EMPTY`, `OCCUPIED`, `TOMBSTONE`), `@dataclass(slots=True) class _Entry[K, V]`, `hash(key) & (capacity - 1)`, tombstone recycling, and `MutableMapping` dunders (`__getitem__`, `__setitem__`, `__delitem__`, `__iter__`, `__len__`).
- **Scaffold**: `from collections.abc import Iterator, MutableMapping`, `from dataclasses import dataclass`, `from enum import IntEnum`, `SlotState(IntEnum)`, `#` prose comments, bottom `main()` (describe `_Entry` and `HashTable` methods as `#` **Drills** without `pass`/dummy return stubs).
- **Ordered Outline**:
  1. **Drill 1**: Define `_Entry[K, V]` and `HashTable[K, V](MutableMapping[K, V])` with `_find_slot`, `_resize` (re-inserting `OCCUPIED` entries and clearing `TOMBSTONE`s), and the 5 `MutableMapping` dunders.
  2. **Drill 2**: Insert 20 key-value pairs (triggering resizes), delete 5 keys (creating tombstones), verify lookups and `in` membership across probe chains, and assert `dict(table)` matches a reference `dict`.

### `920_sqlite_and_json_task_tracker_cli.py` *(Primer)*
- **Defining Concept & Friction Point**: Synthesizing `@dataclass(slots=True)`, `StrEnum`, `argparse` subcommands, `sqlite3` transactional persistence, and `json` export into a complete single-file CLI application with an automated verification run when invoked without arguments.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `sqlite3.Connection`, `sqlite3.Row`, `argparse` subparsers (`add`, `done`, `list`, `export`), `@dataclass(slots=True) class Task`, `StrEnum`, `Path`, `tempfile.TemporaryDirectory`.
- **Scaffold**: Imports, `@dataclass(slots=True) class Task`, `#` prose comments, bottom `main()` (specify `TaskStore` methods as `#` **Drills** without `pass`/dummy stubs).
- **Ordered Outline**:
  1. **Drill 1**: Implement `TaskStore` (`init_schema`, `add_task`, `complete_task`, `list_tasks`, `export_json`) over `sqlite3`.
  2. **Drill 2**: Build `argparse` subcommands (`add`, `done`, `list`, `export`) and run an automated self-test inside `TemporaryDirectory()` when `len(sys.argv) == 1`.

### `930_async_tcp_command_server.py` *(Primer — ~150–200 lines; Parallels `odin_how_to/930_tcp_echo_and_command_server.odin`)*
- **Defining Concept & Friction Point**: Writing a concurrent TCP command server and multi-client loopback self-test in one file using `asyncio.start_server` (`("127.0.0.1", 0)`), `asyncio.open_connection`, line-based framing (`reader.readline()`), `writer.write()` + `await writer.drain()` backpressure, shared server request counter (`STATS`), and deterministic teardown.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `asyncio.start_server`, `server.sockets[0].getsockname()`, `StreamReader.readline()`, `StreamWriter` (`write`, `await drain()`, `close`, `await wait_closed()`), `asyncio.open_connection`, and `asyncio.gather` concurrent multi-client testing.
- **Scaffold**: `import asyncio`, `@dataclass(slots=True) class ServerStats`, `#` prose comments, tiny starter protocol check, bottom `main()` (specify `handle_command`, `client_handler`, `run_self_test` cleanly without `pass`/dummy stubs).
- **Ordered Outline**:
  1. **Drill 1**: Implement `handle_command(raw_line: str, stats: ServerStats) -> tuple[str, bool]` supporting `"PING"` -> `("PONG\n", False)`, `"ADD <a> <b>"` -> `(f"{a + b}\n", False)`, `"STATS"` -> `(f"COMMANDS {stats.commands_handled}\n", False)`, and `"QUIT"` -> `("BYE\n", True)` (incrementing `stats.commands_handled`).
  2. **Drill 2**: Implement `client_handler(reader, writer, stats)` with `try ... finally:` (`writer.close()`, `await writer.wait_closed()`) and `run_self_test()` launching multiple concurrent loopback clients via `asyncio.gather` to exercise `PING`, `ADD`, `STATS`, and `QUIT` across clients inside `async with server:`.

### `940_log_search_and_word_freq_lab/` *(Multi-File Lab — Parallels `odin_how_to/940_log_search_and_word_freq_lab`)*
- **Files**: `main.py`, `indexer.py`, `report.py`
- **Defining Concept & Friction Point**: Multi-file text search & word-frequency analyzer: `indexer.py` streams files line-by-line with regex tokenization (`re.finditer`) into `Counter` and `SearchHit` dataclasses; `report.py` renders ranked word tables and search hits; `main.py` runs the pipeline over `docs/` (or fallback corpus).
- **Keywords, Built-ins & Concepts Breakdown**:
  - `pathlib.Path.rglob`, generator streaming, `re.compile`, `Counter.most_common`, `@dataclass(slots=True, frozen=True) class SearchHit` and `WordStat`.
- **Scaffold**: `#` prose comments, `SearchHit` / `WordStat` dataclasses + `SAMPLE_CORPUS` **Scaffold**, bottom `main()` (zero `pass`/dummy stubs).
- **Ordered Outline**:
  1. In `indexer.py`: **Drill** to implement `scan_text` and `index_directory`.
  2. In `report.py`: **Drill** to implement `top_words` and `render_summary`.
  3. In `main.py`: **Drill** to scan workspace docs (or fallback sample corpus), print matching lines and top 10 words, and verify counts.

### `950_ecs_entity_simulation_lab/` *(Multi-File Lab — Parallels `odin_how_to/950_ecs_entity_simulation_lab`)*
- **Files**: `main.py`, `world.py`, `systems.py`
- **Defining Concept & Friction Point**: Data-oriented ECS simulation in pure Python: `world.py` stores components in contiguous `array("f")` SoA columns with `ComponentFlag(IntFlag)` masks and generational `EntityHandle(idx, gen)`; `systems.py` updates movement, bounds, and health/damage.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `IntFlag`, `EntityHandle`, `array.array("f")` SoA columns, generational recycling, and bitmask subset checks `(mask & required) == required`.
- **Scaffold**: `#` prose comments, `MAX_ENTITIES = 64`, `ComponentFlag`, `EntityHandle`, and `World` data contracts, bottom `main()` (zero `pass`/dummy stubs).
- **Ordered Outline**:
  1. In `world.py`: **Drill** to implement `World.spawn_entity`, `World.despawn_entity`, and `World.is_alive`.
  2. In `systems.py`: **Drill** to implement `movement_system` and `damage_system`.
  3. In `main.py`: **Drill** to spawn 16 entities, step 10 ticks, verify despawned handles report `is_alive == False`, and print surviving state.

### `960_bytecode_vm_and_compiler_lab/` *(Multi-File Lab — Parallels `odin_how_to/960_bytecode_vm_interpreter_lab`)*
- **Files**: `main.py`, `isa.py`, `assembler.py`, `vm.py`
- **Defining Concept & Friction Point**: 32-bit packed ISA (`isa.py`), 2-pass text assembler resolving jump labels (`assembler.py`), and register VM (`vm.py`) using `IntEnum` opcodes, signed 16-bit sign extension, structural `match` dispatch with `assert_never`, and `VMError`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - `Opcode(IntEnum)`, bit-packing `(op << 24) | ...`, signed 16-bit two's-complement extension, 2-pass label resolution, and `match` + `assert_never`.
- **Scaffold**: `#` prose comments, `Opcode(IntEnum)` + `VMError` + `Instruction` contract in `isa.py`, bottom `main()` (zero `pass`/dummy stubs).
- **Ordered Outline**:
  1. In `isa.py`: **Drill** to implement `Instruction.encode` and `Instruction.decode`.
  2. In `assembler.py`: **Drill** to implement 2-pass `assemble_program(source: str) -> list[int]`.
  3. In `vm.py`: **Drill** to implement `run_vm(code: Sequence[int], max_steps: int = 10_000) -> list[int]`.
  4. In `main.py`: **Drill** to assemble and run a 1..10 summation program and assert VM output equals `[55]`.

### `980_arcade_simulation_and_tk_lab/` *(Multi-File Lab — Parallels `odin_how_to/980_raylib_arcade_lab`)*
- **Files**: `main.py`, `game.py`, `renderer.py`
- **Defining Concept & Friction Point**: 60-FPS 2D Space Invaders arcade game in pure stdlib Python (`tkinter.Canvas` + `root.after(16, tick)`), separating pure deterministic state/physics (`game.py` — zero GUI imports!) from rendering (`renderer.py`), with `--headless` automated 10-frame verification in `main.py`.
- **Keywords, Built-ins & Concepts Breakdown**:
  - Pure model-view separation (`GameState`, `Bullet`, `Invader`, `InputState`), AABB/circle collision, `tkinter.Tk`/`Canvas`, and `--headless` CLI execution.
- **Scaffold**: `#` prose comments, `Bullet`, `Invader`, `InputState`, and `GameState` dataclasses in `game.py`; `try: import tkinter` + `--headless` flag parsing boilerplate in `main.py` (convert dispatch branches and game/renderer logic into open **Drills** with zero `pass`/dummy stubs).
- **Ordered Outline**:
  1. In `game.py`: **Drill** to implement `init_game`, `spawn_bullet`, and `update_game`.
  2. In `renderer.py`: **Drill** to implement `render_ascii_snapshot` and `run_tk_window`.
  3. In `main.py`: **Drill** to dispatch `--headless` (10 deterministic frames firing a bullet into an invader, printing ASCII snapshot and score) vs. interactive 800x600 `tkinter` launch.
