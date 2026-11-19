# Tracy Profiler & Hotspot Optimization How-To (Odin & Python) — Per-File Blueprint (`plan.md`)

This document is the authoritative per-file blueprint for `tracy_how_to/`, aligned with [`.scratch/curriculum-alignment/spec.md`](../.scratch/curriculum-alignment/spec.md), [`GLOSSARY.md`](../GLOSSARY.md), [`ADR-0001`](../docs/adr/0001-single-folder-file-flag-and-labs.md), and [`ADR-0002`](../docs/adr/0002-conversational-prose-hash-comments-and-convenience-scaffold.md), and modeled on the causal systems voice of `CodingTemplateExamples/how_to/` and Casey Muratori's *Performance-Aware Programming* (*Computer, Enhance!*).

---

## 1. Global Authoring Rules & Standalone Execution Design

### 1.1 Canonical Vocabulary (`GLOSSARY.md`)
Use these four terms consistently—never drift to avoided synonyms (`"Prompt"`, `"Worked anchor"`, `"Suggested task"`, `"TODO"`, `"cue"`, `"exercise"`, `"lesson file"`, `"module folder"`, `"template"`, `"skeleton"`):
- **Primer**: A self-contained single-file learning unit (`odin run <file>.odin -file` or `python <file>.py`).
- **Lab**: A multi-file learning subfolder (`odin run <dir>` or `python <dir>/main.py`).
- **Scaffold**: Minimal starter code (`~5–20%` soft target of an unfilled **Primer**; shared ABI/domain contracts, slow baselines, and setup boilerplate in a **Lab**).
- **Drill**: A conversational `//` or `#` comment guiding hands-on implementation and IDE autocomplete inside an open section or signature comment.

### 1.2 Standalone Fallback vs. Live Tracy & Chrome JSON Export
1. **Zero-Dependency Standalone Execution**:
   - Every `.odin` **Primer** and **Lab** compiles and runs standalone with `odin check <file>.odin -file` (or `odin check <lab_dir>`) and `odin run` without requiring `TracyClient.dll`, `TracyClient.lib`, or `tracy-profiler.exe`.
   - Use `#config(TRACY_ENABLE, false)` so `TRACY_ENABLE == false` compiles foreign Tracy calls down to zero machine instructions while running a standalone `RDTSC` / `time.Tick` ring-buffer console report, and `-define:TRACY_ENABLE=true` links `TracyClient` C symbols.
   - Every `.py` **Primer** and **Lab** runs with Python 3.12+ standard library only (`ctypes`, `sys.monitoring`, `time.perf_counter_ns`, `tracemalloc`, `json`), dynamically loading `TracyClient.dll` / `libTracyClient.so` via `ctypes` when present and falling back to an in-memory zone recorder when absent.
2. **Chrome Tracing / Spall Export Scope**:
   - Do **not** promise `.spall` or Chrome Tracing `.json` export inside every `.odin` **Primer**. In `tracy_how_to/`, Chrome Tracing / Perfetto JSON export (`ph="X"`, `"C"`, `"i"`, `pid`/`tid`) belongs specifically to Python units **`250`**, **`450`**, **`550`**, **`800/tracy_bridge.py`**, and **`950/profiler.py`**, plus Odin **Primer `500`** (Chrome/Spall export).

### 1.3 Layout, Voice & Hygiene Standards (`spec.md` §4 & `ADR-0002`)
1. **Quiet line-1 run hint**: `// odin run NNN_name.odin -file` (Odin Primers), `# python NNN_name.py` (Python Primers), `// odin run <lab_dir>` / `# python <lab_dir>/main.py` (Lab entries).
2. **Bottom `main` & 1 blank line after openings**: Multi-section **Primers** group topics into focused procedures/functions called sequentially from `main` at the **very bottom** of the file (`main :: proc()` in Odin; `def main() -> None:` + `if __name__ == "__main__": main()` in Python). Leave 1 empty line (two newlines) immediately after every `proc() {` and `def ...:` header.
3. **Comment blocks**:
   - Odin uses compact `/* ... */` blocks (`/*\nprose...\n*/`) with **zero** extra blank lines immediately after `/*` or before `*/`.
   - Python writes **all** prose explanations in `#` comments (zero `"""..."""` docstrings anywhere in `tracy_how_to/`).
