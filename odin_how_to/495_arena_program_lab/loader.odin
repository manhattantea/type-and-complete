package main

import "core:fmt"
import "core:strings"
import "base:runtime"

/*
loader.odin parses compact level strings such as:
    "Entrance:1,2;Great Hall:0,3;Armory:0"

Notice how two distinct allocators partition lifetimes cleanly here:
    scratch_alloc   holds temporary strings.split slices (on ";", ":", ",")
                    that are discarded right after parsing finishes.
    level_alloc     holds ONLY persistent data returned inside Level ([]Room,
                    strings.clone(name_str, level_alloc), and []int connections).

Separating errors with a Load_Error enum ensures malformed lines (empty input,
missing ":", or invalid/out-of-range connection indices) propagate cleanly
without leaking half-built temporary slices.
*/

Load_Error :: enum {
	None,
	Empty_Input,
	Missing_Colon,
	Invalid_Connection_Index,
}

log_loader_contract :: proc(raw_text: string, level_alloc, scratch_alloc: runtime.Allocator) {

	trimmed := strings.trim_space(raw_text)
	fmt.printfln("Loader contract ready for %d bytes (level_alloc=%p, scratch_alloc=%p)", len(trimmed), level_alloc.procedure, scratch_alloc.procedure)
}

// Implement parse_level_line with explicit error propagation (add import "core:strconv" above):
// @(require_results) parse_level_line :: proc(raw_text: string, level_alloc, scratch_alloc: runtime.Allocator) -> (lvl: Level, err: Load_Error)
//
// Suppose raw_text is "Entrance:1;Hall:0":
//   - Trim whitespace with strings.trim_space(raw_text); if len(trimmed) == 0,
//     return {}, .Empty_Input.
//   - Split trimmed on ";" into temporary room tokens using
//     room_tokens, split_err := strings.split(trimmed, ";", scratch_alloc).
//     (Check split_err != nil and propagate or handle it cleanly.)
//   - Allocate rooms := make([]Room, len(room_tokens), level_alloc).
//   - For each room_tokens[i], split on ":" using scratch_alloc. If len(parts) != 2
//     or len(strings.trim_space(parts[0])) == 0, return {}, .Missing_Colon.
//   - Clone the room name into persistent level memory with
//     strings.clone(strings.trim_space(parts[0]), level_alloc).
//   - If parts[1] is non-empty, split it on "," using scratch_alloc, allocate
//     connections := make([]int, len(conn_tokens), level_alloc), parse each
//     integer with strconv.parse_int(strings.trim_space(conn_tokens[j])), and
//     validate ok && conn_idx >= 0 && conn_idx < len(room_tokens) (otherwise
//     return {}, .Invalid_Connection_Index).
//   - Populate rooms[i] and return Level{rooms = rooms}, .None.
//
// Also test malformed input behavior: suppose raw_text is "BrokenRoomWithoutColon"
// (missing ":") -> parse_level_line returns .Missing_Colon; suppose raw_text is
// "Entrance:99" (out of bounds) or "Entrance:abc" -> returns .Invalid_Connection_Index.
