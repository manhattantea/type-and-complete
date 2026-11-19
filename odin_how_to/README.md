# Odin How-To Learning Workspace

Welcome to the **Odin How-To** educational curriculum! This repository is designed to take you from your first lines of Odin through to high-performance systems programming, arena-based memory management, custom allocators, concurrency, C interop, and complete capstone applications.

---

## 1. Quickstart & Toolchain Guide

Odin treats directories as packages by default. When working through single-file **Primers**, use the `-file` flag so Odin compiles the file in isolation rather than trying to build every file in the directory into a single package.

### Running a Primer
Compile and execute any standalone Primer immediately:
```powershell
odin run 001_first.odin -file
```

### Fast Typechecking (`odin check`)
Quickly verify syntax, types, and imports without code generation or linking:
```powershell
odin check 001_first.odin -file
```

### Compiling to an Isolated Binary
Build an executable into the `.build/` directory (which is already configured in `.gitignore`):
```powershell
odin build 001_first.odin -file -out:.build/001_first.exe
```

### Running and Checking Multi-File Labs
Labs live in numbered subdirectories (e.g., `300_packages_and_imports/`). Compile and run them as directory packages:
```powershell
odin check 300_packages_and_imports
odin run 300_packages_and_imports
```

### Running Unit Tests
Odin has a built-in test runner for procedures marked with `@(test)`:
```powershell
odin test 195_unit_testing_with_odin_test.odin -file
```

### Batch Verification Loop (PowerShell)
To quickly verify all Primers in the curriculum:
```powershell
Get-ChildItem -Filter *.odin | ForEach-Object {
    Write-Host "Checking $($_.Name)..." -ForegroundColor Cyan
    odin check $_.FullName -file
    if ($LASTEXITCODE -ne 0) { throw "Check failed on $($_.Name)" }
}
```

---

## 2. Pedagogical Philosophy

### ~5–20% Convenience Scaffolds & Graduated Drills
Most programming tutorials suffer from one of two extremes:
1. **Passive reading**: Full working examples where you read along and nod, but your brain never forms the muscle memory required to write the code yourself.
2. **Blank-canvas paralysis**: An empty file where you don't know what to write, and modern AI coding assistants guess randomly or hallucinate syntax from C++, Go, or Rust.

**Odin How-To** uses an intentional balance defined in [`spec.md`](../.scratch/curriculum-alignment/spec.md), [`GLOSSARY.md`](../GLOSSARY.md), and [`ADR-0002`](../docs/adr/0002-conversational-prose-hash-comments-and-convenience-scaffold.md):
- **~5–20% Soft Scaffold**: Each **Primer** provides `package main`, required `import`s, focused topic section procedures called sequentially from `main :: proc()` at the very bottom of the file (with 1 blank line immediately after every `proc() {` opening), and tiny working starter **Scaffold** lines when introducing brand-new syntax so you see the canonical shape. Every pre-imported package and starter local variable is genuinely used by live starter **Scaffold** code—never `_ = x` silencers and never dummy `return 0` / `return {}` / empty helper stubs (unimplemented helpers live as `//` **Drills** naming exact signatures, parameter types, and return types).
- **Graduated Drills & Causal Explanations**: Conversational `CodingTemplateExamples`-style prose inside compact `/* ... */` blocks (zero extra blank lines immediately after `/*` or before `*/`) and `//` comments explains *why* Odin is designed the way it is from hardware, memory layout, and compiler mechanics. Following a Feynman immediate-explanation rhythm, each new keyword, directive, or stdlib construct is explained plainly right where it appears alongside a concrete hypothetical before/body/after scenario (never ambiguous `{ ... }` placeholders), keeping inline code expressions intact on a single comment line. **Drills** progress naturally from explicit convenience hints (exact identifiers and types for IDE autocomplete) to conversational recall and open synthesis.
- **Core vs. Narrow Primer Sizing & Lab Boundaries**: Core **Primers** target `~150–300+` lines with `~8–15+` **Drills** across everyday combinations and traps, while naturally narrow single-directive **Primers** (`060`, `070`, `140`, `260`, `270`, `330`, `360`, `370`, `640`, `650`, `870`) stay focused at `~85–140` lines with `~4–7` **Drills**. Multi-file **Labs** keep shared ABI/domain contracts, baseline slow paths, and repetitive OS/setup boilerplate as **Scaffold**, leaving domain logic and helper implementations as open **Drills**.

### No Pre-Written Solutions Directory
You will notice there is **no `solutions/` folder** in this repository. This is intentional:
- Having answers in a sibling folder allows IDE autocompletion tools to look up the answers and spoil the **Drill**.
- True understanding comes from reading the explanation, typing the code, seeing it compile with `odin check <file>.odin -file` (or `odin check <lab_dir>`), and experimenting with the result.

