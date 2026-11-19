// odin run 920_json_task_tracker_cli.odin -file

package main

import "core:encoding/json"
import "core:fmt"
import "core:mem/virtual"
import "core:os"
import "core:strconv"
import "core:strings"

/*
Building a persistent CLI tool brings together virtual arenas, JSON
reflection, file I/O, and argument parsing. Notice why 'virtual.Arena' pairs so
cleanly with 'core:encoding/json': unmarshaling an array of structs allocates a
fresh string on the heap for every single 'title' field, plus the backing buffer
of '[dynamic]Task'. When you install 'virtual.arena_allocator(&arena)' as
'context.allocator', every string and array growth goes into one contiguous
virtual region, so 'defer virtual.arena_destroy(&arena)' frees the entire
program's dynamic data in O(1) at exit without per-task cleanup loops.
*/

Task_Status :: enum {
	Todo,
	Done,
}

Task :: struct {
	id:     int         `json:"id"`,
	title:  string      `json:"title"`,
	status: Task_Status `json:"status"`,
	done:   bool        `json:"done"`,
}

arena_backed_allocator_setup :: proc() {

	/*
	When we call 'virtual.arena_init_growing(&arena)', Odin asks the operating
	system to reserve virtual address space and commits physical pages only as
	allocations grow. Assigning 'context.allocator = virtual.arena_allocator(&arena)'
	redirects all downstream heap calls — including 'strings.clone', 'append',
	and 'json.unmarshal' — straight into that arena without altering any helper
	signature.

	Suppose a task title is cloned from a temporary buffer inside a helper. If
	that arena sits in 'main' with 'defer virtual.arena_destroy(&arena)', the
	title stays valid for the whole program and disappears cleanly at return.
	Conversely, never destroy an arena inside a helper that still returns a
	slice or string allocated from it!
	*/

	arena: virtual.Arena
	if err := virtual.arena_init_growing(&arena); err != .None {
		fmt.eprintfln("Failed to initialize virtual arena: %v", err)
		return
	}
	defer virtual.arena_destroy(&arena)

	context.allocator = virtual.arena_allocator(&arena)
	cloned := strings.clone("Arena-owned task title")
	fmt.printfln("Arena allocation active: %q", cloned)

	// Move this growing virtual.Arena setup into your main task runner so every
	// unmarshaled string, dynamic array growth, and cloned title lives inside
	// one arena freed at exit.
}

json_persistence_layer :: proc() {

	/*
	Odin's 'core:encoding/json' inspects struct fields and 'json:"..."' tags at
	runtime via RTTI. Calling 'json.marshal(tasks, json.Marshal_Options{pretty = true})'
	produces indented JSON bytes, and 'json.unmarshal(raw, &tasks)' populates a
	'[dynamic]Task' directly.

	When loading from disk, a missing database file on the very first run is not
	an error — checking 'if !os.exists(path)' lets 'load_tasks' return an empty
	list and 'true' immediately. If the file does exist, 'os.read_entire_file(path) or_return'
	unwraps the '(raw, ok)' pair and returns 'false' cleanly whenever the read
	fails.
	*/

	sample := Task{id = 1, title = "Inspect JSON schema", status = .Todo, done = false}
	encoded, marshal_err := json.marshal(sample, json.Marshal_Options{pretty = true})
	if marshal_err == nil {
		defer delete(encoded)
		fmt.printfln("Sample JSON (%d bytes, temp_tasks.json exists=%v):\n%s", len(encoded), os.exists("temp_tasks.json"), string(encoded))
	}

	// Write these two persistence procedures at file scope:
	// load_tasks :: proc(path: string) -> (tasks: [dynamic]Task, ok: bool)
	// Return tasks, true immediately if !os.exists(path). Otherwise read raw bytes
	// with raw := os.read_entire_file(path) or_return, unmarshal into &tasks via
	// err := json.unmarshal(raw, &tasks), and return tasks, err == nil.
	//
	// save_tasks :: proc(path: string, tasks: []Task) -> bool
	// Marshal tasks with json.Marshal_Options{pretty = true}, return false if
	// marshal_err != nil, and return os.write_entire_file(path, bytes).
}

