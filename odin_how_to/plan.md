# Odin How-To — Exhaustive Per-File Training Outline & Syntax Checklist (`plan.md`)

This document is the authoritative per-file blueprint for `odin_how_to/`. Every implementing agent or model **must** check off every listed keyword, syntax form, built-in, package symbol, and ordered outline step when writing each **Primer** (`NNN_topic.odin`) or **Lab** (`NNN_topic/`).

---

## Global Rules & Anti-Hallucination Checklist (Read Before Writing Any `.odin` File)

1. **Exact Odin Syntax (Never Confuse with C, C++, Go, Rust, Zig, or Jai)**:
   - **NO** `var`, `let`, `const`, `fn`, `func`, `def`, `class`, `interface`, `while`, `public`, `private` keywords.
   - **NO** `#include` or `#import` (Jai uses `#import "Basic";`; Odin uses `package main` and `import "core:fmt"`).
   - **NO** semicolons `;` at the end of statements (only inside C-style `for i := 0; i < n; i += 1` or `if init; cond`).
   - **Declarations**:
     - Variable (type inferred): `x := 42`
     - Variable (explicit type): `x: int = 42`
     - Variable (zero-initialized): `x: int`
     - Variable (uninitialized): `x: int = ---`
     - Constant (untyped): `MAX_COUNT :: 100`
     - Constant (typed): `MAX_COUNT : i32 : 100`
     - Procedure: `compute :: proc(a: int, b: f32) -> (res: f32, ok: bool) { ... }`
     - Type definition: `Vector3 :: struct { x, y, z: f32 }`, `State :: enum { Idle, Running }`, `Value :: union { int, f32, string }`
   - **Pointers**:
     - Pointer type is `^T` (never `*T`).
     - Address-of is `&x`.
     - Dereference is `p^` (postfix `^`, never `*p`).
     - Multi-pointer (for C arrays / pointer indexing) is `[^]T`.
     - Untyped pointer is `rawptr`. Integer pointer is `uintptr`.
   - **Ranges & Slicing**:
     - Half-open range (loops, switch cases): `0..<10`
     - Inclusive range (loops, switch cases, array/bit_set literals): `0..=9`
     - Slice expression (arrays, slices, strings, multi-pointers): `arr[start:end]`, `arr[:end]`, `arr[start:]`, `arr[:]` (uses `:`, never `..`).
2. **File Structure, Voice & Comment Style (`spec.md` & `ADR-0002` Standard)**:
   - Line 1 of every **Primer**: quiet `// odin run NNN_name.odin -file` (or `// odin test 195_unit_testing_with_odin_test.odin -file` for `195`). Lab entry files (`main.odin` / `host.odin`) use `// odin run <lab_dir>`.
   - Multi-section layout: group multi-concept **Primers** into focused topic procedures (typically 3–4 sections) called sequentially from `main :: proc()` placed at the **very bottom** of the file with `=== N. ... ===` section banners.
   - Leave **1 blank line** (two newlines) immediately after every `proc() {` opening brace.
   - Use **compact `/* ... */` blocks** (`/*\nprose...\n*/`) with **zero** extra blank lines immediately after `/*` or immediately before `*/`.
   - Conversational `CodingTemplateExamples/how_to` causal prose: explain *why* from hardware, memory layout, and compiler mechanics; apply a Feynman immediate explanation whenever introducing a new keyword, directive, or stdlib construct; pair syntax illustrations with tiny concrete hypothetical before/body/after scenarios (never ambiguous `{ ... }` or `...` placeholders); keep every inline code expression intact on a single comment line (never split across line wraps).
   - **Zero Banned Comment Noise**: **NO** `"Prompt"`, `"Step N (Prompt)"`, `"Worked anchor"`, `"Suggested task"`, `"Signature:"`, `"Syntax:"`, `"cue:"`, `"exercise:"`, ALL-CAPS headers (`CONCEPT:`, `FRICTION:`), ASCII boxes, `**bold**`, `*italics*`, single/double backticks, fenced code blocks, `---`/`===` comment underlines, `$...$` LaTeX, or `1. / 2.` numbered **Drill** checklists. **NO** `solutions/` files.
   - **~5–20% Soft Scaffold & Graduated Drills**:
     - Core **Primers** target `~150–300+` lines with `~8–15+` **Drills**; naturally narrow **Primers** (`060`, `070`, `140`, `260`, `270`, `330`, `360`, `370`, `640`, `650`, `870`) target `~85–140` lines with `~4–7` **Drills** (`~5–20%` starter **Scaffold** is a soft guideline).
     - Pre-write `package main`, required `import`s, section procedures + bottom `main :: proc()`, and small working convenience **Scaffold** lines when introducing brand-new syntax. Every pre-imported package and starter local variable must be genuinely used by live starter **Scaffold** code—**zero `_ = x` silencers** and **zero dummy `return` / empty helper stubs** (express unimplemented helpers as `//` **Drills** specifying exact names, parameter types, and return types; handle `@(require_results)` returns explicitly).
     - Graduate **Drills** naturally from explicit convenience hints (exact identifiers/types for IDE autocomplete) to conversational recall and open synthesis, including inline `// Try uncommenting:` compiler error experiments.
   - **Multi-File Lab Boundaries**: Judge **Labs** by topical coverage and clean module boundaries; keep shared ABI/domain contracts, baseline slow paths, and repetitive OS/setup boilerplate as **Scaffold**, leaving domain logic and helper implementations as open `//` **Drills**.
   - Every unfilled **Primer** must pass `odin check NNN_name.odin -file` (`exit 0`), and every **Lab** must pass `odin check <lab_dir>` (`exit 0`).

---

## Tier Overview (`000`–`999`)

| Range | Tier Focus | Count |
| :--- | :--- | :--- |
| **`000`–`099`** | **Toolchain, Basic Syntax, Types & Control Flow** | 18 Primers |
| **`100`–`199`** | **Procedures, Defer Idioms, Error Handling (`or_*`) & Testing** | 12 Primers |
| **`200`–`299`** | **Compound Types, Value vs. Reference Semantics & Data Layout** | 16 Primers |
| **`300`–`399`** | **Packages, Scopes, Directives, Attributes & Build Configuration** | 7 Primers, 2 Labs |
| **`400`–`499`** | **Context System, Memory Management, Arenas & Custom Allocators** | 10 Primers, 1 Lab |
| **`500`–`599`** | **Standard Library Essentials (`core:`), Containers, Spall & Tracy Hooks** | 14 Primers, 1 Lab |
| **`600`–`699`** | **Parametric Polymorphism (Generics), Intrinsics & Reflection (RTTI)** | 8 Primers |
| **`700`–`799`** | **Concurrency, Synchronization, Channels, SIMD, SOA & Performance Multipliers** | 10 Primers, 2 Labs |
| **`800`–`899`** | **C Interop (`foreign`), Dynamic Libraries (`dynlib`), Vendor & Low-Level** | 6 Primers, 1 Lab |
| **`900`–`999`** | **Basic Programs & Complete Training Capstones** | 4 Primers, 4 Labs |

**Total Curriculum**: **105 Primers + 11 Multi-File Labs (116 numbered entries)**

---

## Execution Plan & Unified Alignment Tickets

> **Note:** The earlier `.scratch/odin-how-to/spec.md` and `.scratch/odin-how-to/issues/01..10` planning files are **superseded** by [`.scratch/curriculum-alignment/spec.md`](../.scratch/curriculum-alignment/spec.md) and [`.scratch/curriculum-alignment/map.md`](../.scratch/curriculum-alignment/map.md).

### Mandatory Shared Context for Implementing Workers
Before authoring files for any Odin rewrite ticket, every worker must read:
1. [`GLOSSARY.md`](../GLOSSARY.md) — canonical definitions of **Primer**, **Lab**, **Scaffold**, and **Drill**.
2. [`docs/adr/0001-single-folder-file-flag-and-labs.md`](../docs/adr/0001-single-folder-file-flag-and-labs.md) — `-file` standalone **Primer** layout vs. subdirectory multi-file **Lab** package boundaries.
3. [`docs/adr/0002-conversational-prose-hash-comments-and-convenience-scaffold.md`](../docs/adr/0002-conversational-prose-hash-comments-and-convenience-scaffold.md) — conversational prose, compact `/* ... */` blocks, 1 blank line after `proc() {`, bottom `main`, Feynman/hypothetical rules, and `~5–20%` convenience **Scaffold**.
4. [`.scratch/curriculum-alignment/spec.md`](../.scratch/curriculum-alignment/spec.md) & [`.scratch/curriculum-alignment/map.md`](../.scratch/curriculum-alignment/map.md) — unified authoring standard, Core vs. Narrow **Primer** sizing, zero-`_ =`/zero-stub rules, and cross-repo Tracy boundaries.
5. Approved Odin pilot reference: [`odin_how_to/045_for_loops.odin`](045_for_loops.odin) (`289` lines).
6. Gap audits: [`odin-gap-audit.md`](../.scratch/curriculum-alignment/research/odin-gap-audit.md) and [`tracy-gap-audit.md`](../.scratch/curriculum-alignment/research/tracy-gap-audit.md).
7. **Global Rules & Anti-Hallucination Checklist** above, plus your assigned ticket under [`.scratch/curriculum-alignment/issues/`](../.scratch/curriculum-alignment/issues/) and its matching tier section below.

### Ticket Map & Execution Order (`Write-First, Verify-Once`)
- **Wave 1 — Upfront Doc Sync (Ticket `10`)**: Syncs [`odin_how_to/README.md`](README.md) and [`odin_how_to/plan.md`](plan.md) and fixes the immediate `\//` compile error in `001_first.odin:1-2` before parallel tier rewrites begin ([`10-sync-odin-readme-plan-and-001-comment.md`](../.scratch/curriculum-alignment/issues/10-sync-odin-readme-plan-and-001-comment.md)).
- **Wave 2 — Parallel Tier Rewrites (Tickets `13`–`29`)**: 17 disjoint Odin rewrite slices covering all non-pilot **Primers** and **Labs** (`000`–`980`, skipping approved pilot `045_for_loops.odin`), authored with zero intermediate compiler runs.
- **Wave 3 — Single Batched Verification Pass (Ticket `48`)**: Runs `odin check <primer>.odin -file` across all 105 **Primers**, `odin check <lab_dir>` across all 11 **Labs**, `odin build ... -build-mode:dll` on `830_dll_hot_reload_lab/plugin`, and one cross-repo regex hygiene sweep (`0` banned markers, `0` `_ =`, `0` dummy stubs, compact `/* ... */`), fixing only flagged failures in place. Interactive/network entries (`930`, `980`) keep self-contained loopback / `-headless` verification paths.

| Wave | Tickets | Scope & Deliverables | Reference |
| :--- | :--- | :--- | :--- |
| **Wave 1** | **10** | `README.md`, `plan.md`, `001_first.odin:1-2` `\//` fix | [`10-sync-odin-readme-plan-and-001-comment.md`](../.scratch/curriculum-alignment/issues/10-sync-odin-readme-plan-and-001-comment.md) |
| **Wave 2** | **13–29** | 17 parallel tier slices (`000`–`980`, skipping pilot `045`) | [`.scratch/curriculum-alignment/issues/`](../.scratch/curriculum-alignment/issues/) |
| **Wave 3** | **48** | Single batched `odin check` / DLL build / hygiene sweep | [`.scratch/curriculum-alignment/spec.md`](../.scratch/curriculum-alignment/spec.md) |

---

## `000`–`099`: Toolchain, Basic Syntax, Types & Control Flow

### `000_compiling_and_running.odin` *(Primer)*
- **Syntax / CLI / Built-ins Checklist**: `package main`, `import "core:fmt"`, `import "core:os"`, `main :: proc()`, `ODIN_OS`, `ODIN_ARCH`, `ODIN_VENDOR`, `ODIN_VERSION`, `ODIN_DEBUG`, `ODIN_OPTIMIZATION_MODE`, `os.args`, CLI flags: `odin run <file> -file`, `odin build <file> -file -out:.build/000.exe`, `odin check <file> -file`, `-vet`, `-strict-style`, `-debug`, `-o:none`, `-o:minimal`, `-o:speed`, `-o:size`, `--` (passing runtime args).
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:os"`, and bottom `main :: proc()` with live starter convenience lines printing `ODIN_OS` and `len(os.args)`.
- **Ordered Outline**:
  1. Explain why Odin compiles a directory as one package by default (`odin run .`), and why `-file` treats a single `.odin` file as its own self-contained package (`odin run 000_compiling_and_running.odin -file`).
  2. Explain `odin check` (fast typecheck without linking), `odin build` with `-out:.build/...`, `-vet` / `-strict-style` hygiene checks, and passing runtime arguments after `--`.
  3. **Drill**: Print `ODIN_ARCH`, `ODIN_VENDOR`, `ODIN_VERSION`, `ODIN_DEBUG`, and `ODIN_OPTIMIZATION_MODE` using `fmt.println` and `fmt.printfln`.
  4. **Drill**: Loop over `os.args[1:]` and test `odin run 000_compiling_and_running.odin -file -- alpha beta` and `-debug` to observe `ODIN_DEBUG` flip from `false` to `true`.
  5. **Drill**: Verify the file passes `odin check 000_compiling_and_running.odin -file -vet -strict-style` (and test `-o:speed` build).

### `001_first.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `package main`, `import "core:fmt"`, `//` line comment, `/* ... */` nested block comments, `main :: proc()`, `fmt.println`, `fmt.print`, `fmt.printf`, `fmt.printfln`, format verbs `%v` (default value), `%T` (type name), `%#v` (Odin syntax representation), `%%` (literal percent).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()` containing `fmt.println("Hellope!")`.
- **Ordered Outline**:
  1. Explain `package main` (required at the top of every Odin file) and `import "core:fmt"` (importing from the `core` library collection).
  2. Demonstrate nested `/* outer /* inner */ outer */` block comments (and why nested block comments make commenting out large blocks of code effortless compared to C).
  3. Show the starter convenience `fmt.println("Hellope!")` line.
  4. **Drill**: Use `fmt.print` and `fmt.println` to print multiple values (`"Score:"`, `100`, `true`).
  5. **Drill**: Use `fmt.printf` / `fmt.printfln` with `"Value: %v, Type: %T, Syntax: %#v"` on an integer `42` and a string `"Odin"`, plus literal `%%`.

### `005_variables_and_zero_values.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `name: Type = value` (explicit type + init), `name := value` (type inference), `name: Type` (zero-initialization: `0`, `0.0`, `false`, `""`, `nil`), `name: Type = ---` (explicitly uninitialized memory), `a, b := 1, 2` (parallel declaration), `=` (reassignment), `_` (blank identifier to discard unwanted multi-return values, never as `_ = x` silencers).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`, 1 starter convenience line `explicit_number: int = 10` (used/printed).
- **Ordered Outline**:
  1. Explain Odin's colon syntax: the `:` always separates the identifier name on the left from the type on the right (`x: int = 10`); dropping the type gives `x := 10`; dropping the value gives zero-initialized `x: int`.
  2. **Drill**: Declare an integer variable named `"number_variable"` with explicit type `int` and value `42`, then reassign it to `99`.
  3. **Drill**: Declare `"inferred_float"` using `:=` with value `3.14` (explain that float literals default to `f64`, integer literals to `int`).
  4. **Drill**: Declare `"zero_int"` (`int`), `"zero_bool"` (`bool`), and `"zero_string"` (`string`) without values, and print them to verify deterministic zero-initialization.
  5. **Drill**: Declare two variables `"width"` and `"height"` in one statement initialized to `1920` and `1080`, then swap them in one line `width, height = height, width`.
  6. **Drill**: Declare `"raw_scratch"` of type `int` initialized to `---` (uninitialized), then assign `raw_scratch = 7` before printing (`// Try printing raw_scratch before assigning and run with -vet-uninitialized`).

### `010_constants_and_untyped_literals.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `NAME :: value` (untyped compile-time constant), `NAME : Type : value` (typed compile-time constant), untyped integer/float/string/boolean adaptation, compile-time arithmetic in constant declarations (`BUFFER_SIZE :: 1024 * 64`).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`, 1 starter convenience constant `UNTYPED_PI :: 3.141592653589793` (used/printed).
- **Ordered Outline**:
  1. Explain `::` (compile-time binding: the right-hand side is fixed at compile time and has no runtime memory address).
  2. Explain **untyped constants** vs **typed constants**: why `MAX_ITEMS :: 100` can be assigned directly to `u8`, `i32`, `u64`, or `f32` without a cast (as long as it fits!), whereas `TYPED_MAX : int : 100` is locked to `int`.
  3. **Drill**: Declare untyped constant `"GRAVITY"` (`9.81`) and assign it to both an `f32` variable `"gravity_f32"` and an `f64` variable `"gravity_f64"`.
  4. **Drill**: Declare typed constant `"DEFAULT_PORT"` of type `u16` equal to `8080` and constant `"PACKET_BYTES"` equal to `16 * 1024`.
  5. **Error check**: `// Try uncommenting: ptr := &DEFAULT_PORT` (cannot take the address of a constant) and `// Try uncommenting: small: u8 = 300` (constant overflow caught at compile time).

### `015_number_types_and_casting.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `u128`, `int`, `uint`, `uintptr`, `byte` (alias for `u8`), `f16`, `f32`, `f64`, endian types (`i16le`, `i32be`, `u64le`, `u64be`, `f32be`), numeric literals (`0x` hex, `0b` binary, `0o` octal, `1_000_000` underscore separator, `1.5e-3`), `cast(T)x`, `T(x)` type conversion call syntax, `auto_cast x`, `transmute(T)x`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`, 1 starter convenience line `small_byte: u8 = 0xFF` (printed).
- **Ordered Outline**:
  1. Explain Odin's strict numeric typing: unlike C or Jai, **typed numeric variables never implicitly cast** (even widening `u8` -> `u16` or `i32` -> `i64` requires an explicit cast!).
  2. **Drill**: Declare `"hex_mask"` (`u32 = 0xDEAD_BEEF`), `"bin_flags"` (`u16 = 0b1010_0101`), `"big_count"` (`i64 = 5_000_000`), and `"net_port"` (`u16be = 80`).
  3. **Error check**: `// Try uncommenting: big_count = hex_mask` (error: cannot assign `u32` to `i64` without explicit cast).
  4. **Drill**: Convert `"small_byte"` to `u32` using `u32(small_byte)` and `cast(u32)small_byte`, and convert an `f64` `"precise_val"` (`42.9`) to `int` (truncates toward zero).
  5. **Drill**: Use `auto_cast` to assign an `i32` into a variable whose type `i64` is already known (`target_i64: i64 = auto_cast my_i32`).
  6. **Drill**: Use `transmute(u32)f32(1.0)` to reinterpret the raw 32-bit IEEE-754 bit pattern of `1.0` (`0x3f800000`) without numeric conversion.

### `020_booleans_and_comparisons.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `bool`, `b8`, `b16`, `b32`, `b64`, `true`, `false`, `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&` (short-circuit AND), `||` (short-circuit OR), `!` (logical NOT), `size_of`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `bool` (1 byte) vs sized boolean types `b8`, `b16`, `b32`, `b64` (used when matching C/Win32 `BOOL` or GPU uniform buffers where a boolean must be 4 bytes wide).
  2. **Drill**: Declare `"is_active"` (`bool = true`) and `"win32_flag"` (`b32 = true`), and print `size_of(bool)` vs `size_of(b32)`.
  3. **Drill**: Assign `"win32_flag"` from a comparison expression `10 < 20` (untyped boolean results adapt to any `bN` type!).
  4. **Drill**: Combine conditions with `&&`, `||`, and `!`, demonstrating short-circuit evaluation where the right-hand side is skipped.

