# Tracy Profiler & Hotspot Optimization How-To (Odin & Python)

Welcome to **`tracy_how_to/`** — a hands-on performance engineering curriculum with side-by-side Odin (`.odin`) and Python 3.12+ (`.py`) parity. Every **Primer** and **Lab** pairs **Tracy Profiler** instrumentation with Casey Muratori's *Performance-Aware Programming* (*Computer, Enhance!*) **Hotspot-First** methodology and **Five Multipliers** framework.

---

## 1. Quickstart & Zero-Dependency Standalone Design

Every `.odin` and `.py` unit in this directory compiles, passes syntax checks, and runs **out of the box** without requiring `TracyClient.dll`, `TracyClient.lib`, or the `tracy-profiler.exe` GUI to be installed or running:

- **Odin (`#config(TRACY_ENABLE, false)`)**:
  - **Default (`TRACY_ENABLE == false`)**: Conditional `when TRACY_ENABLE` blocks compile foreign Tracy C API calls down to zero instructions, while a lightweight standalone `RDTSC` / `time.Tick` ring-buffer fallback prints console timeline and diagnostic reports (with Chrome Tracing / Spall export covered specifically in **Primer `500`**).
  - **Live Tracy Capture (`-define:TRACY_ENABLE=true`)**: Links `TracyClient.lib` (Windows) / `libTracyClient` (POSIX) and streams nanosecond `RDTSC` zones, memory pool events, thread names, plots, and messages to `tracy-profiler.exe` on `localhost:8086`.
- **Python 3.12+ (`ctypes` + Standard Library Only)**:
  - Searches for `TracyClient.dll` (or `libTracyClient.so` / `libTracyClient.dylib`) next to the script or on `PATH`.
  - When absent, falls back to an in-memory `time.perf_counter_ns()` / `tracemalloc` zone recorder, with Chrome Tracing / Perfetto `.json` export (`ph="X"`, `"C"`, `"i"`, `pid`/`tid`) built into **`250`**, **`450`**, **`550`**, **`800/tracy_bridge.py`**, and **`950/profiler.py`** using zero third-party packages.

### Running Odin Primers & Labs
```sh
# Standalone check and run (zero external binaries required):
odin check 000_tracy_mental_model_and_five_multipliers.odin -file
odin run 000_tracy_mental_model_and_five_multipliers.odin -file

# Live Tracy streaming (when TracyClient.lib is on your library path):
odin run 200_frame_marks_and_scoped_zones.odin -file -define:TRACY_ENABLE=true

# Odin Capstone Multi-File Lab (900):
odin check 900_hotspot_hunt_five_multipliers_lab
odin run 900_hotspot_hunt_five_multipliers_lab -o:speed
```

### Running Python Primers & Labs
```sh
# Standalone syntax check (without writing __pycache__) and run (Python 3.12+, stdlib only):
python -B -m py_compile 050_python_tracy_mental_model_and_multipliers.py
python 050_python_tracy_mental_model_and_multipliers.py

# Python Capstone Multi-File Lab (950):
python 950_python_hotspot_hunt_five_multipliers_lab/main.py
```

### Building & Running the Hybrid Python + Odin SIMD Lab (`800`)
```sh
# 1. Check, run standalone, or build the Odin SIMD DLL kernel:
odin check 800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.odin -file
odin run 800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.odin -file -o:speed
odin build 800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.odin -file -build-mode:dll -o:speed -out:800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.dll

# 2. Run the unified Python <-> Odin offload benchmark (auto-falls back if DLL is not built):
python 800_hybrid_python_odin_tracy_offload_lab/main.py
```

### Verification Workflow (`Write-First, Verify-Once`)
This repository follows a **Write-First, Verify-Once** workflow with zero `.ps1` test harnesses, manifest JSONs, or `solutions/` directories. When authoring or editing multiple **Primers** and **Labs**, complete all edits first and then run standalone `odin check <primer>.odin -file`, `odin check <lab_dir>`, `odin build ... -build-mode:dll`, and `python -B` (`ast.parse`) checks in one batched pass.

---

## 2. Hotspot-First Philosophy & Cross-Repo Boundaries

