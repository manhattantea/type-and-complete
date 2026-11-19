// odin run 580_json_and_binary_serialization.odin -file

package main

import "core:encoding/endian"
import "core:encoding/json"
import "core:fmt"

/*
Real programs serialize data in two very different worlds: human-readable
configuration or save files (where flexibility and readability matter) and
compact binary wire packets (where exact byte order and zero heap allocations
matter). Odin's core library handles both directly.

For JSON, core:encoding/json walks Odin's built-in runtime type information
(RTTI) to read and write structs automatically without a code-generation step.
For binary protocols, core:encoding/endian reads and writes fixed-width integers
into byte slices with an explicit .Little or .Big byte order so your wire
format behaves identically on x86_64, ARM64, and big-endian network headers.
*/

Status_Ping :: struct {
	ok:   bool   `json:"ok"`,
	note: string `json:"note,omitempty"`,
}

// Define two JSON-serializable structs right here at file scope once you start
// the first section:
// Inventory_Item :: struct with fields:
// - name: string (tag json:"name")
// - qty: int (tag json:"qty")
// - equipped: bool (tag json:"equipped,omitempty")
// Save_Game :: struct with nested items:
// - player_name: string (tag json:"player")
// - level: int (tag json:"level")
// - coins: [3]int (tag json:"coins")
// - items: []Inventory_Item (tag json:"items")

json_marshaling_and_tags :: proc() {

	/*
	When we write a raw-string struct tag like json:"player" beside a struct
	field, it attaches compile-time metadata that core:encoding/json reads
	through reflection at runtime to rename the JSON key. Adding ,omitempty
	inside the tag tells json.marshal to skip that field whenever it holds its
	zero value (such as false, 0, "", or an empty slice).

	    Suppose Status_Ping{ok = true, note = ""} is marshaled:
	    Because note is "" and tagged with omitempty, the output is simply
	    {"ok":true} instead of {"ok":true,"note":""}.

	Notice that json.marshal(val, opt) allocates the resulting []byte slice on
	context.allocator and returns (data, err). Always check err != nil and
	register defer delete(data) so the serialized JSON buffer never leaks.
	*/

	ping := Status_Ping{ok = true}
	ping_bytes, ping_err := json.marshal(ping)
	if ping_err != nil {
		fmt.printfln("Marshal ping failed: %v", ping_err)
		return
	}
	defer delete(ping_bytes)
	fmt.printfln("Starter JSON ping: %s", string(ping_bytes))

	// After defining Inventory_Item and Save_Game at file scope, create a
	// Save_Game value with player_name = "Ada", level = 12, coins = {50, 10, 3},
	// and a slice of two Inventory_Item values (one with equipped = true, one
	// with equipped = false).


	// Marshal your Save_Game using:
	// data, err := json.marshal(save, {pretty = true})
	// Check if err != nil, register defer delete(data), and print string(data)
	// to verify nested objects appear under "items" and equipped = false is
	// omitted from the second item.
}

json_unmarshaling_and_ownership :: proc() {

	/*
	Going the other direction, json.unmarshal(json_bytes, &target) parses UTF-8
	JSON text into any typed Odin struct pointer. Because JSON strings and
	arrays can have arbitrary length at runtime, json.unmarshal allocates every
	decoded string and slice field onto context.allocator.

	    Suppose raw_json holds {"player":"Ada","items":[{"name":"Lantern","qty":1}]}:
	        loaded: Save_Game
	        err := json.unmarshal(raw_json, &loaded)
	    Here loaded.player_name and loaded.items (plus each item.name inside it)
	    are fresh heap allocations owned by the caller!

	In real apps, teams often pass context.temp_allocator or a mem.Arena to
	json.unmarshal so one free_all clears the entire decoded tree at once.
	When using the default heap allocator, free each decoded string and slice.
	*/

	sample_json := `{"ok":true,"note":"ready"}`
	decoded: Status_Ping
	err := json.unmarshal(transmute([]u8)sample_json, &decoded)
	if err != nil {
		fmt.printfln("Unmarshal ping failed: %v", err)
		return
	}
	defer delete(decoded.note)
	fmt.printfln("Decoded ping: ok=%v, note=%s", decoded.ok, decoded.note)

	// Unmarshal a raw JSON Save_Game string literal (or the bytes you marshaled
	// in section 1 if moved to a shared helper) into a fresh loaded: Save_Game
	// via json.unmarshal(raw_bytes, &loaded). Check u_err != nil and print
	// loaded.player_name, loaded.level, and each item in loaded.items.


	// Register clean heap cleanup for loaded:
	// delete(loaded.player_name), loop over loaded.items deleting each
	// item.name, and delete(loaded.items).


	// Test error handling by passing malformed JSON such as '{"level":' into
	// json.unmarshal and printing the returned Unmarshal_Error value.
}

binary_wire_endianness :: proc() {

	/*
	Text formats like JSON require parsing quotes, whitespace, and decimal
	digits on every read. Network packets and binary file formats instead pack
	integers straight into fixed byte arrays at known offsets with zero heap
	allocations.

	The catch is byte order (endianness). Suppose you store the 32-bit hex
	value 0x12345678 into a 4-byte slice buf[:]:
	    .Little (x86_64/ARM64 native): bytes are [0x78, 0x56, 0x34, 0x12]
	    .Big    (network byte order):  bytes are [0x12, 0x34, 0x56, 0x78]

	core:encoding/endian gives you explicit put_* and get_* procedures that
	both take a byte slice and a Byte_Order (.Little or .Big) and return a
	bool indicating whether the slice was large enough. Always check that bool
	to guard against truncated packets without panicking!
	*/

	magic_buf: [4]u8
	write_ok := endian.put_u32(magic_buf[:], .Big, 0x4F44494E)
	decoded_magic, read_ok := endian.get_u32(magic_buf[:], .Big)
	fmt.printfln("Wire magic=%s (0x%08X) write_ok=%v read_ok=%v",
		string(magic_buf[:]), decoded_magic, write_ok, read_ok)

	// Encode val := u32(0x12345678) into a buf: [4]u8 first with .Little
	// using endian.put_u32(buf[:], .Little, val), print each byte in hex
	// (%02X), and decode it back with endian.get_u32(buf[:], .Little). Repeat
	// with .Big on the same buffer to compare the reversed byte order.


	// Pack and unpack a 12-byte multi-field binary wire packet into pkt: [12]u8
	// using .Big byte order:
	// - pkt[0:4]:  magic       = u32(0x4F44494E) via endian.put_u32
	// - pkt[4:6]:  version     = u16(3)          via endian.put_u16
	// - pkt[6:8]:  flags       = u16(0x0005)     via endian.put_u16
	// - pkt[8:12]: payload_len = u32(1024)       via endian.put_u32
	// Check every write ok bool, then decode all four fields back using
	// endian.get_u32 and endian.get_u16 and print the parsed header.


	// Verify bounds protection on truncated input: pass pkt[0:2] into
	// endian.get_u32(pkt[0:2], .Big) and confirm ok == false cleanly without
	// crashing or reading out of bounds.
}

main :: proc() {

	fmt.println("=== 1. JSON marshaling and struct tags ===")
	json_marshaling_and_tags()

	fmt.println("\n=== 2. JSON unmarshaling and memory ownership ===")
	json_unmarshaling_and_ownership()

	fmt.println("\n=== 3. Binary wire packets and endianness ===")
	binary_wire_endianness()
}