### `025_strings_and_runes.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `string`, `cstring`, `rune`, `"..."` escaped string literal, `` `...` `` raw string literal (including multi-line), `'A'` / `'🚀'` rune literal, `len(s)` (byte length!), `s[i]` (`u8` byte indexing), `s[start:end]` (zero-allocation substring slice), `raw_data(s)` (`[^]u8`), `transmute([]u8)s`, `for r, byte_offset in s` (UTF-8 rune iteration).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`, 1 starter convenience line `greeting: string = "Hellope, Odin!"` (printed).
- **Ordered Outline**:
  1. Explain that `string` in Odin is an immutable 16-byte header (`data: [^]u8, len: int`), UTF-8 by convention, and **not null-terminated** (unlike C).
  2. **Drill**: Declare `"raw_path"` using a backtick raw string `` `C:\Program Files\Odin` ``, a multi-line raw string block, and `"char_rune"` of type `rune` set to `'Ω'`.
  3. **Drill**: Slice `"greeting"` (`greeting[0:7]`) into `"sub_greeting"` and verify with `raw_data` (and `transmute([]u8)sub_greeting`) that no memory was copied.
  4. **Drill**: Compare ASCII vs multi-byte UTF-8 (`"Aα🚀"`): print `len(utf8_text)` (bytes = 7, not 3 characters!), index `utf8_text[0]` (`u8`), and write a `for codepoint, byte_idx in utf8_text` loop to print each decoded `rune` and its starting byte offset.
  5. **Drill**: Declare `"c_label"` of type `cstring` initialized to `"Hello from C"` (null-terminated pointer for C APIs) and cast `string(c_label)` (which computes length via `strlen`).
  6. **Error check**: `// Try uncommenting: greeting[0] = 'J'` (`string` bytes are immutable).

### `030_operators_and_precedence.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `+`, `-`, `*`, `/`, `%` (remainder, sign of dividend), `%%` (floored modulo, sign of divisor), `&` (AND), `|` (OR), `~` (bitwise XOR when binary `a ~ b`, bitwise NOT when unary `~a`!), `&~` (bit clear / AND-NOT), `<<`, `>>`, `+=`, `-=`, `*=`, `/=`, `&=`, `|=`, `~=`, `&~=`, ternary `cond ? a : b` and `a if cond else b`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain two Odin operator differences from C: (a) `%` vs `%%` on negative numbers (`-7 % 3 == -1` vs `-7 %% 3 == 2`, critical for wrapping ring-buffer indices!), and (b) `~` is **both** unary bitwise NOT (`~x`) and binary XOR (`x ~ y` instead of `^`, since `^` is for pointers!), plus `&~` clears bits and bitwise-vs-comparison precedence differs from C (`(flags & MASK) != 0`).
  2. **Drill**: Compute `"rem"` (`-7 % 3`) and `"wrapped_index"` (`-7 %% 3`) and write a reusable `wrap_ring_index` procedure using `%%`.
  3. **Drill**: Start with `"flags"` (`u8 = 0b0000_0101`), set bit 1 with `|=`, toggle bit 0 with `~=`, clear bit 2 with `&~=`, invert all bits with unary `~flags`, and pack/unpack RGBA/field bits with shifts and masks.
  4. **Drill**: Write `"label"` using C-style ternary `score >= 50 ? "Pass" : "Fail"` and `"clamped_val"` using Python/Odin-style `100 if score > 100 else score`.
  5. **Note**: Mention that Odin has **no** `++` or `--` operators (`i += 1` is always a statement, never an expression).

### `035_scopes_and_shadowing.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: File/package scope (order-independent) vs procedure/block lexical scope (top-to-bottom), anonymous `{ ... }` blocks, shadowing outer variables vs mutating outer variables, `-vet-shadowing`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why file-level declarations (`GLOBAL_LIMIT :: 500` or helper procs) can be placed *below* `main` (order-independent), whereas variables inside `main` only exist from their declaration line down to the closing `}` of their block.
  2. **Drill**: Reference a constant `"FILE_SCOPE_MAGIC"` inside `main` that you declare at the very bottom of the file below `main`.
  3. **Drill**: Create an outer variable `"counter := 10"`, open an anonymous `{ ... }` block, mutate `counter += 5`, and declare a block-local `"temp_val := 99"` that disappears after `}`.
  4. **Error check**: Show how accidentally writing `counter := 20` inside `{ ... }` creates a shadowed variable instead of mutating the outer `counter` (`// Run with odin check 035_scopes_and_shadowing.odin -file -vet-shadowing to see Odin catch this`).

### `040_if_and_init_statements.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `if cond { ... }`, `else if cond { ... }`, `else { ... }`, `if cond do single_stmt`, `if init_stmt; cond { ... }`, multi-return `if val, ok := lookup(...); ok { ... }`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain that Odin `if` conditions do not use parentheses `()` and require either `{ ... }` or `do` for a single statement.
  2. **Drill**: Write an `if / else if / else` chain grading an integer `"temperature"`.
  3. **Drill**: Write a one-liner `if temperature > 30 do fmt.println("Hot!")`.
  4. **Drill**: Write an `if` with an initialization statement: `if doubled := temperature * 2; doubled > 50 { ... } else { ... }`, plus a multi-return `if val, ok := lookup_item(...); ok { ... }`, where the bound variables live across both branches and disappear afterward.

### `045_for_loops.odin` *(Approved Odin Pilot Primer — Keep Intact, `289` Lines)*
- **Syntax / Keywords / Built-ins Checklist**: `for i in 0..<n`, `for i in 1..=n`, `for i := 0; i <= n; i += 2`, `for cond { ... }`, `for { ... }`, `for val in array`, `for val, idx in array`, `#reverse for val, idx in array`, `for &val in array`, loop-scoped `defer`, nested 2D loops, labeled `break search` / `continue search`, backward dynamic-array `ordered_remove(&items, i)`.
- **Scaffold**: `package main`, `import "core:fmt"`, 4 topic section procedures (`range_and_c_style_loops`, `conditional_and_infinite_loops`, `collection_and_reference_loops`, `nested_loops_and_traps`) called from bottom `main :: proc()` with `=== N. ... ===` banners.
- **Ordered Outline**:
  1. Range & C-style loops: `0..<4` vs `1..=5`, unsigned `u32` `0..<empty_len` vs `0..=empty_len - 1` wraparound hazard, C-style step `+2` and signed `int` countdown `i -= 1`.
  2. Conditional & infinite loops: `for countdown > 0`, `for { ... break }`, loop-scoped `defer` firing at the end of every pass including `continue` and `break`.
  3. Collection & reference loops: `for val, idx in items` (value first, index second), `#reverse for` (and why `#reverse` rejects integer ranges), `for &val in` in-place mutation vs read-only copy, and slice min/max scan.
  4. Nested loops, 2D grids & traps: `4x4` multiplication table, labeled `search: for row, y in grid` + `break search`, and backward deletion `ordered_remove(&items, i)` avoiding index-shift bugs.

### `050_switch_and_partial.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `switch expr { case a: ... case b, c: ... case d..=e: ... case: ... }`, `fallthrough`, conditionless `switch { case x < 0: ... }`, `switch init; expr { ... }`, `#partial switch` on `enum`, `case` indentation rule (under `-strict-style`, `case` aligns with `switch`).
- **Scaffold**: `package main`, `import "core:fmt"`, `Traffic_Light :: enum { Red, Yellow, Green }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain that Odin `switch` cases **never fall through by default** (no `break` needed at the end of each `case`!), and `fallthrough` must be written explicitly when desired.
  2. **Drill**: Write a `switch` on an integer `"http_code"` matching single values (`200`), multiple values (`301, 302`), a range (`500..=599`), and default `case:`, plus a character-range tokenizer switch (`'0'..='9'`, `'a'..='z'`) and an explicit `fallthrough` example.
  3. **Drill**: Write a conditionless `switch` checking boolean expressions on `"speed"`.
  4. **Drill**: Write an exhaustive `switch light` over `Traffic_Light` (`case .Red:`, `case .Yellow:`, `case .Green:`), then write a `#partial switch light` that only handles `.Red` (`// Try deleting #partial to see the unhandled enum case error`).

### `055_defer_semantics.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `defer stmt`, `defer { ... }`, LIFO (reverse order) execution at **enclosing block exit**, loop-body `defer` firing per iteration, `defer if cond { ... }` idiom.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain the two golden rules of `defer` in Odin: (a) it runs at the end of the **current `{ ... }` block** (unlike Go's function-scoped `defer`!), and (b) multiple `defer`s in the same block run in **reverse declaration order (LIFO)**.
  2. **Drill**: Register three `defer fmt.println(...)` statements (`"First"`, `"Second"`, `"Third"`) and print `"Body"` to observe `"Body" -> "Third" -> "Second" -> "First"`.
  3. **Drill**: Create an inner `{ ... }` block with its own `defer` and verify it fires *before* the outer code after the `}` continues, plus a loop-body `defer` LIFO demonstration across `continue` / `break`.
  4. **Drill**: Demonstrate the `defer if failed { fmt.println("Rolling back!") }` idiom where `failed` is a `bool` mutated later in the body (proving the condition is evaluated when the `defer` runs at block exit!).

### `060_when_compile_time_branching.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `when cond { ... } else when cond { ... } else { ... }`, `when` ternary (`VAL :: A when COND else B`), `ODIN_OS`, `ODIN_ARCH`, `ODIN_DEBUG`, compile-time constant conditions.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `when` vs `if`: `when` requires a compile-time constant boolean, emits zero branch instructions at runtime, and **does not type-check untaken branches** (so platform-specific identifiers can live safely in `when ODIN_OS == .Linux` on Windows!).
  2. **Drill**: Declare a file-scope constant `"PLATFORM_NAME"` using a compile-time `when` ternary or `when ODIN_OS == .Windows` block.
  3. **Drill**: Inside `main`, write a `when ODIN_DEBUG` block that prints a debug banner (and prove an undeclared identifier inside `when false { undeclared_fn() }` compiles without error!).

### `065_builtin_queries_and_asserts.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `size_of(T)`, `align_of(T)`, `offset_of(T, field)`, `offset_of_by_string(T, "field")`, `offset_of(val.field)`, `type_of(x)`, `typeid_of(T)`, `len(x)`, `cap(x)`, `min(a, b)`, `max(a, b)`, `abs(x)`, `clamp(v, lo, hi)`, `assert(cond, msg)`, `panic(msg)`, `ensure(cond, msg)`, `#assert(compile_time_cond)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `Packet_Header :: struct { magic: u16, version: u8, length: u32 }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain compile-time layout queries (`size_of`, `align_of`, `offset_of`) and compile-time `#assert` vs runtime `assert` (disabled by `-disable-assert`) vs `ensure` (always active even with `-disable-assert`).
  2. **Drill**: Add a compile-time `#assert(size_of(Packet_Header) == 8)` and print `size_of`, `align_of`, and `offset_of` for each field of `Packet_Header`, plus compare with a badly ordered struct (`u8, u64, u8` vs `u64, u8, u8`) to see padding drop.
  3. **Drill**: Compute `min`, `max`, `abs`, and `clamp(health, 0, 100)` on test numbers and verify with `assert` and `ensure`.

### `070_complex_and_quaternions.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `complex32`, `complex64`, `complex128`, imaginary literal `2i`, `real(c)`, `imag(c)`, `conj(c)`, `abs(c)`, `quaternion64`, `quaternion128`, `quaternion256`, `1i`, `1j`, `1k`, `.x`, `.y`, `.z`, `.w` (or `.real`, `.imag`, `.jmag`, `.kmag`).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain that Odin has first-class complex numbers and Hamilton quaternions built into the language for scientific computing and 3D rotations.
  2. **Drill**: Declare `"c1"` (`complex64 = 3 + 4i`) and `"c2"` (`complex64 = 1 - 2i`), compute `c1 * c2`, `real(c1)`, `imag(c1)`, `conj(c1)`, and `abs(c1)` (magnitude = `5`).
  3. **Drill**: Declare `"rot_q"` (`quaternion128 = 1 + 0i + 0j + 0k` or `quaternion(w = 1, x = 0, y = 0, z = 0)`), inspect `.x`, `.y`, `.z`, `.w`, and compute `conj(rot_q)`.

### `075_compound_literals.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: Unified `{ ... }` compound literals: `Type{a, b}`, `Type{field = a}`, untyped `{a, b}` when target type is inferred from variable type or procedure parameter, `[3]int{1, 2, 3}`, `[?]int{1, 2, 3}`, `[]int{1, 2, 3}` (slice literal backed by local stack array!).
- **Scaffold**: `package main`, `import "core:fmt"`, `Color :: struct { r, g, b, a: u8 }`, `draw_pixel :: proc(pos: [2]int, col: Color) { fmt.println(pos, col) }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how Odin's `{ ... }` compound literal works uniformly for arrays, slices, structs, maps, and bit sets—and how you can omit the type name when the compiler already knows the expected type!
  2. **Drill**: Declare `"red"` of type `Color` using `{255, 0, 0, 255}` and `"transparent_green"` using designated fields `{g = 255, a = 128}`.
  3. **Drill**: Call `draw_pixel({10, 20}, {0, 128, 255, 255})` using untyped `{ ... }` literals directly as arguments.
  4. **Drill**: Create a slice literal `nums := []int{10, 20, 30}` inside `main` and explain the stack-lifetime trap (never return a local `[]int{...}` slice literal from a procedure!).

### `080_unroll_and_labeled_control_flow.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `#unroll for`, `#unroll(N) for`, labeled loops `loop_name: for ...`, `break loop_name`, `continue loop_name`, labeled `switch` and `if` blocks (`block_name: if cond { ... break block_name }`).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `#unroll for` (instructs the compiler to duplicate the loop body at compile time for constant ranges/arrays or enums) and labeled control flow (`break label`, `continue label` — which in Odin even works on labeled `if` and `switch` statements!).
  2. **Drill**: Write an `#unroll for i in 0..<4` loop that computes powers of 2 into a `[4]int` array, plus an `#unroll for` over an enum.
  3. **Drill**: Write a 2D grid search `search: for y in 0..<3 { for x in 0..<3 { ... } }` demonstrating both `continue search` and `break search`, plus a labeled `check: if valid { ... break check }` early exit.

---

## `100`–`199`: Procedures, Defer Idioms, Error Handling (`or_*`) & Testing

### `100_procedures_basics.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `name :: proc(param: Type) -> Return_Type`, `a, b: int` grouped parameter types, immutable parameters (cannot reassign `param = ...`), `^T` pointer parameters for mutation, nested local `proc` definitions, procedure type `Op_Proc :: proc(int, int) -> int`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`, 1 starter convenience helper `square :: proc(x: int) -> int { return x * x }` (called from starter code).
- **Ordered Outline**:
  1. Explain `:: proc(...) -> ...` syntax and why all procedure parameters in Odin are **immutable constants** inside the procedure body.
  2. **Drill**: Write `add_and_scale :: proc(a, b: int, scale: int) -> int` plus a nested local helper `proc` (`// Try adding 'a = 0' inside add_and_scale to see the compiler error`).
  3. **Drill**: Write `add_in_place :: proc(target: ^int, delta: int)` that mutates `target^ += delta`.
  4. **Drill**: Define a procedure type `Binary_Op :: proc(a, b: int) -> int` and write `apply_op :: proc(x, y: int, op: Binary_Op) -> int`, calling it from `main`.

### `110_multiple_and_named_returns.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `-> (int, bool)`, `-> (quotient: int, remainder: int)`, `-> (min_val, max_val: int)`, naked `return` (returns current values of named return variables, which start zero-initialized!), `_` blank identifier to discard unwanted return values.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain multiple return values and how named return parameters declare zero-initialized local variables in the procedure scope.
  2. **Drill**: Write `divmod :: proc(a, b: int) -> (quotient: int, remainder: int, ok: bool)` that returns early with `return` (all zeros/`false`) when `b == 0`, and otherwise sets `quotient`, `remainder`, `ok = true` and returns.
  3. **Drill**: Call `divmod(17, 5)` in `main` capturing `q, r, ok`, and call `divmod(10, 0)` discarding `r` with `q2, _, ok2 := divmod(10, 0)`.

### `120_default_and_named_arguments.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `param: Type = default_val`, `param := default_val`, calling with `proc_name(arg_name = val)`, `#caller_location` (`runtime.Source_Code_Location` with `.file_path`, `.line`, `.column`, `.procedure`), `#caller_expression`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "base:runtime"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain default arguments (must be compile-time values, or `#caller_location` / `#caller_expression`) and named arguments at call sites (allowing arguments in any order or skipping middle defaults).
  2. **Drill**: Write `configure_server :: proc(host: string = "127.0.0.1", port: u16 = 8080, max_conns := 64, tls := false)`.
  3. **Drill**: Call `configure_server` from `main` with `()`, with `(port = 9000, tls = true)`, and with `(tls = true, host = "0.0.0.0")`.
  4. **Drill**: Write `trace_value :: proc(val: int, expr := #caller_expression(val), loc := #caller_location)` and an `assert_expr` helper using `#caller_expression` + `#caller_location` that prints `"<file>(<line>) in <procedure>: <expr> = <val>"`, calling them from `main`.

### `130_variadic_and_by_ptr_params.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `vals: ..int` (variadic slice parameter), `..existing_slice` (expanding a slice into a variadic call), mixed fixed + variadic args, `#by_ptr` parameter directive, `#any_int` parameter directive.
- **Scaffold**: `package main`, `import "core:fmt"`, `Big_Payload :: struct { data: [64]f64, id: int }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `nums: ..int` receives a `[]int` slice constructed on the caller's stack, how `#by_ptr` lets a procedure take a large struct by pointer under the hood while callers still pass values/literals without `&`, and how `#any_int` accepts any integer width (`u8`, `i32`, `int`) by converting at the call site.
  2. **Drill**: Write `sum_ints :: proc(nums: ..int) -> int` and a mixed fixed + variadic `format_tagged :: proc(tag: string, vals: ..int)`, calling them with variadic args and `..my_slice`.
  3. **Drill**: Write `inspect_payload :: proc(#by_ptr p: Big_Payload) -> int` and call it directly with a compound literal `inspect_payload(Big_Payload{id = 7})`.
  4. **Drill**: Write `print_index :: proc(#any_int idx: int)` and call it with a `u8`, an `i32`, and a `u64` without casts.

### `140_explicit_procedure_overloading.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `group_name :: proc{proc_a, proc_b, proc_c}` (explicit procedure overload groups).
- **Scaffold**: `package main`, `import "core:fmt"`, `Vec2 :: [2]f32`, `Rect :: struct { x, y, w, h: f32 }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why Odin avoids C++-style implicit overloading across scattered files and instead uses **explicit procedure groups** (`proc{...}`), making every overload visible in one declaration.
  2. **Drill**: Write `area_square :: proc(side: f32) -> f32`, `area_rect :: proc(r: Rect) -> f32`, and `area_dims :: proc(w, h: f32) -> f32`.
  3. **Drill**: Bind them into `area :: proc{area_square, area_rect, area_dims}` and call `area(5.0)`, `area(Rect{0, 0, 4, 3})`, and `area(6.0, 2.0)` in `main`.

### `150_or_else_and_optional_ok.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `or_else` binary expression (`expr or_else fallback`), `Maybe(T)` built-in union, `val, ok := maybe_val.?`, `#optional_ok` directive on procedure declarations, `or_else` on `map[K]V` and `union`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how Odin's `(value, ok_bool)` convention pairs with `or_else` to provide clean inline fallback values for map lookups, type assertions, `Maybe(T).?`, and procedures.
  2. **Drill**: Write `#optional_ok safe_sqrt :: proc(x: f64) -> (res: f64, ok: bool)` (returns `0, false` if `x < 0`).
  3. **Drill**: In `main`, call `v1 := safe_sqrt(16) or_else -1.0`, `v2 := safe_sqrt(-4) or_else 0.0`, and `v3 := safe_sqrt(25)` (1-value call enabled by `#optional_ok`!).
  4. **Drill**: Declare `opt_port: Maybe(u16) = nil`, unwrap it with `port := opt_port.? or_else 8080`, then set `opt_port = 3000` and unwrap again; also practice `or_else` on a `map[string]int` lookup and a `union` type assertion.

