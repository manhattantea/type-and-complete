# python 410_visibility_all_and_circular_imports/main.py

# Visibility, __all__, class attribute name mangling, and circular-import
# resolution lab.
#
# Suggested order across the 5 files in this lab:
# vault/_internal.py -> vault/models.py -> vault/public_api.py ->
# vault/__init__.py -> the sections inside main.py below.

import vault


def public_surface_and_pin_verification() -> None:

    # Python favors explicit package facades over compiler-enforced private
    # keywords. Reading vault.__all__ tells both humans and static analyzers
    # exactly which symbols form the supported public contract.

    print(
        f"Anchors -> vault.__all__={vault.__all__}, "
        f"owner={vault.DEFAULT_OWNER!r}, prefix={vault.DEFAULT_SESSION_PREFIX!r}"
    )

    # After implementing _internal.py, public_api.py, and re-exporting
    # verify_pin in vault/__init__.py, call vault.verify_pin(1234) and
    # vault.verify_pin(9999) and print both booleans (expected: True and False).


    # Inspect vault.__all__ again after extending it and verify that
    # "VaultAccount", "VaultSession", and "verify_pin" are present while
    # "_internal" is absent.


def bidirectional_models_without_cycles() -> None:

    # VaultAccount (in vault/models.py) annotates active_session as
    # VaultSession | None, while VaultSession (in vault/public_api.py) annotates
    # account as VaultAccount | None. Because both modules enable
    # from __future__ import annotations and hide the cross-import inside
    # if TYPE_CHECKING:, the two objects link cleanly at runtime with zero
    # circular-import crash.

    print("Ready to wire bidirectional VaultAccount <-> VaultSession objects.")

    # After implementing VaultAccount and VaultSession and re-exporting them
    # in vault/__init__.py:
    # - Construct account = vault.VaultAccount("ada", "super-secret-key")
    # - Construct session = vault.VaultSession("sess-01", account)
    # - Link them both ways with account.active_session = session
    # - Print account.masked_summary() and session.owner_label() to confirm
    #   both sides cooperate cleanly.


def mangling_and_consenting_adults() -> None:

    # Double-underscore attributes inside a class body (self.__master_key) are
    # rewritten by the Python compiler into self._ClassName__attr. That
    # mechanism exists to prevent accidental attribute name clashes in
    # subclasses, NOT as cryptographic hiding: anyone inspecting dir(obj) can
    # still locate and read the mangled attribute.
    #
    #     Suppose class Box: sets self.__token = "abc".
    #     Accessing box.__token raises AttributeError, while
    #     getattr(box, "_Box__token") returns "abc".
    #
    # Likewise, single-underscore modules like vault._internal are skipped by
    # from vault import *, yet explicit imports still succeed under Python's
    # consenting-adults convention.

    print("Inspecting package attributes on vault:", [n for n in dir(vault) if not n.startswith("__")])

    # After creating account = vault.VaultAccount("ada", "super-secret-key"):
    # - Find the mangled attribute with
    #   [name for name in dir(account) if "master_key" in name]
    # - Read it via getattr(account, "_VaultAccount__master_key") and print it.
    #
    # Try uncommenting below once account is constructed to trigger the
    # AttributeError on the unmangled name:
    # print(account.__master_key)


    # Demonstrate Python's consenting-adults rule for single-underscore internals:
    # - Run from vault import _internal inside this function
    # - Print _internal._INTERNAL_TAG and _internal._hash_pin(1234)
    # - Note in a short comment why from vault import * skips _internal even
    #   though this explicit import works.


def main() -> None:

    print("=== 1. Public surface and deferred internal verification ===")
    public_surface_and_pin_verification()

    print("\n=== 2. Bidirectional models without circular imports ===")
    bidirectional_models_without_cycles()

    print("\n=== 3. Name mangling and consenting-adults visibility ===")
    mangling_and_consenting_adults()


if __name__ == "__main__":
    main()
