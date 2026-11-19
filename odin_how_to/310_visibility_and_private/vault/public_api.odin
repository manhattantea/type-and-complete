package vault

/*
This file defines the public API for package vault.

Declarations without a privacy attribute (such as VAULT_READY and verify_pin)
are exported to any package that imports "vault". Declarations annotated with
@(private) or @(private="package") are shared across sibling files in package
vault, while @(private="file") locks a declaration strictly to public_api.odin.
*/

// Minimal anchor: a file-private constant combined with a package-private
// constant from internal_helpers.odin to compute an exported boolean.

@(private="file")
DEFAULT_PIN_HASH : u32 : 0x1234_5678

VAULT_READY :: INTERNAL_MIX_CONSTANT != DEFAULT_PIN_HASH

// Declare a file-private typed constant SECRET_SALT : u32 : 0x9E3779B9 using
// @(private="file") so neither main.odin nor internal_helpers.odin can read it.


// Declare a package-private constant MAX_ATTEMPTS :: 3 annotated with
// @(private) (or @(private="package")) so internal_helpers.odin could read
// it while main.odin cannot.


// Write an exported procedure verify_pin :: proc(pin: u32) -> bool that
// computes expected := hash_pin(1234) ~ SECRET_SALT, compares it against
// hash_pin(pin) ~ SECRET_SALT, and returns true when they match.
//
// Cross-sibling compile proof: once you add a @(private="file") symbol such
// as FILE_ONLY_SEAL inside internal_helpers.odin, try referencing FILE_ONLY_SEAL
// inside verify_pin here to confirm @(private="file") blocks even sibling files
// in package vault.