4. **Causal voice, Feynman rule & hypothetical scenarios**:
   - Explain *why* the CPU, cache, allocator, or CPython VM behaves that way from first principles rather than pasting Five-Multipliers taxonomy bullet lists or slide-deck headers.
   - Explain every newly introduced keyword, directive, or library primitive immediately in plain language (Feynman style), pair syntax snippets with a concrete hypothetical before/body/after example (never `{ ... }` ambiguity), and keep every inline code expression unbroken on a single comment line.
5. **Banned noise & zero stubs**:
   - Zero legacy labels (`Prompt`, `Worked anchor`, `Suggested task`, `Signature:`, `Syntax:`, `cue:`, `exercise:`, ALL-CAPS `CONCEPT:`/`FRICTION:` banners), zero Markdown formatting (`**bold**`, backticks, `reST` double-backticks, `---`/`===` comment underlines, `$...$` LaTeX), and zero `1. / 2.` numbered **Drill** checklists.
   - Zero `_ =` silencers and zero `pass`, `yield`, or dummy `return 0` / `return ""` / `return {}` / `return []` stubs. Unimplemented helpers, classes, and methods live as `//` or `#` **Drills** specifying exact names, parameter types, and return types; starter sections contain tiny working **Scaffolds**.
6. **Depth, graduated Drills & verification**:
   - Core **Primers** target `~160–260` lines with `~8–12` graduated **Drills** (explicit convenience hints -> conversational recall -> open synthesis + post-fix trace validation). **Labs** are judged on clean module boundaries and topical coverage rather than arbitrary line ceilings.
   - Follow **Write-First, Verify-Once**: zero `.ps1` test harnesses, zero manifest JSONs, zero `solutions/` folders, and verify in one batched pass (`odin check ... -file`, `odin check <lab_dir>`, `odin build ... -build-mode:dll`, `python -B` `ast.parse`, and cross-repo hygiene sweep).

---

## 2. Cross-Repo Boundaries & Curriculum Inventory (`000`–`950`)

Keep `odin_how_to/`, `python_how_to/`, and `tracy_how_to/` strictly separate while preserving all numbered entries (`ADR-0001`):

- **`odin_how_to/` (`595`–`599`, `700`–`790`)**: Owns Odin language mechanics & raw hardware primitives (`core:prof/spall` in `595`, `RDTSC` repetition + `GB/s` in `597`, `#soa` in `700`, cache lines/`#align(64)` in `705`, `#simd` in `710`, IPC unrolling in `715`, standalone Haversine in `790`). Units `596`, `598`, and Lab `599` are slim Odin-idiom `when TRACY_ENABLE` / allocator / mutex integration hooks linking here rather than duplicating `tracy_how_to/`.
- **`python_how_to/` (`550`–`598`, `760`, `865`)**: Owns Python stdlib profiling, VM internals & FFI mechanics (`timeit` `550`, `cProfile` `560`, `dis` `570`, bytecode waste `575`, `mmap`/`memoryview` `580`, `array("d")` `585`, `ParticleSoAPool` `590`, Amdahl Haversine `592`, `__slots__`/`tracemalloc` `595`, `LINE` tracing `760`, `ctypes.from_buffer` `865`). Units `565`, `568`, and Lab `598` are slim stdlib wrappers linking here.
- **`tracy_how_to/` (`000`–`950` — 15 Primers + 3 Labs = 18 Units / 24 Files)**: Owns end-to-end cross-language telemetry, timeline forensics, `TracyC.h` / `ctypes` pinning, nested `Self Time` + recursive zones, named memory pools, thread tracks + GIL/`asyncio` freezes, `TracyPlot`/`TracyMessageC` + `P50`/`P95`/`P99` + Chrome JSON export, profiler-guided Multiplier #1–#4 triage, `sys.monitoring` callback distortion (`700`), hybrid FFI boundary tracing (`800`), and 5-system cold-herring Hotspot Hunt capstones (`900`/`950`). Do not re-teach basic `#soa`/`#simd` or `dis`/`mmap` syntax trivia here—link to the sibling workspaces and focus **Drills** on measuring, diagnosing, and validating fixes on traces.

