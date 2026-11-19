// odin run 670_reflect_struct_fields_and_tags.odin -file

package main

import "core:fmt"
import "core:reflect"

/*
While 'base:runtime' gives you raw Type_Info multi-pointers, 'core:reflect'
turns them into ergonomic slices and lookup helpers for inspecting structs and
values dynamically through Odin's 'any' type.

An 'any' value is a 16-byte fat pointer holding '{data: rawptr, id: typeid}'—a
pointer to the live value in memory paired with its runtime typeid. Combining
'any' with 'reflect.struct_fields_zipped' lets you inspect field names, types,
byte offsets, and metadata tags (such as db:"user_id" required:"true") at
runtime without knowing the struct type at compile time.
*/

Anchor_Metric :: struct {
	sample_id: int `json:"sample_id"`,
}

// Define User_Record :: struct with struct tags for database columns and
// required-field validation:
// id: u64 with tag db:"user_id" required:"true"
// username: string with tag db:"username" required:"true"
// bio: string with tag db:"bio"

struct_fields_and_tags_basics :: proc() {

	/*
	Calling 'reflect.struct_fields_zipped(T)' zips a struct's parallel RTTI
	arrays into a slice of 'reflect.Struct_Field' records (allocated on
	context.temp_allocator by default). Each field carries '.name', '.type',
	'.offset' (its byte distance from the start of the struct), and '.tag'
	('reflect.Struct_Tag'). Calling 'reflect.struct_tag_lookup(field.tag, "key")'
	parses backtick key:"value" pairs and returns '(value, ok)'.
	*/

	fields := reflect.struct_fields_zipped(Anchor_Metric)
	json_name, has_json := reflect.struct_tag_lookup(fields[0].tag, "json")
	fmt.printfln("Starter field: %s (offset=%d, has_json=%v, json=%q)", fields[0].name, fields[0].offset, has_json, json_name)

	// Iterate for field in reflect.struct_fields_zipped(User_Record) and print
	// field.name, field.type.id, field.offset, and field.tag for every field.


	// Look up both "db" and "required" on each User_Record field with
	// reflect.struct_tag_lookup and print whether each column is required.
}

// Write a dynamic struct inspector that reads tags and live field values:
// inspect_struct_tags :: proc(val: any)
// Fetch fields := reflect.struct_fields_zipped(val.id). If len(fields) == 0,
// print a message and return. Otherwise loop over fields, look up "db" and
// "required" with reflect.struct_tag_lookup(field.tag, ...), extract the live
// value via reflect.struct_field_value(val, field), and print field.name,
// field.offset, the tag values, and the runtime field value.

dynamic_any_and_field_values :: proc() {

	/*
	Notice what happens when you pass any struct value to 'val: any': Odin
	automatically takes the address of a temporary or variable and packs
	'{data, id}' into 'val'. Inside the procedure, 'reflect.struct_field_value'
	uses 'val.data' and 'field.offset' to return a new 'any' pointing straight
	at that single field.
	*/

	sample_any: any = Anchor_Metric{sample_id = 7}
	fmt.printfln("Starter any id: %v (value=%v)", sample_any.id, sample_any)

	// Instantiate alice := User_Record{id = 101, username = "alice", bio = "systems dev"}
	// and call inspect_struct_tags(alice).


	// Call inspect_struct_tags on a non-struct value (such as 42) to verify your
	// len(fields) == 0 guard handles non-structs cleanly.
}

// Write a dynamic struct-tag validator using raw field.offset pointer math:
// validate_required_fields :: proc(val: any) -> bool
// Fetch fields := reflect.struct_fields_zipped(val.id). If len(fields) == 0
// or val.data == nil, return false. Track all_ok := true and loop over fields.
// For each field, look up req, has_req := reflect.struct_tag_lookup(field.tag, "required")
// and skip the field when !has_req || req != "true". Otherwise compute the
// live field address directly from the struct base pointer with
// field_ptr := rawptr(uintptr(val.data) + field.offset) and switch on
// field.type.id:
// - case u64: if (^u64)(field_ptr)^ == 0, print an error naming field.name and set all_ok = false
// - case int: if (^int)(field_ptr)^ == 0, print an error naming field.name and set all_ok = false
// - case string: if len((^string)(field_ptr)^) == 0, print an error naming field.name and set all_ok = false
// Return all_ok.

offset_based_tag_validator :: proc() {

	/*
	Why expose 'field.offset' at all? Because computing
	'rawptr(uintptr(val.data) + field.offset)' lets serializers, binary decoders,
	and validators read or mutate struct fields in O(1) pointer arithmetic
	without branching on field names at runtime.

	    Suppose user := User_Record{id = 0, username = "", bio = "hi"}:
	    Because id sits at offset 0 and username sits at offset 8, adding
	    field.offset to uintptr(val.data) points directly at each field's raw
	    bytes so validate_required_fields catches both missing required values
	    while ignoring the optional bio field.
	*/

	metric := Anchor_Metric{sample_id = 99}
	metric_fields := reflect.struct_fields_zipped(Anchor_Metric)
	metric_any: any = metric
	metric_ptr := rawptr(uintptr(metric_any.data) + metric_fields[0].offset)
	fmt.printfln("Starter offset read: sample_id=%d (offset=%d)", (^int)(metric_ptr)^, metric_fields[0].offset)

	// Test validate_required_fields on a valid User_Record (id = 42,
	// username = "ada", bio = "") and confirm it returns true even though
	// optional bio is empty.


	// Test validate_required_fields on an invalid User_Record (id = 0,
	// username = "", bio = "guest") and confirm it prints field errors for
	// both id and username and returns false.


	// Define a second tagged struct (for example Config :: struct with a
	// required:"true" port: int and host: string) and pass it to
	// validate_required_fields to verify the validator works across any struct.


	// Extend validate_required_fields with a case f32 check (rejecting 0.0)
	// or test passing an empty struct / nil any to confirm the validator fails
	// safely without dereferencing nil pointers.
}

main :: proc() {

	defer free_all(context.temp_allocator)

	fmt.println("=== 1. Struct fields and tags basics ===")
	struct_fields_and_tags_basics()

	fmt.println("\n=== 2. Dynamic any and field values ===")
	dynamic_any_and_field_values()

	fmt.println("\n=== 3. Offset-based struct-tag validator ===")
	offset_based_tag_validator()
}
