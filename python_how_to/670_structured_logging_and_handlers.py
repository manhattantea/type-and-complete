# python 670_structured_logging_and_handlers.py

import io
import logging


def logger_hierarchy_and_module_isolation() -> None:

    # Python's logging module organizes loggers into a global, dot-separated
    # tree keyed by name. Calling logging.getLogger("app.db.pool") returns a
    # singleton logger whose parent is "app.db", whose parent is "app", whose
    # parent is the root logger "".
    #
    # By convention, every module declares logger = logging.getLogger(__name__)
    # at module scope. Two design rules keep multi-module logging clean:
    # - Libraries NEVER configure handlers or call logging.basicConfig() or root
    #   logging.info(...). Calling logging.info(...) implicitly runs basicConfig
    #   on the global root logger, hijacking formatting for the whole process.
    # - Only the application's entry point (main) attaches handlers and formatters.
    #
    #     Suppose module_a uses logging.getLogger("demo.auth") and module_b uses
    #     logging.getLogger("demo.db"). Both inherit from "demo" without sharing
    #     handlers, and calling logger.handlers.clear() before wiring in tests
    #     prevents duplicate handlers from piling up across repeated runs.

    module_logger = logging.getLogger(__name__)
    print(f"Starter logger {module_logger.name!r} effective level:", logging.getLevelName(module_logger.getEffectiveLevel()))

    # Inspect the logger hierarchy by creating parent = logging.getLogger("demo.app")
    # and child = logging.getLogger("demo.app.worker"). Print child.parent.name
    # and child.parent.parent.name to see the dot-separated tree structure.


    # Verify singleton identity and module isolation: confirm
    # logging.getLogger("demo.app.worker") is child is True, and confirm a
    # sibling logger logging.getLogger("demo.app.cache") has its own distinct
    # handlers list and does not share handlers attached to child.


    # Practice idempotent test setup: attach a StreamHandler(io.StringIO()) to
    # test_logger = logging.getLogger("demo.isolated") twice without clearing,
    # print len(test_logger.handlers) (expected: 2), then call
    # test_logger.handlers.clear() before attaching so len stays 1.


def two_stage_filtering_and_dual_handlers() -> None:

    # Log levels are ordered integers:
    # DEBUG=10 < INFO=20 < WARNING=30 < ERROR=40 < CRITICAL=50.
    # Every emitted record passes through TWO gates in sequence:
    # - The Logger's own level threshold.
    # - Each attached Handler's level threshold.
    #
    #     Suppose logger is left at its default NOTSET (which inherits root's
    #     WARNING=30) and you attach a handler with handler.setLevel(logging.DEBUG).
    #     Calling logger.info("hi") produces NOTHING because gate 1 (the logger
    #     at WARNING) drops INFO before the handler ever sees it!
    #
    # Two-stage filtering shines when you wire dual handlers to one logger: set
    # logger.setLevel(logging.DEBUG), attach a console handler at WARNING for
    # terse alerts, and attach a verbose debug handler at DEBUG for diagnostics.

    probe_stream = io.StringIO()
    probe_logger = logging.getLogger("demo.starter_gate")
    probe_logger.handlers.clear()
    probe_logger.propagate = False
    probe_logger.setLevel(logging.INFO)
    probe_handler = logging.StreamHandler(probe_stream)
    probe_handler.setLevel(logging.INFO)
    probe_logger.addHandler(probe_handler)
    probe_logger.info("Starter gate active")
    print("Starter stream:", probe_stream.getvalue().strip())

    # Reproduce the two-stage filtering trap: create trap_logger = logging.getLogger("demo.trap")
    # (leaving its level at NOTSET/default WARNING), set propagate = False, clear
    # handlers, attach a StreamHandler(io.StringIO()) set to logging.DEBUG, call
    # trap_logger.info("dropped"), and print the empty stream output. Then call
    # trap_logger.setLevel(logging.DEBUG), emit again, and verify it appears.


    # Wire dual handler thresholds on svc_logger = logging.getLogger("demo.dual"):
    # set svc_logger.setLevel(logging.DEBUG) and propagate = False, clear handlers,
    # then attach console_handler = logging.StreamHandler(console_stream) at
    # logging.WARNING and audit_handler = logging.StreamHandler(audit_stream) at
    # logging.DEBUG with distinct logging.Formatter patterns. Emit debug, info,
    # and warning records and print both streams to compare.


    # Dynamically adjust console_handler.setLevel(logging.INFO) at runtime without
    # rebuilding the logger, emit another info message, and verify console_stream
    # now captures INFO while svc_logger itself stayed untouched.


def propagation_trap_lazy_formatting_and_exceptions() -> None:

    # After a logger's own handlers process a record, logging bubbles the same
    # record upward to every ancestor logger by default (logger.propagate = True).
    # If both a child logger and a parent (or root) logger have handlers attached,
    # every record prints TWICE unless you set child.propagate = False or leave
    # handlers only on the parent:
    #
    #     Suppose parent = logging.getLogger("demo.net") has a handler and
    #     child = logging.getLogger("demo.net.http") also has a handler.
    #     With child.propagate = True (default), child.warning("timeout") emits
    #     once from child's handler and a second time from parent's handler!
    #
    # Two more everyday idioms:
    # - Lazy % formatting: write logger.debug("Read %d rows from %s", count, src)
    #   instead of an f-string. Logging skips string interpolation completely
    #   when DEBUG is disabled.
    # - logger.exception("...") inside an except block logs at ERROR level and
    #   automatically attaches exc_info=True with the full traceback.

    parent_buf = io.StringIO()
    parent_log = logging.getLogger("demo.prop_starter")
    parent_log.handlers.clear()
    parent_log.propagate = False
    parent_log.setLevel(logging.INFO)
    parent_log.addHandler(logging.StreamHandler(parent_buf))
    parent_log.info("Parent ready")
    print("Starter parent log:", parent_buf.getvalue().strip())

    # Demonstrate the propagate=True double-logging trap:
    # create parent = logging.getLogger("demo.pkg") and child = logging.getLogger("demo.pkg.sub"),
    # attach separate StringIO StreamHandlers to both (propagate=False on parent,
    # propagate=True on child), log child.warning("ping"), and print both buffers
    # to see "ping" appear in BOTH. Then set child.propagate = False, log
    # child.warning("isolated"), and confirm parent's buffer does not receive it.


    # Practice lazy % formatting on svc = logging.getLogger("demo.service"):
    # set svc.setLevel(logging.DEBUG), propagate = False, clear handlers, attach a
    # StreamHandler(log_stream) with Formatter("%(levelname)s [%(name)s] %(message)s"),
    # and emit .debug("Parsed %d items from %s", 42, "cache.bin") and .info(...).


    # Trigger a ZeroDivisionError inside try ... except ZeroDivisionError: and
    # call svc.exception("Failed to process request"), then print log_stream.getvalue()
    # to verify the ERROR record includes the full Python traceback.


def main() -> None:

    print("=== 1. Logger hierarchy and module isolation ===")
    logger_hierarchy_and_module_isolation()

    print("\n=== 2. Two-stage level filtering and dual handlers ===")
    two_stage_filtering_and_dual_handlers()

    print("\n=== 3. Propagation trap, lazy formatting, and logger.exception ===")
    propagation_trap_lazy_formatting_and_exceptions()


if __name__ == "__main__":
    main()