### `160_or_return_error_propagation.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `or_return` postfix operator, error enums (`Error :: enum { None, ... }` where `.None == 0` is success!), `union #shared_nil`, `#optional_allocator_error` (`runtime.Allocator_Error`), `@(require_results)` procedure attribute.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "base:runtime"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `or_return` works: if a call returns `(T, Err)` or `(Err)` where the last return value is a `bool` (`false` = failure) or an `enum` / `union` (`!= nil / 0` = error), `or_return` strips that last value and immediately returns it from the enclosing procedure if non-zero/`false`!
  2. **Drill**: Define `Parse_Error :: enum { None, Empty_String, Invalid_Header, Out_Of_Bounds }` and combine it with `runtime.Allocator_Error` into `Load_Error :: union #shared_nil { Parse_Error, runtime.Allocator_Error }`.
  3. **Drill**: Write `@(require_results) check_header :: proc(s: string) -> (body: string, err: Parse_Error)` and `@(require_results) allocate_and_parse :: proc(s: string) -> (buf: []u8, err: Load_Error)` chaining `body := check_header(s) or_return` and `#optional_allocator_error` allocation (`make([]u8, len(body)) or_return`)!
  4. **Drill**: Call `allocate_and_parse` in `main` on valid and invalid inputs (`// Try calling allocate_and_parse("bad") without capturing its return values to see @(require_results) error`).

### `170_or_break_and_or_continue.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `or_break`, `or_continue`, `or_break label`, `or_continue label` inside `for` loops, enum errors with `or_break`.
- **Scaffold**: `package main`, `import "core:fmt"`, `parse_digit :: proc(ch: u8) -> (digit: int, ok: bool) { if ch >= '0' && ch <= '9' do return int(ch - '0'), true; return 0, false }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `or_continue` skips the rest of the current loop iteration when a `(val, ok)` expression returns `false`/error, and `or_break` exits the loop (or a labeled outer loop) immediately.
  2. **Drill**: Loop over the bytes of `"1a2b3c"` and sum only valid digits using `d := parse_digit(ch) or_continue`, plus a nested labeled loop using `or_continue outer`.
  3. **Drill**: Loop over `"456!789"` accumulating a number until the first non-digit stops the loop via `d := parse_digit(ch) or_break`, plus an enum-error `or_break` Drill.

### `180_deferred_procedure_attributes.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `@(deferred_out=exit_proc)`, `@(deferred_in=exit_proc)`, `@(deferred_in_out=exit_proc)`, `@(deferred_none=exit_proc)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how Odin achieves deterministic RAII-style scope guards *without* hidden C++ constructors/destructors: attaching `@(deferred_in=unlock)` or `@(deferred_out=end_scope)` to an entry procedure automatically inserts a `defer exit_proc(...)` at the caller's call site!
  2. **Drill**: Define `Scope_Token :: struct { name: string }`, write `end_profile_scope :: proc(tok: Scope_Token)` that prints `"[END] "`, and write `@(deferred_out=end_profile_scope) profile_scope :: proc(name: string) -> Scope_Token` that prints `"[BEGIN] "`.
  3. **Drill**: Write `@(deferred_in=...)` (passes entry arguments to exit proc) and `@(deferred_in_out=...)` (passes entry args + return value to exit proc) scope guards, and test nested `{ ... }` blocks in `main`.

### `185_closures_and_passing_state.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: Inline procedure literals `fn := proc(x: int) -> int { ... }`, why local variable capture is forbidden (`#no_capture`), passing state explicitly via `(val: int, state: ^State)` or `context.user_ptr`, `slice.sort_by` comparator pattern.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:slice"`, `Filter_State :: struct { min_val, max_val: int }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why Odin procedures never implicitly allocate a heap closure environment (so every `proc(...)` is just a plain function pointer!).
  2. **Error check**: Show an inline `proc` inside `main` (`// Try referencing a local variable 'threshold' inside the proc literal to see the compiler error`).
  3. **Drill**: Write `count_matching :: proc(items: []int, state: ^Filter_State, pred: proc(x: int, s: ^Filter_State) -> bool) -> int` and call it with an inline `proc` literal that reads `s.min_val` and `s.max_val`, plus sort a slice using `slice.sort_by`.
  4. **Drill**: Show the alternative using `context.user_ptr = &filter_state` so a 1-argument `pred: proc(x: int) -> bool` casts `(^Filter_State)(context.user_ptr)` inside its body.

### `190_custom_iterators.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: Iterator state struct + step procedure `next :: proc(it: ^Iter) -> (val: T, idx: int, cond: bool)`, `for val, idx in next(&it)`, `for val in next(&it)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain Odin's zero-overhead custom iterator convention: any procedure that returns `(Value, bool)` or `(Value, Index, bool)` can be called directly in `for v in step_proc(&it)` — the loop calls `step_proc(&it)` on every iteration until the trailing `bool` is `false`!
  2. **Drill**: Define `Step_Range_Iter :: struct { current, stop, step, index: int }`.
  3. **Drill**: Write `step_range_next :: proc(it: ^Step_Range_Iter) -> (val: int, idx: int, ok: bool)` that advances `it.current += it.step` and `it.index += 1` while `it.current < it.stop`.
  4. **Drill**: Write a stateful collection cursor iterator over a slice (e.g., filtering positive numbers) and iterate both iterators in `main`.

### `195_unit_testing_with_odin_test.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:testing"`, `@(test)` attribute on `proc(t: ^testing.T)`, `testing.expect(t, cond, msg)`, `testing.expect_value(t, actual, expected)`, `testing.expectf(t, cond, fmt, ..args)`, automatic leak detection in `odin test`, CLI: `odin test 195_unit_testing_with_odin_test.odin -file`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:testing"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `odin test <file>.odin -file` discovers all `@(test)` procedures in the package, runs them in parallel by default, and checks for memory leaks in tests automatically!
  2. **Drill**: Write a pure procedure `clamp_and_double :: proc(x, lo, hi: int) -> int`.
  3. **Drill**: Write `@(test) test_clamp_and_double :: proc(t: ^testing.T)` using `testing.expect_value` and `testing.expect` on in-range, below-lo, and above-hi inputs, plus a `@(test)` procedure exercising leak-free dynamic allocation (`make`/`defer delete`) and calling `clamp_and_double` in `main` so both `odin run` and `odin test` work.

---

## `200`–`299`: Compound Types, Value vs. Reference Semantics & Data Layout

### `200_fixed_arrays_and_swizzling.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `[N]T`, `[H][W]T` 2D grids, `[?]T{...}`, ranged compound literals `[0..=3 = 10, 4 = 99]`, array arithmetic (`a + b`, `a - b`, `a * b`, `a * scalar`), swizzling (`.x`, `.y`, `.z`, `.w`, `.r`, `.g`, `.b`, `.a`, `.xy`, `.zyx`, `.rgba`, `.bgra`, lvalue swizzle `v.xy = {1, 2}`), `builtin.swizzle(v, 2, 1, 0)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`, 1 starter convenience line `v1 := [3]f32{1.0, 2.0, 3.0}` (used/printed).
- **Ordered Outline**:
  1. Explain that fixed arrays `[N]T` in Odin support direct element-wise arithmetic (`v1 + v2`, `v1 * 2.0`), shader-style vector swizzling up to 4 components (`xyzw` / `rgba`), and row-major 2D `[H][W]T` grids.
  2. **Drill**: Declare `"v2"` (`[3]f32{4.0, 5.0, 6.0}`), compute `sum_vec := v1 + v2` and `scaled := v1 * 10.0`.
  3. **Drill**: Extract `xy_pair := v1.xy` (`[2]f32`), reverse `reversed := v1.zyx`, and mutate `v1.xz = {99.0, 88.0}` via lvalue swizzling.
  4. **Drill**: Declare `"color_rgba"` (`[4]u8{255, 128, 64, 255}`) and convert it to BGRA in one expression `color_rgba.bgra`, initialize an `[8]int` table using ranged indices `[0..=3 = 1, 4..=7 = 2]`, and build a small `[3][3]int` 2D grid.

### `205_slices_and_views.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `[]T`, `runtime.Raw_Slice { data: rawptr, len: int }`, `arr[:]`, `arr[start:end]`, `arr[:end]`, `arr[start:]`, `copy(dst, src)`, `len(s)`, `raw_data(s)`, `nil` slice (`s == nil` vs `len(s) == 0`).
- **Scaffold**: `package main`, `import "core:fmt"`, `import "base:runtime"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain that a slice `[]T` is a 16-byte view (`data` pointer + `len`) into contiguous memory; slicing never allocates or copies elements, and holding a slice view into a `[dynamic]T` becomes dangling if `append` reallocates!
  2. **Drill**: Create `backing := [6]int{10, 20, 30, 40, 50, 60}`, take `middle := backing[1:5]`, mutate `middle[0] = 999`, print `backing` to prove they share memory, and copy into an independent buffer with `copy(dst[:], middle)`.
  3. **Drill**: Inspect `transmute(runtime.Raw_Slice)middle` (or `raw_data(middle)` and `len(middle)`), compare `empty_slice: []int` (`nil`, `len == 0`) with `backing[0:0]` (non-nil pointer, `len == 0`), and show why a slice view into a growing `[dynamic]int` invalidates across `append` reallocation.

### `210_value_vs_reference_and_for_ref.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: Value copy semantics (`[N]T`, `struct`) vs header reference semantics (`[]T`, struct containing `[]T` aliasing!), `for v in items` (value copy) vs `for &v in items` (pointer reference to element on `[dynamic]T`, `map[K]V`, and nested 2D grids), passing `[N]T` vs `^[N]T` vs `[]T` to procedures.
- **Scaffold**: `package main`, `import "core:fmt"`, `Item :: struct { id: int, hp: int }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain the trap that catches C/Python/JS developers in Odin: `for item in items { item.hp += 10 }` modifies a **temporary copy** (or fails to compile on read-only binding); to mutate elements of an array, slice, dynamic array, map, or 2D grid in place, write `for &item in items { item.hp += 10 }`! Also explain why copying a struct that holds a `[]T` slice still aliases the slice's backing buffer.
  2. **Drill**: Create `party := [3]Item{{1, 50}, {2, 60}, {3, 70}}`, run a `for &member, idx in party` loop that adds `25` to `member.hp`, plus `for &v` over a `[dynamic]Item`, `map[string]Item`, and nested 2D `[2][2]int` grid.
  3. **Drill**: Write `try_zero_array :: proc(a: [3]int)` (does not affect caller!) vs `zero_slice :: proc(s: []int)` (mutates caller's backing array!) and demonstrate struct-containing-slice aliasing in `main`.

### `215_dynamic_arrays.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `[dynamic]T`, `runtime.Raw_Dynamic_Array { data, len, cap, allocator }`, `make([dynamic]T)`, `make([dynamic]T, len, cap)`, `defer delete(arr)`, `append(&arr, val)`, `append(&arr, ..slice)`, `pop(&arr)`, `pop_safe(&arr)`, `ordered_remove(&arr, idx)`, `unordered_remove(&arr, idx)`, `clear(&arr)`, `resize(&arr, n)`, `reserve(&arr, cap)`, `shrink(&arr)`, passing `^[dynamic]T` when appending inside a procedure.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `[dynamic]T` (32-byte header storing `data`, `len`, `cap`, and `allocator` right inside the header!), why `append(&arr, ...)` takes a pointer `^[dynamic]T`, and why **storing a pointer `&arr[0]` across an `append` is a bug** if reallocation moves the buffer!
  2. **Drill**: Create `nums := make([dynamic]int, 0, 8)` with `defer delete(nums)`, `append` individual ints and a slice `..[]int{40, 50}`, demonstrate live `&nums[0]` pointer invalidation across capacity growth, and print `len(nums)` and `cap(nums)`.
  3. **Drill**: Demonstrate `ordered_remove(&nums, 1)` (preserves order, shifts elements) vs `unordered_remove(&nums, 1)` (O(1), swaps last element into index `1`), including safe backward removal with `unordered_remove` inside a loop.
  4. **Drill**: Write `append_countdown :: proc(list: ^[dynamic]int, start: int)` taking `^[dynamic]int` and call it from `main`.

### `220_fixed_capacity_dynamic_arrays.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `[dynamic; N]T` (built-in fixed-capacity stack dynamic array), struct-embedded `[dynamic; N]T`, `append(&arr, x)`, `pop(&arr)`, `clear(&arr)`, `len(arr)`, `cap(arr)`, `import "core:container/small_array"` (`small_array.Small_Array(N, T)`).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `[dynamic; N]T`: a dynamic-length array whose `N` elements live **inline on the stack or struct** (zero heap allocations, no `make` or `delete` needed!), supporting `append`, `pop`, `clear`, `ordered_remove`, and `unordered_remove`.
  2. **Drill**: Declare `recent_events: [dynamic; 4]string` (no `make` or `delete`!), `append` 4 event strings, check `len(recent_events)` and `cap(recent_events)`, `pop` one, and iterate `for ev in recent_events[:]`, plus embed a `[dynamic; 8]int` buffer inside a struct.

### `225_maps.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `map[K]V`, `make(map[K]V)`, `defer delete(m)`, `m[k] = v`, `val, ok := m[k]`, `k in m`, `k not_in m`, `delete_key(&m, k)`, `clear(&m)`, `reserve(&m, cap)`, `len(m)`, `cap(m)`, `for k, v in m`, `for k, &v in m`, composite keys (`map[[2]int]Tile`), nested `map[string][dynamic]int` cleanup.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain built-in hash maps `map[K]V` (any comparable type `K` where `==` is defined works as a key: strings, ints, enums, pointers, fixed arrays `[2]int`, non-slice structs!) and the difference between `clear(&m)` (keeps backing capacity) vs `delete(m)` (frees memory).
  2. **Drill**: Create `prices := make(map[string]int)` with `defer delete(prices)`, insert `"apple" = 120`, `"banana" = 80`, `"cherry" = 250`.
  3. **Drill**: Look up `"banana"` with `price, found := prices["banana"]`, check `"mango" not_in prices`, and use `prices["mango"] or_else 0`.
  4. **Drill**: Iterate `for item, &cost in prices` to apply a 10% discount in place, compare `clear(&prices)` vs `delete(prices)`, build a `map[[2]int]string` (composite fixed-array coordinate key), and build a nested `map[string][dynamic]int` with proper per-entry `delete` cleanup before deleting the outer map!

### `230_structs_and_literals.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `Name :: struct { ... }`, grouped fields `x, y, z: f32`, struct tags ``field: Type `tag` ``, positional literal `Vec3{1, 2, 3}`, field-named literal `Vec3{x = 1, z = 3}`, zero literal `Vec3{}`, nested structs, struct equality `a == b`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain Odin struct definitions, why structs are comparable with `==` and `!=` as long as all their fields are comparable, and how designated field initialization leaves omitted fields zeroed.
  2. **Drill**: Define `Vec2 :: struct { x, y: f32 }` and `Player :: struct { name: string, pos: Vec2, health: int, alive: bool }`.
  3. **Drill**: Construct `"hero"` using named fields (`pos = {10, 20}`, `health = 100`, `alive = true`), mutate `hero.pos.x += 5`, and compare two `Vec2` values with `==`.

### `235_struct_memory_layout_directives.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `struct #packed { ... }`, `struct #align(N) { ... }`, `struct #raw_union { ... }`, `struct #all_or_none { ... }`, `size_of`, `align_of`, `offset_of`, `#assert`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how the compiler orders and pads struct fields by default vs `#packed` (1-byte alignment, no padding for network/binary file headers), `#align(64)` (cache-line alignment to avoid false sharing), `#raw_union` (all fields start at offset 0 like C `union`), and `#all_or_none` (compound literals must specify either 0 fields `{}` or *all* fields!).
  2. **Drill**: Define `Padded_Header :: struct { a: u8, b: u32, c: u8 }` and `Packed_Header :: struct #packed { a: u8, b: u32, c: u8 }`, print `size_of` and `offset_of` for both (`12` bytes vs `6` bytes), and reorder fields (`b: u32, a: u8, c: u8`) to observe size drop without `#packed`!
  3. **Drill**: Define `Cache_Line_Counter :: struct #align(64) { count: u64 }` and `#assert(align_of(Cache_Line_Counter) == 64)`.
  4. **Drill**: Define `Register32 :: struct #raw_union { full: u32, bytes: [4]u8 }`, write `full = 0x01020304`, and read `bytes`.

### `240_enums_and_enumerated_arrays.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `Name :: enum Backing_Int { A, B = 5, C }`, implicit selector `.A`, `min(Enum)`, `max(Enum)`, `len(Enum)`, `for e in Enum`, **enumerated array** `[Enum]Value_Type`, `[Enum][dynamic]T` bucket table, `#partial [Enum]Value_Type{ .A = 10 }`, `#sparse [Sparse_Enum]Value_Type`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain two of Odin's best ergonomic features: (a) **implicit selector expressions** (`.North` anywhere the compiler knows the enum type, including `switch`, comparisons, assignments, and struct literals), and (b) **enumerated arrays** `[My_Enum]T` indexed directly by enum values instead of integer casts!
  2. **Drill**: Define `Tile_Kind :: enum u8 { Grass, Water, Mountain, Road }`.
  3. **Drill**: Declare an enumerated array `movement_cost := [Tile_Kind]f32{ .Grass = 1.0, .Water = 5.0, .Mountain = 3.5, .Road = 0.5 }` and index `movement_cost[.Mountain]`.
  4. **Drill**: Iterate `for kind in Tile_Kind` printing each `kind` and `movement_cost[kind]`, create a `#partial [Tile_Kind]bool{ .Water = true }` hazard table, and build an `[Tile_Kind][dynamic]string` bucket table (with `defer delete` per bucket!).

### `245_bit_sets_and_bit_fields.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `bit_set[Enum; Underlying]`, `bit_set[0..<8; u8]`, set union `a + b` (or `a | b`), intersection `a & b`, difference `a - b` (or `a &~ b`), symmetric difference `a ~ b`, membership `flag in bs`, `flag not_in bs`, subset `a <= b`, `card(bs)` (popcount), `incl(&bs, .Flag)`, `excl(&bs, .Flag)`, `bit_field Backing_Int { field: Type | bits, ... }` (including enum fields!).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why `bit_set` replaces error-prone `(1 << FLAG)` bitmask macros with type-safe set operations, and `bit_field` packs sub-byte/multi-bit integer/bool/enum fields into an exact backing integer width.
  2. **Drill**: Define `Status_Effect :: enum { Poisoned, Burning, Frozen, Shielded }` and `Status_Set :: bit_set[Status_Effect; u8]`.
  3. **Drill**: Create `active := Status_Set{.Poisoned, .Shielded}`, add `.Burning` with `incl(&active, .Burning)` or `+`, check `.Frozen not_in active`, test set algebra (`+`, `&`, `-`, `~`, `<=`), and print `card(active)`.
  4. **Drill**: Define `Gba_Sprite_Attr :: bit_field u16 { y_coord: u8 | 8, affine: bool | 1, double_size: bool | 1, mode: u8 | 2, mosaic: bool | 1, palette_256: bool | 1, shape: Sprite_Shape | 2 }` (with an enum field!), instantiate it, and print its `u16(attr)` value.

### `250_unions_and_type_switches.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `union { T1, T2, ... }`, `nil` default state, `union #no_nil { T1, T2 }`, `union #shared_nil { Err_A, Err_B }`, type assertion `v, ok := u.(T1)`, `u.(T1) or_else default`, `switch v in u { case T1: ... case nil: ... }`, `switch &v in u` (mutating the active variant in place!).
- **Scaffold**: `package main`, `import "core:fmt"`, `Circle :: struct { radius: f32 }`, `Rect :: struct { w, h: f32 }`, `Shape :: union { Circle, Rect }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain tagged unions: a `union` stores a hidden tag alongside the payload; by default `nil` is a valid empty state unless `#no_nil` is specified, and `#shared_nil` merges multiple error enums' `0` (`None`) values so any `.None` equals `nil`!
  2. **Drill**: Declare `s: Shape = Circle{radius = 5.0}`, extract `c, ok := s.(Circle)`, then use `switch &v in s` to double `v.radius` in place and compute area across `case Circle:`, `case Rect:`, `case nil:`.
  3. **Drill**: Define a `#no_nil` AST expression union (`Expr :: union #no_nil { Int_Lit, Add_Expr }`), plus `Net_Error :: enum { None, Timeout }` and `Disk_Error :: enum { None, Full }` combined into `App_Error :: union #shared_nil { Net_Error, Disk_Error }` verifying `Net_Error.None == nil`.

