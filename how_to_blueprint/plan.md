# Generalized `<topic>_how_to/` Curriculum Blueprint & Authoring Playbook

Use this blueprint whenever planning, scaffolding, or rewriting a `<lang>_how_to/` or `<tool>_how_to/` learning workspace in any programming language (e.g., Odin, Python, Tracy, C, Rust, Zig, Jai, Go, TypeScript). Pointing an agent at this document provides all standing architectural, formatting, pedagogical, and verification rules upfront so no pre-execution interview is needed.

---

## 1. Core Philosophy & Canonical Vocabulary (`GLOSSARY.md`)

A `how_to/` workspace teaches a language or systems tool through **runnable, top-to-bottom source files** modeled on the conversational, first-principles commentary of `CodingTemplateExamples/how_to/`, paired with live starter **Scaffolds** and open hands-on **Drills**.

Always use these four canonical terms in plans, docs, tickets, and comments:

| Canonical Term | Definition | Strictly Banned Synonyms |
| :--- | :--- | :--- |
| **Primer** | A self-contained single-file learning unit run directly from the workspace folder. | *lesson file, exercise file, sample, tutorial script* |
| **Lab** | A numbered multi-file subfolder (`NNN_<name>_lab/`) for concepts spanning multiple files, packages, or build targets (e.g., package visibility, hot-reload DLLs, multi-module capstones). | *module folder, project lesson, subproject* |
| **Scaffold** | Minimal pre-written starter code that compiles/runs out of the box and anchors syntax (`~5–20%` soft guideline in a **Primer**; shared domain contracts & setup boilerplate in a **Lab**). | *template, skeleton, worked anchor, boilerplate stub* |
| **Drill** | A conversational `//` or `#` comment guiding hands-on coding practice and IDE autocompletion inside an open section. | *Prompt, Step N (Prompt), TODO, cue, exercise, suggested task* |

---

## 2. Workspace Architecture & Packaging Rules (`ADR-0001`)

1. **Flat Single-Folder Workspace + Numbered Lab Subfolders**:
   - All standalone **Primers** live together in one flat `<topic>_how_to/` directory with 3-digit prefixes (`000_...`, `001_...`, `005_...`, ..., `930_...`) so learners can browse the entire curriculum in a single file tree.
   - Multi-file **Labs** live in numbered subdirectories inside the same folder (`300_..._lab/`, `830_..._lab/`, `950_..._lab/`).
   - In languages where a directory normally compiles as one package (such as Odin or Go), run standalone **Primers** in single-file mode (`odin run <primer>.odin -file`, `go run <primer>.go`) and **Labs** as directory packages (`odin run <lab_dir>`).
2. **Keep Separate Topics in Separate Workspaces**:
   - Keep language and tool curricula in distinct root folders (e.g., `odin_how_to/`, `python_how_to/`, `tracy_how_to/`). When a language workspace touches an external tool covered by its own workspace (e.g., Tracy profiling hooks), keep the language **Primer** focused on native language/stdlib wrappers and cross-link to the dedicated tool workspace rather than duplicating long lectures or capstone pipelines.
3. **Forbidden Artifacts**:
   - **Zero `solutions/` directories** anywhere in the repository.
   - **Zero external `.ps1` / `.sh` test harnesses or manifest JSONs**—verification uses a single post-authoring batched compiler/AST/regex pass (see Section 8).

---

## 3. File Structure, `4+` Lesson Functions, & Non-Strict Length Targets

### 3.1 The `4+` Lesson Function Structure with `main` at the Very Bottom
Every **Primer** is organized as a sequence of self-contained **"lesson functions"** (topic procedures/functions) called from `main` at the bottom of the file:

1. **Line 1 Quiet Run Hint**:
   - Place a single, quiet comment on line 1 showing the exact command to run or test the file (with no banner borders around it):
     - `// odin run 045_for_loops.odin -file`
     - `# python 050_for_while_and_loop_else.py`
     - `// cargo script 045_ownership.rs` (or `rustc 045_ownership.rs && ./045_ownership`)
