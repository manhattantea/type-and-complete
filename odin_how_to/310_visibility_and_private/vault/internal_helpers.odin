#+private
package vault

/*
Placing #+private before the package declaration makes every top-level symbol
in this file private to package vault by default.

Sibling files in the same folder (such as public_api.odin) can read everything
declared here, while external importers (such as main.odin) cannot see any of
it. To lock an entire file to itself alone, replace #+private with #+private file.
You can also override a single symbol inside this file with @(private="file").
*/

// Minimal anchor: package-private constant referenced by public_api.odin.

INTERNAL_MIX_CONSTANT : u32 : 0x5BF03635

// Define hash_pin :: proc(pin: u32) -> u32 that mixes pin using
// (pin * 2654435761) ~ INTERNAL_MIX_CONSTANT and returns the u32 digest.


// Define mask_pin :: proc(raw_pin: u32) -> u32 that keeps only the lower
// 16 bits via raw_pin & 0x0000_FFFF.


// Declare @(private="file") FILE_ONLY_SEAL : u32 : 0xCAFE_BABE here, then
// test referencing FILE_ONLY_SEAL from public_api.odin to prove that
// @(private="file") overrides #+private and hides it from sibling files too.