| Unit | Language | Type | Focus |
| :--- | :--- | :--- | :--- |
| **`000_tracy_mental_model_and_five_multipliers.odin`** | Odin | Primer *(Pilot)* | Sampling vs. instrumentation, `RDTSC` vs. `tick_now()` distortion, `[16]Zone_Event` `%%` wraparound, Amdahl's Law, and IPC post-fix trace. |
| **`050_python_tracy_mental_model_and_multipliers.py`** | Python | Primer | `PyLongObject`/`PyFloatObject` sizing, `RingBufferProfiler` (`perf_counter_ns`), `dis.Bytecode` hotspot share, Amdahl prediction, and post-fix trace. |
| **`100_odin_tracy_c_api_and_zero_cost_flags.odin`** | Odin | Primer | `#config(TRACY_ENABLE, false)`, `TracyC.h` ABI layout, persistent `Srcloc` registry (zero `fmt.ctprintf` dangling pointers), `defer` leak safety, and off-vs-on timing. |
| **`150_python_tracy_ctypes_api_and_zero_cost_gates.py`** | Python | Primer | `ctypes.Structure` layout, `try_load_tracy_library()` + `SourceLocationRegistry` wired into `@tracy_instrument`, `try...finally` unwind, and identity zero-cost gate. |
| **`200_frame_marks_and_scoped_zones.odin`** | Odin | Primer | `@(deferred_out)` RAII zones, nested parent-stack `Self Time` + recursive `depth == 1` rule, `frame_mark` / `frame_mark_start`/`end`, `zone_value`, and post-fix spike drop. |
| **`250_python_frame_marks_and_scoped_zones.py`** | Python | Primer | `with tracy.zone(...)`, nested `Self Time` + recursive `depth == 1` accounting, `FrameMark` spike remediation, and Chrome JSON span export. |
| **`300_tracy_memory_allocator_and_arena_tracking.odin`** | Odin | Primer | `Tracy_Allocator` (`___tracy_emit_memory_alloc_named` / `free_named`), `backing` recursion guard, `mem.Arena` vs. heap churn (`0 B` steady state), and leak checks. |
| **`350_python_tracy_memory_and_object_churn.py`** | Python | Primer | `tracemalloc` + `gc.get_stats()` per zone: retained leaks vs. Gen-0 GC sweep (`threshold 700`) vs. `__slots__` pools and `0 B` `array("d")` reuse. |
| **`400_thread_naming_locks_and_false_sharing.odin`** | Odin | Primer | **Multiplier #5**: Safe persistent thread naming, mutex wait/hold vs. thread-local merge, timeline spans, and 3-way `#align(64)` false-sharing comparison. |
| **`450_python_threads_gil_and_asyncio_traces.py`** | Python | Primer | **Multiplier #5**: Isolated GIL-bound vs. GIL-releasing threads (`wall_ns - thread_time_ns`), `asyncio` blocking-`sleep` freeze + `to_thread` fix, and multi-`tid` Chrome JSON. |
| **`500_tracy_plots_messages_and_frame_budgets.odin`** | Odin | Primer | `TracyPlot`, `TracyMessageC`, real cache/entity compute bursts, `P50`/`P95`/`P99` 16.67 ms budget analysis, Chrome/Spall export, and post-fix verification. |
| **`550_python_plots_messages_and_frame_budgets.py`** | Python | Primer | Live GC/cache-miss plotting, timeline markers, `P50`/`P95`/`P99` budgets, Chrome Tracing / Perfetto JSON export, and post-fix remediation. |
| **`600_diagnosing_waste_ipc_simd_and_cache_in_tracy.odin`** | Odin | Primer | **Multipliers #1–#4**: `cycles/item` + `effective_gb_per_sec` triage across Waste, L1/L2/L3 cache sweep (`#soa`), 4-way IPC unrolling, and direct-store `#simd[4]f32`. |
| **`650_diagnosing_python_waste_cache_and_ipc.py`** | Python | Primer | **Multipliers #1–#4**: `ns/item`, `dis.Bytecode(..., adaptive=True)`, `memoryview` MB/s, AoS -> hoisted SoA -> C-backed reduction / FFI preview. |
| **`700_python_tracy_zones_and_sys_monitoring.py`** | Python | Primer | Python 3.12 `sys.monitoring` (`PY_START`/`PY_RETURN`) callback distortion, `sys.monitoring.DISABLE`, and `PY_UNWIND` exception cleanup. |
| **`800_hybrid_python_odin_tracy_offload_lab/`** | Python + Odin | Lab (3 files) | Unified Python <-> Odin `.dll` timeline (`main.py`, `tracy_bridge.py`, `odin_simd_kernel.odin`), Chrome JSON layers, and `N`-size FFI crossover. |
| **`900_hotspot_hunt_five_multipliers_lab/`** | Odin | Lab (3 files) | Odin capstone (`main.odin`, `profiler.odin`, `simulation.odin`): persistent `Srcloc` table, 2 hotspots vs. cold herrings, `0` allocs, and full checksum parity. |
| **`950_python_hotspot_hunt_five_multipliers_lab/`** | Python | Lab (3 files) | Python capstone (`main.py`, `profiler.py`, `simulation.py`): nested `Self Time` + `tracemalloc`, Chrome JSON export, cold preservation, and `0 B` `array("d")` speedup. |

