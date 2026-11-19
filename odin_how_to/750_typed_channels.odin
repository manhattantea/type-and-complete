// odin run 750_typed_channels.odin -file

package main

import "core:fmt"
import "core:sync/chan"
import "core:thread"

/*
Sharing raw memory between threads forces every reader and writer to obey the
same locking discipline. Channels invert that model: instead of sharing data
under locks, threads communicate by sending typed values over a synchronized
message queue in 'core:sync/chan'.

Internally, 'chan.Chan(T)' holds a mutex, condition variables, and an optional
ring buffer. Buffered channels ('cap > 0') store up to cap items so senders
keep running until the buffer fills; unbuffered channels ('cap == 0') have zero
storage, forcing sender and receiver to meet simultaneously at a handoff.

This file is split into three sections called from main at the bottom so you
can practice buffered pipelines, unbuffered rendezvous, and multi-worker
fan-out step by step.
*/

Fan_Worker_Ctx :: struct {
	worker_id: int,
	tasks:     chan.Chan(int, .Recv),
	results:   chan.Chan(int, .Send),
}

buffered_channels_and_direction :: proc() {

	/*
	When we allocate a channel with 'c, err := chan.create(chan.Chan(int), 4, context.allocator)',
	it means "create a thread-safe queue of 4 integers using the current
	allocator". Because 'chan.create' is marked '@(require_results)', always
	inspect 'err' (a 'runtime.Allocator_Error' that equals '.None' on success)
	and pair it with 'defer chan.destroy(c)' so heap memory never leaks.

	Odin lets you narrow a bidirectional 'chan.Chan(T)' into send-only or
	receive-only views using 'chan.as_send(c)' ('chan.Chan(T, .Send)') and
	'chan.as_recv(c)' ('chan.Chan(T, .Recv)'). If a helper accidentally tries
	to receive from a '.Send' handle, the compiler catches it immediately.

	    Suppose jobs has capacity 4 and a producer sends 10, 20, 30 then closes:
	        chan.send(tx, 10)
	        chan.send(tx, 20)
	        chan.send(tx, 30)
	        chan.close(tx)
	    A consumer looping 'for val, ok := chan.recv(rx); ok; val, ok = chan.recv(rx)'
	    receives 10, 20, 30 in FIFO order, and on the 4th call 'chan.recv' sees
	    the channel is closed and empty, returning (0, false) to end the loop.
	*/

	// Starter anchor creating a 1-slot channel and checking its allocator result:

	anchor_ch, anchor_err := chan.create(chan.Chan(int), 1, context.allocator)
	if anchor_err == .None {
		defer chan.destroy(anchor_ch)
		sent := chan.send(chan.as_send(anchor_ch), 42)
		val, ok := chan.recv(chan.as_recv(anchor_ch))
		fmt.printfln("Starter channel echo: sent=%v, val=%d, ok=%v (Thread=%dB)",
			sent, val, ok, size_of(thread.Thread))
	}

	// Write a producer procedure at file scope with exact signature:
	// producer_worker :: proc(tx: chan.Chan(int, .Send))
	// Inside it, send 10, 20, and 30 using chan.send(tx, val), then call
	// chan.close(tx) so the receiver knows no further items will arrive.


	// Create a buffered channel jobs, err := chan.create(chan.Chan(int), 4, context.allocator),
	// check err == .None and register defer chan.destroy(jobs). Spawn a thread
	// running producer_worker with thread.create_and_start_with_poly_data(chan.as_send(jobs), producer_worker),
	// drain all items in a loop with:
	// for val, ok := chan.recv(chan.as_recv(jobs)); ok; val, ok = chan.recv(chan.as_recv(jobs))
	// Print each value, verify their sum equals 60, and join/destroy the thread.


	// Verify compile-time direction safety by uncommenting the line below:
	// rx_only := chan.as_recv(anchor_ch); chan.send(rx_only, 99)
}

unbuffered_rendezvous_channels :: proc() {

	/*
	Passing capacity 0 to 'chan.create(chan.Chan(string), 0, context.allocator)'
	creates an unbuffered rendezvous channel. Because zero slots exist in
	memory, 'chan.send' cannot drop off a value and walk away; the sender
	blocks until another thread enters 'chan.recv', and vice versa.

	    Suppose ping_ch has capacity 0:
	    If main calls chan.send(ping_ch, "hello") on the ONLY thread before any
	    receiver thread exists, main waits forever for a receiver that can never
	    run (single-thread deadlock). With a separate thread running chan.recv,
	    both threads meet at the handoff point and resume together.
	*/

	// Write a rendezvous sender procedure at file scope with exact signature:
	// rendezvous_sender :: proc(tx: chan.Chan(string, .Send))
	// Have it print "Sender arriving at rendezvous...", send "handoff-ok" via
	// chan.send(tx, "handoff-ok"), and then print "Sender cleared rendezvous!".


	// Create an unbuffered channel rch, err := chan.create(chan.Chan(string), 0, context.allocator),
	// guard with if err == .None and defer chan.destroy(rch), spawn
	// rendezvous_sender on a worker thread, receive the message on this thread
	// using msg, ok := chan.recv(chan.as_recv(rch)), print msg and ok, and
	// join/destroy the worker thread.


	// Build a 2-channel unbuffered ping-pong exchange: create ping and pong
	// channels (both cap == 0), spawn a responder thread that waits on ping and
	// replies on pong for 3 rounds, and drive 3 "ping" -> "pong" round-trips
	// from here before joining/destroying the responder.
}

fan_out_worker_channels :: proc() {

	/*
	Channels in 'core:sync/chan' are safe for multiple producers and multiple
	consumers simultaneously. You can fan work out across N worker threads by
	handing every worker the same 'chan.Chan(int, .Recv)' tasks handle and the
	same 'chan.Chan(int, .Send)' results handle.

	Pay close attention to shutdown order:
	The coordinator pushes all tasks, calls 'chan.close(tasks)', waits for all
	workers to finish via 'thread.join' (each worker exits when 'chan.recv'
	returns 'ok == false'), and ONLY THEN calls 'chan.close(results)'. Closing
	results before workers exit would cause a send on a closed channel!
	*/

	// Starter anchor confirming Fan_Worker_Ctx layout:

	fmt.printfln("Starter Fan_Worker_Ctx size: %dB", size_of(Fan_Worker_Ctx))

	// Write a fan-out worker procedure at file scope with exact signature:
	// fan_out_worker :: proc(ctx: ^Fan_Worker_Ctx)
	// Loop with:
	// for job, ok := chan.recv(ctx.tasks); ok; job, ok = chan.recv(ctx.tasks)
	// For each job, compute job * job, send it to ctx.results, and print which
	// ctx.worker_id processed which job.


	// Create buffered channels tasks (cap 8) and results (cap 8) with explicit
	// error checks and defer chan.destroy. Declare contexts: [3]Fan_Worker_Ctx
	// and workers: [3]^thread.Thread, spawn 3 threads passing &contexts[w], send
	// tasks 1 through 6 into chan.as_send(tasks), and close tasks immediately.


	// Join and destroy all 3 worker threads, then close results, drain every
	// value from chan.as_recv(results) until ok == false, and assert the total
	// sum of squares equals 91 (1 + 4 + 9 + 16 + 25 + 36).
}

main :: proc() {

	fmt.println("=== 1. Buffered channels and compile-time direction ===")
	buffered_channels_and_direction()

	fmt.println("\n=== 2. Unbuffered rendezvous channels ===")
	unbuffered_rendezvous_channels()

	fmt.println("\n=== 3. Multi-worker fan-out and fan-in ===")
	fan_out_worker_channels()
}
