// odin run 910_custom_hash_table.odin -file

package main

import "core:fmt"
import "core:hash"
import "core:mem"

/*
Odin ships a built-in 'map[K]V' type, yet building an open-addressed hash table
from scratch pulls together nearly every systems skill in the language:
parametric polymorphism ('$K, $V: typeid'), explicit 'mem.Allocator' tracking,
FNV-1a byte hashing, power-of-2 bitmask indexing, linear probing with
tombstones, and load-factor resizing.

Why open addressing with tombstones? In a flat contiguous slice of slots,
looking up a key hashes straight to a starting index and walks forward slot by
slot until finding the key or hitting an '.Empty' slot. If deleting an item
reset its slot straight back to '.Empty', any key that collided earlier and
landed further down the probe chain would suddenly become unreachable! Marking
deleted slots as '.Tombstone' keeps probe chains intact while allowing new
inserts to reuse the vacated slot.
*/

Slot_State :: enum u8 {
	Empty,
	Occupied,
	Tombstone,
}

// Define these two polymorphic structs at file scope before writing table procs:
// Entry($K, $V: typeid) :: struct { key: K, val: V, state: Slot_State }
// Table($K, $V: typeid) :: struct { entries: []Entry(K, V), count: int, allocator: mem.Allocator }

hashing_and_power_of_two_masking :: proc() {

	/*
	A hash table turns an arbitrary key into a bucket index in two steps: hash
	the key's bytes into a 64-bit integer, then wrap that integer into
	'0..<cap'.

	For 'string' keys, be careful not to hash the 'string' struct header itself!
	A 'string' in Odin is 16 bytes ('data' pointer + 'len'). Hashing the header
	would hash the memory address rather than the characters, so two equal
	strings at different addresses would produce different hashes! Passing
	'transmute([]u8)key' hands 'hash.fnv64a' the actual character bytes. For
	plain value types like 'int' or structs, copying 'k := key' into a local
	variable lets 'mem.ptr_to_bytes(&k)' expose its raw stack bytes safely.

	Next comes wrapping the 64-bit hash into '0..<cap'. Integer modulo ('%')
	uses a slow hardware division instruction, whereas masking 'int(h) & (cap - 1)'
	runs in a single cycle — provided 'cap' is a power of 2!
	Suppose someone initializes a table with capacity 10 instead of 16. Because
	'10 - 1' is 9 (binary 0b1001), 'int(h) & 9' can only ever yield 0, 1, 8, or 9,
	leaving slots 2..=7 permanently unreachable and causing an infinite probe loop
	once 4 keys are inserted! Rounding every requested capacity up with a
	'next_pow2' helper guarantees 'cap - 1' is always an all-ones bitmask.
	*/

	// Live preview of string byte hashing, value byte hashing, and bitmasking:

	key_text := "alpha"
	str_hash := hash.fnv64a(transmute([]u8)key_text)
	id := 42
	id_hash := hash.fnv64a(mem.ptr_to_bytes(&id))
	cap := 8
	fmt.printfln("hash(%q)=0x%x -> slot %d | hash(%d)=0x%x -> slot %d", key_text, str_hash, int(str_hash) & (cap - 1), id, id_hash, int(id_hash) & (cap - 1))

	// Write a power-of-2 capacity rounding helper at file scope:
	// next_pow2 :: proc(n: int) -> int
	// Start with cap := 8 and double it (cap *= 2 or cap <<= 1) while cap < n,
	// returning cap. Test it on 0, 8, 10, and 17 to confirm it yields 8, 8, 16, 32.
	//
	// Write a generic hash helper at file scope:
	// hash_key :: proc(key: $K) -> u64
	// Use compile-time branching: when K == string { return hash.fnv64a(transmute([]u8)key) }
	// In the else branch, copy k := key and return hash.fnv64a(mem.ptr_to_bytes(&k)).
}