### `255_pointers_and_multi_pointers.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `^T`, `&x`, `p^`, automatic field/index dereference `p.field` and `arr_ptr[i]`, `nil`, `[^]T` (multi-pointer), `raw_data(slice_or_arr)`, `mem.ptr_to_bytes`, indexing `mp[i]`, slicing `mp[:n]`, pointer offset `mp[offset:]`, `rawptr`, `uintptr` alignment.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:mem"`, `Node :: struct { val: int, next: ^Node }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why Odin separates `^T` (pointer to **one** `T` — no pointer arithmetic allowed!) from `[^]T` (pointer to **0 or more contiguous** `T`s — supports indexing `mp[i]` and slicing `mp[0:n]`, used for C buffers and backing arrays).
  2. **Drill**: Create two stack `Node`s, link `n1.next = &n2`, and walk them via `curr: ^Node = &n1` accessing `curr.val` (auto-dereferenced!).
  3. **Drill**: Obtain `mp: [^]int = raw_data(scores[:])` from a `[4]int` array, read `mp[2]`, advance by slicing `mp_shifted := mp[1:]`, slice it back into `bounded: []int = mp[0:4]`, and practice `mem.ptr_to_bytes` + `uintptr` alignment arithmetic.

### `260_distinct_types_and_aliases.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `Alias :: Type` (type alias) vs `Distinct_Type :: distinct Type` (new nominal type with identical layout and operations!).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `distinct`: unlike C `typedef` (which is just a weak alias), `Entity_Id :: distinct u64` and `Texture_Id :: distinct u64` are incompatible types at compile time while retaining all `u64` operators (`+`, `==`, `<`) among values of the same distinct type!
  2. **Drill**: Define `Seconds :: distinct f64`, `Meters :: distinct f64`, and alias `Float64_Alias :: f64`.
  3. **Drill**: Declare `dt: Seconds = 0.5` and `dist: Meters = 10.0` (untyped literals adapt automatically!), compute `dt + Seconds(1.0)`, and write `velocity :: proc(d: Meters, t: Seconds) -> f64 { return f64(d) / f64(t) }` (`// Try calling velocity(dt, dist) in the wrong order to see the type error`).

### `265_using_and_subtype_polymorphism.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `using field: Base_Type` inside a `struct`, `#subtype`, implicit pointer/value upcasting (`^Derived` -> `^Base` when `using` field is at offset 0), downcasting safely via a tagged `variant: union { ^Player, ^Enemy }` field on the base struct.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how Odin handles composition and subtype polymorphism without classes or hidden vtables: embedding `using entity: Entity` at offset 0 of `Player` lets you access `player.pos` directly *and* pass `&player` to any `proc(e: ^Entity)`!
  2. **Drill**: Define `Entity :: struct { id: u64, pos: [2]f32, variant: union { ^Player, ^Door } }`, `Player :: struct { using base: Entity, stamina: f32 }`, and `Door :: struct { using base: Entity, locked: bool }`.
  3. **Drill**: Write `move_entity :: proc(e: ^Entity, delta: [2]f32) { e.pos += delta }` and call `move_entity(&player, {1, 2})` directly without casting `&player` (`// Try placing a field before 'using base' to see non-offset-0 upcast fail`).
  4. **Drill**: Write `interact :: proc(e: ^Entity)` that switches on `switch v in e.variant` to handle `^Player` and `^Door` type-safely.

### `270_any_and_typeid.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `any`, `typeid`, `typeid_of(T)`, `v.id`, `v.data`, `switch x in any_val`, `val, ok := any_val.(T)`, lifetime hazard of returning an `any` pointing to a local stack variable!
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain that `any` is `{ data: rawptr, id: typeid }` (16 bytes): assigning `a: any = 42` puts `42` on the stack and points `a.data` at it (which is why you must **never** return an `any` referencing a local stack variable after the procedure returns!).
  2. **Drill**: Write `describe_any :: proc(a: any)` using `switch v in a { case int: ... case string: ... case bool: ... case: ... }` and print `a.id`.
  3. **Drill**: Call `describe_any` from `main` with `123`, `"Odin"`, `true`, and `[2]int{1, 2}`.

### `280_matrices_and_linalg.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `matrix[Rows, Cols]T` (`1 <= Rows, Cols <= 4`), `#row_major matrix[R, C]T`, `m[row, col]`, matrix * matrix (`m1 * m2`), matrix * vector (`m * v`), `transpose(m)`, `determinant(m)`, `inverse(m)`, `adjugate(m)`, `matrix_trace(m)`, `import "core:math/linalg"`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:math/linalg"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain Odin's built-in `matrix[R, C]T` type: written in mathematical row-by-row literal order, stored column-major in memory by default (matching OpenGL/GLSL/Vulkan, or row-major with `#row_major`), and supporting native `*` multiplication with vectors!
  2. **Drill**: Declare a 2x2 scaling/rotation `mat := matrix[2, 2]f32{ 2, 0, 0, 3 }` (note how scalar `1` cast to `matrix[2, 2]f32(1)` creates an identity matrix!), multiply `pt := [2]f32{4, 5}` via `transformed := mat * pt`, and compare `#row_major matrix[2, 2]f32` memory order.
  3. **Drill**: Compute `determinant(mat)`, `inverse(mat)`, verify `inverse(mat) * transformed == pt`, and build `matrix[4, 4]f32` + `linalg.matrix4_translate_f32` / `linalg.dot` / `linalg.cross` transforms.

---

## `300`–`399`: Packages, Scopes, Directives, Attributes & Build Configuration

### `300_packages_and_imports/` *(Multi-File Lab)*
- **Files**:
  - `300_packages_and_imports/main.odin` (`package main`, `import "core:fmt"`, `import "geometry"`, `import m "geometry"`)
  - `300_packages_and_imports/sibling.odin` (`package main`)
  - `300_packages_and_imports/geometry/shapes.odin` (`package geometry`)
- **Syntax / Keywords / Built-ins Checklist**: `package main`, `package geometry`, `import "geometry"`, aliased `import geo "geometry"`, package-shared types, directory-as-package compilation (`odin run 300_packages_and_imports` without `-file`!).
- **Scaffold**: Minimal `package` headers + shared `Point2D` / `Circle` contract in `geometry/shapes.odin` + `main :: proc()` in `main.odin` (only 1 minimal cross-file anchor call, zero `_ =` silencers).
- **Ordered Outline**:
  1. In `sibling.odin`: **Drill** to write `sibling_helper :: proc(x: int) -> int` and share package-scoped types with `main.odin` with **no** `import`!
  2. In `geometry/shapes.odin`: **Drill** to implement `circle_area :: proc(c: Circle) -> f32` and `rect_perimeter` using package-shared types.
  3. In `main.odin`: **Drill** to import `"geometry"`, call `sibling_helper`, and call `geometry.circle_area`.

### `310_visibility_and_private/` *(Multi-File Lab)*
- **Files**:
  - `310_visibility_and_private/main.odin` (`package main`, `import "vault"`)
  - `310_visibility_and_private/vault/public_api.odin` (`package vault`)
  - `310_visibility_and_private/vault/internal_helpers.odin` (`#+private`, `package vault`)
- **Syntax / Keywords / Built-ins Checklist**: Exported by default, `@(private)` / `@(private="package")` (visible across files in `package vault`, hidden from `package main`), `@(private="file")` (visible only inside that single `.odin` file!), file-top tags `#+private` and `#+private file`.
- **Scaffold**: `package` headers + 1 minimal exported anchor constant/entry + `main :: proc()` in `main.odin`.
- **Ordered Outline**:
  1. In `vault/internal_helpers.odin`: **Drill** to add `#+private` at the very top of the file and write `hash_pin :: proc(pin: u32) -> u32`.
  2. In `vault/public_api.odin`: **Drill** to write `@(private="file") SECRET_SALT :: 0x9E3779B9`, demonstrate cross-sibling access to `hash_pin` vs file-only `@(private="file")`, and expose `verify_pin :: proc(pin: u32) -> bool`.
  3. In `main.odin`: **Drill** to call `vault.verify_pin(1234)` (`// Try calling vault.hash_pin or vault.SECRET_SALT from main.odin to see the visibility error`).

### `320_build_tags_and_file_suffixes.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: File tags at line 1 before `package`: `#+build windows, linux, darwin`, `#+build amd64, arm64`, `#+build !freestanding`, `#+vet !unused-variables`, filename suffix conventions (`_windows.odin`, `_linux.odin`, `_darwin.odin`, `_unix.odin`, `_amd64.odin`, `_test.odin`).
- **Scaffold**: `#+build windows, linux, darwin` at top, `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain the two ways Odin selects files per platform without preprocessor macros: (a) automatic filename suffixes (`net_windows.odin` is only compiled on Windows; `foo_test.odin` is only compiled during `odin test`!), and (b) `#+build` tags at the very top of a file before `package` (noting how multi-file `_os` packages split implementations cleanly).
  2. **Drill**: Inspect and test `#+build` and `#+vet` file tags, combine `ODIN_OS` / `ODIN_ARCH` checks with `when`, and print target platform details inside `main`.

### `330_compile_time_config_and_defines.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `#config(IDENT, default_val)`, `#defined(IDENT)`, CLI `-define:IDENT=val` (bool, int, or string).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `#config(NAME, default)` reads a compile-time constant passed via `-define:NAME=...` on the command line (or falls back to `default`).
  2. **Drill**: Declare `APP_TITLE :: #config(APP_TITLE, "OdinApp")`, `MAX_THREADS :: #config(MAX_THREADS, 4)`, and `VERBOSE :: #config(VERBOSE, false)`.
  3. **Drill**: Print all three in `main` and use `when #defined(CUSTOM_FLAG)` to detect if `-define:CUSTOM_FLAG=true` was provided on the CLI.

### `340_load_and_embed_files.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `#load("relative_path")` (`[]u8`), `#load("relative_path", string)`, `#load_hash("relative_path", "sha256")`, `#exists("relative_path")`, `#file`, `#directory`, `#line`, `#procedure`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `#load` bakes any file's bytes directly into the binary's read-only data segment at compile time (zero runtime file I/O!), and how `#exists` checks whether a file exists at compile time.
  2. **Drill**: Use `HAS_PLAN :: #exists("plan.md")` and embed `"001_first.odin"` (or `"plan.md"`) as a compile-time `string` constant using `#load("001_first.odin", string)`.
  3. **Drill**: Print `len(EMBEDDED_SOURCE)`, `#file`, `#directory`, `#line`, and `#procedure` inside `main`.

### `350_init_fini_static_and_rodata.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `@(init)` on `proc "contextless" ()` or `proc()`, `@(fini)` on `proc()`, `@(priority_index=N)`, `@(static)` on a local variable inside a procedure, `@(rodata)` on a constant array, `@(cold)`, `@(deprecated="msg")`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `@(init)` (runs automatically before `main`), `@(fini)` (runs after `main` exits), `@(priority_index=N)` ordering, `@(static)` (local variable stored in static memory that keeps its value across calls), and `@(rodata)` (places a constant lookup table in read-only memory so you can take its address `&TABLE[i]`).
  2. **Drill**: Write multiple `@(init)` and `@(fini)` hooks with explicit `@(priority_index=N)` to observe deterministic startup/shutdown ordering.
  3. **Drill**: Write `next_id :: proc() -> int` containing `@(static) counter: int = 0` that increments and returns `counter` on each call.
  4. **Drill**: Declare `@(rodata) SIN_TABLE := [4]f32{0.0, 0.7071, 1.0, 0.7071}` and take a pointer `&SIN_TABLE[2]`.

### `360_bounds_check_and_type_assert_directives.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `#bounds_check`, `#no_bounds_check`, `#type_assert`, `#no_type_assert`, CLI `-no-bounds-check`, `-no-type-assert`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain that Odin bounds-checks all array/slice/string indexing by default (preventing buffer overflows!), and lets you disable bounds checks on a single statement or hot inner loop with `#no_bounds_check` after verifying lengths once up front.
  2. **Drill**: Write `dot_product_fast :: proc(a, b: []f32) -> f32` and a flat 2D `#no_bounds_check` hot loop that assert sizes once up front before indexing.

### `370_collections_and_ols_setup.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: Library collections (`core:`, `base:`, `vendor:`, custom `-collection:shared=path/to/dir` imported via `import "shared:my_pkg"`), `ols.json` schema (`collections`, `enable_semantic_tokens`, `enable_hover`, `enable_snippets`, `checker_args`).
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how Odin's three built-in collections (`base`, `core`, `vendor`) work and how `-collection:<name>=<dir>` + `ols.json` configure custom project-wide package roots for both the compiler and IDE language server.
  2. **Drill**: Construct a `Config_OLS :: struct` matching `ols.json` fields (`checker_args: string`, `enable_snippets: bool`, etc.) and print a sample `ols.json` configuration for this workspace.

### `380_vet_flags_and_compiler_hygiene.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `-vet`, `-vet-unused`, `-vet-unused-variables`, `-vet-unused-imports`, `-vet-shadowing`, `-vet-using-stmt`, `-vet-using-param`, `-vet-cast`, `-vet-semicolon`, `-vet-tabs`, `-vet-uninitialized`, `-strict-style`, `-warnings-as-errors`, `#+vet` file tag.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain every check enabled by `-vet` and `-strict-style` (1TBS attached braces, trailing commas on multi-line compound literals, case label alignment, no unneeded semicolons or casts).
  2. **Drill**: Write a multi-line struct literal with trailing commas, a `switch` statement formatted for `-strict-style`, and interactive `// Try uncommenting:` experiments triggering `-vet-shadowing`, `-vet-cast`, `-vet-unused-variables`, and `-vet-semicolon` (`odin check 380_vet_flags_and_compiler_hygiene.odin -file -vet -strict-style`).

---

## `400`–`499`: Context System, Memory Management, Arenas & Custom Allocators

### `400_implicit_context_system.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `context` keyword (`runtime.Context`), `context.allocator`, `context.temp_allocator`, `context.logger`, `context.assertion_failure_proc`, `context.user_ptr`, `context.user_index`, scoped `context` modification (`{ context.user_index = 99; ... }`, `context.allocator = arena_alloc`).
- **Scaffold**: `package main`, `import "core:fmt"`, `import "base:runtime"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how every normal Odin procedure secretly receives a hidden `context: ^runtime.Context` pointer: modifying `context.user_index = 42` or `context.allocator = my_alloc` copies the `Context` on the current stack frame and passes the modified copy to all procedures called within that scope, automatically restoring the old `context` when the scope exits!
  2. **Drill**: Write `print_current_user :: proc()` (zero parameters!) that reads `context.user_index` and `context.user_ptr`.
  3. **Drill**: Call `print_current_user()` in `main`, then open an inner `{ ... }` block where you set `context.user_index = 777` and `context.user_ptr = &secret_name`, call `print_current_user()`, and call it again outside the block to confirm restoration, plus wrap an unchanged helper in `context.allocator = arena_alloc`.

### `410_new_make_free_and_delete.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `new(T)`, `new_clone(val)`, `free(ptr)`, `make([]T, len)`, `make([dynamic]T, len, cap)`, `make(map[K]V, cap)`, `delete(slice_or_dyn_or_map_or_string)`, explicit allocator parameter `new(T, alloc)` / `make([]T, len, alloc)` / `delete(x, alloc)`, deep-free struct vs arena, `runtime.Allocator_Error`.
- **Scaffold**: `package main`, `import "core:fmt"`, `Transform :: struct { pos: [3]f32, scale: f32 }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain the golden pairing rule in Odin (`docs/odin/faq.md`):
     - `new(T)` / `new_clone(v)` allocates a **single** item -> free it with `free(ptr)`.
     - `make(...)` allocates a **collection** (`[]T`, `[dynamic]T`, `map[K]V`) -> free it with `delete(col)`.
  2. **Drill**: Allocate a `^Transform` on the heap with `new(Transform)` and another with `new_clone(Transform{pos = {1, 2, 3}, scale = 2.0})`, paired with `defer free(...)`.
  3. **Drill**: Allocate a `[]f32` of length 8 with `make([]f32, 8)` and a `[dynamic]int` with `make([dynamic]int, 0, 16)`, paired with `defer delete(...)`, check the optional `err` second return `buf, err := make([]byte, 256)`, and compare deep-freeing a multi-field struct vs bulk arena cleanup.

### `420_tracking_allocator_leak_detection.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:mem"`, `mem.Tracking_Allocator`, `mem.tracking_allocator_init(&track, context.allocator)`, `mem.tracking_allocator(&track)`, `mem.tracking_allocator_destroy(&track)`, `track.allocation_map` (`entry.location`, `entry.size`), `track.bad_free_array` (`entry.location`, `entry.memory`).
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:mem"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why every Odin application should wrap `context.allocator` in a `mem.Tracking_Allocator` during development: it records the `#caller_location` (`file:line`) of every allocation and immediately catches memory leaks and invalid frees on shutdown!
  2. **Drill**: Initialize `track: mem.Tracking_Allocator` with `mem.tracking_allocator_init(&track, context.allocator)`, assign `context.allocator = mem.tracking_allocator(&track)`, and write the `defer` block that loops over `track.allocation_map` and `track.bad_free_array` before calling `mem.tracking_allocator_destroy(&track)`.
  3. **Drill**: Allocate a `make([]int, 64)` and `defer delete` it cleanly (`0 leaks`), include a commented-out leak experiment (`// leaked := make([]u8, 1024); fmt.println(len(leaked))`) plus a `track.bad_free_array` double-free/stack-free experiment (no `_ =` silencers!).

### `430_temp_allocator_and_frame_loops.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `context.temp_allocator`, `free_all(context.temp_allocator)`, `fmt.tprintf`, `make([]T, n, context.temp_allocator)`, `runtime.DEFAULT_TEMP_ALLOCATOR_TEMP_GUARD()`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `context.temp_allocator`: a thread-local scratch allocator meant for short-lived allocations (like `fmt.tprintf` strings or temporary slices within a single frame or request) that are all wiped at once with `free_all(context.temp_allocator)` at the end of each loop iteration—and why storing a `fmt.tprintf` string across frames is a dangling-pointer hazard!
  2. **Drill**: Run a `for frame in 0..<5` loop that formats a temporary status string with `msg := fmt.tprintf("Frame %d: %d entities", frame, frame * 10)` and allocates a temp slice `scratch := make([]int, 32, context.temp_allocator)`, ending the loop body with `free_all(context.temp_allocator)`, plus demonstrate the cross-frame `fmt.tprintf` dangling trap.

### `440_string_allocation_ownership.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:strings"`, `import "core:mem"`, zero-alloc string slicing `s[a:b]`, temp-allocated `fmt.tprintf` / `strings.clone(s, context.temp_allocator)`, heap-allocated `fmt.aprintf` / `strings.clone(s)` / `strings.concatenate` / `strings.clone_to_cstring` (must call `delete(...)`!), `map[string]string` owned key/value tracking, `strings.Builder` (`strings.builder_make()`, `defer strings.builder_destroy(&b)`).
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:mem"`, `import "core:strings"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain the #1 cause of memory leaks in beginner Odin code: not knowing which string helpers allocate on `context.allocator` vs `context.temp_allocator` vs zero-allocation views.
  2. **Drill**: Set up `mem.Tracking_Allocator` at the top of `main`.
  3. **Drill**: Create a zero-alloc slice view, a `fmt.tprintf` string (freed via `free_all(context.temp_allocator)`), a `heap_str := fmt.aprintf("ID-%d", 42)` paired with `defer delete(heap_str)`, a `cloned := strings.clone("owned")` paired with `defer delete(cloned)`, and a `map[string]string` with owned keys/values freed before deleting the map, verifying `Tracking_Allocator` reports 0 leaks at exit!

