// odin run 180_deferred_procedure_attributes.odin -file

package main

import "core:fmt"

/*
C++ relies on hidden constructor and destructor calls (RAII) for scope guards,
which obscures where cleanup runs. Odin keeps cleanup explicit with 'defer',
but requiring every caller to remember 'defer unlock(&mu)' after 'lock(&mu)' is
still easy to forget.

Odin bridges both worlds with deferred procedure attributes ('@(deferred_...)').
When we attach '@(deferred_in=end_fn)' or '@(deferred_out=end_fn)' to an entry
procedure, it tells the compiler to automatically insert 'defer end_fn(...)' in
the caller's scope right after calling the entry procedure. Cleanup still runs
deterministically when the caller's enclosing '{ ... }' block exits (not only
at function return), with zero hidden object lifetimes:
- '@(deferred_in = exit_proc)' forwards the entry procedure's input arguments.
- '@(deferred_none = exit_proc)' calls 'exit_proc()' with zero arguments.
- '@(deferred_out = exit_proc)' forwards the entry procedure's return values.
- '@(deferred_in_out = exit_proc)' forwards inputs first, then return values.
*/

end_banner :: proc(tag: string) {

	fmt.printfln("[end] %v", tag)
}

@(deferred_in = end_banner)
begin_banner :: proc(tag: string) {

	fmt.printfln("[begin] %v", tag)
}

deferred_in_and_none :: proc() {

	/*
	Suppose you call 'begin_banner("demo")' at the start of a '{ ... }' block.
	Because 'begin_banner' carries '@(deferred_in = end_banner)', the compiler
	rewrites that call site as:
	    begin_banner("demo")
	    defer end_banner("demo")

	When execution reaches the closing brace '}' of that block, 'end_banner("demo")'
	runs automatically with the exact same argument passed to 'begin_banner'.
	When an exit helper needs no arguments at all, '@(deferred_none = cleanup)'
	emits 'defer cleanup()' instead.
	*/

	{
		begin_banner("demo")
		fmt.println("inside demo block")
	}
	fmt.println("after demo block")

	// Define 'Fake_Mutex :: struct { name: string, locked: bool }' at file scope,
	// along with 'unlock_mutex :: proc(m: ^Fake_Mutex)' (sets 'm.locked = false'
	// and prints an unlock message) and '@(deferred_in = unlock_mutex) lock_mutex :: proc(m: ^Fake_Mutex)'
	// (sets 'm.locked = true' and prints a lock message).


	// Declare 'mu := Fake_Mutex{name = "audio"}', open an inner '{ ... }' block,
	// call 'lock_mutex(&mu)', print 'mu.locked' inside (expected: true), and print
	// 'mu.locked' right after the closing brace '}' (expected: false).


	// Write 'end_batch :: proc()' (zero parameters) and attach
	// '@(deferred_none = end_batch)' to 'begin_batch :: proc(batch_id: int)'.
	// Call 'begin_batch(42)' inside a small '{ ... }' block and observe
	// 'end_batch()' firing automatically on block exit.
}

deferred_out_scope_tokens :: proc() {

	/*
	Sometimes the cleanup procedure needs state produced inside the entry
	procedure—such as a start timestamp, an arena checkpoint, or a token struct—
	that did not exist in the caller's arguments. Attaching '@(deferred_out = exit_proc)'
	tells Odin to pass the entry procedure's return value(s) into 'exit_proc'.

	    Suppose 'tok := start_work("mesh")' returns a 'Scope_Token':
	    the compiler inserts 'defer stop_work(tok)' right at the call site.
	    Even if you discard the return value by calling 'start_work("mesh")'
	    without assigning it, Odin still captures the returned token in a hidden
	    temporary and hands it to 'stop_work' when the enclosing block exits!
	*/

	fmt.println("deferred_out forwards return values from entry to exit automatically.")

	// Define 'Scope_Token :: struct { name: string, depth: int }' and
	// 'end_profile_scope :: proc(tok: Scope_Token)' (prints "[END] %v (depth %v)")
	// at file scope.


	// Write '@(deferred_out = end_profile_scope) profile_scope :: proc(name: string, depth: int) -> Scope_Token'
	// that prints "[BEGIN] %v (depth %v)" and returns 'Scope_Token{name = name, depth = depth}'.


	// Call 'profile_scope("outer", 1)' at the top of this procedure, then open a
	// nested '{ ... }' block calling 'profile_scope("inner", 2)'. Print a status
	// line inside and after the nested block to confirm '[END] inner' runs at
	// the inner '}' while '[END] outer' waits for this procedure to exit.
	// Also test calling 'profile_scope("first", 1)' and 'profile_scope("second", 2)'
	// in the same block to observe LIFO teardown order.
}

deferred_in_out_pairing :: proc() {

	/*
	When cleanup needs both the caller's original input parameters (such as a
	pointer to mutate or a label to log) AND a value returned by the entry
	procedure (such as the previous state to restore), use '@(deferred_in_out = exit_proc)'.

	The exit procedure signature must list all input parameters of the entry
	procedure first in exact order, followed immediately by all return values of
	the entry procedure.

	    Suppose 'push_indent :: proc(depth: ^int, label: string) -> (prev: int)':
	    then 'pop_indent' must have signature 'proc(depth: ^int, label: string, prev: int)'.
	*/

	fmt.println("deferred_in_out forwards inputs first, followed by return values.")

	// Define 'pop_indent :: proc(depth: ^int, label: string, prev: int)' at file
	// scope that prints leaving 'label' and restores 'depth^ = prev'. Then write
	// '@(deferred_in_out = pop_indent) push_indent :: proc(depth: ^int, label: string) -> (prev: int)'
	// that captures 'prev = depth^', increments 'depth^ += 1', prints entering
	// 'label' at the new depth, and returns 'prev'.


	// Declare 'indent := 0', call 'push_indent(&indent, "scene")', then open an
	// inner '{ ... }' block calling 'push_indent(&indent, "entities")' and print
	// 'indent' inside (expected: 2) and after the inner block closes (expected: 1).
	//
	// Try swapping 'prev: int' before 'depth: ^int' in 'pop_indent' to observe the
	// compiler's signature-order check for '@(deferred_in_out)'.
}

main :: proc() {

	fmt.println("=== 1. @(deferred_in) and @(deferred_none) ===")
	deferred_in_and_none()

	fmt.println("\n=== 2. @(deferred_out) scope tokens ===")
	deferred_out_scope_tokens()

	fmt.println("\n=== 3. @(deferred_in_out) state save and restore ===")
	deferred_in_out_pairing()
}
