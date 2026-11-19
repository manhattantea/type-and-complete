// odin run 800_foreign_c_interop.odin -file

package main

import "core:c"
import "core:c/libc"
import "core:fmt"
import "core:strings"

/*
One of Odin's strongest systems features is zero-overhead C interoperability.
Because Odin compiles native machine code through LLVM, Odin procedures using
the C calling convention and compiled C functions share the exact same ABI,
stack layout, and object-file symbols. There is no JNI serialization layer and
no runtime wrapper generator sitting in between.

Talking to a C library takes two parts: a 'foreign import' declaration naming
the library file to link against, and a 'foreign' block declaring the C
function signatures. When a procedure inside a foreign block ends with '---'
instead of a '{ ... }' body, it tells Odin: "This symbol has no Odin body;
resolve its address at link time."

Because C runtime library names differ by operating system, we guard
'foreign import' with compile-time 'when ODIN_OS' branches so the same file
compiles cleanly on Windows, Linux, and macOS.
*/

when ODIN_OS == .Windows {
	foreign import crt "system:msvcrt.lib"
} else {
	foreign import crt "system:c"
}

foreign crt {
	@(link_name = "puts")
	c_puts :: proc "c" (str: cstring) -> c.int ---

	@(link_name = "cos")
	c_cos :: proc "c" (x: c.double) -> c.double ---
}

c_types_and_libc_calls :: proc() {

	/*
	C integer widths vary by compiler and operating system (for example, C's
	'long' is 32 bits on Windows x64 but 64 bits on Linux x64). Rather than
	guessing bit widths, import "core:c" and use exact ABI aliases such as
	c.int, c.uint, c.size_t, c.double, and c.char.

	Odin also ships "core:c/libc" with ready-made bindings for standard C
	functions like libc.abs and libc.strlen, while 'foreign' blocks let you bind
	any external C library symbol directly. Notice '@(link_name = "puts")':
	that attribute lets you name the Odin symbol 'c_puts' locally while linking
	against the C symbol 'puts'.
	*/

	sample_int: c.int = -42
	abs_val := libc.abs(sample_int)
	fmt.printfln("Foreign C baseline: libc.abs(%d) = %d", sample_int, abs_val)
	fmt.printfln("Foreign C cos(0.0) = %.2f", c_cos(0.0))

	// Declare val: c.int = -128, pass it to libc.abs into abs_result, and
	// print both values using fmt.printfln.


	// Declare angle: c.double = 3.141592653589793 and call c_cos(angle) into
	// cos_val, then print cos_val formatted with %.4f using fmt.printfln.
}

cstrings_and_multi_pointers :: proc() {

	/*
	An Odin 'string' is a 16-byte header holding a byte pointer and a byte
	length, and it is NOT guaranteed to end with a zero byte. By contrast, a C
	'cstring' is a single raw pointer ending in '\0'. Passing a dynamic Odin
	string where C expects a cstring is a compile error.

	String literals like "Hellope" automatically include a trailing '\0' in
	read-only memory, so they coerce directly to cstring. For runtime Odin
	strings, convert them with strings.clone_to_cstring and free the result
	with delete.

	For C arrays, Odin uses multi-pointers written as [^]T. Suppose a C array
	is backed by raw_buf := [3]c.int{10, 20, 30} and c_ptr: [^]c.int = &raw_buf[0].
	You can index c_ptr[i] without bounds checks, or slice it over a known
	length with c_ptr[0:3] to get a safe bounds-checked []c.int slice.
	*/

	dynamic_msg := strings.clone("Runtime Odin text")
	defer delete(dynamic_msg)
	cloned_c, clone_err := strings.clone_to_cstring(dynamic_msg)
	defer delete(cloned_c)
	if clone_err == nil {
		fmt.printfln("Converted cstring length via libc.strlen: %d", libc.strlen(cloned_c))
	}

	// Declare greeting: cstring = "Hello from Odin foreign C FFI!"
	// Call status := c_puts(greeting) and print status with fmt.printfln.


	// Pass greeting to libc.strlen(greeting) into byte_len (type c.size_t)
	// and print byte_len with fmt.printfln.


	// Declare raw_buf := [4]c.int{10, 20, 30, 40} and take a multi-pointer:
	// c_ptr: [^]c.int = &raw_buf[0]
	// Slice it into safe_slice := c_ptr[0:4] and print safe_slice with
	// fmt.printfln.


	// Try uncommenting below to confirm Odin rejects passing a string as cstring:
	// odin_str: string = "Dynamic Odin string"
	// c_puts(odin_str)
}

variadics_and_link_prefix :: proc() {

	/*
	Many C libraries group functions under a common prefix (such as gl_, rl_,
	or isdigit/isalpha) and use C varargs (such as printf). Odin supports both directly on
	foreign blocks:

	When we place '@(link_prefix = "is")' above a foreign block, Odin prepends
	"is" to every procedure name inside that block when resolving linker symbols.
	So declaring 'digit' inside that block links against the C symbol 'isdigit'
	while keeping your Odin call sites clean.

	When we write '#c_vararg' before the variadic parameter of a C procedure:
	    c_printf :: proc "c" (format: cstring, #c_vararg args: ..any) -> c.int ---
	it tells Odin to pass arguments using C's ABI vararg rules instead of
	packing an Odin []any slice.
	*/

	// Add a foreign block right here (or at file scope) referencing crt with
	// @(link_prefix = "is") declaring two C character classifiers:
	// digit :: proc "c" (ch: c.int) -> c.int ---
	// alpha :: proc "c" (ch: c.int) -> c.int ---
	// Call digit('7') and alpha('A') and print whether each returned non-zero.


	// Declare a C variadic printf binding inside a foreign crt block using:
	// @(link_name = "printf") c_printf :: proc "c" (format: cstring, #c_vararg args: ..any) -> c.int ---
	// Call c_printf("C vararg int=%d double=%.2f\n", c.int(2026), c.double(3.5))
	// and print the returned character count with fmt.printfln.
}

main :: proc() {

	fmt.println("=== 1. C types and libc calls ===")
	c_types_and_libc_calls()

	fmt.println("\n=== 2. C strings and multi-pointers ===")
	cstrings_and_multi_pointers()

	fmt.println("\n=== 3. C varargs and link prefixes ===")
	variadics_and_link_prefix()
}