### `450_fixed_buffer_arena.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:mem"`, `mem.Arena`, `mem.arena_init(&arena, buf[:])`, `mem.arena_allocator(&arena)`, `mem.Arena_Temp_Memory`, `mem.begin_arena_temp_memory(&arena)`, `mem.end_arena_temp_memory(temp)`, `arena.offset`, `arena.peak_used`, `free_all(arena_alloc)`, `mem.Allocator_Error.Out_Of_Memory`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:mem"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how a fixed-buffer `mem.Arena` works: you hand it a `[]byte` slice (on the stack or heap), and every allocation just bumps `arena.offset` forward with alignment padding; `free_all` resets `arena.offset = 0` in O(1)!
  2. **Drill**: Declare `backing_buf: [1024]byte`, initialize `arena: mem.Arena` with `mem.arena_init(&arena, backing_buf[:])`, and obtain `alloc := mem.arena_allocator(&arena)`.
  3. **Drill**: Allocate several slices and structs using `alloc`, print `arena.offset` and `arena.peak_used` after each allocation, test `mem.Arena_Temp_Memory` checkpoint/rewind, attempt an allocation larger than 1024 bytes to observe `.Out_Of_Memory`, and reset with `free_all(alloc)`.

### `460_virtual_memory_arenas.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:mem/virtual"`, `virtual.Arena`, `virtual.arena_init_growing(&arena)`, `virtual.arena_init_static(&arena, reserved, commit_size)`, `virtual.arena_allocator(&arena)`, `virtual.arena_free_all(&arena)`, `virtual.arena_destroy(&arena)`, `arena.total_used`, `arena.total_reserved`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:mem/virtual"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `core:mem/virtual`: unlike `mem.Arena` (which needs a pre-allocated `[]byte`), `virtual.Arena` reserves address space directly from the OS virtual memory manager (`VirtualAlloc` on Windows / `mmap` on POSIX) and commits physical pages on demand—ideal for messy graphs or ASTs with zero per-node `free`!
  2. **Drill**: Initialize `v_arena: virtual.Arena` with `err := virtual.arena_init_growing(&v_arena)` and `defer virtual.arena_destroy(&v_arena)`.
  3. **Drill**: Obtain `v_alloc := virtual.arena_allocator(&v_arena)`, set `context.allocator = v_alloc` inside a scope, allocate a `[dynamic]int`, a `map[string]int`, and a linked graph/tree without freeing them individually, print `v_arena.total_used`, and call `virtual.arena_free_all(&v_arena)`.

### `470_scratch_arenas_and_temp_blocks.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `virtual.Arena_Temp`, `virtual.arena_temp_begin(&arena)`, `virtual.arena_temp_end(temp)`, `virtual.arena_scratch_block(&arena)` (uses `@(deferred_out)` to automatically rewind the arena on block exit!), `mem.Arena_Temp_Memory`, `mem.begin_arena_temp_memory(&arena)`, `mem.end_arena_temp_memory(temp)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:mem/virtual"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain arena checkpoints (`Arena_Temp`): how a procedure can save an arena's current offset (`arena_temp_begin`), allocate megabytes of temporary intermediate data, and rewind the arena back to that exact offset (`arena_temp_end`) while keeping allocations made *before* the checkpoint intact—plus the two-arena scratch aliasing hazard when passing the same arena as both persistent and scratch!
  2. **Drill**: Initialize a `virtual.Arena`, allocate a persistent slice `perm_ids := make([]int, 4, alloc)`, print `arena.total_used`.
  3. **Drill**: Open a scratch block using `temp := virtual.arena_temp_begin(&arena)` (or `{ virtual.arena_scratch_block(&arena); ... }`), allocate a large temporary slice inside it, end the temp block, verify `arena.total_used` rewound back while `perm_ids` is still valid, and contrast safe two-arena scratch vs single-arena aliasing.

### `480_custom_and_panic_allocators.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `runtime.Allocator { procedure: Allocator_Proc, data: rawptr }`, `runtime.Allocator_Mode` (`.Alloc`, `.Alloc_Non_Zeroed`, `.Free`, `.Free_All`, `.Resize`, `.Query_Features`, `.Query_Info`), `mem.panic_allocator()`, `mem.nil_allocator()`, `mem.Rollback_Stack_Allocator`, `mem.rollback_stack_allocator_init`, `mem.rollback_stack_allocator`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:mem"`, `import "base:runtime"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how every allocator in Odin implements a single signature: `Allocator_Proc :: #type proc(allocator_data: rawptr, mode: Allocator_Mode, size, alignment: int, old_memory: rawptr, old_size: int, location := #caller_location) -> ([]byte, Allocator_Error)`.
  2. **Drill**: Write a `Counting_Allocator_Data :: struct { backing: runtime.Allocator, alloc_calls: int, bytes_allocated: int }` and `counting_allocator_proc` that increments counters on `.Alloc` and delegates all modes to `data.backing.procedure(...)`.
  3. **Drill**: Wrap `context.allocator` in your counting allocator in `main`, perform 3 allocations, print `alloc_calls` and `bytes_allocated`, exercise `mem.Rollback_Stack_Allocator` (LIFO rollbacks), and scope a zero-allocation hot loop with `context.allocator = mem.panic_allocator()`.

### `490_pool_and_handle_allocations.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:mem"`, `mem.Dynamic_Pool`, `mem.dynamic_pool_init(&pool)`, `mem.dynamic_pool_allocator(&pool)`, `mem.dynamic_pool_free_all(&pool)`, `mem.dynamic_pool_destroy(&pool)`, generational handle `{ index: u32, generation: u32 }` pattern.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:mem"`, `Entity_Handle :: struct { idx: u32, gen: u32 }`, `Entity_Slot :: struct { gen: u32, active: bool, name: string }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why systems/game programmers combine **block/slab pools (`mem.Dynamic_Pool`)** with **generational handles (`idx` + `gen`)** over raw heap pointers: `mem.Dynamic_Pool` grows in fixed-size slabs and frees all nodes in O(1), while freeing slot `3` increments `slots[3].gen` so any stale handle `{idx = 3, gen = 1}` immediately detects it is invalid!
  2. **Drill**: Initialize a `mem.Dynamic_Pool` (`mem.dynamic_pool_init(&pool)` + `defer mem.dynamic_pool_destroy(&pool)`), allocate several nodes via `mem.dynamic_pool_allocator(&pool)`, and reset/free them with `mem.dynamic_pool_free_all(&pool)`.
  3. **Drill**: Write `slot_alloc`, `slot_free`, and `slot_get` for an `[8]Entity_Slot` pool in `main`, allocate an entity `"Goblin"`, free it, allocate `"Dragon"` into the reused slot, and verify looking up the old `"Goblin"` handle returns `nil, false` because its generation no longer matches!

### `495_arena_program_lab/` *(Multi-File Lab)*
- **Files**:
  - `495_arena_program_lab/main.odin` (`package main`)
  - `495_arena_program_lab/level.odin` (`package main`)
  - `495_arena_program_lab/loader.odin` (`package main`)
- **Syntax / Keywords / Built-ins Checklist**: `virtual.Arena`, two-arena architecture (`level_arena` for persistent level state + `scratch_arena` rewound per load/command), `mem.Tracking_Allocator`, `strings.clone(s, level_alloc)`, explicit error propagation on malformed input lines.
- **Scaffold**: File headers + struct declarations in `level.odin` (`Room :: struct { name: string, connections: []int }`, `Level :: struct { rooms: []Room }`), zero dummy `return {}` stubs.
- **Ordered Outline**:
  1. In `loader.odin`: **Drill** to write `parse_level_line(raw_text: string, level_alloc, scratch_alloc: runtime.Allocator) -> (Level, bool)` that uses `scratch_alloc` for temporary split buffers, propagates malformed-line errors cleanly, and allocates the final `Room` slice and cloned room names into `level_alloc`.
  2. In `level.odin`: **Drill** to write `print_level(lvl: Level)` and `reset_level(level_arena: ^virtual.Arena)`.
  3. In `main.odin`: **Drill** to set up `Tracking_Allocator`, initialize `level_arena` and `scratch_arena`, load 2 levels sequentially (rewinding `scratch_arena` after each load and resetting `level_arena` between levels), test malformed line handling, and verify 0 leaks.

---

## `500`–`599`: Standard Library Essentials (`core:`), Containers, Spall & Tracy Hooks

### `500_fmt_and_string_builders.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:fmt"`, `import "core:strings"`, `fmt.printf`, `fmt.bprintf(buf[:], fmt_str, ..args)` (stack-buffer formatting, zero heap allocation!), `fmt.tprintf` (temp allocator), `fmt.aprintf` (heap allocator), `fmt.sbprintf(&builder, ...)`, `strings.Builder`, `strings.builder_make()`, `strings.builder_init_none(&b)` / `strings.builder_from_bytes(buf[:])`, `strings.builder_reset(&b)`, `strings.builder_destroy(&b)`, `strings.to_string(b)`, format verbs `%v`, `%#v`, `%T`, `%d`, `%08x`, `%b`, `%.3f`, `%p`, `%q`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:strings"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain the three zero/low-overhead ways to format strings in Odin without leaking memory: `fmt.bprintf` into a stack `[N]u8` array, `fmt.tprintf` into `temp_allocator`, and `fmt.sbprintf` into a reusable `strings.Builder` (reset with `strings.builder_reset(&b)` across iterations).
  2. **Drill**: Declare `stack_buf: [64]u8`, format a message into it with `res := fmt.bprintf(stack_buf[:], "Player %d: HP=%04d (0x%02x)", 1, 75, 75)`, and print `res`.
  3. **Drill**: Create `b := strings.builder_make()` with `defer strings.builder_destroy(&b)`, append 3 lines with `fmt.sbprintf(&b, ...)`, print `strings.to_string(b)`, and reuse the builder across iterations via `strings.builder_reset(&b)`.

### `510_strings_and_strconv.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:strings"`, `import "core:strconv"`, `strings.trim_space`, `strings.has_prefix`, `strings.has_suffix`, `strings.contains`, `strings.index`, `strings.split_iterator(&rem, sep)` (zero-allocation tokenizing loop!), `strings.split_lines_iterator(&rem)`, `strings.split` (`defer delete(parts)`), `strconv.parse_int(s)`, `strconv.parse_u64(s, 16)`, `strconv.parse_f64(s)`, `strconv.parse_bool(s)`, `strconv.itoa(buf[:], n)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:strings"`, `import "core:strconv"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why `strings.split_iterator(&s, ",")` and `strings.split_lines_iterator(&s)` are preferred over `strings.split(s, ",")` in hot paths: iterators advance a slice view over `s` with **zero heap allocations**, whereas `split` allocates a `[]string` slice that you must `delete`!
  2. **Drill**: Given `csv_row := " 10, 25, -4, 100 "`, loop `for token in strings.split_iterator(&csv_row, ",")`, trim whitespace with `strings.trim_space(token)`, parse each integer with `val, ok := strconv.parse_int(trimmed)`, and iterate lines with `strings.split_lines_iterator`.
  3. **Drill**: Parse hex values with `strconv.parse_u64(s, 16)`, a float `"3.1415"` with `strconv.parse_f64`, a bool `"true"` with `strconv.parse_bool`, and convert an `int` back to a string in a stack `[32]u8` buffer with `strconv.itoa(buf[:], sum)`.

### `520_slice_and_sort_algorithms.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:slice"`, `slice.sort(s)`, `slice.reverse_sort(s)`, `slice.sort_by(s, less_proc)`, `slice.sort_by_key(s, key_proc)`, `slice.is_sorted(s)`, `slice.binary_search(s, target)`, `slice.unique(s)`, `slice.clone(s)`, `slice.fill(s, val)`, `slice.reverse(s)`, `slice.equal(a, b)`, `slice.reinterpret([]Dst, src_slice)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:slice"`, `Score_Entry :: struct { name: string, points: int }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `core:slice` utilities for sorting, searching, deduplicating, cloning, comparing, and reinterpreting slice memory.
  2. **Drill**: Sort an `[]int` slice ascending with `slice.sort(nums[:])`, deduplicate with `slice.unique`, clone with `slice.clone` (`defer delete`), and search for `42` with `idx, found := slice.binary_search(nums[:], 42)`.
  3. **Drill**: Sort a slice of `Score_Entry` descending by `.points` using `slice.sort_by(...)` and by key using `slice.sort_by_key(...)`.
  4. **Drill**: Use `slice.reinterpret([]u8, u32_slice[:])` to view a slice of `u32` values as raw bytes (`len` automatically scales by `4`).

### `530_containers_queue_and_pq.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:container/queue"`, `import pq "core:container/priority_queue"`, `queue.Queue(T)`, `queue.init(&q)`, `defer queue.destroy(&q)`, `queue.push_back(&q, v)`, `queue.push_front(&q, v)`, `queue.pop_front(&q)`, `queue.pop_front_safe(&q)`, `queue.len(q)`, `pq.Priority_Queue(T)`, `pq.init(&p, less_proc, pq.default_swap_proc(T))`, `defer pq.destroy(&p)`, `pq.push(&p, v)`, `pq.pop(&p)`, `pq.remove(&p, idx)`, `pq.fix(&p, idx)`, `pq.len(p)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:container/queue"`, `import pq "core:container/priority_queue"`, `Task :: struct { priority: int, name: string }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `core:container/queue` (a double-ended ring buffer O(1) push/pop at both ends) and `core:container/priority_queue` (a binary heap ordered by a custom `less` procedure).
  2. **Drill**: Initialize `q: queue.Queue(string)` with `queue.init(&q)` and `defer queue.destroy(&q)`, push 3 strings to back/front, drain with `for val, ok := queue.pop_front_safe(&q); ok; val, ok = queue.pop_front_safe(&q)`, and run a small BFS worklist loop.
  3. **Drill**: Initialize `task_heap: pq.Priority_Queue(Task)` with a `less` proc ordering smaller `.priority` numbers first, push 3 tasks out of order, test `pq.fix` / `pq.remove` on an updated task, and pop them in priority order.

### `540_os_files_and_directories.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:os"`, `import "core:path/filepath"`, `os.write_entire_file(path, data)`, `os.read_entire_file(path)` (`defer delete(data)`), `os.open`, `os.read`, `os.close`, `os.read_dir`, `os.exists(path)`, `os.remove(path)`, `filepath.join`, `filepath.dir`, `filepath.base`, `filepath.ext`, `filepath.stem`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:os"`, `import "core:path/filepath"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain whole-file helpers (`os.read_entire_file` returns `(data: []byte, success: bool)` allocated on `context.allocator`, so always `defer delete(data)`!) vs. handle-based chunked I/O (`os.open` / `os.read` / `os.close`) and directory listings (`os.read_dir`).
  2. **Drill**: Build paths safely with `filepath.join`, write `"Hello from Odin file I/O!\n"` using `os.write_entire_file`, check `os.exists`, read it back with `os.read_entire_file` (`defer delete(data)`), and remove the temp file with `os.remove`.
  3. **Drill**: Open a file handle with `os.open` (`defer os.close`), read fixed `[64]u8` chunks in a loop with `os.read`, and list directory entries via `os.read_dir` (cleaning up `os.file_info_slice_delete`).
  4. **Drill**: Inspect `"odin_how_to/540_os_files_and_directories.odin"` with `filepath.dir`, `filepath.base`, `filepath.stem`, and `filepath.ext`.

### `550_io_streams_and_bufio.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:io"`, `import "core:bufio"`, `import "core:bytes"`, `import "core:strings"`, `strings.Reader`, `strings.to_reader(&r, src_str)`, `bufio.Scanner`, `bufio.scanner_init(&scanner, reader)`, `defer bufio.scanner_destroy(&scanner)`, `bufio.scanner_scan(&scanner)`, `bufio.scanner_text(&scanner)`, `bufio.Writer`, `bufio.writer_init(&w, stream)`, `defer bufio.writer_destroy(&w)`, `bufio.writer_write_string(&w, s)`, `bufio.writer_flush(&w)`, `bytes.Buffer`, `bytes.buffer_init(&buf, nil)`, `bytes.buffer_to_stream(&buf)`, `io.write_string(stream, s)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:io"`, `import "core:bufio"`, `import "core:bytes"`, `import "core:strings"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `core:io` defines a unified `io.Stream` vtable interface used across files, sockets, strings, and byte buffers, and how `bufio.Scanner` and `bufio.Writer` buffer line-by-line reads and batched writes.
  2. **Drill**: Create a `strings.Reader` over a multi-line string, initialize a `bufio.Scanner` with `bufio.scanner_init(&sc, strings.to_reader(&r, multi_line))`, and loop `for bufio.scanner_scan(&sc)` printing each line with `bufio.scanner_text(&sc)`.
  3. **Drill**: Create a `bytes.Buffer`, wrap its `io.Stream` (`bytes.buffer_to_stream(&buf)`) in a `bufio.Writer` (`bufio.writer_init` + `defer bufio.writer_destroy`), write multiple chunks with `bufio.writer_write_string`, observe buffered vs flushed output via `bufio.writer_flush`, and print `bytes.buffer_to_string(&buf)`.

### `560_cli_args_and_core_flags.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:os"`, `import "core:flags"`, `os.args` (`[]string`, where `os.args[0]` is executable path), struct tags `` `args:"name=...,pos=...,required" usage:"..."` ``, `flags.parse(&opts, args_slice, .Odin)` vs `flags.Parsing_Style.Unix`, enum flags.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:os"`, `import "core:flags"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `os.args` provides raw command-line arguments and how `core:flags` uses runtime reflection (`core:reflect`) to parse Odin-style (`-opt:val`) or UNIX-style (`--opt=val`) CLI flags directly into a typed struct!
  2. **Drill**: Define `Log_Mode :: enum { Quiet, Normal, Debug }` and `Cli_Options :: struct { input: string `args:"pos=0" usage:"Input filename"`, threads: int `usage:"Worker thread count"`, mode: Log_Mode `usage:"Output mode"`, verbose: bool `usage:"Enable verbose output"` }`.
  3. **Drill**: Parse simulated argument slices using both `.Odin` (`-threads:8`) and `.Unix` (`--threads=8`) styles (or `os.args[1:]` if non-empty) and print the populated `opts` struct.

### `570_logging_with_core_log.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:log"`, `context.logger`, `log.create_console_logger(lowest = .Debug)`, `defer log.destroy_console_logger(logger)`, `log.create_multi_logger`, `log.Level` (`.Debug`, `.Info`, `.Warning`, `.Error`, `.Fatal`), `log.debug`, `log.debugf`, `log.info`, `log.infof`, `log.warnf`, `log.errorf`, `log.Options`.
- **Scaffold**: `package main`, `import "core:log"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why `context.logger` is built into `context`: any library or deeply nested procedure can call `log.infof(...)` or `log.errorf(...)` without global singletons, and callers control where logs go (console, file, `log.create_multi_logger`, or nil logger in tests) by setting `context.logger`!
  2. **Drill**: Create `logger := log.create_console_logger(lowest = .Debug)` with `defer log.destroy_console_logger(logger)`, assign `context.logger = logger`, and emit `.Debug`, `.Info`, `.Warning`, and `.Error` messages from both `main` and a helper procedure, plus combine loggers with `log.create_multi_logger`.

### `580_json_and_binary_serialization.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:encoding/json"`, `import "core:encoding/endian"`, struct tag `` `json:"key_name,omitempty"` ``, `json.marshal(val, opt)` (`defer delete(json_bytes)`), `json.unmarshal(json_bytes, &target_struct)`, nested JSON structs, `endian.put_u32(buf[:], .Little, val)`, `endian.get_u32(buf[:], .Little)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:encoding/json"`, `import "core:encoding/endian"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain automatic struct-to-JSON marshaling/unmarshaling via `core:encoding/json` and deterministic binary wire encoding via `core:encoding/endian`.
  2. **Drill**: Define nested structs (`Inventory_Item`, `Save_Game :: struct { player_name: string `json:"player"`, level: int `json:"level"`, coins: [3]int `json:"coins"`, items: []Inventory_Item `json:"items"` }`), marshal to JSON bytes (`json.marshal`), print `string(data)`, and unmarshal into a fresh `loaded: Save_Game` variable (freeing allocated slices/strings!).
  3. **Drill**: Encode a multi-field binary wire packet (`magic`, `version`, `payload_len`) in both `.Little` and `.Big` endian using `endian.put_u32` / `put_u16` and decode back with `endian.get_u32` / `get_u16`.