task_commands_and_mutations :: proc() {

	/*
	Keep two Odin value-semantics rules in mind when mutating tasks:
	First, appending to a dynamic array can reallocate its backing buffer, so
	'cmd_add' must take a pointer 'tasks: ^[dynamic]Task'.
	Second, looping with 'for t in tasks' gives you a read-only copy of each
	'Task'! Writing 't.done = true' would not compile (or if copied to a local,
	would leave the array untouched). Using 'for &t in tasks' binds 't' directly
	to each element slot inside the slice so setting 't.done = true' and
	't.status = .Done' mutates the stored task in place.
	*/

	demo_list: [dynamic]Task
	defer delete(demo_list)
	append(&demo_list, Task{id = 1, title = "Initial task", status = .Todo, done = false})
	for &t in demo_list {
		t.status = .Done
		t.done = true
	}
	fmt.printfln("In-place task mutation preview: #%d %q (%v)", demo_list[0].id, demo_list[0].title, demo_list[0].status)

	// Write the three command procedures at file scope:
	// cmd_add :: proc(tasks: ^[dynamic]Task, title: string)
	// Compute next_id := 1 if len(tasks^) == 0 else tasks^[len(tasks^) - 1].id + 1,
	// and append(tasks, Task{id = next_id, title = strings.clone(title), status = .Todo, done = false}).
	//
	// cmd_complete :: proc(tasks: ^[dynamic]Task, id: int) -> bool
	// Loop with for &t in tasks^; when t.id == id, set t.done = true and
	// t.status = .Done and return true. Return false if no task matched id.
	//
	// cmd_list :: proc(tasks: []Task)
	// Print each task with "[x]" or "[ ]", its id, title, and status.
}

cli_subcommand_dispatch :: proc() {

	/*
	Real CLI tools inspect 'args := os.args[1:]' and dispatch on 'args[0]' to
	handle subcommands like 'add', 'done', and 'list'. Notice a common pitfall:
	passing no arguments ('len(args) == 0') during automated runs should fall
	back cleanly to a self-contained demo rather than hanging or failing with a
	non-zero exit!

	Suppose the user runs:
	    odin run 920_json_task_tracker_cli.odin -file -- done 1
	Here 'args[0]' is "done" and 'args[1]' is "1". Checking 'len(args) < 2'
	before reading 'args[1]' prevents out-of-bounds panics, and
	'strconv.parse_int(args[1])' safely rejects non-numeric IDs like "done abc".
	*/

	args := os.args[1:]
	sample_id, id_ok := strconv.parse_int("1")
	fmt.printfln("CLI args received: %d (sample parsed id=%d, ok=%v)", len(args), sample_id, id_ok)

	// Implement subcommand dispatch over args := os.args[1:] backed by
	// db_path := "temp_tasks.json" inside your arena-backed runner:
	// - When len(args) == 0, run a self-contained demo: schedule
	//   defer os.remove(db_path), load tasks, cmd_add two tasks, cmd_complete(1),
	//   save_tasks, reload into a fresh list, and display with cmd_list.
	// - When args[0] == "add", verify len(args) >= 2 (or join args[1:] with
	//   strings.join), call cmd_add, and persist with save_tasks.
	// - When args[0] == "done", verify len(args) >= 2, parse id via
	//   strconv.parse_int(args[1]), call cmd_complete, and persist with save_tasks.
	// - When args[0] == "list", load and call cmd_list(tasks[:]).
	// - On any unknown subcommand, print a clear usage summary.
}

main :: proc() {

	fmt.println("=== 1. Virtual arena allocator setup ===")
	arena_backed_allocator_setup()

	fmt.println("\n=== 2. JSON persistence layer ===")
	json_persistence_layer()

	fmt.println("\n=== 3. Task mutations and commands ===")
	task_commands_and_mutations()

	fmt.println("\n=== 4. CLI subcommand dispatch ===")
	cli_subcommand_dispatch()
}