2. **`4 or More` Focused Topic Functions per Standard Primer**:
   - Break each standard **Primer** into **4 or more topic functions** (e.g., `for_loops_and_lazy_ranges`, `while_sentinels_and_continue_traps`, `loop_else_and_nested_early_returns`, `iteration_mutation_trap_preview`).
   - Each topic function acts as a mini-lesson containing:
     1. Conversational first-principles prose explaining the mechanics, keywords, and concrete hypothetical scenarios.
     2. A tiny, live working **Scaffold** (1–4 statements) that runs out of the box and demonstrates the baseline construct.
     3. **`2–4` graduated `#` / `//` Drills** right below the **Scaffold** for the learner to implement inside that function.
   - *(Exception)*: Naturally narrow single-directive or single-helper **Primers** may use **2–3 topic functions** when 4 would force artificial padding.
3. **`main` Always at the Very Bottom**:
   - Place `main` (`main :: proc()`, `def main() -> None:` + `if __name__ == "__main__": main()`, `fn main()`) at the **very bottom of the file**.
   - Inside `main`, call each topic function in order, preceded by a runtime section banner print:
     ```python
     def main() -> None:

         print("=== 1. For loops and lazy ranges ===")
         for_loops_and_lazy_ranges()

         print("\n=== 2. While, sentinels, and continue traps ===")
         while_sentinels_and_continue_traps()

         print("\n=== 3. Loop-else and nested early returns ===")
         loop_else_and_nested_early_returns()

         print("\n=== 4. Mutation-during-iteration trap preview ===")
         iteration_mutation_trap_preview()


     if __name__ == "__main__":
         main()
     ```
   - Putting `main` at the bottom lets learners read top-to-bottom while allowing anyone to scroll straight to the bottom to see the file's table of contents at a glance.

### 3.2 Soft, Non-Strict Length, Drill & Scaffold Ranges
Treat all line counts, **Drill** counts, and **Scaffold** percentages as **soft pedagogical targets, never rigid pass/fail linter gates**:

| Unit Type | Target Line Range (Soft) | Lesson Functions | Graduated Drills | Starter Scaffold Range (Soft) |
| :--- | :---: | :---: | :---: | :---: |
| **Core / Standard Primer** | **`~160–300+` lines** *(soft floor `~150L`)* | **`4+` functions** | **`~8–15+` Drills** | **`~5–20%`** live code (`1–4` lines/section) |
| **Naturally Narrow Primer** *(single directive / narrow utility)* | **`~90–145` lines** *(soft floor `~85L`)* | **`2–3` functions** | **`~4–7` Drills** | **`~5–20%`** live code (`1–4` lines/section) |
| **Multi-File Lab** (`NNN_<name>_lab/`) | **Unbounded** *(sized by clean module seams)* | Clean entry + module files | **`~6–15+` Drills** across files | Shared ABI/domain types + setup boilerplate |

- **Why ranges are non-strict**: A rich core topic (like loops, strings, allocators, or concurrency) naturally spans `180–290` lines across `4–5` lesson functions, whereas a single-directive topic stays crisp at `100–130` lines. Never pad a file with obscure CLI flag trivia or repetitive busywork just to cross a line threshold, and never truncate a good explanation to stay under a ceiling.
- **Flexible comment & Scaffold balance**: The `~5–20%` **Scaffold** figure is a rule of thumb. Include enough runnable starter code so imports/variables are genuinely used and the learner sees immediate console output, while keeping the meat of the topic in conversational prose and open **Drills**.

---

## 4. Exact Whitespace, Comment & Syntax Hygiene Rules (`ADR-0002`)

1. **One Blank Line After Every Function/Procedure Opening**:
   - Always leave **1 empty line (two newlines)** immediately after every procedure or function opening header (`my_section :: proc() {`, `def my_section() -> None:`, `fn my_section() {`) before the first comment or code line.
   - *(Scoped docstring exception)*: If a function carries a 1-line docstring specifically to demonstrate runtime `__doc__` or `doctest`, place the 1 empty line immediately after that 1-line docstring.