---

## 3. Per-Unit Technical & Pedagogical Blueprint (`000`–`950`)

### `000_tracy_mental_model_and_five_multipliers.odin` *(Approved Pilot — Odin Primer, 206 lines, 8 Drills)*
- **Core Goal**: Ground why measurement precedes optimization (95%/5% rule + Amdahl's Law), contrast timer-based sampling profilers with `RDTSC` instrumentation profilers (Tracy/Spall), and demonstrate profiler self-distortion and post-fix trace verification directly in standalone Odin.
- **Machine Mechanics & Concepts**:
  - `intrinsics.read_cycle_counter()` (`RDTSC` / `CNTVCT_EL0`) vs. OS `time.tick_now()` (`QueryPerformanceCounter` / `clock_gettime`).
  - Lock-free fixed `[16]Zone_Event` ring buffer with Odin's floored modulo `%%` (`rb.count %% len(rb.events)`) to avoid heap allocations inside timed zones.
  - Compiler dead-code elimination (DCE) under `-o:speed` and why computed sinks must be printed or consumed.
- **Sections & Drills**:
  - Top-level **Scaffold**: `Zone_Event`, `Zone_Ring_Buffer`, `//` **Drills** for `begin_zone` and `end_zone` (zero dummy bodies).
  - `timers_and_overhead`: Back-to-back `RDTSC` vs. `tick_now()` starter **Scaffold**, plus **Drills** benchmarking 1,000 calls of each and contrasting 1 coarse batch zone vs. 50,000 inner-loop zones (`~89%` distortion).
  - `ring_buffer_and_wraparound`: Starter **Scaffold**, plus **Drill** pushing 20 zones (`z0`..`z19`) and inspecting wraparound slots `0..=3` vs. `4..=15`.
  - `amdahl_pipeline_and_multipliers`: Starter cold check **Scaffold**, plus **Drills** for `amdahl_speedup`, a 3-stage pipeline (`cold_init`, `hot_serial_loop`, `cold_report`), and a **post-fix IPC trace** (`hot_unrolled_loop` with 4 independent accumulators `s0..s3` verifying measured speedup).
  - `main` at the bottom.

### `050_python_tracy_mental_model_and_multipliers.py` *(Python Primer)*
- **Core Goal**: Apply the Tracy hotspot model to CPython by measuring why `PyObject` boxing and interpreter dispatch dominate naive Python loops, building a `RingBufferProfiler`, predicting gains with Amdahl's Law, and verifying a post-fix trace.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - **Strip the pre-solved `RingBufferProfiler` body (`050:97-115`)**: Convert all `RingBufferProfiler` methods (`zone`, `record`, `summary`) into `#` **Drills** specifying exact method signatures and behavior (with only a tiny working baseline **Scaffold** in each section and zero `pass` or dummy `return` stubs).
  - Add a `sys.getsizeof` probe inspecting `PyLongObject` / `PyFloatObject` memory footprint vs. raw 8-byte machine scalars.
  - Add a **post-fix trace validation** **Drill**: rewrite `sum_coordinates_hot` with hoisted `LOAD_FAST` locals / C-backed `sum()`, re-run `RingBufferProfiler`, and compare measured speedup against `amdahl_max_speedup`.
- **Sections**: `boxing_and_bytecode_waste`, `ring_buffer_and_amdahl`, `baseline_vs_optimized_trace`, `main` at bottom.

### `100_odin_tracy_c_api_and_zero_cost_flags.odin` *(Odin Primer)*
- **Core Goal**: Bind Tracy's C ABI (`TracyC.h`: `___tracy_source_location_data`, `___tracy_c_zone_context`, `___tracy_emit_zone_begin`, `___tracy_emit_zone_end`, `___tracy_emit_frame_mark`) using `#config(TRACY_ENABLE, false)` and `when TRACY_ENABLE` so disabled builds emit zero instructions.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - **Eliminate the `fmt.ctprintf` dangling-pointer bug (`100:74-75`)**: Explain causally why Tracy's background telemetry thread reads `Tracy_Source_Location_Data` pointers asynchronously *after* the instrumented procedure returns—so passing `fmt.ctprintf` (`context.temp_allocator`) into `.function`/`.file` or `.name` creates a use-after-free hazard as soon as the temp arena resets.
  - Replace with compile-time static/constant `cstring` literals or a **persistent `@(static)` / fixed `Srcloc` registry table** (`register_srcloc`), verify `size_of` / `offset_of` C ABI layout, add a **Drill** contrasting early-return zone leaks against `defer zone_end(ctx)` / `@(deferred_out)`, and benchmark `TRACY_ENABLE == false` dead-code elimination vs. `true`.
- **Sections**: `c_abi_layout_and_lifetime`, `zero_cost_gates_and_zones`, `early_return_safety_and_timing`, `main` at bottom.

### `150_python_tracy_ctypes_api_and_zero_cost_gates.py` *(Python Primer)*
- **Core Goal**: Bind `TracyClient.dll` / `libTracyClient.so` from pure Python via `ctypes.Structure`, keep source-location pointers pinned for Tracy's background C thread, and build a zero-overhead decorator gate.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - **Wire `try_load_tracy_library()` and `SourceLocationRegistry` directly into `@tracy_instrument`** rather than leaving them disconnected.
  - Explain `argtypes` / `restype` C ABI truncation risks when binding `___tracy_emit_zone_begin` (`ctypes.POINTER(TracySourceLocationData)` -> `TracyCZoneCtx`) and fallback behavior when no shared library is present.
  - Include **Drills** verifying `ctypes.sizeof(TracyCZoneCtx) == 8`, pinned `bytes` + struct retention in `SourceLocationRegistry`, `disabled_fn is original_fn` identity check, `disabled` vs. `enabled` call-overhead timing, and `try ... finally:` exception-safe zone closing.
- **Sections**: `ctypes_abi_and_pinned_registry`, `library_loader_and_zero_cost_gate`, `overhead_and_exception_safety`, `main` at bottom.

### `200_frame_marks_and_scoped_zones.odin` *(Odin Primer)*
- **Core Goal**: Use `@(deferred_out = zone_end)` for 1-line RAII scoped zones, `FrameMark` / `frame_mark_start` / `frame_mark_end` for frame slicing, `zone_text` / `zone_value` for spike attribution, and nested parent-stack `Self Time` accounting.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - **Add nested `Self Time` parent-stack accounting (`self_cycles = elapsed - child_cycles`)** to achieve 1:1 parity with `250`, plus a **recursive zone Drill** applying the *Computer, Enhance!* Part 2 `depth == 1` rule so recursive self-calls do not double-count inclusive time.
  - Cover discontinuous `frame_mark_start` / `frame_mark_end` for secondary periodic subsystems alongside primary `frame_mark()`.
  - Add a **post-fix trace validation Drill**: diagnose Frame #3's entity-count spike (`zone_value = 4096`), remediate the quadratic/heavy bottleneck, and re-run to confirm Frame #3 drops below the 16.67 ms budget.
- **Sections**: `scoped_zones_and_nested_self_time`, `recursive_zones_and_discontinuous_frames`, `frame_spike_triage_and_fix`, `main` at bottom.

### `250_python_frame_marks_and_scoped_zones.py` *(Python Primer)*
- **Core Goal**: Implement nested `@contextmanager` scoped zones separating `Self Time` (`elapsed_ns - child_ns`) from `Inclusive Time`, recursive zone handling, `FrameMark` budget spike detection, and Chrome JSON span export.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - **Add a recursive zone Drill** tracking active call depth per zone name so `inclusive_ns` only accumulates when `depth == 1`, preventing >100% inclusive-time inflation.
  - Add a **post-fix trace validation Drill** remediating Frame #4's `Narrowphase` spike (`value=2000`) and confirming the frame histogram falls under 16.67 ms, plus Chrome JSON `"ph": "X"` span inspection.
- **Sections**: `nested_self_time_and_recursion`, `frame_marks_and_spike_tags`, `post_fix_trace_and_json_export`, `main` at bottom.

### `300_tracy_memory_allocator_and_arena_tracking.odin` *(Odin Primer)*
- **Core Goal**: Wrap Odin's `context.allocator` in a `Tracy_Allocator` (`runtime.Allocator_Proc`) emitting named pool events (`___tracy_emit_memory_alloc_named` / `free_named`), catch per-frame heap churn and leaks, and compare against `mem.Arena` / `context.temp_allocator`.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - **Contrast per-frame heap churn against a real `mem.Arena` / `context.temp_allocator` + `free_all` multi-frame loop** achieving `0` backing-heap allocations after setup (`post-fix trace validation`).
  - Explain causally why `Tracy_Allocator`'s internal `active_allocs` map must use `t_alloc.backing` rather than `context.allocator` (infinite allocator recursion), and test `.Resize` and `.Free_All` modes.
  - Include an intentional **leak-diagnosis Drill** proving `current_bytes > 0` flags unfreed frame allocations.
- **Sections**: `tracy_allocator_and_recursion_guard`, `heap_churn_vs_arena_reuse`, `leak_diagnosis_and_resize`, `main` at bottom.

### `350_python_tracy_memory_and_object_churn.py` *(Python Primer)*
- **Core Goal**: Combine `tracemalloc` and `gc.get_stats()` / `gc.get_count()` inside named memory zones to distinguish retained leaks, transient `PyObject` GC churn, `__slots__` object-pool reuse, and zero-alloc `array("d")` buffers.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - Contrast all four memory signatures: (1) **retained leak** (`net_delta_bytes > 0` across frames), (2) **transient GC churn** (`net == 0`, `peak >> 0`), (3) **`__slots__` pool reuse**, and (4) **`array("d")` steady-state reuse** (`net == 0`, `peak == 0`).
  - Demonstrate a real **Generation-0 GC sweep** crossing `gc.get_threshold()[0]` (`700`) mid-frame inside a high-churn zone, plus a **post-fix trace validation Drill** verifying `0` GC collections and `0 B` net growth after switching to `array("d")`.
- **Sections**: `memory_zone_tracker_and_gc_stats`, `leak_vs_churn_vs_slots_pool`, `zero_alloc_array_post_fix`, `main` at bottom.

### `400_thread_naming_locks_and_false_sharing.odin` *(Odin Primer — Multiplier #5)*
- **Core Goal**: Diagnose **Multiplier #5 (Multithreading)** failures using thread naming, lock wait-vs-hold instrumentation, per-thread timeline spans, and cache-line alignment (`#align(64)`).
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - **Safe persistent thread naming**: Forbid relying on `fmt.ctprintf` across worker lifetimes; use static/arena-pinned `cstring` names (`Worker_0`..`Worker_3`).
  - **3-way false-sharing Drill** grounded in MESI cache-coherency invalidations: compare unaligned `[4]i64` (false sharing on 1 cache line) vs. `[4]Padded_Slot` (`#align(64)` direct slot writes) vs. thread-local register accumulation written once at the end.
  - Add per-thread `[start_cycle, end_cycle]` span timestamps showing serialization vs. overlap, plus a **mutex remediation Drill** replacing lock-in-loop with thread-local reduction + single merge (`wait_cycles -> 0`).
- **Sections**: `thread_naming_and_timeline_spans`, `mutex_contention_and_local_merge`, `three_way_false_sharing_lab`, `main` at bottom.

### `450_python_threads_gil_and_asyncio_traces.py` *(Python Primer — Multiplier #5)*
- **Core Goal**: Separate GIL-bound CPU thread serialization from GIL-releasing I/O overlap, measure explicit `threading.Lock` contention, and diagnose blocking `asyncio` event-loop freezes.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - **Cleanly isolate GIL-bound pure-Python CPU threads** (`wall_ns` vs. `thread_time_ns` showing sequential turn-taking without an artificial `sleep` inside a lock) **from GIL-releasing I/O / sleep threads** (overlapping across OS `tid` tracks).
  - Separate `threading.Lock` wait/hold contention measurement into its own focused Drill.
  - Demonstrate a synchronous blocking `time.sleep` inside an `asyncio` coroutine freezing all sibling coroutines on the event-loop track, then **remediate with `asyncio.to_thread`** and verify concurrent overlap (`total_wall_ms < sum_of_task_ms`) via exported multi-`tid` Chrome JSON tracks.
- **Sections**: `gil_cpu_vs_io_threads`, `lock_wait_vs_hold_contention`, `asyncio_freeze_and_to_thread_fix`, `main` at bottom.

### `500_tracy_plots_messages_and_frame_budgets.odin` *(Odin Primer)*
- **Core Goal**: Correlate `TracyPlot` numerical series (`Number`, `Memory`, `Percentage`) and `TracyMessageC` state markers against a 16.67 ms (60 FPS) frame budget, compute latency percentiles, export Chrome/Spall JSON, and verify post-fix remediation.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - **Replace fake `time.sleep` delays** (`500:122-124`) with real cache/entity compute bursts so frame durations reflect actual CPU work.
  - Add **`P50`/`P95`/`P99` percentile frame-budget analysis**, **Chrome/Spall trace export** (explicitly scoped here for Odin), and a **post-fix trace validation Drill** confirming `P95`/`P99` drop back under 16.67 ms after fixing the entity/cache burst.
- **Sections**: `plots_and_colored_messages`, `compute_burst_and_percentiles`, `chrome_spall_export_and_post_fix`, `main` at bottom.

### `550_python_plots_messages_and_frame_budgets.py` *(Python Primer)*
- **Core Goal**: Emit `TracyPlot` (`ph="C"`) curves and `TracyMessage` (`ph="i"`) markers in Python, compute `P50`/`P95`/`P99` frame budgets, export Chrome Tracing / Perfetto JSON, and verify post-fix remediation.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - **Replace hardcoded `CacheHitPct = 12.0 / 98.0` constants** (`550:111-113`) with a real measured hit/miss counter (cache lookup simulation or real Gen-0 GC pressure) driving frame duration.
  - Include **`P50`/`P95`/`P99`** reporting, Chrome Tracing JSON (`ph="X"`, `"C"`, `"i"`) verification, and a **post-fix trace validation Drill** proving `P95` drops below budget once the invalidation storm is fixed.
- **Sections**: `flight_recorder_plots_and_messages`, `real_cache_miss_and_percentiles`, `chrome_json_and_post_fix_budget`, `main` at bottom.

### `600_diagnosing_waste_ipc_simd_and_cache_in_tracy.odin` *(Odin Primer — Multipliers #1–#4)*
- **Core Goal**: Use profiler metrics (`cycles_per_item`, `effective_gb_per_sec`, Self vs. Total Time) to diagnose and eliminate **Multipliers #1–#4** cleanly one bottleneck at a time, and observe the L1 -> L2 -> L3 cache throughput cliff.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - Add an explicit **Multiplier #1 (Waste)** baseline stage (`> 20 cycles/item` from redundant helper calls, formatting, or temp allocations) cleanly separated from **Multiplier #4 (AoS Cache Misses)**, **Multiplier #2 (IPC 4-way unrolling)**, and **Multiplier #3 (`#simd[4]f32`)**.
  - Add **`effective_gb_per_sec`** alongside `cycles_per_item`.
  - Add an **L1 / L2 / L3 working-set size sweep** (moving beyond `1024` items so cache bandwidth cliffs appear clearly in measurements).
  - Replace `simd.to_array` copy loops (`600:80`) with **direct `#simd[4]f32` vector loads/stores**, linking to `odin_how_to/700, 705, 710, 715` for Odin syntax details.
- **Sections**: `zone_diagnosis_metrics`, `isolated_multiplier_stages`, `l1_l2_l3_working_set_sweep`, `main` at bottom.

### `650_diagnosing_python_waste_cache_and_ipc.py` *(Python Primer — Multipliers #1–#4)*
- **Core Goal**: Diagnose hot Python zones by `ns/item`, executed adaptive VM opcodes, and `memoryview` byte bandwidth (`MB/s`), progressing from AoS object loops to hoisted SoA `array("d")`, C-backed reductions, and FFI offload awareness.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - Inspect **`dis.Bytecode(fn, adaptive=True)`** loop-body opcodes rather than static full-function instruction count.
  - Compute true **`memoryview` bytes/item (`mv.nbytes / len(mv)`) and effective MB/s** instead of hardcoding `16` bytes/item.
  - Progress cleanly across Stage 1 (AoS object loop), Stage 2 (hoisted `LOAD_FAST` + SoA `array("d")`), Stage 3 (C-backed `sum()` / `math.sumprod` / `memoryview`), plus a short **Drill** noting when no built-in C reducer exists (`ctypes`/Odin offload preview linking to `800`). Link to `python_how_to/570, 580, 585` for raw VM/`memoryview` fundamentals.
- **Sections**: `adaptive_bytecode_and_bandwidth_metrics`, `aos_to_soa_to_c_reduction`, `when_builtins_arent_enough`, `main` at bottom.

### `700_python_tracy_zones_and_sys_monitoring.py` *(Python Primer)*
- **Core Goal**: Instrument Python functions transparently via Python 3.12+ `sys.monitoring` (`PY_START`, `PY_RETURN`, `PY_UNWIND`), measure callback overhead directly, and eliminate overhead on cold/hot boundaries with `sys.monitoring.DISABLE`.
- **Required Gap & Bug Fixes (`spec.md` §5.2)**:
  - Attach **`sys.monitoring` callbacks directly** to measure callback distortion on a hot inner helper vs. coarse pipeline stages (rather than benchmarking only `@contextmanager` loops).
  - Add a **Drill** returning **`sys.monitoring.DISABLE`** from a callback to drop future monitoring overhead to zero after first hit.
  - Add a **`PY_UNWIND` exception-unwind Drill** raising an exception inside a monitored target to prove active profiler zones close cleanly without corrupting the call stack.
- **Sections**: `sys_monitoring_auto_zones`, `callback_distortion_and_disable`, `py_unwind_exception_safety`, `main` at bottom.

### `800_hybrid_python_odin_tracy_offload_lab/` *(Multi-File Lab — Python + Odin)*
- **Files**: `main.py`, `tracy_bridge.py`, `odin_simd_kernel.odin`
- **Core Goal**: Keep high-level orchestration in Python, store coordinates in contiguous `array("f")` SoA buffers, offload the 95% hotspot across `ctypes` to an Odin `#simd[4]f32` DLL kernel, and inspect both Python and Odin layers on one timeline.
- **Lab Scaffold Boundaries & Required Fixes (`spec.md` §4.4, §5.2)**:
  - Keep `SAMPLE_CORPUS`/input generation, `load_odin_simd_kernel`, and naive Python baseline as **Scaffold**; keep kernel math and bridge recorder/exporter methods as `#`/`//` **Drills** (zero dummy `return` or `pass` stubs).
  - `tracy_bridge.py`: add **Chrome Trace JSON export** (`pid`/`tid` layers separating Python orchestration from Odin native kernel zones).
  - `odin_simd_kernel.odin` + `main.py`: add an **`N`-size FFI crossover Drill** comparing tiny `N = 16` (where `ctypes` call overhead dominates) against `N = 50_000` (where Odin `#simd[4]f32` wins >50x), verifying checksum parity and automatic pure-Python fallback if the `.dll` is not built.

### `900_hotspot_hunt_five_multipliers_lab/` *(Multi-File Lab — Odin Capstone)*
- **Files**: `main.odin`, `profiler.odin`, `simulation.odin`
- **Core Goal**: Profile a 5-system Odin simulation (`load_world_config`, `build_spatial_tags`, `step_entity_kinematics`, `evaluate_sensor_polynomials`, `audit_frame_checksum`), ignore the cold `<1%` herrings, fix only the 2 true hotspots across Multipliers #1–#4, and prove parity.
- **Lab Scaffold Boundaries & Required Fixes (`spec.md` §4.4, §5.2)**:
  - `profiler.odin`: provide nested `Self Cycles` + `Tracking_Allocator` **Scaffold** and add a **persistent fixed `Srcloc` table** (preventing overwrites/dangling pointers), with open **Drills** for zone stack enter/exit and hotspot report formatting.
  - `simulation.odin`: remove the extreme `math.pow` outlier in `evaluate_sensor_polynomials` so Multipliers #2 (IPC) & #3 (Horner + `#simd[4]f32`) isolate cleanly; fix `audit_frame_checksum` to check **full-state buffer parity** rather than 64 strided elements; keep baseline systems as **Scaffold** and optimized replacements as `//` **Drills**.
  - `main.odin`: verify cold systems (`<1%`) remain unmodified, assert `0` heap allocations in optimized frames, assert full-state checksum parity, and print before/after hotspot triage tables.

### `950_python_hotspot_hunt_five_multipliers_lab/` *(Multi-File Lab — Python Capstone)*
- **Files**: `main.py`, `profiler.py`, `simulation.py`
- **Core Goal**: Profile a 5-stage Python simulation (`load_world_config`, `build_tag_lookup`, `step_entity_kinematics`, `compute_signal_energy`, `audit_frame_checksum`), ignore cold `<1%` functions, fix the 2 true hotspots using SoA `array("d")` + C-backed bulk reduction, and prove `0 B` steady-state allocations.
- **Lab Scaffold Boundaries & Required Fixes (`spec.md` §4.4, §5.2)**:
  - `profiler.py`: add **Chrome Trace JSON export** and optional `TracyClient.dll` hook parity alongside nested `self_ns` + `tracemalloc` delta tracking (`#` **Drills** for recorder/exporter methods, zero `pass` stubs).
  - `simulation.py`: keep `SimWorld` contracts and baseline slow systems as **Scaffold**; leave `step_entity_kinematics_fast` (`array("d")` SoA, `0 B` allocs) and `compute_signal_energy_fast` (hoisted `LOAD_FAST` + C-backed reduction) as `#` **Drills**.
  - `main.py`: assert checksum parity within `1e-9`, assert `0 B` net heap growth per optimized frame, assert cold functions remain unmodified, and verify multi-frame `P95` and total speedup breakdown.