1. **Keep 95% of your code simple**: Never micro-optimize cold setup, parsing, or reporting code (Amdahl's Law).
2. **Find the 5% hotspot with Tracy**: Use frame marks, nested `Self Time` vs. `Total Time`, memory pool hooks, thread timelines, and plots to prove where time and allocations actually occur—then re-run the trace after every fix to verify real speedup.
3. **Diagnose the bottleneck across the Five Multipliers**:
   - **Multiplier #1 — Waste**: Interpreter dispatch, per-item `PyObject` boxing, heap allocations, or redundant calls inside hot loops.
   - **Multiplier #2 — Instructions Per Clock (IPC)**: Loop-carried dependency chains (`sum += x`) stalling superscalar ports (`IPC < 1.0`) -> break chains with independent accumulators.
   - **Multiplier #3 — SIMD**: Scalar math (`addss`/`mulss`) processing 1 lane per instruction instead of `#simd[4]f32` / `simd.fma` vectors (or offloaded native kernels).
   - **Multiplier #4 — Caching**: Bloated AoS structs or `list[Object]` pointer-chasing wasting 64-byte cache lines -> contiguous `#soa` / `array("d")` / `memoryview`.
   - **Multiplier #5 — Multithreading**: Lock contention, GIL serialization, blocking calls in `asyncio`, or multi-core **false sharing** across 64-byte cache lines (`#align(64)`).

### Responsibility Boundaries vs. `odin_how_to/` & `python_how_to/`
All three curriculum workspaces remain separate and preserve their numbered entries (`ADR-0001`):

- **`odin_how_to/` (`595`–`599`, `700`–`790`)**: Owns Odin language mechanics and raw hardware primitives (`595` `core:prof/spall`, `597` `RDTSC` repetition + `GB/s`, `700` `#soa`, `705` cache lines/`#align(64)`, `710` `#simd`, `715` IPC unrolling, `790` standalone Haversine). Units `596`, `598`, and Lab `599` are slim Odin-idiom `when TRACY_ENABLE` / allocator / mutex integration hooks linking here.
- **`python_how_to/` (`550`–`598`, `760`, `865`)**: Owns Python stdlib profiling, VM internals, and FFI mechanics (`550` `timeit`, `560` `cProfile`, `570` `dis`, `575` bytecode waste, `580` `mmap`/`memoryview`, `585` `array("d")`, `590` `ParticleSoAPool`, `592` Amdahl Haversine, `595` `__slots__`/`tracemalloc`, `760` `LINE` tracing, `865` `ctypes.from_buffer`). Units `565`, `568`, and Lab `598` are slim stdlib wrappers linking here.
- **`tracy_how_to/` (`000`–`950`)**: Owns end-to-end cross-language telemetry, timeline forensics, `TracyC.h` / `ctypes` pinning, nested `Self Time` + recursive zones, named memory pools, thread tracks + GIL/`asyncio` freezes, `TracyPlot`/`TracyMessageC` + `P50`/`P95`/`P99` + Chrome JSON export, profiler-guided Multiplier #1–#4 triage, `sys.monitoring` callback distortion (`700`), hybrid FFI boundary tracing (`800`), and 5-system cold-herring Hotspot Hunt capstones (`900`/`950`).

---

## 3. Curriculum Inventory (`000`–`950` — 15 Primers + 3 Labs = 18 Units / 24 Files)

| Unit | Language | Type | Focus |
| :--- | :--- | :--- | :--- |
| [`000_tracy_mental_model_and_five_multipliers.odin`](000_tracy_mental_model_and_five_multipliers.odin) | Odin | Primer *(Pilot)* | Profiling before optimizing, `RDTSC` vs. `tick_now()` distortion, ring-buffer `%%` wraparound, Amdahl's Law, and IPC post-fix trace. |
| [`050_python_tracy_mental_model_and_multipliers.py`](050_python_tracy_mental_model_and_multipliers.py) | Python | Primer | CPython bytecode/`PyObject` sizing waste, Amdahl's Law, `RingBufferProfiler`, and post-fix trace validation. |
| [`100_odin_tracy_c_api_and_zero_cost_flags.odin`](100_odin_tracy_c_api_and_zero_cost_flags.odin) | Odin | Primer | `#config(TRACY_ENABLE, false)`, `TracyC.h` ABI layout, persistent `Srcloc` lifetime (zero `fmt.ctprintf` dangling pointers), and zero-cost gates. |
| [`150_python_tracy_ctypes_api_and_zero_cost_gates.py`](150_python_tracy_ctypes_api_and_zero_cost_gates.py) | Python | Primer | Binding `TracyClient.dll` via `ctypes.Structure`, wired `SourceLocationRegistry` + `try_load_tracy_library()`, exception-safe zones, and identity zero-cost decorators. |
| [`200_frame_marks_and_scoped_zones.odin`](200_frame_marks_and_scoped_zones.odin) | Odin | Primer | `@(deferred_out)` RAII zones, nested `Self Time` parent stack + recursive zones, `FrameMark` / `frame_mark_start`/`end`, `ZoneValue`, and post-fix spike drop. |
| [`250_python_frame_marks_and_scoped_zones.py`](250_python_frame_marks_and_scoped_zones.py) | Python | Primer | `with tracy.zone(...)`, nested `Self Time` + recursive zone accounting, `FrameMark` spike remediation, and Chrome JSON span export. |
| [`300_tracy_memory_allocator_and_arena_tracking.odin`](300_tracy_memory_allocator_and_arena_tracking.odin) | Odin | Primer | Wrapping `context.allocator` (`Tracy_Allocator`), `mem.Arena` vs. per-frame heap churn (`0 B` steady state), leak detection, and recursion guard. |
| [`350_python_tracy_memory_and_object_churn.py`](350_python_tracy_memory_and_object_churn.py) | Python | Primer | Correlating `tracemalloc` & `gc.get_stats()` per zone: retained leaks vs. Gen-0 GC churn vs. `__slots__` pools and `0 B` `array("d")` reuse. |
| [`400_thread_naming_locks_and_false_sharing.odin`](400_thread_naming_locks_and_false_sharing.odin) | Odin | Primer | **Multiplier #5**: Safe persistent thread naming, mutex wait/hold vs. thread-local merge, timeline spans, and 3-way `#align(64)` false-sharing comparison. |
| [`450_python_threads_gil_and_asyncio_traces.py`](450_python_threads_gil_and_asyncio_traces.py) | Python | Primer | **Multiplier #5**: Isolated GIL-bound vs. GIL-releasing threads (`wall_ns - thread_time_ns`), `asyncio` blocking-`sleep` freeze + `to_thread` fix, and multi-`tid` Chrome JSON. |
| [`500_tracy_plots_messages_and_frame_budgets.odin`](500_tracy_plots_messages_and_frame_budgets.odin) | Odin | Primer | `TracyPlot`, `TracyMessageC`, real compute bursts, `P50`/`P95`/`P99` 16.67 ms budget analysis, Chrome/Spall export, and post-fix verification. |
| [`550_python_plots_messages_and_frame_budgets.py`](550_python_plots_messages_and_frame_budgets.py) | Python | Primer | Live GC/cache-miss plotting, timeline markers, `P50`/`P95`/`P99` budgets, Chrome Tracing / Perfetto JSON export, and post-fix remediation. |
| [`600_diagnosing_waste_ipc_simd_and_cache_in_tracy.odin`](600_diagnosing_waste_ipc_simd_and_cache_in_tracy.odin) | Odin | Primer | **Multipliers #1–#4**: `cycles/item` + `GB/s` triage across Waste, L1/L2/L3 cache sweep (`#soa`), 4-way IPC unrolling, and direct-store `#simd[4]f32`. |
| [`650_diagnosing_python_waste_cache_and_ipc.py`](650_diagnosing_python_waste_cache_and_ipc.py) | Python | Primer | **Multipliers #1–#4**: `ns/item`, `dis.Bytecode(..., adaptive=True)`, `memoryview` MB/s, AoS -> hoisted SoA -> C-backed reduction / FFI preview. |
| [`700_python_tracy_zones_and_sys_monitoring.py`](700_python_tracy_zones_and_sys_monitoring.py) | Python | Primer | Python 3.12 `sys.monitoring` (`PY_START`/`PY_RETURN`) callback distortion, `sys.monitoring.DISABLE`, and `PY_UNWIND` exception cleanup. |
| [`800_hybrid_python_odin_tracy_offload_lab/`](800_hybrid_python_odin_tracy_offload_lab/odin_simd_kernel.odin) | Python + Odin | Lab (3 files) | Offloading a Python hotspot zero-copy to an Odin `#simd[4]f32` DLL (`main.py`, `tracy_bridge.py`, `odin_simd_kernel.odin`), Chrome JSON layers, and `N`-size FFI crossover. |
| [`900_hotspot_hunt_five_multipliers_lab/`](900_hotspot_hunt_five_multipliers_lab/main.odin) | Odin | Lab (3 files) | Odin capstone (`main.odin`, `profiler.odin`, `simulation.odin`): persistent `Srcloc` table, 2 true hotspots vs. cold herrings, `0` allocs, and full checksum parity. |
| [`950_python_hotspot_hunt_five_multipliers_lab/`](950_python_hotspot_hunt_five_multipliers_lab/main.py) | Python | Lab (3 files) | Python capstone (`main.py`, `profiler.py`, `simulation.py`): nested `Self Time` + `tracemalloc`, Chrome JSON export, cold preservation, and `0 B` `array("d")` speedup. |

---

## 4. Authoring Style (`GLOSSARY.md` & `ADR-0002`)

Every unit in `tracy_how_to/` uses four shared terms—**Primer** (single-file unit), **Lab** (multi-file subfolder), **Scaffold** (`~5–20%` starter code / shared Lab contracts), and **Drill** (`//` or `#` hands-on practice comments)—and follows these authoring rules:

- **Causal hardware & VM prose**: Explanations follow the `CodingTemplateExamples/how_to/` voice—reasoning from CPU pipelines, cache lines, allocators, and CPython internals rather than repeating slide-deck bullet lists.
- **Feynman explanations & concrete scenarios**: Every new keyword, directive, or library construct is explained immediately in plain language and paired with a concrete before/body/after hypothetical scenario.
- **Clean layout & comment hygiene**: Multi-section **Primers** put `main` at the very bottom, leave 1 blank line after every `proc() {` or `def ...:` opening, use compact Odin `/* ... */` blocks (no extra leading/trailing blank lines), keep all Python prose in `#` comments (no `"""..."""` docstrings), and avoid Markdown noise (`**bold**`, backticks, `---` underlines).
- **Zero `_ =` or dummy stubs**: Starter imports and locals are used by live **Scaffold** code; unimplemented helpers and methods are expressed as **Drills** specifying exact names, parameter types, and return types rather than `pass` or dummy `return` stubs. There is intentionally no `solutions/` folder.
