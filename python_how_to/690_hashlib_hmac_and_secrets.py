# python 690_hashlib_hmac_and_secrets.py

import hashlib
import hmac
import io
import secrets


def secrets_csprng_vs_random() -> None:

    # Python's random module uses the Mersenne Twister PRNG—fast and repeatable
    # with random.Random(seed) for simulations and games, but completely
    # predictable to an attacker after observing 624 outputs. Never use random
    # for passwords, API keys, session IDs, or reset tokens.
    #
    # Always use secrets, which draws from the OS cryptographic RNG (os.urandom):
    # - secrets.token_bytes(32): 32 cryptographic random bytes (256-bit key).
    # - secrets.token_hex(16): 32 lowercase hex characters (2 chars per byte).
    # - secrets.token_urlsafe(24): URL-safe Base64 token string.
    # - secrets.randbelow(n): unbiased random integer in [0, n).

    session_token = secrets.token_urlsafe(16)
    print("Starter CSPRNG token:", session_token, f"(len={len(session_token)})")

    # Generate a 16-byte hex API key via secrets.token_hex(16) and a 32-byte
    # raw key via secrets.token_bytes(32). Print the hex key, len(hex_key) == 32,
    # and len(raw_key) == 32.


    # Pick a random 6-digit numeric verification code using secrets.randbelow(1_000_000)
    # formatted with zero-padding (f"{code:06d}") so leading zeros are preserved.


def streaming_hashlib_and_file_digest() -> None:

    # Cryptographic hash functions (hashlib.sha256(), hashlib.blake2b()) consume
    # bytes incrementally via .update(chunk) and return raw bytes (.digest()) or
    # lowercase hex (.hexdigest()). Never read a huge file into RAM with .read()
    # just to hash it!
    #
    #     Suppose payload = b"chunked-stream-payload-v1".
    #     Calling h = hashlib.sha256(), then h.update(payload[:10]) and
    #     h.update(payload[10:]) produces the exact same digest as hashing
    #     payload all at once.
    #
    # Python 3.11+ adds hashlib.file_digest(file_obj, "sha256"), which streams
    # directly from any binary file-like object (such as an "rb" file or
    # io.BytesIO) in C without manual chunk loops.

    starter_hash = hashlib.sha256(b"hello").hexdigest()
    print("Starter SHA-256('hello')[:16]:", starter_hash[:16])

    # Define payload = b"chunked-stream-payload-v1" and compute its SHA-256 hex
    # digest via stream_hex = hashlib.file_digest(io.BytesIO(payload), "sha256").hexdigest().
    # Also hash payload incrementally with h = hashlib.sha256(), calling
    # h.update(...) on two slices of payload, and assert h.hexdigest() == stream_hex.


    # Try uncommenting the line below to see TypeError when file_digest receives
    # a text stream (io.StringIO) instead of a binary stream:
    # hashlib.file_digest(io.StringIO("must be binary"), "sha256")


def hmac_signing_and_constant_time_compare() -> None:

    # To verify both integrity and authenticity (for example signing a webhook
    # payload), naive sha256(key + message) is vulnerable to length-extension
    # attacks. hmac.new(key_bytes, msg_bytes, hashlib.sha256) uses a keyed
    # double-hash construction that prevents length extension.
    #
    # Just as critical: NEVER verify a MAC or secret token with ==! Standard ==
    # short-circuits on the first mismatched byte, leaking timing differences.
    # Always compare digests and tokens with hmac.compare_digest(a, b) (also
    # aliased as secrets.compare_digest(a, b)), which runs in constant time and
    # expects matching types (both bytes or both ASCII str).

    key = b"demo-key"
    mac = hmac.new(key, b"ping", hashlib.sha256).hexdigest()
    print("Starter HMAC ok:", hmac.compare_digest(mac, hmac.new(key, b"ping", hashlib.sha256).hexdigest()))

    # Generate a 32-byte key signing_key = secrets.token_bytes(32) and sign
    # msg = b"user_id=42&role=admin" with
    # sig = hmac.new(signing_key, msg, hashlib.sha256).hexdigest().
    # Verify sig against a freshly computed expected_sig via
    # hmac.compare_digest(sig, expected_sig) (expect True).


    # Flip the last character of sig to create tampered_sig and check
    # hmac.compare_digest(tampered_sig, expected_sig) (expect False), then
    # also test secrets.compare_digest on two matching vs mismatched ASCII tokens.


def main() -> None:

    print("=== 1. secrets CSPRNG vs predictable random ===")
    secrets_csprng_vs_random()

    print("\n=== 2. Streaming hashlib and file_digest ===")
    streaming_hashlib_and_file_digest()

    print("\n=== 3. HMAC signing and constant-time compare_digest ===")
    hmac_signing_and_constant_time_compare()


if __name__ == "__main__":
    main()
