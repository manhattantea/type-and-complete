// odin run 050_switch_and_partial.odin -file

package main

import "core:fmt"

/*
Odin's 'switch' removes C's most notorious switch footgun: silent fallthrough.
Every 'case' exits the switch automatically when its body finishes, so you never
write 'break' at the end of a case. If you actually want execution to continue
into the next case body, you ask for it explicitly with 'fallthrough'.

Switch cases also accept comma-separated values, inclusive ranges (such as
'0'..='9' or 500..=599), conditionless boolean cases, and compile-time
exhaustiveness checks on enums.

This file is split into three small sections called from main at the bottom so
you can read top to bottom and run the program at any point.
*/

Traffic_Light :: enum {
	Red,
	Yellow,
	Green,
}

value_ranges_and_fallthrough :: proc() {

	/*
	Notice how Odin formats switches under -strict-style: each 'case' label sits
	at the exact same indentation column as 'switch', keeping the block flat.

	Inside a switch, you can match single values, comma lists, inclusive ranges
	using ..=, and a bare 'case:' fallback (there is no 'default' keyword).
	When we write 'fallthrough' as the last statement of a case, Odin jumps
	unconditionally straight into the body of the very next case without testing
	that next case's pattern:

	    Suppose tier := 2:
	        switch tier {
	        case 2:
	            fmt.println("Editor")
	            fallthrough
	        case 1:
	            fmt.println("Viewer")
	        }
	        // prints Editor, then Viewer
	*/

	// Here is a basic value switch with a bare 'case:' fallback:

	status := 200
	switch status {
	case 200:
		fmt.println("Status 200: OK")
	case:
		fmt.println("Other status")
	}

	// Declare http_code := 503 and write a switch http_code matching:
	// - 200       -> print "OK"
	// - 301, 302  -> print "Redirect"
	// - 500..=599 -> print "Server Error"
	// - case:     -> print "Unknown Status"


	// Combine switch with an initialization statement just like 'if':
	// write switch code := 404; code { ... } handling 400..=499 ("Client Error")
	// and case: ("Other"), then verify code is out of scope after the closing }.


	// Practice explicit fallthrough for cascading permissions:
	// declare role_level := 2 and write a switch role_level with:
	// - case 3: print "Admin tools" then fallthrough
	// - case 2: print "Editor tools" then fallthrough
	// - case 1: print "Viewer tools"
	// - case:   print "Guest"
	// Run it with role_level = 2, then change it to 3 to verify the cascade.
}

tokenizer_ranges_and_conditionless_switch :: proc() {

	/*
	Because inclusive ranges work on characters and bytes too, 'switch' makes a
	clean, fast tokenizer without long chains of 'if ch >= ... && ch <= ...'.

	    Suppose ch := '7':
	        switch ch {
	        case '0'..='9':
	            fmt.println("Digit")
	        }

	When you omit the expression after 'switch' completely, each 'case' accepts
	any boolean condition and Odin evaluates them from top to bottom, stopping at
	the first match. That turns awkward if / else if ladders into an aligned
	decision table.
	*/

	// Here is a single-character switch preview:

	first_char := '7'
	switch first_char {
	case '0'..='9':
		fmt.printfln("'%c' is an ASCII digit", first_char)
	case:
		fmt.printfln("'%c' is not a digit", first_char)
	}

	// Build a tokenizer loop over sample := "a7+ \tZ":
	// iterate with for ch in sample and switch ch using:
	// - case '0'..='9':               -> print digit
	// - case 'a'..='z', 'A'..='Z':    -> print letter
	// - case '+', '-', '*', '/':      -> print operator
	// - case ' ', '\t':               -> print whitespace
	// - case:                         -> print unknown


	// Declare speed := 85 and write a conditionless switch { ... } with cases:
	// - case speed > 100: print "Excessive"
	// - case speed > 65:  print "Highway"
	// - case speed > 0:   print "City"
	// - case:             print "Parked"


	// Write a helper procedure above main named:
	// classify_char :: proc(ch: rune) -> string
	// Use a switch ch with '0'..='9' and 'a'..='z', 'A'..='Z' ranges, then call
	// classify_char on '9', 'm', and '#' here and print the results.
}

enums_and_partial_switch :: proc() {

	/*
	When switching on an 'enum', Odin knows every variant at compile time and
	forces you to handle all of them (or add a default 'case:'). That compiler
	check pays off later: if someone adds Traffic_Light.Flashing_Yellow next month,
	every plain switch on Traffic_Light flags a compile error until updated.

	Notice also that inside 'case .Red:', you can omit the enum type name and
	write the leading dot directly (implicit selector syntax).

	When we write '#partial switch' in front of an enum switch, it tells Odin
	"I intentionally only care about the cases listed here; skip the unhandled
	variant error".
	*/

	// Here is an exhaustive switch on Traffic_Light using implicit selectors:

	light := Traffic_Light.Yellow
	switch light {
	case .Red:
		fmt.println("Light: Stop")
	case .Yellow:
		fmt.println("Light: Caution")
	case .Green:
		fmt.println("Light: Go")
	}

	// Write a #partial switch light that only handles case .Yellow: and prints
	// "Yellow light check!".
	// Try temporarily deleting #partial to see Odin report the unhandled .Red
	// and .Green variants at compile time.


	// Define Packet_Kind :: enum { Ping, Data, Ack, Disconnect } above main.
	// Declare pkt := Packet_Kind.Data, write an exhaustive switch pkt covering
	// all four variants, then write a #partial switch pkt handling only
	// case .Ping, .Ack: to act as a heartbeat filter.


	// Practice an early 'break' inside a switch case:
	// unlike C where 'break' ends every case, in Odin 'break' inside a switch
	// exits the switch immediately when an inner guard fails.
	// Write a switch pkt where case .Data: declares payload_ok := false, runs
	// if !payload_ok do break, and puts fmt.println("Dispatching payload") after it
	// so you confirm the trailing line is skipped.
}

main :: proc() {

	fmt.println("=== 1. Values, ranges, and explicit fallthrough ===")
	value_ranges_and_fallthrough()

	fmt.println("\n=== 2. Tokenizer ranges and conditionless switch ===")
	tokenizer_ranges_and_conditionless_switch()

	fmt.println("\n=== 3. Exhaustive enums and #partial switch ===")
	enums_and_partial_switch()
}