2. **Compact Block Comments (`/* ... */`) vs. Line Comments (`#` / `//`)**:
   - **Compiled / brace languages (`/* ... */` + `//`)**: Use compact `/* ... */` blocks for multi-line explanations and `//` for **Drills** and short notes. Never leave an empty blank line immediately after `/*` or immediately before `*/`:
     ```odin
     /*
     Good: prose starts on the line right after /* and closes right after the last line.
     */
     ```
   - **Python & languages where `"""..."""` is a runtime string (`#` only)**: Write **100% of prose explanations and Drills in `#` comments**. Because `"""..."""` is a runtime string literal that renders in low-contrast string colors in most IDE themes and populates `__doc__` in memory, forbid `"""..."""` / `'''...'''` everywhere except:
     1. Assigned/printed multi-line string values in the dedicated strings **Primer**.
     2. Minimal 1-line `__doc__` inspection targets in the dedicated functions/decorators/dynamic-import **Primers**.
     3. Target functions carrying `>>>` examples in a dedicated `doctest` **Primer**.
3. **Never Split Inline Code Expressions Across Comment Line Wraps**:
   - When a comment or **Drill** includes an inline code statement, signature, or loop header, keep the entire code expression unbroken on a single comment line (wrap prose *before* or *after* the code expression, never mid-statement):
     - Good:
       ```odin
       // Loop over scores using for score, idx in scores and print each pair.
       ```
     - Bad (splits `for score, idx in scores` across lines):
       ```odin
       // Loop over scores using for score, idx
       // in scores and print each pair.
       ```
4. **Zero Markdown, ReST, LaTeX, or Label Noise in Source Comments**:
   - Source files are read directly in an IDE text editor, not rendered through a Markdown previewer. Comments and strings must contain **zero**:
     - Legacy/textbook labels: `Prompt`, `Step N`, `Worked anchor`, `Suggested task`, `Signature:`, `Syntax:`, `cue:`, `exercise:`, `TODO:`, `CONCEPT:`, `FRICTION:`.
     - Markdown/ReST formatting: `**bold**`, `*italics*`, single backticks (`` ` ``), `reST` double-backticks (```` `` ````), fenced code blocks (```` ``` ````), or `$...$` LaTeX math (`$O(1)$` -> write `O(1)`).
     - Comment underline dividers: `// ---`, `# ---`, `// ===`, `# ===` (`===` is allowed **only** inside runtime `print("=== 1. ... ===")` string literals in `main`).
     - Numbered checklist **Drills** (`// 1. Do X`, `// 2. Do Y`)—separate distinct **Drills** with 2 blank lines and write each as natural conversational prose.

---

## 5. Pedagogical Voice: First-Principles, Feynman Rhythm & Hypotheticals

1. **First-Principles Causal Explanations (`CodingTemplateExamples` Voice)**:
   - Explain *why* the language, memory model, compiler, or CPU works the way it does (stack vs. heap, cache lines, pointer aliasing, iterator state, ABI layout) rather than listing dry syntax rules or slide-deck taxonomies.
   - Prefer everyday combinations and real-world bugs over obscure standard-library flag trivia.
2. **The Feynman Immediate-Explanation Rhythm**:
   - Whenever introducing a new keyword, directive, operator, or stdlib construct (e.g., `#reverse`, `for &val`, `defer`, `:=`, `enumerate`, `contextmanager`, `RDTSC`), explain what it means **immediately right at that spot** in plain, conversational words:
     > *"When we put #reverse in front of a collection loop, it means Odin starts at the final index (len - 1) and steps backward down to 0."*
   - Treat "new construct followed immediately by plain-English explanation" as a natural guiding rhythm rather than rigid mechanical bookkeeping.
3. **The Concrete Hypothetical Scenario Rule (No Ambiguous `{ ... }`)**:
   - Never write prose snippets with vague `{ ... }` or `...` placeholders that force the learner to guess initial values, variable scope, or side effects.
   - Always pair a construct with a concrete before / body / after scenario using real values and explicit scoping notes:
     > *"Suppose nums := [3]int{10, 20, 30}. Running for &val in nums { val += 1 } mutates each element in place so nums becomes {11, 21, 31}, and val only exists inside the loop body."*
