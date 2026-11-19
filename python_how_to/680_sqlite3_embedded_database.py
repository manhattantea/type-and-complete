# python 680_sqlite3_embedded_database.py

from contextlib import closing
import sqlite3


def connection_closing_vs_transactions() -> None:

    # Python bundles the full SQLite relational database engine in sqlite3,
    # letting you persist to a single file or spin up an instant ":memory:"
    # database with zero server setup.
    #
    # One sharp friction point surprises nearly everyone coming from open():
    # with conn: commits or rolls back a TRANSACTION—it does NOT close conn!
    # - Exiting with conn: normally calls conn.commit().
    # - Exiting with conn: via an exception calls conn.rollback() and re-raises.
    # - In both cases, conn stays open! On Windows, an unclosed connection keeps
    #   the database file locked on disk.
    #
    #     Suppose you write:
    #         with closing(sqlite3.connect(":memory:")) as conn:
    #             with conn:
    #                 conn.execute("CREATE TABLE t (x INTEGER)")
    #     The inner with conn: commits the transaction, and the outer
    #     contextlib.closing(conn) guarantees conn.close() runs on exit.
    #
    # Setting conn.row_factory = sqlite3.Row replaces plain positional tuples
    # with Row objects supporting column-name access (row["username"], dict(row))
    # as well as positional indexing (row[0]).

    print("Embedded SQLite version:", sqlite3.sqlite_version)

    # Open with closing(sqlite3.connect(":memory:")) as conn: and set
    # conn.row_factory = sqlite3.Row. Inside a with conn: block, create table
    # users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, credits INTEGER NOT NULL)
    # and insert ("ada", 150), ("grace", 300), and ("linus", 75), then select
    # all rows and print dict(row) for each.


    # Verify automatic transaction rollback on exception: inside a
    # try: with conn: ... block, update "linus" to add 500 credits and then
    # trigger sqlite3.IntegrityError by inserting a duplicate username "ada".
    # Catch sqlite3.IntegrityError as err, print err, and re-query "linus" to
    # confirm credits rolled back to 75.


    # Check that closing(conn) actually closed the handle after exiting the
    # outer with block by trying conn.execute("SELECT 1") inside
    # try ... except sqlite3.ProgrammingError as err: and printing err.


def parameterized_queries_positional_and_named() -> None:

    # Never interpolate values into SQL strings with f-strings, +, or %:
    # writing f"SELECT * FROM users WHERE username = '{name}'" opens an
    # immediate SQL injection hole and breaks on legitimate names like "O'Brien".
    # Always pass parameters as the second argument to execute(sql, params):
    # - Positional (?): conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    # - Named (:key): conn.execute("INSERT INTO items VALUES (:id, :name)", {"id": 1, "name": "orb"})
    #
    # Watch out for Python's 1-tuple syntax trap on positional queries:
    #     Suppose min_credits = 100.
    #     (min_credits,) with a trailing comma is a 1-element tuple -> works!
    #     (min_credits) without a comma is just the int 100 -> raises ProgrammingError!
    #
    # Named :key placeholders read much more cleanly when a query has 3+ fields
    # or reuses the same parameter twice, and conn.executemany(sql, seq) runs
    # one prepared statement across many parameter tuples or dicts in one pass.

    with closing(sqlite3.connect(":memory:")) as conn:
        with conn:
            conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO items VALUES (:id, :name)", {"id": 1, "name": "orb"})
        print("Starter named insert:", conn.execute("SELECT id, name FROM items").fetchall())

    # Open an in-memory database with closing(...) and conn.row_factory = sqlite3.Row.
    # Create table products (sku TEXT PRIMARY KEY, title TEXT NOT NULL, price_cents INTEGER NOT NULL).
    # Batch-insert 3 products using conn.executemany with named :key placeholders:
    # "INSERT INTO products (sku, title, price_cents) VALUES (:sku, :title, :price_cents)".


    # Query products with price_cents >= :min_price AND price_cents <= :max_price
    # using a parameter dict, and also run a positional ? query for a single
    # sku passing (target_sku,) with the required trailing comma. Print both results.


    # Try uncommenting the line below inside an open connection block to see
    # ProgrammingError when passing (100) instead of a 1-tuple (100,):
    # conn.execute("SELECT ? + 1", (100))


def foreign_keys_pragma_and_integrity_errors() -> None:

    # SQLite has one famous historical quirk: even if your CREATE TABLE
    # statement declares REFERENCES parent(id), SQLite parses the foreign key
    # constraint and silently IGNORES it unless you enable enforcement on every
    # new connection with conn.execute("PRAGMA foreign_keys = ON")!
    #
    #     Suppose orders(user_id) has REFERENCES users(id) ON DELETE CASCADE:
    #     Without PRAGMA foreign_keys = ON, inserting an order with user_id=999
    #     (no matching user!) succeeds silently, leaving an orphan row.
    #     With PRAGMA foreign_keys = ON, SQLite immediately raises IntegrityError
    #     on orphan inserts and cascades deletes to child rows automatically.

    with closing(sqlite3.connect(":memory:")) as conn:
        fk_state = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        print("Default PRAGMA foreign_keys on new connection:", fk_state)

    # Create two tables in an in-memory connection BEFORE enabling the PRAGMA:
    # accounts (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL) and
    # orders (id INTEGER PRIMARY KEY, account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE).
    # Insert an orphan order with account_id=999 while PRAGMA foreign_keys is 0
    # and observe that SQLite allows it without raising an error.


    # Now open a fresh in-memory connection, run conn.execute("PRAGMA foreign_keys = ON"),
    # create the same accounts and orders tables, and verify that inserting an
    # orphan order with account_id=999 raises sqlite3.IntegrityError.


    # In that same PRAGMA foreign_keys = ON connection, insert a valid account
    # (id=1, email="ada@example.com") and two orders for account_id=1. Then
    # delete account id=1 and query orders to confirm ON DELETE CASCADE removed
    # both child order rows automatically.


def main() -> None:

    print("=== 1. Connection closing vs transactions ===")
    connection_closing_vs_transactions()

    print("\n=== 2. Positional (?) and named (:key) placeholders ===")
    parameterized_queries_positional_and_named()

    print("\n=== 3. PRAGMA foreign_keys = ON and integrity errors ===")
    foreign_keys_pragma_and_integrity_errors()


if __name__ == "__main__":
    main()