### `590_time_and_random.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:time"`, `import "core:math/rand"`, `time.Tick`, `time.tick_now()`, `time.tick_since(start)`, `time.duration_milliseconds(d)`, `time.duration_microseconds(d)`, `time.Stopwatch`, `time.stopwatch_start(&sw)`, `time.stopwatch_stop(&sw)`, `time.stopwatch_duration(sw)`, `rand.Default_Random_State`, `rand.create(seed_u64)`, `context.random_generator = rand.default_random_generator(&rng)`, `rand.int_max(n)`, `rand.float32_range(lo, hi)`, `rand.shuffle(slice)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:time"`, `import "core:math/rand"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain high-resolution monotonic timing with `time.tick_now()` / `time.Stopwatch` and deterministic seeding of `context.random_generator` via `core:math/rand`.
  2. **Drill**: Start a `time.Stopwatch` (and `start := time.tick_now()`), run a loop computing 100,000 integer operations, stop the timer, and print elapsed microseconds.
  3. **Drill**: Create an explicit `state: rand.Default_Random_State = rand.create(1337)`, set `context.random_generator = rand.default_random_generator(&state)`, generate 3 random ints with `rand.int_max(100)`, and shuffle an `[5]int{1, 2, 3, 4, 5}` slice with `rand.shuffle(deck[:])`.

### `595_profiling_with_spall.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:prof/spall"`, `spall.Context`, `spall.Buffer`, `spall.context_create("trace.spall")`, `defer spall.context_destroy(&spall_ctx)`, `spall.buffer_create(backing_slice, thread_id)`, `defer spall.buffer_destroy(&spall_ctx, &spall_buf)`, nested `spall.SCOPED_EVENT(&spall_ctx, &spall_buf, #procedure)`, Hotspot-First Optimization Rule (never optimize without a profiler trace from Spall or **Tracy** — see `../tracy_how_to/`).
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:os"`, `import "core:prof/spall"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `core:prof/spall` and the **Hotspot-First Rule**: Odin ships with first-party support for producing Spall profiler traces with sub-10-nanosecond overhead using `spall.SCOPED_EVENT` (which uses `@(deferred_in_out)` under the hood to record start/end timestamps!).
  2. **Drill**: Create a `spall.Context` and a stack/heap-backed `spall.Buffer`, instrument outer and nested helper procedures (`outer_step`, `heavy_step`) with `spall.SCOPED_EVENT(ctx, buf, #procedure)`, flush/destroy the buffer and context, and clean up the temporary `.spall` file with `os.remove`.

### `596_profiling_with_tracy_zones_and_frames.odin` *(Primer — Slim Odin-Idiom Integration Hooks; see `tracy_how_to/` for Full Telemetry)*
- **Cross-Repo Boundary**: Keep `596` focused strictly on **Odin language integration hooks** (`#config(TRACY_ENABLE, false)` + `when TRACY_ENABLE` compile-time elimination, `@(deferred_out)` + `#caller_location` scoped zone guard, and `cstring` / `Srcloc` ergonomics). Do **not** duplicate `tracy_how_to/` Five-Multipliers lectures, `TracyPlot`/`TracyMessageC` flight recorders (`tracy_how_to/500`), or full timeline forensics (`tracy_how_to/000,100,200`).
- **Syntax / Keywords / Built-ins Checklist**: `TRACY_ENABLE :: #config(TRACY_ENABLE, false)` (`-define:TRACY_ENABLE=true`), `when TRACY_ENABLE`, `@(deferred_out = tracy_zone_end)`, `#caller_location`, lightweight `tracy_zone` / `tracy_frame_mark` Odin wrapper hooks.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "base:intrinsics"`, `import "base:runtime"`, `TRACY_ENABLE :: #config(TRACY_ENABLE, false)`, `Tracy_Zone_Ctx :: struct { name: string, start_cycle: u64 }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how Odin combines `#config(TRACY_ENABLE, false)` + `when TRACY_ENABLE` + `@(deferred_out)` + `#caller_location` so Tracy instrumentation compiles to zero instructions when disabled and closes zones automatically on any `return` or block exit (linking to `tracy_how_to/100` & `tracy_how_to/200` for C ABI pinning and nested Self-Time analysis).
  2. **Drill**: Implement Odin-idiom `tracy_zone(name: string, loc := #caller_location) -> Tracy_Zone_Ctx` + `@(deferred_out = tracy_zone_end)` and `tracy_frame_mark()` gated by `when TRACY_ENABLE` (with a tiny standalone cycle summary when disabled).
  3. **Drill**: Instrument 2–3 small Odin procedures across a few frames, confirming `when TRACY_ENABLE == false` compiles cleanly with zero runtime dependency on `TracyClient.dll`.

### `597_repetition_testing_and_rdtsc.odin` *(Primer — Inspired by Computer, Enhance! Part 2 & Part 3)*
- **Syntax / Keywords / Built-ins Checklist**: `import "base:intrinsics"`, `import "core:time"`, `intrinsics.read_cycle_counter()` (`RDTSC` on x86_64 / `CNTVCT_EL0` on ARM64), `time.tick_now()`, `time.tick_since`, `time.duration_nanoseconds`, `Repetition_Stats :: struct { min_cycles, max_cycles, total_cycles: u64, runs: u64, bytes_per_run: u64 }`, throughput calculation (`gigabytes_per_sec = f64(bytes) / f64(nanoseconds)`), L1 vs. L3 working-set sweep, preventing dead-code elimination (checksum sink).
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:time"`, `import "base:intrinsics"`, `Repetition_Stats :: struct { min_cycles: u64, max_cycles: u64, total_cycles: u64, runs: u64 }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain Casey Muratori's **Repetition Testing** methodology from *Computer, Enhance!*:
     - Once a profiler (**Tracy** or **Spall**) identifies a hotspot procedure, how do you know if your change actually made it faster or how close it is to the hardware speed limit?
     - Why `intrinsics.read_cycle_counter()` (`RDTSC`) measures elapsed CPU reference cycles with ~10–20 cycle overhead vs. OS wall-clock calls, and why **`min_cycles`** across N repetitions is the true hardware execution cost (because OS interrupts, context switches, and frequency transitions only ever *add* positive delay to a deterministic CPU loop!).
     - Why compiler dead-code elimination (`-o:speed`) will silently delete a benchmarked loop if you don't consume its output in a checksum sink.
  2. **Drill**: Write `record_sample :: proc(stats: ^Repetition_Stats, cycles: u64)` that updates `min_cycles`, `max_cycles`, `total_cycles`, and `runs`.
  3. **Drill**: Benchmark reading/summing across an L1-resident buffer (`16 KB`) vs. an L3/RAM-resident buffer (`8 MB`) over 32 repetitions using `intrinsics.read_cycle_counter()` and `time.tick_now()`, compute `GB/s` and `cycles_per_element`, and print the checksum sink.

### `598_tracy_memory_and_lock_profiling.odin` *(Primer — Slim Odin-Idiom Integration Hooks; see `tracy_how_to/` for Full Telemetry)*
- **Cross-Repo Boundary**: Keep `598` focused strictly on **Odin language integration hooks** (`context.allocator` wrapping via `runtime.Allocator_Proc` and `@(deferred_in)`/`sync.Mutex` guard hooks gated by `when TRACY_ENABLE`). Do **not** duplicate `tracy_how_to/300` named memory-pool leak hunts or `tracy_how_to/400` multi-thread false-sharing/lock-contention timeline benchmarks.
- **Syntax / Keywords / Built-ins Checklist**: `runtime.Allocator`, `runtime.Allocator_Mode`, `when TRACY_ENABLE`, `sync.Mutex`, scoped `tracy_lock_guard` wrapper pattern.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:sync"`, `import "base:runtime"`, `TRACY_ENABLE :: #config(TRACY_ENABLE, false)`, `Tracy_Memory_Tracker :: struct`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how Odin's implicit `context.allocator` and `sync.Mutex` (`@(deferred_in)`) let you attach allocation and lock hooks globally without touching call sites (linking to `tracy_how_to/300` and `tracy_how_to/400` for named pool tracking, allocator recursion traps, and multi-thread lock contention timelines).
  2. **Drill**: Implement a minimal `tracy_tracking_allocator_proc` wrapping `backing: runtime.Allocator` that tracks active/peak bytes and dispatches Tracy memory hooks inside `when TRACY_ENABLE`.
  3. **Drill**: Implement a lightweight `tracy_lock_guard(&mu, name)` wrapper and verify both hooks in a small single-scope check in `main` (zero `_ =` silencers).

### `599_tracy_hotspot_profiler_lab/` *(Multi-File Lab — Slim Odin-Idiom Profiling Lab; see `tracy_how_to/900` for Five-Multipliers Capstone)*
- **Cross-Repo Boundary**: Keep `599` as a concise Odin-idiom `@(deferred_out)` + `context.allocator` zone/allocation hotspot exercise (`main.odin`, `tracy_prof.odin`, `workload.odin`) demonstrating how Odin's `context` and `defer` isolate a single allocating hotspot. For the full 5-system cold-herring Five-Multipliers Hotspot Hunt capstone, see [`tracy_how_to/900_hotspot_hunt_five_multipliers_lab/`](../tracy_how_to/900_hotspot_hunt_five_multipliers_lab/).
- **Files**:
  - `599_tracy_hotspot_profiler_lab/main.odin` (`package main`)
  - `599_tracy_hotspot_profiler_lab/tracy_prof.odin` (`package main`)
  - `599_tracy_hotspot_profiler_lab/workload.odin` (`package main`)
- **Syntax / Keywords / Built-ins Checklist**: `@(deferred_out)` scoped zone stack (Self Cycles = `total_cycles - child_cycles`), `context.allocator` per-zone allocation tracking, isolating and fixing the single allocating hotspot while leaving cold procedures untouched.
- **Scaffold**: `Profiler_State`, `Zone_Scope`, and `Zone_Entry` contracts in `tracy_prof.odin`; baseline `workload.odin` stage contracts; before/after entry in `main.odin` (zero `_ =` silencers and zero dummy returns).
- **Ordered Outline**:
  1. In `tracy_prof.odin`: **Drill** to implement `prof_zone_begin(name: string, loc := #caller_location) -> Zone_Scope` and `prof_zone_end(scope: Zone_Scope)` tracking nested self cycles and `context.allocator` bytes, plus `prof_print_table()`.
  2. In `workload.odin`: **Drill** to instrument the pipeline with `prof_zone(...)`, spot the allocating hotspot stage, and write an allocation-free replacement keeping cold procedures intact.
  3. In `main.odin`: **Drill** to run baseline vs. fixed passes, verify identical checksums and 0 heap leaks, and link to `tracy_how_to/900` for the full Five-Multipliers Hotspot Hunt.

---

## `600`–`699`: Parametric Polymorphism (Generics), Intrinsics & Reflection (RTTI)

### `600_explicit_parametric_polymorphism.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `$T: typeid` (explicit compile-time type parameter), `$N: int` (explicit compile-time constant value parameter), calling `my_proc(int, 4, ...)`, generic `alloc_slice`, overload group over generic specializations.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain Odin's `$` prefix for compile-time parameters: `$T: typeid` means the caller passes a **type** (like `int` or `f32`) as an argument, and the compiler generates a specialized version of the procedure for that type!
  2. **Drill**: Write `make_filled_array :: proc($N: int, $T: typeid, value: T) -> [N]T` that fills and returns an `[N]T` array, plus a generic `alloc_slice :: proc($T: typeid, count: int) -> []T` (`defer delete`).
  3. **Drill**: Call `make_filled_array(4, f32, 1.5)` and `make_filled_array(3, string, "hi")`, and group specialized helpers in an explicit `proc{...}` overload group in `main`.

### `610_implicit_polymorphism_parapoly.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `a: $T` (implicitly deduced type), `s: []$T` (slice of deduced element type `T`), `arr: [$N]$T` (fixed array of deduced length `N` and element type `T`), `ptr: ^$T`, `m: map[$K]$V`, `$T/[]$E` (constrained specialization: `T` is any slice type whose element is `E`), allocator-aware `filter_slice`, return-only `$T` limit.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how placing `$` inside a parameter's type annotation (`items: []$T`) lets Odin deduce `T` automatically from the argument without the caller typing the type name (and why a return-only `$T` cannot be deduced without a parameter!).
  2. **Drill**: Write `swap_values :: proc(a, b: ^$T)` and test it on two `int`s and two `string`s.
  3. **Drill**: Write `reverse_in_place :: proc(items: []$T)`, `fixed_array_len :: proc(arr: [$N]$T) -> int { return N }`, and an allocator-aware `filter_slice :: proc(items: []$T, pred: proc(T) -> bool, allocator := context.allocator) -> []T`, calling them in `main`.

### `620_polymorphic_structs_and_unions.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `Box($T: typeid) :: struct { value: T }`, `Ring_Buffer($N: int, $T: typeid) :: struct { data: [N]T, head, tail, count: int }`, `Stack($T: typeid) :: struct`, `Result($T, $E: typeid) :: union { T, E }`, procedures taking `rb: ^Ring_Buffer($N, $T)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how structs and unions take compile-time `$T: typeid` and `$N: int` parameters to create zero-overhead generic containers and error unions.
  2. **Drill**: Define `Ring_Buffer($N: int, $T: typeid) :: struct { data: [N]T, read_idx, write_idx, count: int }`, `Stack($T: typeid) :: struct`, and `Result($T, $E: typeid) :: union { T, E }`.
  3. **Drill**: Write `ring_push :: proc(rb: ^Ring_Buffer($N, $T), item: T) -> bool` and `ring_pop :: proc(rb: ^Ring_Buffer($N, $T)) -> (item: T, ok: bool)`, plus stack/result helpers, and test `Ring_Buffer(4, int)` and `Result(int, string)` in `main`.

### `630_where_clauses_and_intrinsics.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "base:intrinsics"`, `proc(...) -> ... where cond1, cond2`, `where` clauses on polymorphic structs, `intrinsics.type_is_numeric(T)`, `intrinsics.type_is_integer(T)`, `intrinsics.type_is_float(T)`, `intrinsics.type_is_enum(T)`, `intrinsics.type_is_struct(T)`, `intrinsics.type_has_field(T, "field_name")`, `intrinsics.type_field_type(T, "field_name")`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "base:intrinsics"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `where` clauses + `base:intrinsics` give Odin compile-time type constraints on both procedures and polymorphic structs with crystal-clear error messages when a caller passes an unsupported type.
  2. **Drill**: Write `dot_product :: proc(a, b: [$N]$T) -> T where N > 0, intrinsics.type_is_numeric(T)` and call it on `[3]f32` and `[4]int` (`// Try calling dot_product on [2]string to see the where-clause error`).
  3. **Drill**: Write `extract_id :: proc(record: $T) -> u64 where intrinsics.type_is_struct(T), intrinsics.type_has_field(T, "id")` and a `where`-constrained polymorphic struct `Numeric_Range($T: typeid) where intrinsics.type_is_numeric(T)`, testing both in `main`.

### `640_constant_baked_parameters.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: Value parameter `$flag: bool`, `$Mode: Enum`, or `$factor: int` mixed with runtime parameters (`filter :: proc(data: []f32, $clamp_negatives: bool)`), compile-time `when flag` / `when Mode` inside generic procedure body.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain **constant value baking**: marking a parameter with `$` (`$debug_trace: bool`, `$Mode: Filter_Mode`) specializes the procedure at compile time so `when` completely eliminates branches inside tight loops!
  2. **Drill**: Write `transform_samples :: proc(samples: []f32, gain: f32, $clamp_unit: bool)` where `when clamp_unit` clamps each output to `-1.0..=1.0`, plus a `$Mode: Enum` loop specialization procedure, and call both from `main`.

### `650_selector_call_expressions_vtables.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: Selector call expression `x->proc_field(args)` (rewritten by the compiler to `x.proc_field(x, args)` or `(&x)->proc_field(args)`), heterogeneous `[]^Plugin` vtable slice pattern.
- **Scaffold**: `package main`, `import "core:fmt"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why Odin does not have methods on structs, and why it provides the `->` selector call operator specifically for **procedure pointers stored as struct fields** (like COM/C vtables or plugin interfaces: `widget->draw(dt)` passes `widget` or `&widget` as the first argument to `widget.draw`!).
  2. **Drill**: Define `Counter_Plugin :: struct { count: int, step: int, add: proc(self: ^Counter_Plugin, n: int), reset: proc(self: ^Counter_Plugin) }`.
  3. **Drill**: Instantiate multiple plugin instances into a heterogeneous `[]^Counter_Plugin` vtable slice and invoke `p->add(5)` and `p->reset()` using `->`.

### `660_runtime_type_information.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "base:runtime"`, `type_info_of(T_or_typeid)` (`^runtime.Type_Info`), `runtime.type_info_base(ti)` (strips `distinct` / alias wrappers to reach the underlying type), `ti.size`, `ti.align`, `ti.id`, `#partial switch v in ti.variant` (`runtime.Type_Info_Integer`, `runtime.Type_Info_Float`, `runtime.Type_Info_Struct`, `runtime.Type_Info_Enum`, `runtime.Type_Info_Slice`), RTTI pretty-printer.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "base:runtime"`, `Custom_Int :: distinct i32`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how Odin's built-in RTTI table stores a `runtime.Type_Info` record for every type used in the program (which is how `fmt.println`, `json.marshal`, and `flags.parse` work without code generation!).
  2. **Drill**: Write `print_type_details :: proc(id: typeid)` and a small RTTI pretty-printer that fetches `ti := type_info_of(id)` and `base_ti := runtime.type_info_base(ti)`, prints `.size` and `.align`, and uses `#partial switch info in base_ti.variant` to inspect enum, integer, slice, and struct variants.
  3. **Drill**: Call `print_type_details` and your RTTI pretty-printer on `Custom_Int`, an enum type, a slice, and a struct type.

### `670_reflect_struct_fields_and_tags.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:reflect"`, `reflect.struct_fields_zipped(T)`, `field.name`, `field.type`, `field.offset`, `field.tag` (`reflect.Struct_Tag`), `reflect.struct_tag_lookup(field.tag, "key")`, `reflect.struct_field_value(struct_any, field)`, dynamic `field.offset` tag validator.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:reflect"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `core:reflect` builds on `Type_Info` to let you iterate struct fields, read struct field values dynamically via `field.offset`, and parse custom metadata tags (like `` `db:"user_id" validate:"nonzero"` ``) at runtime!
  2. **Drill**: Define `User_Record :: struct { id: u64 `db:"user_id" required:"true"`, username: string `db:"username" required:"true"`, bio: string `db:"bio"` }`.
  3. **Drill**: Write `inspect_struct_tags :: proc(val: any)` and a `validate_required_fields :: proc(val: any) -> bool` validator using `reflect.struct_fields_zipped`, `reflect.struct_tag_lookup`, `field.offset`, and `reflect.struct_field_value`.

---

## `700`–`799`: Concurrency, Synchronization, Channels, SIMD, SOA & Performance Multipliers

### `700_soa_data_layout.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `#soa[N]Struct`, `#soa[]Struct`, `#soa[dynamic]Struct`, `make(#soa[]Struct, n)`, `make(#soa[dynamic]Struct, 0, cap)`, `delete_soa(s)`, `append_soa(&s, item)`, `s.field_name[i]` (contiguous field array access!) vs `s[i].field_name` (virtual AoS element access), `soa_zip(a = slice_a, b = slice_b)`, `soa_unzip(soa_slice)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `Particle :: struct { x, y, vx, vy, life: f32 }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain **Array of Structures (AoS)** vs **Structure of Arrays (SoA)**: why updating `x += vx` across 10,000 entities wastes CPU cache lines if unused fields sit interleaved, and how Odin's `#soa` keyword automatically transforms a single `struct` into separate parallel arrays (`particles.x[i]`, `particles.vx[i]`) without manual boilerplate!
  2. **Drill**: Declare `fixed_soa: #soa[4]Particle`, populate elements via `fixed_soa[i] = ...`, and access the contiguous float array `fixed_soa.x` directly as a `[4]f32`!
  3. **Drill**: Create `dyn_soa := make(#soa[dynamic]Particle, 0, 8)` with `defer delete_soa(dyn_soa)`, `append_soa` 3 particles, allocate `make(#soa[]Particle, n)` (`defer delete_soa`), update `dyn_soa.x[i] += dyn_soa.vx[i]`, and demonstrate both `soa_zip` and `soa_unzip`.

