// odin run 320_build_tags_and_file_suffixes.odin -file
#+build windows, linux, darwin
#+build amd64, arm64
#+build !freestanding
#+vet !unused-variables

package main

import "core:fmt"

/*
Instead of C's #ifdef preprocessor macros scattered inside functions, Odin
selects entire source files per platform and CPU architecture at the package
level. Separating platform code into clean files keeps business logic free of
nested conditional blocks and guarantees non-matching files are skipped before
any OS-specific symbols are typechecked.

Two rules govern how Odin picks files:

    #+build ...   must appear at the very top of the file BEFORE 'package'
    _os.odin      automatic filename suffixes when compiling a directory package

Watch the placement of #+build tags carefully. If you place #+build or #+vet
below the 'package' line, the compiler treats them as ordinary comments and
silently ignores them.
*/

build_tag_rules_and_targets :: proc() {

	/*
	Build tags combine multiple constraints cleanly on file-top comment lines.
	Commas on the same #+build line act as logical OR, separate #+build lines
	act as logical AND, and a leading '!' negates a tag:

	    #+build windows, linux, darwin   -> compiles on Windows OR Linux OR macOS
	    #+build amd64, arm64             -> AND requires 64-bit x86 OR ARM64
	    #+build !freestanding            -> AND excludes freestanding targets

	Suppose an audio backend calls WASAPI on Windows and ALSA on Linux, and
	only supports 64-bit CPUs. Putting '#+build windows, linux' and
	'#+build amd64, arm64' above 'package audio' keeps the whole file out of
	macOS or 32-bit builds automatically.

	Inside any file that passes those tags, Odin exposes compile-time target
	constants (ODIN_OS, ODIN_ARCH, ODIN_VENDOR, ODIN_VERSION, ODIN_DEBUG,
	ODIN_ENDIAN) that you can inspect directly or branch on with 'when'.
	*/

	// Here is a live check printing the current OS and CPU architecture:

	fmt.printfln("Target OS: %v | Arch: %v", ODIN_OS, ODIN_ARCH)

	// Print ODIN_VENDOR, ODIN_VERSION, ODIN_DEBUG, and ODIN_ENDIAN using
	// fmt.printfln so you can see every compile-time target constant.


	// Define a helper procedure target_summary :: proc() -> string above
	// build_tag_rules_and_targets that returns "64-bit desktop target" when
	// size_of(uintptr) == 8, or "other target" otherwise, then print its result
	// here.


	// Re-run this file with '-debug' (odin run 320_build_tags_and_file_suffixes.odin -file -debug)
	// and observe ODIN_DEBUG flip from false to true.
}

filename_suffixes_and_os_layout :: proc() {

	/*
	When you compile a multi-file directory package (without -file), Odin
	automatically filters files based on filename suffixes right before the
	.odin extension. You do not even need #+build tags for standard OS splits:

	    net_windows.odin       compiled only on Windows
	    net_linux.odin         compiled only on Linux
	    net_darwin.odin        compiled only on macOS
	    net_unix.odin          compiled on Linux, macOS, FreeBSD, OpenBSD, NetBSD
	    simd_amd64.odin        compiled only on x86-64
	    asm_windows_amd64.odin compiled only on Windows x86-64
	    parser_test.odin       compiled only when running 'odin test'

	Suppose you build a cross-platform windowing package under platform/. You
	place the shared Window struct and exported open_window(title: string) proc
	in platform/platform.odin, and have it call an internal os_open_window proc.
	Then platform_windows.odin implements os_open_window using Win32 calls,
	platform_linux.odin implements os_open_window using X11 or Wayland, and
	platform_test.odin holds @(test) checks that never bloat normal builds.
	Each OS file sees only its own native APIs, and callers never see #ifdefs.
	*/

	// Use compile-time 'when' branching inside a helper or right here to
	// compute a path_sep: string constant or local: "\\" when ODIN_OS == .Windows,
	// else "/". Print path_sep along with a platform greeting inside a
	// when ODIN_OS == .Windows / else when ODIN_OS == .Linux / else block.


	// Write a second 'when' check comparing ODIN_ARCH == .amd64 against
	// ODIN_ARCH == .arm64 and print which instruction family is active.


	// Write a helper is_unix_family :: proc() -> bool using compile-time
	// when ODIN_OS == .Linux || ODIN_OS == .Darwin || ODIN_OS == .FreeBSD
	// and print its return value here.
}

per_file_vet_and_tag_experiments :: proc() {

	/*
	Line 5 of this file carries '#+vet !unused-variables', which tells the
	compiler to relax the unused-variable check in this specific file even when
	you pass -vet on the command line. Per-file vet overrides work the exact
	same way as #+build tags and must also sit before 'package'.

	Note that because we run this single Primer with '-file', Odin skips suffix
	filtering on the filename itself and honors the #+build and #+vet tags at
	the top of the file.
	*/

	fmt.println("Check line 5 (#+vet !unused-variables) by testing an unread variable under -vet.")

	// Test the per-file #+vet override: declare unused_demo := 42 without
	// reading it, then run:
	// odin check 320_build_tags_and_file_suffixes.odin -file -vet
	// It passes because line 5 disables unused-variables. Remove line 5 and
	// re-run the same command to watch -vet catch unused_demo immediately.


	// Experiment with #+build filtering: temporarily change line 2 to exclude
	// your current OS (for example #+build !windows on Windows) and run
	// odin check 320_build_tags_and_file_suffixes.odin -file to see Odin report
	// that no source files matched the target platform, then restore line 2.
}

main :: proc() {

	fmt.println("=== 1. Build tag rules and target constants ===")
	build_tag_rules_and_targets()

	fmt.println("\n=== 2. Filename suffixes and multi-file OS layout ===")
	filename_suffixes_and_os_layout()

	fmt.println("\n=== 3. Per-file #+vet and tag experiments ===")
	per_file_vet_and_tag_experiments()
}
