// odin run 570_logging_with_core_log.odin -file

package main

import "core:fmt"
import "core:log"

/*
In C or C++, subsystems that want to emit diagnostics either reach for a global
singleton logger or force every function in the call chain to accept a logger
pointer. Both choices create friction: globals break when two tests run with
different verbosity, and threading a logger parameter through twenty layers of
helpers pollutes every API signature.

Odin solves this by placing 'context.logger' directly inside the implicit
'context' struct passed invisibly to every Odin procedure. Any procedure at
any call depth can call log.debugf, log.infof, log.warnf, or log.errorf, and
the call automatically routes to whatever logger the caller installed on
context.logger. When a caller wants quiet tests, file output, or multi-sink
routing, it swaps context.logger for that scope without editing a single
downstream signature.
*/

// Define a subsystem helper procedure right here at file scope once you reach
// the second section:
// simulate_subsystem :: proc(worker_id: int)
// Notice it takes zero logger arguments. Inside it, emit a log.debugf message
// for worker startup and a log.warnf message for simulated queue latency.

context_logger_and_levels :: proc() {

	/*
	Every logger in core:log filters messages against a minimum severity called
	log.Level. Ordered from least to most severe, the five levels are:
	.Debug, .Info, .Warning, .Error, and .Fatal.

	When we assign context.logger = logger, it means every log.* call made in
	this procedure—and inside any procedure it calls—checks its level against
	logger.lowest_level before formatting or printing anything. Messages below
	that threshold are dropped right at the check.

	    Suppose dev_log := log.create_console_logger(lowest = .Warning) and
	    you set context.logger = dev_log:
	        log.debug("skipped")   // dropped silently (.Debug < .Warning)
	        log.warn("printed")    // emitted to console (.Warning >= .Warning)

	Because log.create_console_logger allocates any optional state or uses
	standard handles cleanly via its helper, always pair it with
	defer log.destroy_console_logger(logger). Also keep in mind that log.fatal
	and log.fatalf do more than print: they intentionally terminate execution
	via runtime.panic or os.exit, so save .Fatal for unrecoverable crashes.
	*/

	// Here is a quick starter console logger bound at .Info level:

	prev_logger := context.logger
	defer context.logger = prev_logger

	starter_logger := log.create_console_logger(lowest = .Info)
	defer log.destroy_console_logger(starter_logger)
	context.logger = starter_logger
	log.infof("Contextual logger active (lowest=%v)", log.Level.Info)

	// Create a debug-capable console logger named debug_logger using:
	// debug_logger := log.create_console_logger(lowest = .Debug)
	// Pair it with defer log.destroy_console_logger(debug_logger) and bind it
	// to context.logger. Then emit one message at each non-fatal severity
	// using log.debug, log.infof, log.warnf, and log.errorf.


	/*
	You can also customize what metadata prefixes each line by passing a
	log.Options bit_set into log.create_console_logger. When we pass
	opt = log.Options{.Level, .Short_File_Path, .Line, .Procedure, .Terminal_Color},
	it tells the logger to include the source filename, line number, and
	calling procedure name via #caller_location, while dropping the full date
	and timestamp if you want compact terminal output.
	*/

	// Create a compact logger named compact_logger with lowest = .Debug,
	// opt = log.Options{.Level, .Short_File_Path, .Line, .Procedure}, and
	// ident = "NET". Bind it to context.logger and log a packet-size info
	// line to compare its prefix against starter_logger.


	// Test silencing logs inside a nested { ... } block without touching the
	// outer logger: open a { ... } block, save outer := context.logger with
	// defer context.logger = outer, assign context.logger = log.nil_logger(),
	// and call log.info("you should not see this"). After the closing },
	// emit one log.info("outer logger restored") to prove outer state holds.
}

implicit_propagation_and_subsystems :: proc() {

	/*
	How does a helper procedure several stack frames deep know which logger to
	use without taking a logger argument? Every regular "odin" procedure
	receives an invisible pointer to the caller's context by value-copy on
	modification. Inside a procedure, reassigning context.logger only changes
	that procedure's local context (and any deeper calls it makes); as soon as
	it returns, the caller's context.logger is untouched.

	    Suppose main sets context.logger = debug_logger and calls pipeline():
	        pipeline() overrides context.logger = quiet_logger (.Warning)
	        -> validate_item() inside pipeline() sees quiet_logger
	        -> pipeline() returns
	        -> main still has debug_logger active
	*/

	prev_logger := context.logger
	defer context.logger = prev_logger

	trace_logger := log.create_console_logger(lowest = .Debug)
	defer log.destroy_console_logger(trace_logger)
	context.logger = trace_logger
	log.debug("Subsystem propagation scope ready")

	// After writing simulate_subsystem :: proc(worker_id: int) at file scope,
	// call simulate_subsystem(7) here and verify its log.debugf and log.warnf
	// lines route straight through context.logger with no logger parameter.


	// Now wrap a second call in a quieter dynamic scope: open a { ... } block,
	// create quiet_logger := log.create_console_logger(lowest = .Warning) with
	// defer log.destroy_console_logger(quiet_logger), set context.logger = quiet_logger,
	// and call simulate_subsystem(8). Confirm the .Debug startup line vanishes
	// while the .Warning latency line still prints.
}

multi_logger_routing :: proc() {

	/*
	Often one log stream needs to go to two places at once—say, verbose .Debug
	output to your terminal during development and .Warning-or-higher records
	to a separate audit log or file sink. Rather than calling two loggers at
	every log site, log.create_multi_logger fans a single log.* call out to
	every child logger you hand it.

	    Suppose console_log has lowest = .Debug and alert_log has
	    lowest = .Warning, and you build:
	        multi := log.create_multi_logger(console_log, alert_log)
	    When you log.debug("tick"), only console_log prints it because
	    alert_log rejects .Debug. When you log.error("disk full"), both print!

	Notice memory ownership: log.create_multi_logger allocates a small slice
	holding copies of the child logger structs on context.allocator, so always
	pair it with defer log.destroy_multi_logger(multi). Destroying the multi
	logger frees only that wrapper slice; each child logger still needs its own
	defer log.destroy_console_logger(...) registered before the multi logger
	(so LIFO defer destroys multi first, then the children).
	*/

	prev_logger := context.logger
	defer context.logger = prev_logger

	fmt.printfln("Logger header size: %v bytes", size_of(log.Logger))

	// Create two child loggers with separate thresholds:
	// - dev_log := log.create_console_logger(lowest = .Debug, ident = "DEV")
	// - alert_log := log.create_console_logger(lowest = .Warning, opt = log.Options{.Level, .Line}, ident = "ALERT")
	// Register defer log.destroy_console_logger for each before creating multi.


	// Combine both children using:
	// multi := log.create_multi_logger(dev_log, alert_log)
	// Register defer log.destroy_multi_logger(multi) and set context.logger = multi.
	// Emit one log.debugf, one log.infof, and one log.errorf to confirm .Debug
	// and .Info print once under DEV while .Error fans out to DEV and ALERT.


	// Experiment with filtering at the multi-logger vs child level: assign
	// multi.lowest_level = .Info before setting context.logger = multi and see
	// the .Debug message get dropped before even reaching dev_log.
}

main :: proc() {

	fmt.println("=== 1. Context logger and severity levels ===")
	context_logger_and_levels()

	fmt.println("\n=== 2. Implicit propagation and subsystems ===")
	implicit_propagation_and_subsystems()

	fmt.println("\n=== 3. Multi-logger routing ===")
	multi_logger_routing()
}