### `705_cache_lines_bandwidth_and_false_sharing.odin` *(Primer — Inspired by Computer, Enhance! "Caching", "Part 3: Moving Data" & "Multithreading")*
- **Syntax / Keywords / Built-ins Checklist**: `import "base:intrinsics"`, `import "core:thread"`, `import "core:time"`, `size_of(T)`, `align_of(T)`, `offset_of(T, field)`, `struct #align(64) { ... }` (64-byte cache-line alignment), `intrinsics.prefetch_read_data(address, locality)`, L1/L2/L3 cache hierarchy working-set sizes (~32 KB L1d, ~512 KB–1 MB L2, ~16–64 MB L3), 64-byte cache lines (`16 x f32` or `8 x i64` per line), stride-1 sequential access vs. strided/pointer-chasing cache misses, live multi-thread **False Sharing** timing.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:thread"`, `import "core:time"`, `import "base:intrinsics"`, `CACHE_LINE_SIZE :: 64`, `Padded_Counter :: struct #align(64) { value: i64 }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain **Multiplier #4 (Caching & Data Movement)** from *Computer, Enhance!*:
     - Modern CPUs do not read single bytes or single `f32`s from RAM; memory moves in **64-byte cache lines**.
     - If a hot loop touches 4 bytes inside a 64-byte struct and skips the remaining 60 bytes (or chases heap pointers to random cache lines), **93.75% of memory bandwidth and L1 cache capacity is wasted**!
     - Why **Working-Set Size** determines your speed ceiling: a loop that fits inside L1 (~32 KB) streams at high bandwidth (~4 cycle latency), whereas blowing past L3 into Main RAM drops bandwidth drastically (~200+ cycle latency).
     - Explain **False Sharing** via MESI cache-coherency invalidations: if Thread 0 writes `counters[0]` and Thread 1 writes `counters[1]` inside a plain `[4]i64` array, both counters sit on the **exact same 64-byte cache line**, forcing core 0 and core 1 to bounce exclusive ownership back and forth! Padding each slot with `struct #align(64)` puts each thread on its own cache line.
  2. **Drill**: Compare `size_of([4]i64)` (32 bytes) vs. `size_of([4]Padded_Counter)` (256 bytes) and verify `align_of(Padded_Counter) == 64`.
  3. **Drill**: Spawn 2–4 worker threads (`core:thread`) hammering `[4]i64` vs. `[4]Padded_Counter` and time both runs (`time.tick_now()` / `intrinsics.read_cycle_counter()`) to measure real false-sharing contention vs. cache-line-isolated speedup!
  4. **Drill**: Demonstrate stride-1 contiguous traversal vs. strided traversal across L1 vs. L3 working-set sizes, plus `intrinsics.prefetch_read_data(&data[i + 16], 3)`.

### `710_simd_vectors.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `#simd[N]T` (`N` power of 2: `4`, `8`, `16`), `import "core:simd"`, lane-wise `+`, `-`, `*`, `/`, `simd.from_array(arr)`, `simd.to_array(vec)`, `simd.from_slice(Vec_Type, slice)`, `simd.extract(vec, idx)`, `simd.replace(vec, idx, val)`, `simd.reduce_add_ordered(vec)`, `simd.reduce_max(vec)`, `simd.lanes_lt(a, b)`, `simd.lanes_eq(a, b)`, `simd.select(mask, true_vec, false_vec)`, `simd.fma(a, b, c)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:simd"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `#simd[N]T` hardware SIMD registers (SSE/AVX on x86_64, NEON on ARM64) and `core:simd` intrinsics for data-parallel math and branchless masking.
  2. **Drill**: Declare `a := #simd[4]f32{1, 2, 3, 4}`, `b := #simd[4]f32{10, 20, 30, 40}`, and `c := #simd[4]f32{0.5, 0.5, 0.5, 0.5}`, compute `res := simd.fma(a, b, c)` (`a * b + c`), and sum all 4 lanes with `simd.reduce_add_ordered(res)`.
  3. **Drill**: Compute a lane-wise comparison mask `mask := simd.lanes_gt(res, #simd[4]f32{50, 50, 50, 50})` and blend branchlessly with `clamped := simd.select(mask, #simd[4]f32{50, 50, 50, 50}, res)`, then slice-loop over a byte buffer with `#simd[16]u8` to scan/count matching bytes!

### `715_ipc_dependency_chains_and_unrolling.odin` *(Primer — Inspired by Computer, Enhance! "Instructions Per Clock", "Analyzing Dependency Chains" & "Part 5: Computation")*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:simd"`, `import "base:intrinsics"`, `#no_bounds_check`, superscalar execution ports, instruction **Latency** vs. **Throughput**, loop-carried **Dependency Chains** (`sum += data[i]`), 4-way scalar accumulator interleaving (`sum0, sum1, sum2, sum3`), 4-way SIMD vector accumulator interleaving (`vec0, vec1: #simd[4]f32`), Horner's Rule & `simd.fma` for polynomial evaluation.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:simd"`, `import "base:intrinsics"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain **Multiplier #2 (Instructions Per Clock / IPC)** and **Dependency Chains** from *Computer, Enhance!*:
     - Modern x86_64 and ARM64 cores are superscalar out-of-order machines capable of executing **4 to 6+ instructions per clock cycle** on a *single thread*—but **only** if those instructions do not wait on each other!
     - Why a naive `for x in data { total += x }` loop stalls waiting on a 3–4 cycle floating-point addition latency dependency chain, and how 4-way scalar interleaving + `#simd[4]f32` multi-accumulators saturate execution ports.
  2. **Drill**: Write `sum_serial :: proc(data: []f32) -> f32` (1 accumulator `total`) and `sum_interleaved_4x :: proc(data: []f32) -> f32` (4 independent accumulators `s0, s1, s2, s3` stepping by `i += 4` with `#no_bounds_check`, plus cleanup loop for `len(data) % 4`, returning `(s0 + s1) + (s2 + s3)`).
  3. **Drill**: Write `sum_simd_interleaved :: proc(data: []f32) -> f32` using two `#simd[4]f32` accumulators (`v0`, `v1`) processing 8 `f32`s per loop iteration, verify identical sums, and compare cycle counts with `intrinsics.read_cycle_counter()`.

### `720_threads_basics.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:thread"`, `thread.Thread`, `thread.create_and_start_with_poly_data(arg, worker_proc)`, `thread.create_and_start_with_poly_data2(arg1, arg2, worker_proc)`, `thread.join(t)`, `thread.join_multiple(..threads)`, `thread.destroy(t)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:thread"`, `Worker_Range :: struct { data: []int, partial_sum: int }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how `thread.create_and_start_with_poly_data` spawns an OS thread passing a typed pointer (`^Worker_Range`) directly to your worker procedure without unsafe `rawptr` casts, and how each thread automatically initializes and cleans up its own thread-local `context.temp_allocator`.
  2. **Drill**: Write `sum_worker :: proc(r: ^Worker_Range)` and a 2-argument worker for `thread.create_and_start_with_poly_data2`.
  3. **Drill**: Split an `[8]int` array across worker structs in `main`, spawn threads with `create_and_start_with_poly_data` / `poly_data2`, wait with `thread.join_multiple(..threads[:])`, `thread.destroy` them, and print the combined sum.

### `730_mutex_and_wait_group.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:sync"`, `import "core:thread"`, `sync.Mutex`, `sync.lock(&m)`, `sync.unlock(&m)`, `sync.guard(&m)` (scoped lock using `@(deferred_in=unlock)`!), `sync.RW_Mutex`, `sync.shared_guard(&rw)`, `sync.Wait_Group`, `sync.wait_group_add(&wg, n)`, `sync.wait_group_done(&wg)`, `sync.wait_group_wait(&wg)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:sync"`, `import "core:thread"`, `Shared_State :: struct { mu: sync.Mutex, wg: sync.Wait_Group, total: int }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why `sync.Mutex`, `sync.RW_Mutex`, and `sync.Wait_Group` in Odin are **zero-initialized structs** (no `init` or `destroy` call needed!) and how `sync.guard(&state.mu)` / `sync.shared_guard(&rw)` unlock automatically at scope exit!
  2. **Drill**: Write a worker procedure that calls `defer sync.wait_group_done(&state.wg)`, acquires `sync.guard(&state.mu)`, and updates `state.total`; spawn 4 threads with `sync.wait_group_add(&state.wg, 4)` and `sync.wait_group_wait(&state.wg)`.
  3. **Drill**: Add a multi-thread `sync.RW_Mutex` Drill with concurrent reader threads calling `sync.shared_guard(&rw)` and a writer thread calling `sync.guard(&rw)`.

### `740_atomics_and_lock_free.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:sync"`, `import "core:thread"`, `sync.atomic_load(&x)`, `sync.atomic_store(&x, v)`, `sync.atomic_load_explicit(&x, .Acquire)`, `sync.atomic_store_explicit(&x, v, .Release)`, `sync.atomic_add(&x, delta)` (returns **old** value before addition!), `sync.atomic_sub(&x, delta)`, `sync.atomic_exchange(&x, new_v)`, `sync.atomic_compare_exchange_strong(&x, expected, desired)` -> `(old_val, ok)`, `sync.Atomic_Memory_Order` (`.Relaxed`, `.Acquire`, `.Release`, `.Acq_Rel`, `.Seq_Cst`), CLI `-vet-atomic-access`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:sync"`, `import "core:thread"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain atomic operations in `core:sync`, noting: (a) `sync.atomic_add(&counter, 1)` returns the **previous** value (so thread 1 gets `0`, thread 2 gets `1`), (b) `.Release`/`.Acquire` pairs publish non-atomic writes safely across threads without a mutex, and (c) `-vet-atomic-access` warns if you read an atomic variable with a plain non-atomic access!
  2. **Drill**: Declare `next_slot: int = 0`, claim 3 slot indices with `slot := sync.atomic_add(&next_slot, 1)`, read with `sync.atomic_load(&next_slot)`, and write `atomic_update_max :: proc(max_val: ^int, candidate: int)` using a `sync.atomic_compare_exchange_strong` CAS loop.
  3. **Drill**: Spawn a 2-thread producer/consumer handshake using `sync.atomic_store_explicit(&ready, true, .Release)` and `for !sync.atomic_load_explicit(&ready, .Acquire) {}` to safely publish payload data across threads.

### `750_typed_channels.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:sync/chan"`, `import "core:thread"`, `chan.Chan(T)`, `chan.create(chan.Chan(T), cap, context.allocator)`, `defer chan.destroy(c)`, `chan.as_send(c)` (`chan.Chan(T, .Send)`), `chan.as_recv(c)` (`chan.Chan(T, .Recv)`), `chan.send(c, val)`, `val, ok := chan.recv(c)`, `chan.close(c)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:sync/chan"`, `import "core:thread"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain typed channels in `core:sync/chan`: how `chan.create` allocates a thread-safe buffered or unbuffered (rendezvous) queue, how direction-restricted handles (`chan.Chan(T, .Send)` vs `chan.Chan(T, .Recv)`) enforce producer/consumer roles at compile time, and how `chan.close(c)` signals `ok == false` to receivers once drained.
  2. **Drill**: Create a buffered channel `jobs, err := chan.create(chan.Chan(int), 4, context.allocator)` with `defer chan.destroy(jobs)`, spawn a producer thread sending `10, 20, 30` via `chan.as_send(jobs)` and closing, and receive all items in `main` until `ok == false`.
  3. **Drill**: Build a fan-out / rendezvous (`cap == 0`) channel Drill coordinating multiple worker threads.

### `760_thread_pool_tasks.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:thread"`, `thread.Pool`, `thread.Task`, `thread.pool_init(&pool, context.allocator, thread_count)`, `defer thread.pool_destroy(&pool)`, `thread.pool_start(&pool)`, `thread.pool_add_task(&pool, context.allocator, task_proc, data_rawptr, user_index)`, `thread.pool_finish(&pool)`, `thread.pool_pop_done(&pool)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:thread"`, `Job_Output :: struct { results: [8]int }`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain why spawning raw OS threads per small job is expensive, and how `thread.Pool` maintains a fixed set of worker threads pulling `thread.Task` items from a work queue.
  2. **Drill**: Write `square_task :: proc(task: thread.Task)` that casts `out := (^Job_Output)(task.data)` and writes `out.results[task.user_index] = task.user_index * task.user_index`.
  3. **Drill**: Initialize a 2-thread `thread.Pool` in `main`, add tasks (including parallel slice chunking), inspect completed tasks via `thread.pool_pop_done(&pool)` as well as `thread.pool_finish(&pool)`, and print `output.results`.

### `770_cond_sema_and_barriers.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:sync"`, `sync.Cond`, `sync.cond_wait(&cond, &mu)`, `sync.cond_signal(&cond)`, `sync.cond_broadcast(&cond)`, `sync.Barrier`, `sync.barrier_init(&b, thread_count)`, `sync.barrier_wait(&b)`, `sync.Sema`, `sync.sema_post(&s, count)`, `sync.sema_wait(&s)`, `sync.Once`, `sync.once_do(&once, init_proc)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:sync"`, `import "core:thread"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain condition variables (`sync.Cond` paired with a `sync.Mutex` for predicate-based wakeups with `cond_wait` / `cond_signal` / `cond_broadcast`), phase synchronization (`sync.Barrier`, where all N threads reach Phase 1 before any starts Phase 2), counting semaphores (`sync.Sema`), and thread-safe lazy init (`sync.Once`).
  2. **Drill**: Implement a `sync.Cond` producer/consumer Drill where a worker blocks inside `for !state.ready { sync.cond_wait(&state.cond, &state.mu) }` until the producer sets `ready = true` and calls `sync.cond_signal` / `sync.cond_broadcast`.
  3. **Drill**: Run `sync.once_do(&once, init_global_table)` across threads, coordinate a 2-phase `sync.Barrier`, and signal work slots with `sync.Sema`.

### `780_concurrent_pipeline_lab/` *(Multi-File Lab)*
- **Files**:
  - `780_concurrent_pipeline_lab/main.odin` (`package main`)
  - `780_concurrent_pipeline_lab/pipeline.odin` (`package main`)
- **Syntax / Keywords / Built-ins Checklist**: `thread.create_and_start_with_poly_data`, `sync.Mutex`, `sync.guard`, `sync.atomic_add`, `free_all(context.temp_allocator)` inside worker loop, `mem.Tracking_Allocator`, multi-worker error collection.
- **Scaffold**: File headers + `Work_Item` and `Batch_Context` structs in `pipeline.odin` (zero `_ =` silencers or dummy returns).
- **Ordered Outline**:
  1. In `pipeline.odin`: **Drill** to write `worker_loop :: proc(ctx: ^Batch_Context)` that atomically claims work indices via `idx := sync.atomic_add(&ctx.next_index, 1)`, uses `context.temp_allocator` for per-item scratch work followed by `free_all(context.temp_allocator)`, and collects per-item results and errors safely under `sync.guard`.
  2. In `main.odin`: **Drill** to wrap `context.allocator` in `mem.Tracking_Allocator`, populate 16 `Work_Item`s, run 4 workers to completion, print aggregated output + error summary, and verify 0 memory leaks.

### `790_five_multipliers_haversine_lab/` *(Multi-File Lab — Standalone Hardware Multipliers without a Profiler Library)*
- **Cross-Repo Boundary**: `790` owns the standalone 5-stage Odin Haversine optimization progression (`#soa`, `#simd`, 4-way IPC unrolling, `#align(64)` multi-thread reduction, `RDTSC` repetition timing) without repeating Tracy client/GUI lectures (`tracy_how_to/`). Keep all helper code clean with zero `_ =` silencers and zero dummy `return` stubs.
- **Files**:
  - `790_five_multipliers_haversine_lab/main.odin` (`package main`)
  - `790_five_multipliers_haversine_lab/naive_clean.odin` (`package main`)
  - `790_five_multipliers_haversine_lab/optimized_multipliers.odin` (`package main`)
- **Syntax / Keywords / Built-ins Checklist**: `intrinsics.read_cycle_counter()`, `#soa[]Pair`, `#simd[4]f32`, `simd.fma`, `simd.reduce_add_ordered`, `struct #align(64)` (preventing false sharing across threads), `thread.create_and_start_with_poly_data`, `#no_bounds_check`.
- **Scaffold**: File headers + `Coord_Pair :: struct { x0, y0, x1, y1: f32 }` and `Benchmark_Result :: struct { name: string, sum: f32, min_cycles: u64 }` in `main.odin`, plus `compute_naive_wasted` baseline contract.
- **Ordered Outline**:
  1. In `naive_clean.odin`: **Drill** to implement Stage 0 (`compute_naive_wasted`): an intentionally "Clean Code" heap-pointer-chasing vtable/union version with a single serial accumulator demonstrating Multiplier #1 Waste + Multiplier #4 Cache Misses.
  2. In `optimized_multipliers.odin`: **Drill** to implement Stage 1 (`compute_de_wasted_aos`), Stage 2 (`compute_ipc_unrolled`), Stage 3 (`compute_simd_soa`), and multi-threaded `#align(64)` partial reduction.
  3. In `main.odin`: **Drill** to run a repetition test (`intrinsics.read_cycle_counter()`) across all stages, assert every stage matches within `1e-2`, and print the progressive `min_cycles` speedup table.

---

## `800`–`899`: C Interop (`foreign`), Dynamic Libraries (`dynlib`), Vendor & Low-Level

### `800_foreign_c_interop.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:c"`, `import "core:c/libc"`, `c.int`, `c.uint`, `c.size_t`, `c.double`, `c.char`, `cstring`, OS-guarded `when ODIN_OS == .Windows` (`foreign import crt "system:msvcrt.lib"`) vs. `.Linux`/`.Darwin` (`"system:c"`), `foreign crt { ... }`, `@(link_name="...")`, `@(link_prefix="...")`, `#c_vararg`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:c"`, `import "core:c/libc"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how Odin talks directly to C libraries with zero wrapper overhead: `when ODIN_OS == .Windows` guards platform-specific `foreign import` library names (`"system:msvcrt.lib"` vs `"system:c"`), and `foreign` blocks declare C function signatures using `core:c` types (`c.int`, `c.size_t`, `cstring`, `rawptr`, `[^]T`, `#c_vararg`) and `@(link_prefix="...")`.
  2. **Drill**: Declare an OS-guarded `foreign` block calling C functions (including `@(link_prefix)` and `#c_vararg` printf/snprintf), alongside `core:c/libc` (`abs`, `strlen`, `cos`), and print the results in `main`.

### `810_calling_conventions_and_c_callbacks.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `proc "odin" (...)` (default: passes hidden `context` pointer), `proc "c" (...)` (C ABI: **no** implicit `context`), `proc "stdcall" (...)`, `proc "fastcall" (...)`, `proc "contextless" (...)`, restoring `context = runtime.default_context()` (or `context = (^runtime.Context)(user_data)^`) inside a real `proc "c" (..., user_data: rawptr)` callback, `libc.qsort`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:c"`, `import "core:c/libc"`, `import "base:runtime"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain `proc "contextless"` (no hidden `context`, useful for pure math/leaf procs) and the crucial rule for `proc "c"` callbacks invoked by C libraries (like `qsort`, GLFW, SDL, Win32, or audio callbacks): they receive **no `context`**, so before calling any Odin procedure needing an allocator or logger (`fmt.println`, `make`, `log.info`), you **must** restore `context = runtime.default_context()` or dereference a `^runtime.Context` passed via `user_data: rawptr` inside the callback!
  2. **Drill**: Write a `proc "contextless"` leaf helper, a `compare_ints_c :: proc "c" (a, b: rawptr) -> c.int` for `libc.qsort` that restores `context = runtime.default_context()`, and a real C-style callback `on_event_c :: proc "c" (val: c.int, user_data: rawptr)` that restores `context` from `user_data` inside the callback body before formatting/allocating.
  3. **Drill**: Pass `compare_ints_c` to `libc.qsort` on an `[6]int` array and invoke the `user_data` callback in `main`.