open_addressing_and_tombstones :: proc() {

	/*
	Once capacity is guaranteed to be a power of 2, probing forward wraps around
	the end of the slice cheaply: 'idx = (idx + 1) & mask' where
	'mask := len(t.entries) - 1'.

	Suppose keys A and B both hash to slot 3 in an 8-slot table. Key A lands at
	slot 3 ('.Occupied'), and key B probes to slot 4 ('.Occupied'). If you later
	delete key A and set slot 3 to '.Tombstone', looking up key B still starts at
	slot 3, sees '.Tombstone' instead of '.Empty', keeps probing to slot 4, and
	finds B! Meanwhile, inserting a new key C remembers the first '.Tombstone' it
	crossed at slot 3 so it can reuse that slot if C is not already present
	further down the chain.
	*/

	// Live reference to all three Slot_State enum values:

	sample_slots := [3]Slot_State{.Empty, .Occupied, .Tombstone}
	fmt.printfln("Slot lifecycle states: %v", sample_slots)

	// Write table lifecycle and lookup procedures at file scope:
	// table_init :: proc(t: ^Table($K, $V), initial_cap := 16, allocator := context.allocator)
	// Round initial_cap with cap := next_pow2(initial_cap), store t.allocator,
	// allocate t.entries = make([]Entry(K, V), cap, allocator), and zero t.count.
	//
	// table_destroy :: proc(t: ^Table($K, $V))
	// Free t.entries with delete(t.entries, t.allocator) and reset t^ = {}.
	//
	// table_get :: proc(t: ^Table($K, $V), key: K) -> (val: V, ok: bool)
	// Return {}, false if len(t.entries) == 0. Otherwise probe up to len(t.entries)
	// steps from int(hash_key(key)) & mask: stop with {}, false on .Empty, skip
	// .Tombstone, and return e.val, true when .Occupied && e.key == key.
	//
	// table_remove :: proc(t: ^Table($K, $V), key: K) -> bool
	// Probe in the same way; on match, set entry.state = .Tombstone, decrement
	// t.count -= 1, and return true (or false if .Empty is reached).
}

load_factor_and_resizing :: proc() {

	/*
	Linear probing slows down sharply as the table fills up because probe chains
	merge into long clusters. Keeping occupancy at or below 70 percent ensures
	short average probes. Using integer arithmetic avoids floating-point rounding:
	'(t.count + 1) * 10 >= len(t.entries) * 7' checks whether adding one more key
	would reach 70 percent.

	When resizing, you cannot copy the old slice directly into a larger buffer
	because 'mask := len(t.entries) - 1' changed — every key's home slot depends
	on the new mask! Allocating a fresh zeroed slice of length 'new_cap',
	resetting 't.count = 0', re-inserting only '.Occupied' slots via 'table_put',
	and deleting 'old_entries' both re-hashes every key to its new bucket and
	purges every accumulated '.Tombstone' automatically.
	*/

	// Quick integer load-factor check for 5 items in an 8-slot table:

	count := 5
	cap := 8
	needs_grow := (count + 1) * 10 >= cap * 7
	fmt.printfln("At %d/%d occupancy, adding 1 item triggers resize: %v", count, cap, needs_grow)

	// Write resizing and insertion at file scope:
	// table_resize :: proc(t: ^Table($K, $V), new_cap: int)
	// Save old_entries := t.entries, allocate t.entries = make([]Entry(K, V), next_pow2(new_cap), t.allocator),
	// reset t.count = 0, re-insert every .Occupied entry with table_put, and call
	// delete(old_entries, t.allocator).
	//
	// table_put :: proc(t: ^Table($K, $V), key: K, val: V)
	// Call table_init(t) lazily when len(t.entries) == 0, and call
	// table_resize(t, len(t.entries) * 2) when (t.count + 1) * 10 >= len(t.entries) * 7.
	// When probing, record first_tombstone := -1 on the first .Tombstone seen,
	// update in place if an .Occupied slot matches key, and only insert into
	// first_tombstone (or the .Empty slot) once you know key is not further down!
}

tracking_allocator_verification :: proc() {

	/*
	Because 'Table' allocates its backing slice through an explicit
	'mem.Allocator', wrapping 'context.allocator' in 'mem.Tracking_Allocator'
	proves immediately whether 'table_resize' and 'table_destroy' free every
	single allocation without leaking old backing buffers.
	*/

	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	defer mem.tracking_allocator_destroy(&track)
	context.allocator = mem.tracking_allocator(&track)

	probe_buf := make([]u8, 16)
	delete(probe_buf)
	fmt.printfln("Tracking allocator active (open allocations after probe cleanup: %d)", len(track.allocation_map))

	// Using this tracked context.allocator:
	// Declare scores: Table(string, int), call table_init(&scores, 10) to verify
	// next_pow2 rounds 10 up to 16, and register defer table_destroy(&scores).
	// Loop i in 0..<20 inserting fmt.tprintf("player_%d", i) -> i * 10, then
	// call free_all(context.temp_allocator) and print scores.count and len(scores.entries).
	// Look up an existing key and a missing key using table_get(&scores, "player_3") or_else -1
	// and table_get(&scores, "missing") or_else -1, remove 3 keys with table_remove,
	// verify removed keys return false while remaining keys still resolve,
	// destroy scores, and assert len(track.allocation_map) == 0.
}

main :: proc() {

	fmt.println("=== 1. Hashing and power-of-2 bitmasking ===")
	hashing_and_power_of_two_masking()

	fmt.println("\n=== 2. Open addressing and tombstones ===")
	open_addressing_and_tombstones()

	fmt.println("\n=== 3. Load factor and resizing ===")
	load_factor_and_resizing()

	fmt.println("\n=== 4. Tracking allocator verification ===")
	tracking_allocator_verification()
}