### Inline Compiler Error Experiments
Throughout the **Primers**, you will encounter inline commented-out experiments such as:
```odin
// Try uncommenting: ptr := &DEFAULT_PORT
```
Uncommenting these lines demonstrates what Odin's typechecker and vetter reject (e.g. taking the address of a compile-time constant, implicit type conversions, mutating immutable strings, or variable shadowing under `-vet-shadowing`).

---

## 3. Curriculum Roadmap (`000`–`999`)

The curriculum spans 10 tiers comprising **105 single-file Primers** and **11 multi-file Labs** (116 numbered entries):

| Tier Range | Tier Focus | Deliverables |
| :--- | :--- | :--- |
| **`000`–`099`** | **Toolchain, Basic Syntax, Types & Control Flow** | 18 Primers (`000`–`080`) covering CLI flags, entry points, declarations, constants, numeric types, casting, booleans, strings, operators, scopes, `if`, `for`, `switch`, `#partial`, `defer`, `when`, builtin queries, complex/quaternions, compound literals, and `#unroll`. |
| **`100`–`199`** | **Procedures, Defer Idioms, Error Handling & Testing** | 12 Primers (`100`–`190`) covering procedure syntax, multiple return values, named returns, default arguments, variadic parameters, overload groups (`proc{...}`), `or_return`, `or_else`, `Maybe(T)`, procedure attributes, and `@(test)`. |
| **`200`–`299`** | **Compound Types, Value vs. Reference Semantics & Layout** | 16 Primers (`200`–`280`) covering fixed arrays, slices, dynamic arrays, maps, structs, unions, enums, bit sets, bit fields, pointers (`^T`, `[^]T`), `distinct` types, `using`, and linear algebra matrices. |
| **`300`–`399`** | **Packages, Scopes, Directives, Attributes & Build Configuration** | 7 Primers & 2 Labs (`300`–`380`) covering package imports, private visibility, build tags (`#+build`), file embedding (`#load`), compiler vetters, and multi-file package architecture. |
| **`400`–`499`** | **Context System, Memory Management, Arenas & Allocators** | 10 Primers & 1 Lab (`400`–`490`) covering Odin's implicit `context`, manual allocators (`new`/`make`/`delete`), tracking allocators, temporary scratch allocators, buffer arenas, virtual memory arenas, and arena architecture. |
| **`500`–`599`** | **Standard Library Essentials (`core:`), Containers, Spall & Tracy Hooks** | 14 Primers & 1 Lab (`500`–`599`) covering `core:fmt`, `core:strings`, `core:slice`, `core:os`, `core:io`/`core:bufio`, `core:flags`, `core:log`, `core:encoding/json`, `core:time`, Spall (`595`), `RDTSC` repetition testing (`597`), and slimmed Odin-idiom `when TRACY_ENABLE` / allocator / mutex integration hooks (`596`, `598`, Lab `599`) linking to [`tracy_how_to/`](../tracy_how_to/README.md). |
| **`600`–`699`** | **Parametric Polymorphism (Generics), Intrinsics & Reflection** | 8 Primers (`600`–`670`) covering generic procedures (`$T`), generic structs, `where` clauses, compile-time type queries, `runtime.Type_Info`, and struct field reflection. |
| **`700`–`799`** | **Concurrency, Synchronization, Channels, SIMD, SOA & Performance Multipliers** | 10 Primers & 2 Labs (`700`–`790`) covering `#soa` layout, cache lines & false sharing (`705`), SIMD hardware vectors, IPC dependency chains & unrolling (`715`), OS threads, mutexes, `sync.Cond`/barriers/semaphores (`770`), atomics, channels, thread pools, concurrent pipeline lab (`780`), and the standalone Five Multipliers Haversine lab (`790`). |
| **`800`–`899`** | **C Interop, Dynamic Libraries, Vendor & Low-Level** | 6 Primers & 1 Lab (`800`–`870`) covering `foreign` blocks, C calling conventions, DLL runtime loading (`core:dynlib`), Windows-safe hot-reloading loop (`830`), assembly/intrinsics, zero-heap programming, and `vendor:` collections. |
| **`900`–`999`** | **Basic Programs & Complete Training Capstones** | 4 Primers & 4 Labs (`900`–`999`) synthesizing everything: binary hex dumper, generic hash table, arena-backed task tracker, TCP server, concurrent search tool, entity simulation, bytecode VM, and 2D Raylib game loop. |