### `820_dynamic_library_loading.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:dynlib"`, `dynlib.Library`, `dynlib.load_library(path)`, `dynlib.unload_library(lib)`, `dynlib.symbol_address(lib, "symbol_name")`, `dynlib.initialize_symbols(&table, path, "prefix_")`, `dynlib.last_error()`, OS guards (`when ODIN_OS == .Windows` vs `.Linux` / `.Darwin`).
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:dynlib"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain runtime shared-library loading via `core:dynlib`, highlighting OS-guarded library paths (`kernel32.dll` on Windows vs `libc.so.6`/`libSystem.B.dylib` on POSIX) and `dynlib.initialize_symbols(&my_api_struct, dll_path, "")` which uses Odin's RTTI to bind every procedure pointer field in a struct!
  2. **Drill**: Define an OS-guarded API table struct and load both via `dynlib.initialize_symbols` and manual `dynlib.load_library` + `dynlib.symbol_address` + `dynlib.unload_library` (handling `dynlib.last_error()` cleanly).

### `830_dll_hot_reload_lab/` *(Multi-File Lab — Inspired by `CodingTemplateExamples/examples/dll`)*
- **Files**:
  - `830_dll_hot_reload_lab/host.odin` (`package main` — host executable)
  - `830_dll_hot_reload_lab/shared_api.odin` (`package main` — shared `Game_Memory` struct & `Plugin_API` function table)
  - `830_dll_hot_reload_lab/plugin/plugin.odin` (`package plugin` — compiled to DLL via `odin build 830_dll_hot_reload_lab/plugin -build-mode:dll -out:plugin.dll`)
- **Syntax / Keywords / Built-ins Checklist**: `@(export)` attribute on `proc "c" (mem: ^Game_Memory)`, `-build-mode:dll` (or `-build-mode:shared`), `os.last_write_time_by_name`, copying `plugin.dll` -> `plugin_live.dll` before `dynlib.initialize_symbols` so Windows doesn't file-lock `plugin.dll` during rebuilds, standalone simulation fallback in `host.odin` when no DLL is built yet!
- **Scaffold**: File headers + `Game_Memory` and `Plugin_API` contracts in `shared_api.odin` + ABI callback signature `game_update :: proc "c" (mem: ^Game_Memory)` restoring `context` in `plugin.odin` (zero `_ =` silencers).
- **Ordered Outline**:
  1. In `plugin/plugin.odin`: **Drill** to complete `@(export) game_update :: proc "c" (mem: ^Game_Memory)` restoring `context = runtime.default_context()`, initializing `mem` on first run, and updating `mem.tick` and `mem.player_x`.
  2. In `host.odin`: **Drill** to write `load_plugin_api` (copies `plugin.dll` to `plugin_live.dll` and calls `dynlib.initialize_symbols`), run a reload loop checking `os.last_write_time_by_name` (plus a clean standalone simulation fallback when `plugin.dll` is absent), and clean up.

### `850_inline_assembly_and_simd_intrinsics.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "base:intrinsics"`, `intrinsics.read_cycle_counter()`, `intrinsics.count_ones(x)`, `intrinsics.count_leading_zeros(x)`, `intrinsics.count_trailing_zeros(x)`, `intrinsics.reverse_bits(x)`, `intrinsics.byte_swap(x)`, `intrinsics.overflow_add(a, b)` -> `(res, did_overflow)`, inline `asm (param_types) -> return_type { "assembly", "constraints" }` (with `#clobber` or constraint syntax).
- **Scaffold**: `package main`, `import "core:fmt"`, `import "base:intrinsics"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain CPU hardware intrinsics in `base:intrinsics` (portable across x86_64/ARM64) and Odin's LLVM-style inline `asm` expression for raw machine instructions.
  2. **Drill**: Measure CPU cycles around a small calculation with `c0 := intrinsics.read_cycle_counter()`, test `count_ones`, `count_trailing_zeros`, `reverse_bits`, `byte_swap`, and checked arithmetic `res, overflowed := intrinsics.overflow_add(u8(250), u8(20))`.
  3. **Drill**: On `when ODIN_ARCH == .amd64`, write an inline `asm` expression adding two integers (`add eax, ecx`) and demonstrating clobber/constraint rules.

### `860_freestanding_and_bedrock_mode.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: CLI flags `-default-to-panic-allocator`, `-default-to-nil-allocator`, `-bedrock`, `-no-rtti`, `-disable-non-constant-globals`, `@(link_section="...")`, `@(rodata)`, stack-only data structures (`[N]T`, `[dynamic; N]T`, `strings.builder_from_bytes(buf[:])`, fixed `mem.Arena` over stack `[N]byte`).
- **Scaffold**: `package main`, `import "core:mem"`, `import "core:strings"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain how to write zero-heap / embedded / kernel-grade Odin code that runs cleanly with `-default-to-panic-allocator` (where *any* accidental heap allocation immediately panics with the exact offending line!).
  2. **Drill**: Set `context.allocator = mem.panic_allocator()` at the start of `main`, format/build strings with `strings.builder_from_bytes(buf[:])` and manipulate `[dynamic; 16]int` + a stack-backed `mem.Arena` over `buf: [512]byte`, verifying zero heap touches.

### `870_vendor_collection_overview.odin` *(Naturally Narrow Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "vendor:stb/image"` / `import rl "vendor:raylib"` (or `vendor:zlib`), how `vendor:` ships pre-configured C/Odin multimedia & game libraries right inside the Odin compiler distribution (`odin root`/vendor).
- **Scaffold**: `package main`, `import "core:fmt"`, `import rl "vendor:raylib"`, `import stbi "vendor:stb/image"`, `main :: proc()`.
- **Ordered Outline**:
  1. Explain Odin's batteries-included `vendor:` collection (`raylib`, `sdl2`/`sdl3`, `glfw`, `vulkan`, `directx`, `OpenGL`, `wgpu`, `miniaudio`, `stb`, `box2d`, `lua`, `microui`, `cgltf`).
  2. **Drill**: Use `vendor:raylib` headless math/color helpers (`rl.Color`, `rl.Vector2`, `rl.ColorToHSV`, `rl.CheckCollisionCircles`) alongside a second `vendor:` package (`vendor:stb/image` or `vendor:zlib`) without opening a GUI window, and note how `980_raylib_arcade_lab` opens a live window.

---

## `900`–`999`: Basic Programs & Complete Training Capstones

> **Lab & Capstone Hygiene**: All `900`–`980` Primers and Labs have **zero `_ =` silencers** and **zero dummy `return nil` / `return false` / `return .None` stubs**—express unimplemented helpers as `//` **Drills** specifying exact names, parameter types, and return types.

### `900_binary_file_dumper.odin` *(Primer — Inspired by `CodingTemplateExamples/examples/dump_binary_file.jai`)*
- **Syntax / Keywords / Built-ins Checklist**: `core:os`, `core:fmt`, `os.args`, `os.read_entire_file`, `defer delete(data)`, 16-byte row slicing `data[offset:min(offset+16, len(data))]`, `%08x` offset printing, `%02x` hex byte printing, printable ASCII range `' '..='~'`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:os"`, `main :: proc()` with live starter file read (zero dummy `dump_bytes` stub).
- **Ordered Outline**:
  1. **Drill**: Write `dump_bytes :: proc(data: []u8, max_rows := 16)` that loops through `data` in 16-byte chunks (`for offset := 0; offset < len(data); offset += 16`), prints the 8-digit hex address, prints 16 hex byte columns (padding short final rows with spaces), and prints the 16-character ASCII gutter (replacing non-printable bytes outside `0x20..=0x7E` with `'.'`).
  2. **Drill** in `main`: Read the file specified in `os.args[1]` (or default to `"900_binary_file_dumper.odin"` itself!), call `dump_bytes(bytes, 12)`, and `defer delete(bytes)`.

### `910_custom_hash_table.odin` *(Primer — Inspired by `CodingTemplateExamples/examples/hash_table_test.jai`)*
- **Syntax / Keywords / Built-ins Checklist**: Parametric polymorphism `Hash_Table($K, $V: typeid) :: struct`, `Slot_State :: enum u8 { Empty, Occupied, Tombstone }`, `import "core:hash"`, `mem.Allocator`, power-of-2 capacity rounding (`next_pow2`) + bitmask indexing `idx := int(h) & (cap - 1)`, linear probing, load-factor resize (`70%`), `or_else`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:hash"`, `import "core:mem"`, `Slot_State :: enum u8 { Empty, Occupied, Tombstone }`, `main :: proc()`.
- **Ordered Outline**:
  1. **Drill**: Define `Entry($K, $V: typeid) :: struct { key: K, val: V, state: Slot_State }` and `Table($K, $V: typeid) :: struct { entries: []Entry(K, V), count: int, allocator: mem.Allocator }`.
  2. **Drill**: Write `next_pow2`, `table_init` (enforcing power-of-2 capacity for `& (cap - 1)` masking), `table_destroy`, `table_put` (linear probing with `hash.fnv64a(transmute([]u8)...)` or integer hash, resizing at 70% occupancy), `table_get -> (V, bool)`, and `table_remove` (setting `.Tombstone`).
  3. **Drill**: In `main`, wrap `context.allocator` in `mem.Tracking_Allocator`, insert 20 key-value pairs (triggering a resize), verify lookups and removals, destroy the table, and confirm 0 leaks.

### `920_json_task_tracker_cli.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `core:encoding/json`, `core:os`, `core:mem/virtual` (`virtual.Arena`), `core:strings`, `os.args[1:]` CLI subcommands (`add`, `done`, `list`), `Task_Status :: enum { Todo, Done }`, `Task :: struct { id: int, title: string, done: bool }`, `or_return`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:os"`, `import "core:encoding/json"`, `import "core:mem/virtual"`, `Task :: struct { id: int `json:"id"`, title: string `json:"title"`, done: bool `json:"done"` }`, `main :: proc()`.
- **Ordered Outline**:
  1. **Drill**: Write `load_tasks(path: string) -> ([dynamic]Task, bool)` and `save_tasks(path: string, tasks: []Task) -> bool` using `json.unmarshal` and `json.marshal(tasks, {pretty = true})`.
  2. **Drill**: Write commands `cmd_add(&tasks, title)`, `cmd_complete(&tasks, id)`, and `cmd_list(tasks[:])`.
  3. **Drill**: In `main`, initialize a single `virtual.Arena` as `context.allocator` (`defer virtual.arena_destroy(&arena)`), dispatch subcommands from `os.args[1:]` (falling back to a self-contained add/complete/list/save/reload demo when no CLI args are passed), and remove the temp file on exit.

### `930_tcp_echo_and_command_server.odin` *(Primer)*
- **Syntax / Keywords / Built-ins Checklist**: `import "core:net"`, `import "core:thread"`, `import "core:strings"`, `import "core:strconv"`, `net.Endpoint`, `net.listen_tcp`, `net.accept_tcp`, `net.dial_tcp`, `net.recv_tcp`, `net.send_tcp`, `net.close`, partial `recv` newline framing, malformed command handling, `free_all(context.temp_allocator)`.
- **Scaffold**: `package main`, `import "core:fmt"`, `import "core:net"`, `import "core:thread"`, `import "core:strings"`, `import "core:strconv"`, `main :: proc()`.
- **Ordered Outline**:
  1. **Drill**: Write `handle_command :: proc(line: string) -> string` that parses `"PING"` -> `"PONG\n"`, `"ADD <a> <b>"` -> `"<a+b>\n"` (using `fmt.tprintf`), handles malformed commands/args gracefully (`"ERR ...\n"`), and `"QUIT"` -> `"BYE\n"`.
  2. **Drill**: Write `server_proc :: proc(listen_sock: net.TCP_Socket)` that accepts a client via `net.accept_tcp`, accumulates partial `net.recv_tcp` reads until `'\n'` boundaries, responds via `net.send_tcp`, and calls `free_all(context.temp_allocator)` after each request.
  3. **Drill**: In `main`, bind `net.listen_tcp(net.Endpoint{address = net.IP4_Loopback, port = 0})` (loopback self-test), spawn `server_proc` on a background thread, connect with `net.dial_tcp`, send `"PING"`, `"ADD 15 27"`, a malformed command, and `"QUIT"`, print replies, and join the thread.

### `940_log_search_and_word_freq_lab/` *(Multi-File Lab)*
- **Files**:
  - `940_log_search_and_word_freq_lab/main.odin` (`package main`)
  - `940_log_search_and_word_freq_lab/indexer.odin` (`package main`)
  - `940_log_search_and_word_freq_lab/report.odin` (`package main`)
- **Syntax / Keywords / Built-ins Checklist**: `core:os`, `core:path/filepath`, `core:strings`, `core:slice`, `core:mem/virtual`, `map[string]int`, zero-allocation word tokenization, sorting word counts with `slice.sort_by`.
- **Scaffold**: File headers + `Word_Stat :: struct { word: string, count: int }` and `Search_Result :: struct { file: string, line_num: int, line_text: string }` (zero `_ =` silencers or dummy returns).
- **Ordered Outline**:
  1. In `indexer.odin`: **Drill** to write `scan_text_buffer(filename, content: string, query: string, freq_map: ^map[string]int, hits: ^[dynamic]Search_Result)` that splits lines and ASCII words without extra allocations.
  2. In `report.odin`: **Drill** to write `top_n_words(freq_map: map[string]int, n: int, alloc: mem.Allocator) -> []Word_Stat` sorted descending by `.count` with `slice.sort_by`.
  3. In `main.odin`: **Drill** to scan `.md` files (or sample files), print matching lines and the top 10 most frequent words, backed by a `virtual.Arena`.

### `950_ecs_entity_simulation_lab/` *(Multi-File Lab)*
- **Files**:
  - `950_ecs_entity_simulation_lab/main.odin` (`package main`)
  - `950_ecs_entity_simulation_lab/world.odin` (`package main`)
  - `950_ecs_entity_simulation_lab/systems.odin` (`package main`)
- **Syntax / Keywords / Built-ins Checklist**: `Entity_Handle :: struct { idx: u32, gen: u32 }`, `Component_Flag :: enum { Position, Velocity, Health, AI }`, `Component_Mask :: bit_set[Component_Flag; u8]`, `#soa[MAX_ENTITIES]Vec2`, `#simd[4]f32`, `free_all(context.temp_allocator)`.
- **Scaffold**: File headers + `MAX_ENTITIES :: 64`, `Component_Flag`, `Component_Mask`, and `World` struct declaration in `world.odin` (zero `_ =` silencers or dummy returns).
- **Ordered Outline**:
  1. In `world.odin`: **Drill** to write `spawn_entity(w: ^World, mask: Component_Mask) -> Entity_Handle`, `despawn_entity(w: ^World, h: Entity_Handle) -> bool` (incrementing generation!), and `is_alive(w: ^World, h: Entity_Handle) -> bool`.
  2. In `systems.odin`: **Drill** to write `movement_system(w: ^World, dt: f32)` updating `#soa` positions/velocities (including a `#simd[4]f32` batch pass where `{.Position, .Velocity}` apply), and `damage_system(w: ^World)` despawning entities whose `health <= 0`.
  3. In `main.odin`: **Drill** to spawn 16 entities, step the simulation for 10 ticks calling `movement_system`, `damage_system`, and `free_all(context.temp_allocator)` each tick, and print surviving entities.

### `960_bytecode_vm_interpreter_lab/` *(Multi-File Lab)*
- **Files**:
  - `960_bytecode_vm_interpreter_lab/main.odin` (`package main`)
  - `960_bytecode_vm_interpreter_lab/isa.odin` (`package main`)
  - `960_bytecode_vm_interpreter_lab/assembler.odin` (`package main`)
  - `960_bytecode_vm_interpreter_lab/vm.odin` (`package main`)
- **Syntax / Keywords / Built-ins Checklist**: `Opcode :: enum u8 { Load_Imm, Add, Sub, Mul, Cmp_Lt, Jmp, Jmp_If_Zero, Print, Halt }`, `Instruction :: bit_field u32 { op: Opcode | 8, dst: u8 | 4, src_a: u8 | 4, imm16: i16 | 16 }`, `[dynamic; 64]u32` stack, `VM_Error :: enum { None, Stack_Overflow, Invalid_Opcode, Unknown_Mnemonic }`, `or_return`, `#partial switch`.
- **Scaffold**: File headers + `Opcode` and `Instruction` bit_field definitions in `isa.odin` (zero `_ =` silencers or dummy returns).
- **Ordered Outline**:
  1. In `assembler.odin`: **Drill** to write `assemble_program(source: string, out_code: ^[dynamic]Instruction) -> (err: VM_Error)` using `strings.split_iterator` and `strconv.parse_int` + `or_return`.
  2. In `vm.odin`: **Drill** to write `run_vm(code: []Instruction) -> (err: VM_Error)` executing an instruction-pointer loop with an exhaustive `switch inst.op` over a `[16]i64` register file.
  3. In `main.odin`: **Drill** to assemble a small loop program (computing `1 + 2 + ... + 10` and printing the result), execute it on `run_vm`, and verify the output.

### `980_raylib_arcade_lab/` *(Multi-File Lab — Inspired by `CodingTemplateExamples/examples/invaders`)*
- **Files**:
  - `980_raylib_arcade_lab/main.odin` (`package main`)
  - `980_raylib_arcade_lab/game.odin` (`package main`)
  - `980_raylib_arcade_lab/render.odin` (`package main`)
- **Syntax / Keywords / Built-ins Checklist**: `import rl "vendor:raylib"`, `rl.InitWindow`, `defer rl.CloseWindow()`, `rl.SetTargetFPS(60)`, `rl.WindowShouldClose()`, `rl.GetFrameTime()`, `rl.IsKeyDown(.LEFT)` / `rl.IsKeyPressed(.SPACE)`, `rl.BeginDrawing()`, `defer rl.EndDrawing()`, `rl.ClearBackground`, `rl.DrawRectangleV`, `rl.DrawCircleV`, `rl.DrawText`, `fmt.ctprintf` (temp-allocated `cstring` for Raylib text!), `free_all(context.temp_allocator)`, `mem.Tracking_Allocator`.
- **Scaffold**: File headers + `Bullet`, `Invader`, and `Game_State` structs (`player_pos: rl.Vector2`, `bullets: [dynamic; 32]Bullet`, `invaders: [dynamic; 24]Invader`, `score: int`, `game_over: bool`) in `game.odin` (zero `_ =` silencers or dummy returns).
- **Ordered Outline**:
  1. In `game.odin`: **Drill** to write `init_game(g: ^Game_State)` and `update_game(g: ^Game_State, dt: f32)` (moving player with arrow/A-D keys, spawning bullets into fixed-capacity `[dynamic; 32]Bullet` on Spacebar, moving invaders, checking `rl.CheckCollisionCircleRec`, removing hit invaders with `unordered_remove`, and incrementing `g.score`).
  2. In `render.odin`: **Drill** to write `draw_game(g: ^Game_State)` using `rl.BeginDrawing()` + `defer rl.EndDrawing()`, drawing player, bullets, invaders, and the HUD score via `rl.DrawText(fmt.ctprintf("SCORE: %d", g.score), 16, 16, 20, rl.RAYWHITE)`.
  3. In `main.odin`: **Drill** to wrap `context.allocator` in `mem.Tracking_Allocator`, support a `-headless` flag (running 10 simulated frames if `-headless` is passed, else opening the 800x600 window loop calling `update_game`, `draw_game`, and `free_all(context.temp_allocator)` each frame!), and verify 0 heap leaks on exit.
