// odin run 060_when_compile_time_branching.odin -file

package main

import "core:fmt"

/*
'when' is Odin's compile-time branch (replacing C's '#if' and '#ifdef' without a
separate text preprocessor). Because the condition is known during compilation,
only the chosen branch makes it into the binary—zero runtime branch instructions
are emitted.

Even better, Odin parses the syntax of untaken 'when' branches but does NOT
type-check them. Suppose you write 'when ODIN_OS == .Linux { linux_only_call() }'
and compile on Windows: the Windows build succeeds even though linux_only_call
does not exist on Windows.

This file is split into two small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

PLATFORM_TAG :: "Windows-Host" when ODIN_OS == .Windows else "POSIX-or-Other-Host"

compile_time_branches_and_untyped_skip :: proc() {

	/*
	Notice how 'A when COND else B' works directly in file-scope constant
	declarations (like PLATFORM_TAG above). Inside procedures, 'when' behaves
	like 'if / else if / else' except its condition must be a compile-time
	constant boolean such as ODIN_DEBUG or ODIN_OS == .Windows.
	*/

	// Here we print PLATFORM_TAG and prove an untaken 'when false' branch skips
	// type-checking of undeclared identifiers:

	fmt.printfln("Compiled platform tag: %v", PLATFORM_TAG)
	when false {
		undeclared_linux_only_syscall(12345)
	}

	// Write a when ODIN_DEBUG { ... } else { ... } block that prints a debug
	// banner when compiled with -debug and a release banner otherwise.
	// Try running with: odin run 060_when_compile_time_branching.odin -file -debug


	// Write a when ODIN_OS == .Windows / else when ODIN_OS == .Linux / else chain
	// printing which OS this binary targets. Inside a branch for an OS you are
	// not running on, include a call like posix_only_stub() to verify Odin
	// skips type-checking that untaken branch.


	// Verify that 'when' requires a compile-time constant:
	// declare runtime_mode := true and try uncommenting the when check below:
	// when runtime_mode { fmt.println("runtime") }
}

architecture_and_when_ternary :: proc() {

	/*
	You can also inspect target pointer width and CPU architecture (ODIN_ARCH)
	at compile time to pick cache-line sizes, SIMD widths, or buffer defaults
	with zero runtime cost.

	Because 'when' ternaries resolve during compilation, they are legal in '::'
	constant declarations at both file scope and procedure scope:

	    Suppose TARGET_LANES :: 8 when ODIN_ARCH == .amd64 else 4:
	        On x86-64 builds TARGET_LANES is folded directly to the constant 8,
	        while on ARM64 builds it folds directly to 4.
	*/

	// Here is a compile-time 64-bit check using size_of(uintptr):

	IS_64_BIT :: size_of(uintptr) == 8
	fmt.printfln("64-bit target: %v (ODIN_ARCH=%v)", IS_64_BIT, ODIN_ARCH)

	// Write a when ODIN_ARCH == .amd64 / else when ODIN_ARCH == .arm64 / else chain
	// printing the target CPU architecture name.


	// Declare a local constant SIMD_LANES :: 8 when ODIN_ARCH == .amd64 else 4
	// and a file-scope constant CACHE_PAD :: 64 when ODIN_ARCH == .amd64 else 32
	// above main, then print both values here.
}

main :: proc() {

	fmt.println("=== 1. Compile-time when and untaken branch skipping ===")
	compile_time_branches_and_untyped_skip()

	fmt.println("\n=== 2. Target architecture and when ternary constants ===")
	architecture_and_when_ternary()
}
