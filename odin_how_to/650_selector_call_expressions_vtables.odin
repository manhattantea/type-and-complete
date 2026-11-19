// odin run 650_selector_call_expressions_vtables.odin -file

package main

import "core:fmt"

/*
Odin intentionally keeps data and behavior separate: structs do not have
methods, and everyday functions are free-standing procedures taking structs
explicitly (update_player(&player, dt)).

When you interoperate with C/COM APIs, plugin interfaces, or dynamic vtables,
however, structs store procedure pointers as fields. To keep those call sites
readable, Odin provides the selector call operator '->':

    x->proc_field(args)      rewrites to  x.proc_field(x, args)
    (&x)->proc_field(args)   rewrites to  x.proc_field(&x, args)

When your set of variants is fixed at compile time, prefer a tagged 'union' and
'switch'. Reserve '->' vtable structs for open plugin boundaries and C FFI.
*/

Formatter_Plugin :: struct {
	prefix: string,
	format: proc(self: Formatter_Plugin, msg: string) -> string,
}

// Define Counter_Plugin :: struct with fields:
// count: int, step: int, add: proc(self: ^Counter_Plugin, n: int), and
// reset: proc(self: ^Counter_Plugin).
// You can supply inline proc literals when constructing Counter_Plugin or
// write helper procedures counter_add and counter_reset at file scope.

selector_call_basics :: proc() {

	/*
	Notice why '(&plugin)->add(5)' needs '&plugin': Counter_Plugin's add field
	expects 'self: ^Counter_Plugin' so it can mutate count in place. Putting
	'&' on the receiver passes the struct's pointer as the first argument.
	*/

	anchor_plugin := Formatter_Plugin{
		prefix = "[INFO]",
		format = proc(self: Formatter_Plugin, msg: string) -> string {

			return fmt.tprintf("%s %s", self.prefix, msg)
		},
	}
	fmt.printfln("Starter selector call: %s", anchor_plugin->format("vtable ready"))

	// Instantiate plugin := Counter_Plugin{count = 0, step = 2, add = ..., reset = ...}
	// where add adds n * self.step to self.count and reset sets self.count = 0.
	// Call (&plugin)->add(5) and (&plugin)->add(3), print plugin.count
	// (expected: 16), then call (&plugin)->reset() and print plugin.count (0).


	// Try uncommenting below to confirm calling plugin->add(1) without '&'
	// fails when the procedure field expects ^Counter_Plugin:
	// plugin->add(1)
}

// Define a base vtable struct and two concrete plugin structs that embed it at
// offset 0 using 'using base: Plugin':
// Plugin :: struct { name: string, apply: proc(self: ^Plugin, value: int) -> int }
// Add_Plugin :: struct { using base: Plugin, delta: int }
// Mul_Plugin :: struct { using base: Plugin, factor: int }
//
// Write add_plugin_apply :: proc(self: ^Plugin, value: int) -> int and
// mul_plugin_apply :: proc(self: ^Plugin, value: int) -> int that cast
// '(^Add_Plugin)(self)' or '(^Mul_Plugin)(self)' to read delta or factor.

heterogeneous_vtable_slice :: proc() {

	/*
	Placing 'using base: Plugin' as the very first field of Add_Plugin and
	Mul_Plugin puts the Plugin header at byte offset 0. That lets a single
	heterogeneous slice '[]^Plugin{&adder.base, &muller.base}' store pointers
	to completely different concrete structs and dispatch 'p->apply(10)' through
	one uniform loop—the same C-style pattern used by Odin's Allocator and
	io.Stream interfaces.
	*/

	fmt.printfln("Starter Formatter_Plugin size: %d bytes", size_of(Formatter_Plugin))

	// Instantiate an Add_Plugin (delta = 5) and a Mul_Plugin (factor = 3),
	// pack their base pointers into plugins := []^Plugin{&adder.base, &muller.base},
	// loop for p in plugins, and print p.name alongside p->apply(10)
	// (expected: 15 and 30).


	// Chain the plugins sequentially by feeding value := 4 through each p in
	// plugins (value = p->apply(value)) and printing the final result.
}

main :: proc() {

	fmt.println("=== 1. Selector call basics ===")
	selector_call_basics()

	fmt.println("\n=== 2. Heterogeneous vtable slice ===")
	heterogeneous_vtable_slice()
}
