# python -m unittest -v 195_unit_testing_with_unittest.py

from collections.abc import Callable
import unittest
from unittest.mock import MagicMock, patch
import warnings


# Python ships a complete xUnit-style test runner and mocking library in the
# standard library (unittest and unittest.mock) with zero external packages.
# You can run this file either via:
# - python -m unittest -v 195_unit_testing_with_unittest.py
# - python 195_unit_testing_with_unittest.py
#
# First, we need real code under test AND a concrete collaborator object so our
# mocking and patch.object tests have a real target rather than placeholders.
# Below is a tiny working Notifier class whose .send(msg) method records sent
# alerts onto self.sent—ready for both direct calls and patch.object(Notifier, "send", ...).


class Notifier:

    def __init__(self) -> None:

        self.sent: list[str] = []

    def send(self, msg: str) -> str:

        self.sent.append(msg)
        return f"sent:{msg}"


# Define the functions under test right here at module level so TestClampAndScale
# below can call them cleanly:
#
# Write clamp_and_scale(val: float, lo: float, hi: float, scale: float = 1.0) -> float:
# - Raise ValueError("lo must be <= hi") whenever lo > hi.
# - If val < lo or val > hi, emit a warning via
#   warnings.warn("val was clamped to bounds", UserWarning, stacklevel=2)
#   so tests can verify warning emission with self.assertWarns(UserWarning).
# - Clamp val into [lo, hi] with clamped = min(max(val, lo), hi) and return
#   clamped * scale.


# Write notify_clamped(val: float, lo: float, hi: float, notifier: Notifier) -> float:
# Call result = clamp_and_scale(val, lo, hi). Whenever result != val (meaning
# clamping happened), call notifier.send(f"clamped={result}"). Return result.


# Write dispatch_with_callback(val: float, lo: float, hi: float, on_clamp: Callable[[str], None]) -> float:
# Call result = clamp_and_scale(val, lo, hi). Whenever result != val, invoke
# on_clamp(f"clamped={result}"). Return result.


# How unittest.TestCase executes your tests:
# - Discovery scans the module for unittest.TestCase subclasses and runs every
#   method whose name begins with test_ as an independent test case.
# - Per-test isolation: setUp(self) runs fresh BEFORE every individual test_*
#   method, and tearDown(self) runs AFTER every individual test_* method (even
#   if that test failed!). Never stash mutable state on class attributes shared
#   across tests—create fresh instances in setUp(self).
# - Core assertions:
#   - self.assertEqual(a, b) for exact equality.
#   - self.assertAlmostEqual(a, b, places=7) for IEEE-754 floats (avoiding
#     0.1 * 3.0 != 0.30000000000000004 failures).
#   - with self.assertRaises(ValueError) as ctx: captures an expected error;
#     ALWAYS put follow-up checks like "lo" in str(ctx.exception) AFTER the
#     with block closes, because lines after the raising call inside the with
#     block never execute!
#   - with self.assertWarns(UserWarning) as warn_ctx: verifies a warning fired
#     and lets you inspect warn_ctx.warning AFTER the with block closes.
#   - with self.subTest(val=val, scale=scale): runs table-driven rows inside
#     one test_* method so every failing row is reported individually instead
#     of aborting on the first failure.
# - Mocking and patching:
#   - MagicMock() acts as a stand-in callable/object that records every call so
#     you can check mock.assert_called_once_with(...) or mock.assert_not_called().
#   - with patch.object(Notifier, "send", return_value="mocked") as mock_send:
#     temporarily replaces Notifier.send ONLY inside the with block and
#     automatically restores the real method on exit (even if an error occurs).
#
# Note on Python 3.12+ exit codes: python -m unittest exits with status 5 if
# zero test_* methods are discovered. This starter TestCase includes setUp,
# tearDown, and test_notifier_baseline so both unittest and python exit 0 right
# away before you add the remaining tests.


class TestClampAndScale(unittest.TestCase):

    def setUp(self) -> None:

        self.default_bounds = (0.0, 10.0)
        self.notifier = Notifier()

    def tearDown(self) -> None:

        self.notifier.sent.clear()

    def test_notifier_baseline(self) -> None:

        receipt = self.notifier.send("ready")
        self.assertEqual(receipt, "sent:ready")
        self.assertEqual(self.notifier.sent, ["ready"])

    # Verify setUp / tearDown per-test isolation:
    # Add test_setup_starts_with_clean_notifier(self) -> None asserting that
    # self.notifier.sent == [] and self.default_bounds == (0.0, 10.0), proving
    # test_notifier_baseline's "ready" message did NOT leak into this test.


    # Write table-driven subtests for clamp_and_scale:
    # Add test_valid_cases_with_subtests(self) -> None defining a list of
    # (val, scale, expected) cases covering:
    # - below lo (e.g., val=-5.0, scale=2.0 -> 0.0)
    # - inside bounds (e.g., val=4.0, scale=2.5 -> 10.0)
    # - above hi (e.g., val=15.0, scale=0.5 -> 5.0)
    # - float precision (e.g., val=0.1, scale=3.0 -> 0.3)
    # Loop with lo, hi = self.default_bounds and
    # with self.subTest(val=val, scale=scale):, checking each result using
    # self.assertAlmostEqual(got, expected, places=7).
    # (Wrap out-of-bounds calls or use warnings.catch_warnings if you want quiet
    # output while testing subtest values.)


    # Test expected exceptions with assertRaises:
    # Add test_invalid_bounds_raises(self) -> None using
    # with self.assertRaises(ValueError) as ctx: calling clamp_and_scale(5.0, 10.0, 0.0).
    # AFTER the with block exits, assert "lo" in str(ctx.exception).


    # Test warning emission with assertWarns:
    # Add test_clamping_emits_user_warning(self) -> None using
    # with self.assertWarns(UserWarning) as warn_ctx: calling
    # result = clamp_and_scale(25.0, 0.0, 10.0).
    # AFTER the with block exits, assert self.assertEqual(result, 10.0) and
    # self.assertIn("clamped", str(warn_ctx.warning)).


    # Test standalone callbacks with MagicMock:
    # Add test_callback_with_magic_mock(self) -> None:
    # - Create mock_cb = MagicMock(), call
    #   dispatch_with_callback(15.0, 0.0, 10.0, mock_cb), and verify
    #   mock_cb.assert_called_once_with("clamped=10.0").
    # - Create quiet_cb = MagicMock(), call
    #   dispatch_with_callback(5.0, 0.0, 10.0, quiet_cb), and verify
    #   quiet_cb.assert_not_called().


    # Test concrete attribute replacement with unittest.mock.patch.object:
    # Add test_patch_object_on_notifier_send(self) -> None:
    # - Inside with patch.object(Notifier, "send", return_value="mocked") as mock_send:,
    #   call result = notify_clamped(20.0, 0.0, 10.0, self.notifier).
    # - Assert self.assertEqual(result, 10.0),
    #   mock_send.assert_called_once_with("clamped=10.0"), and
    #   self.assertEqual(self.notifier.sent, []) (confirming the real send was
    #   swapped out while inside the with block).
    # - AFTER the with block exits, call self.notifier.send("restored") and
    #   assert self.assertEqual(self.notifier.sent, ["restored"]) to prove
    #   patch.object cleanly restored Notifier.send!


if __name__ == "__main__":
    unittest.main()