4. **Graduated Drill Progression (Unlabeled)**:
   - Without adding any tier labels, graduate the **Drills** across each **Primer**:
     - **Early Drills**: Explicit convenience guidance naming exact types, variable names, and function calls so the learner and IDE autocomplete build momentum.
     - **Mid-file Drills**: Conversational recall combining the current construct with earlier concepts.
     - **Late-file Drills**: Open synthesis tasks (e.g., nested loops/structures, edge-case filtering, before/after measurement, or `// Try uncommenting:` / `# Try uncommenting:` compiler/runtime error experiments).

---

## 6. Zero Dummy Stubs, Zero `_ =` Silencers, & Multi-File Lab Seams

1. **Zero Unused-Variable Silencers**:
   - Never emit `_ = x`, `(void)x`, or dummy discard statements just to silence unused-variable or unused-import warnings.
   - Every pre-imported package/module and every starter variable in a **Primer** or **Lab** must be genuinely used by the live 1–4 line starter **Scaffold** in that section.
2. **Zero Dummy Function/Class Stubs**:
   - Never pre-declare uncalled helper functions, classes, or methods with `pass`, `yield`, `todo!()`, or dummy `return 0` / `return ""` / `return {}` / `return nil` bodies.
   - Instead, pre-declare only the **4+ void lesson functions** (and `main`) with live 1–4 line starter **Scaffolds**, and express all helper functions, custom structs/classes, and methods that the learner needs to build as `//` or `#` **Drills** specifying exact names, parameter types, and return types.
   - *(ABI callback exception)*: Pre-declare a non-lesson signature only when required by a cross-file ABI contract (e.g., an `@(export)` hot-reload plugin proc or FFI callback) that already executes live starter **Scaffold** code.
3. **Multi-File Lab Scaffold Boundaries**:
   - In multi-file **Labs**, keep **only**:
     1. **Shared domain/ABI contracts**: core structs/dataclasses/enums, baseline unoptimized slow paths (in profiling Labs), and sample data constants (`SAMPLE_CORPUS`).
     2. **Repetitive OS/environment setup boilerplate**: allocator/arena setup, CLI `--headless` flag parsing, optional GUI/FFI library loading (`try: import tkinter`).
   - Convert all domain algorithms, dispatch branches, and helper methods into open **Drills**.
   - Keep package/module-visibility **Labs** minimal (`1–2` anchor constants/exports used by `main` so the package compiles out of the box, with all other exports and helpers left as **Drills**).

---

## 7. Standard `000`–`980` Curriculum Tier Map (Adaptable to Any Language)

When designing a new `<lang>_how_to/` workspace, use this proven 10-tier progression (`~80–115` **Primers** + `~8–12` **Labs**, numbered with gaps of `5` or `10` for easy insertion):