### Cross-Repo Performance & Tracy Boundary (`596`, `598`, `599` vs. `tracy_how_to/`)
- **`odin_how_to/`** owns Odin language mechanics and raw hardware primitives (`core:prof/spall` in `595`, `RDTSC` repetition + `GB/s` in `597`, `#soa` in `700`, cache lines/`#align(64)` in `705`, `#simd` in `710`, IPC unrolling in `715`, standalone Haversine in `790`).
- **`596`, `598`, and Lab `599`** stay focused as slim Odin-idiom integration hooks (`when TRACY_ENABLE` / `#config`, `@(deferred_out)` + `#caller_location`, `context.allocator`, and `sync.Mutex` guards). For full Tracy client-server telemetry, `TracyPlot`/`TracyMessageC`, multi-thread timeline forensics, and the 5-system Five-Multipliers Hotspot Hunt capstone, see [`tracy_how_to/`](../tracy_how_to/README.md).

---

## 4. Anti-Hallucination & Syntax Cheat Sheet

Odin is designed for clear, direct systems programming without hidden control flow or unexpected runtime overhead. If you come from C, C++, Go, Rust, Zig, or Jai, keep this cheat sheet handy to avoid falling back into syntax from other languages.

### Keywords Prohibited in Odin
- ❌ **No `var`, `let`, `const`**: All variable declarations use colon syntax (`x: int = 42`, `x := 42`, `x: int`).
- ❌ **No `fn`, `func`, `def`, `function`**: Procedures use `proc` (`add :: proc(a, b: int) -> int { return a + b }`).
- ❌ **No `while` or `do-while`**: `for` is the only loop keyword in Odin (`for cond { ... }`, `for { ... }`).
- ❌ **No `class` or `interface`**: Odin is data-oriented (`struct`, `enum`, `union`).
- ❌ **No `#include` or `#import`**: Use `package main` and `import "core:fmt"`.
- ❌ **No semicolons `;`** at line ends: Semicolons are optional and discouraged, except inside C-style `for` headers and `if` init statements.

### Declarations & Unused Variables
- **One Mental Model (`name : Type = value`)**:
  - Keep both `Type` and `= value` -> `x: int = 42`
  - Omit `Type` (`:` and `=` touch) -> `x := 42` (**never** write `x: int := 42`!)
  - Omit `= value` -> `x: int` (deterministically zero-initialized!)
- **Strict Unused-Variable Rule**: Every local variable and import in Odin **must be genuinely read or used**, otherwise `odin check` immediately reports `'x' declared but not used`. Starter **Scaffolds** never use `_ = x` silencers; use `_` only to discard unwanted positions in multi-return calls (such as `q, _, ok := divmod(10, 0)`).
- **Format Verbs Required**: `fmt.printf` and `fmt.printfln` always require a verb after `%` (`%v` value, `%T` type, `%#v` Odin literal syntax, `%%` literal percent)—**never** bare `% %` (which is Jai syntax).
```odin
x := 42                 // Inferred type (int)
x: int = 42             // Explicit type and initial value
x: int                  // Zero-initialized (0, 0.0, false, "", nil)
x: int = ---            // Explicitly uninitialized memory (garbage/scratch)
PI :: 3.14159265        // Untyped compile-time constant
PORT : u16 : 8080       // Typed compile-time constant
```

### Pointers & References
```odin
p: ^int                 // Pointer to int (NOT *int)
ptr := &x               // Address-of operator (&)
val := ptr^             // Dereference operator (postfix ^, NOT *ptr)
mp: [^]u8               // Multi-pointer (indexable pointer for C buffers)
raw: rawptr             // Untyped raw pointer (equivalent to void* in C)
uptr: uintptr           // Pointer-sized unsigned integer
```

### Slices & Ranges
```odin
0..<10                  // Half-open range (0 through 9)
0..=9                   // Inclusive range (0 through 9)
slice := arr[0:4]       // Slicing uses colon (NOT ..)
full := arr[:]          // Slice entire array
```

### Numbers & Casting
- **Strict Typing**: Typed numeric variables *never* implicitly cast, even for widening (`u8` to `u32` requires explicit conversion).
```odin
u32(val)                // Type conversion call
cast(u32)val            // Explicit cast operator
auto_cast val           // Inferred cast when destination type is unambiguous
transmute(u32)f32_val   // Bitwise reinterpretation (sizes must match!)
```

### Strings & Runes
```odin
"Hello"                 // UTF-8 string (16-byte header: data pointer + length)
`C:\Path\Raw`           // Backtick raw string literal (no escaping)
'Ω'                     // Unicode rune literal (32-bit codepoint)
cstring                 // Null-terminated pointer for C APIs
```

### Modulo & Bitwise Operators
```odin
-7 % 3                  // Truncated remainder (-1, sign follows dividend)
-7 %% 3                 // Floored modulo (2, sign follows divisor — ring buffers!)
a ~ b                   // Binary bitwise XOR (Odin uses ~ instead of ^)
~a                      // Unary bitwise NOT
a &~ b                  // Bit clear (AND-NOT)
```

Happy coding in Odin!
