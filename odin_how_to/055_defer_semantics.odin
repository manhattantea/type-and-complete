// odin run 055_defer_semantics.odin -file

package main

import "core:fmt"

/*
'defer' schedules a statement or '{ ... }' block to run automatically whenever
control leaves the current scope.

If you come from Go, pay close attention to Odin's two golden rules for defer.
First, defer is block-scoped, not procedure-scoped: in Go, 'defer' waits until
the entire function returns, whereas in Odin it runs at the closing '}' of the
immediate enclosing '{ ... }' block—whether that block is a procedure, an
anonymous '{ ... }' scope, an 'if' body, or a single pass of a 'for' loop.
Second, multiple defers in the same block execute in LIFO (Last-In, First-Out)
order—reverse registration order—so newer dependent resources clean up first.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

block_scope_and_lifo :: proc() {

	/*
	When you open resource A and then open resource B (which uses A), B must be
	torn down before A. Executing defers in reverse registration order guarantees
	this automatically:

	    Suppose inside an inner block you write:
	        {
	            defer fmt.println("First")
	            defer fmt.println("Second")
	            fmt.println("Body")
	        }
	        fmt.println("After")

	    Output is: Body -> Second -> First -> After. Notice that both defers
	    finish at the inner '}' before "After" runs!
	*/

	// Here is a procedure-scoped defer that runs when block_scope_and_lifo exits:

	defer fmt.println("[section exit] Starter defer fired at end of block_scope_and_lifo")
	fmt.println("[section start] Inside block_scope_and_lifo")

	// Open an inner { ... } block to observe block-scoped LIFO order:
	// inside it, register three defer fmt.println calls labeled "First", "Second",
	// and "Third", then print "Body". Right after the closing }, print "After block".
	// Confirm the output prints Body -> Third -> Second -> First -> After block.


	// Practice a multi-statement defer block:
	// open an inner { ... } block, print "Opening file", register:
	// defer { fmt.println("Flushing buffer"); fmt.println("Closing file") }
	// then print "Writing bytes" and verify both lines in the defer block run
	// together when the inner block ends.


	// Model paired resource cleanup in an inner { ... } block:
	// print "Acquire Handle" paired with defer fmt.println("Release Handle"),
	// then print "Lock Mutex" paired with defer fmt.println("Unlock Mutex"),
	// then print "Working...". Verify Mutex unlocks before Handle releases.
}

loop_body_defer_and_lifo :: proc() {

	/*
	Because defer belongs to its immediate '{ ... }' block, putting 'defer' inside
	a loop body makes it run at the end of EVERY iteration—even if that pass
	hits 'continue' or 'break'.

	    Suppose for i in 0..<2 {
	        defer fmt.printfln("cleanup %v", i)
	        fmt.printfln("work %v", i)
	    }
	    // prints: work 0, cleanup 0, work 1, cleanup 1

	Multiple defers inside a loop body also unwind in LIFO order per iteration.
	And remember: defer evaluates expressions when the block exits, not when the
	defer line is registered.
	*/

	// Here is a quick 2-pass loop showing per-iteration defer cleanup:

	for pass in 0..<2 {
		defer fmt.printfln("  pass %v finished", pass)
		fmt.printfln("  pass %v running", pass)
	}

	// Test loop-body defer LIFO across continue and break:
	// write for step in 0..<4 and register two defers at the top of the loop:
	// defer fmt.printfln("close A (%v)", step)
	// defer fmt.printfln("close B (%v)", step)
	// Skip step == 1 with: if step == 1 do continue
	// Exit at step == 3 with: if step == 3 do break
	// Print fmt.printfln("body (%v)", step) below those checks.
	// Confirm close B always prints before close A on every pass, including 1 and 3.


	// Practice placing a counter update in defer to avoid infinite-loop continue bugs:
	// declare attempt := 0 and loop while attempt < 5:
	// put defer attempt += 1 on the very first line inside the loop body,
	// skip even attempts with: if attempt % 2 == 0 do continue
	// print odd attempts, then print attempt after the loop (expected: 5).


	// Verify exit-time evaluation:
	// open an inner { ... } block, declare label := "initial",
	// register defer fmt.println("deferred label =", label),
	// then reassign label = "updated" before the block closes.
	// Notice it prints "updated", proving defer reads label at block exit.
}

conditional_rollback_with_defer_if :: proc() {

	/*
	When we write 'defer if failed { ... }', the entire 'if' statement is what
	gets deferred. Because defer runs at block exit, 'failed' is inspected at the
	end of the scope rather than when the defer line is reached.

	This lets you place error-rollback logic right next to setup code and flip a
	single 'committed = true' flag at the bottom of the happy path.
	*/

	// Here is a short block showing a quiet happy-path defer if check:

	{
		had_error := false
		defer if had_error do fmt.println("Rollback triggered!")
		fmt.println("Happy path completed without rollback")
	}

	// Open an inner { ... } block, declare transaction_failed := false,
	// register defer if transaction_failed { fmt.println("Rolling back transaction!") },
	// print "Applying changes...", and set transaction_failed = true before the }
	// to watch the deferred rollback fire at scope exit.


	// Write a helper procedure above main named:
	// run_job :: proc(should_fail: bool) -> bool
	// Inside run_job, declare committed := false and register:
	// defer if !committed { fmt.println("Job aborted: cleaning temp state") }
	// If should_fail is true, return false early (rollback fires!).
	// Otherwise set committed = true and return true (rollback skipped!).
	// Call both run_job(true) and run_job(false) here and print their returns.


	// Combine defer with a labeled block exit:
	// write step: if true { ... } with a defer fmt.println("step cleanup") inside,
	// then exit early using break step before a trailing print line to verify
	// defer still executes when breaking out of a labeled block.
}

main :: proc() {

	fmt.println("=== 1. Block scope and LIFO order ===")
	block_scope_and_lifo()

	fmt.println("\n=== 2. Loop-body defer and LIFO per pass ===")
	loop_body_defer_and_lifo()

	fmt.println("\n=== 3. Conditional rollback with defer if ===")
	conditional_rollback_with_defer_if()
}