| Tier | Number Range | Core Topics Covered |
| :--- | :---: | :--- |
| **Tier 0: Foundations & Control Flow** | `000`–`080` | Compiling/running & CLI flags (`000`), printing & formatting (`001`), variables/bindings (`005`), constants/literals (`010`), numeric types & casting (`015`), booleans & short-circuiting (`020`), strings/UTF-8/bytes (`025`), operators & bit manipulation (`030`), lexical scope & shadowing (`035`), `if`/`else` (`040`), `for`/`while` loops (`045`–`055`), pattern matching/`switch` (`060`), `defer`/RAII/context managers (`065`–`075`), assertions & panic/recovery (`080`). |
| **Tier 1: Functions, Closures & Testing** | `100`–`195` | Procedure/function signatures & multiple returns (`100`–`120`), closures/lambdas/callbacks (`130`–`150`), error-handling idioms (`160`–`180`), iterators/generators (`185`), built-in unit testing framework (`195`). |
| **Tier 2: Collections & Data Layouts** | `200`–`280` | Fixed arrays, slices & aliasing (`200`–`210`), dynamic arrays & capacity growth (`215`–`220`), hash maps & sets (`225`–`240`), queues/deques/heaps (`245`–`255`), sorting & binary search (`260`–`270`), mutation-during-iteration traps (`280`). |
| **Tier 3: Custom Types, Structs/Classes & Dispatch** | `300`–`395` | Package/module Labs (`300`–`310`), structs/classes & memory alignment (`320`–`340`), enums/bit_sets/tagged unions (`350`–`370`), interfaces/protocols/vtable or union dispatch (`380`–`395`). |
| **Tier 4: Memory Management / Packaging & Config** | `400`–`495` | Pointers/references, stack vs. heap, arenas, scratch allocators, tracking allocators, pool/handle allocators (or modules, packaging, `.env` config, linters, and bundles in managed languages). |
| **Tier 5: Runtime Internals, Benchmarking & Profiling** | `500`–`598` | String/memory lifecycles (`500`–`540`), high-resolution timers & benchmarking (`550`), profiler & trace integration (`560`–`575`), zero-copy buffers/`mmap` (`580`), SoA/object pools & hotspot workflow (`585`–`592`), memory & profiling **Labs** (`595`–`598`). |
| **Tier 6: Standard Library I/O, Formats & CLI** | `600`–`695` | Filesystem & paths (`600`), buffered streams (`610`), JSON/CSV/TOML (`620`), binary packing (`630`), regex/scanning (`640`), time/dates (`650`), CLI flag parsing (`660`), structured logging (`670`), embedded DB/crypto/subprocesses (`680`–`695`). *(Or parametric polymorphism/reflection if placed in `600`.)* |
| **Tier 7: Generics, Metaprogramming & Hardware Efficiency** | `700`–`790` | Generics/type parameters, reflection/AST inspection, AoS-to-SoA, 64-byte cache-line alignment & false sharing, explicit SIMD vectors, instruction-level parallelism (IPC), and data-oriented performance capstones. |
| **Tier 8: Concurrency, FFI, Networking & Hot Reload** | `800`–`890` | Threads, mutexes, atomics, thread pools/channels/async (`800`–`840`), concurrent pipeline **Lab** (`850`), C ABI FFI & SIMD offload (`860`–`865`), DLL/plugin hot-reload **Lab** (`870`), TCP/UDP sockets & graceful shutdown (`880`–`890`). |
| **Tier 9: Single-File & Multi-File Capstones** | `900`–`980` | Binary hex dumper (`900`), custom open-addressing hash table (`910`), persistent CLI task tracker (`920`), concurrent TCP command server (`930`), log search & word-frequency **Lab** (`940`), generational ECS simulation **Lab** (`950`), bytecode VM & assembler **Lab** (`960`), interactive/headless arcade simulation **Lab** (`980`). |

---

## 8. Low-Overhead Agent Execution Workflow (`Write-First, Verify-Once`)

When instructing an agent or multi-agent team to create or rewrite a `<topic>_how_to/` workspace:

1. **Pilot 1–2 Representative Primers First (Only When Starting a Brand-New Language)**:
   - Author one early syntax **Primer** (`001` or `045`/`050`) and confirm the language's exact comment style, line-1 run hint, 1-blank-line function spacing, `4+` lesson function layout, and bottom `main`.
2. **Wave 1 — Upfront Documentation Sync**:
   - Write or update `<topic>_how_to/README.md` and `<topic>_how_to/plan.md` first so parallel workers share an authoritative file list and never collide on `plan.md`.
3. **Wave 2 — Parallel Disjoint Tier Authoring (`Zero Intermediate Compiler Runs`)**:
   - Split the workspace into `~10–15` disjoint tier tickets (`6–12` files per ticket).
   - Workers author all assigned files using file tools only (`write_file` / `edit_file`) with **zero per-file compiler or shell invocations during authoring**.
4. **Wave 3 — Single Batched Verification & Targeted Repair Pass**:
   - Run **one** batched verification script across the entire workspace after all authoring tickets complete:
     1. **Compile / Typecheck / Syntax Check**: e.g., `odin check <file> -file` + `odin check <lab_dir>`, `python -B` `ast.parse`, `cargo check`, `zig ast-check`, etc.
     2. **Automated Hygiene Regex Sweep**: verify zero banned markers (`Prompt`, `Worked anchor`, `Suggested task`, `Signature:`, `Syntax:`, `cue:`, `exercise:`, `TODO`), zero comment formatting noise (`**bold**`, backticks in comments, `---`/`===` comment underlines, `$...$` LaTeX), zero dummy stubs (`pass`, `_ =`, dummy returns), zero unallowed docstrings, and compact `/* ... */` blocks.
   - Repair **only** the specific lines/files flagged by the batched pass and re-verify just those repaired targets.
