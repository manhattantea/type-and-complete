// odin run 310_visibility_and_private

package main

import "core:fmt"
import "vault"

/*
In Odin, top-level package declarations are exported by default so packages
stay concise without repetitive 'public' keywords. When you want to hide
implementation details inside a package or inside one file, you opt into
encapsulation with attributes or file-top tags:

    @(private) or @(private="package")  visible to sibling files in the same package, hidden from importers
    @(private="file")                   visible only inside the single .odin file where it is declared
    #+private / #+private file          placed before 'package' to apply package or file privacy to the whole file

Keeping internal helpers private ensures external callers depend only on your
stable exported API while sibling files inside the package still cooperate.
*/

exported_api_access :: proc() {

	/*
	Because VAULT_READY in vault/public_api.odin has no privacy attribute,
	package main can read it through the vault qualifier. Meanwhile,
	INTERNAL_MIX_CONSTANT in vault/internal_helpers.odin sits under #+private,
	so vault/public_api.odin can read it to compute VAULT_READY, while
	package main cannot see it at all.
	*/

	// Here is a live call reading the exported anchor from package vault:

	fmt.printfln("Vault subsystem ready: %v", vault.VAULT_READY)

	// After defining hash_pin in vault/internal_helpers.odin and SECRET_SALT
	// plus verify_pin(pin: u32) -> bool in vault/public_api.odin, call
	// vault.verify_pin(1234) and vault.verify_pin(9999), store the booleans
	// in ok_valid and ok_wrong, and print both results with fmt.printfln.
}

encapsulation_boundaries :: proc() {

	/*
	Both package-private and file-private declarations trigger compile errors
	when an external package tries to reference them. The difference between
	@(private) and @(private="file") shows up inside vault/ itself: sibling
	files in package vault can share @(private) symbols, whereas @(private="file")
	blocks even siblings in the same folder.
	*/

	fmt.println("Uncomment any hidden vault symbol below to verify compile-time visibility errors.")

	// Try uncommenting each line one at a time to see the compiler enforce
	// package-level and file-level privacy boundaries:
	// fmt.println(vault.INTERNAL_MIX_CONSTANT)
	// fmt.println(vault.DEFAULT_PIN_HASH)
	// fmt.println(vault.hash_pin(1234))
	// fmt.println(vault.SECRET_SALT)
}

main :: proc() {

	fmt.println("=== 1. Exported API access ===")
	exported_api_access()

	fmt.println("\n=== 2. Encapsulation boundaries ===")
	encapsulation_boundaries()
}
