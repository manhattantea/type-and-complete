// odin run 705_cache_lines_bandwidth_and_false_sharing.odin -file

package main

import "base:intrinsics"
import "core:fmt"
import "core:thread"
import "core:time"

/*
Multiplier #4 in Casey Muratori's Computer, Enhance! ("Caching" and "Part 3:
Moving Data") explains why memory layout dominates arithmetic cost on modern
CPUs. Hardware never loads a single f32 or i64 from RAM; memory moves in
64-byte cache lines (16 x f32 or 8 x i64).

When a tight loop reads 4 bytes from a 64-byte struct and skips the other 60
cold bytes, 93.75% of cache capacity and memory bandwidth is thrown away. Even
worse, working-set size sets a sharp speed cliff across the cache hierarchy:

    L1d cache (~32 KB per core)      ~4 cycles, highest bandwidth
    L2 cache  (~512 KB - 1 MB/core)  ~12-15 cycles
    L3 cache  (~16 - 64 MB shared)   ~40-60 cycles
    Main RAM                         ~200+ cycles per cache miss

When multiple threads enter the picture, two threads writing to adjacent fields
inside the same 64-byte cache line trigger False Sharing: MESI cache coherency
forces the cores to bounce exclusive line ownership back and forth even though
no logical data is shared.

This file is split into four sections called from main at the bottom so you
can read top to bottom and run the program at any point.
*/

CACHE_LINE_SIZE :: 64
FALSE_SHARING_ITERS :: 20_000_000

Padded_Counter :: struct #align(64) {
	value: i64,
}

Bloated_Entity :: struct {
	pos_x:      f32,
	cold_state: [60]u8,
}

cache_lines_and_struct_padding :: proc() {

	/*
	When we write 'struct #align(64)', Odin forces both the struct's starting
	alignment and its padded size up to multiples of 64 bytes so every element
	in a [4]Padded_Counter array begins on its own private cache line.

	    Suppose bad: [4]i64 and good: [4]Padded_Counter:
	        size_of([4]i64)            == 32 bytes  (all 4 share 1 cache line!)
	        size_of([4]Padded_Counter) == 256 bytes (4 isolated cache lines!)

	Below, we also touch 'intrinsics.prefetch_read_data(&anchor_buf[0], 3)',
	which asks the CPU to pull a 64-byte line ahead of time (the locality
	argument 0..=3 must be a compile-time constant, where 3 keeps the line in
	all cache levels).
	*/

	// Here is a quick starter measurement of one cache-line prefetch and read:

	anchor_buf: [64]f32
	intrinsics.prefetch_read_data(&anchor_buf[0], 3)
	tick_start := time.tick_now()
	t0 := intrinsics.read_cycle_counter()
	anchor_sum := anchor_buf[0] + anchor_buf[15]
	t1 := intrinsics.read_cycle_counter()
	elapsed := time.tick_since(tick_start)
	fmt.printfln("line=%dB | Padded_Counter=%dB (align=%dB) | Bloated_Entity=%dB | sum=%v (%d cyc, %.2f us)",
		CACHE_LINE_SIZE, size_of(Padded_Counter), align_of(Padded_Counter),
		size_of(Bloated_Entity), anchor_sum, t1 - t0, time.duration_microseconds(elapsed))

	// Add compile-time #assert checks proving align_of(Padded_Counter) == CACHE_LINE_SIZE
	// and size_of(Padded_Counter) == CACHE_LINE_SIZE, then declare bad_counters: [4]i64
	// and good_counters: [4]Padded_Counter. Print size_of([4]i64), size_of([4]Padded_Counter),
	// offset_of(Padded_Counter, value), and the byte distance between slots:
	// uintptr(&bad_counters[1]) - uintptr(&bad_counters[0]) vs
	// uintptr(&good_counters[1]) - uintptr(&good_counters[0]).


	// Check cache-line boundaries directly on anchor_buf: compute how many f32
	// values fit in 64 bytes (CACHE_LINE_SIZE / size_of(f32)) and compare
	// uintptr(&anchor_buf[15]) / 64 against uintptr(&anchor_buf[16]) / 64 to see
	// index 16 cross into the next cache line.
}

working_set_and_bandwidth_cliffs :: proc() {

	/*
	Suppose you have 4,096 entities. Stored as []Bloated_Entity (64 bytes each),
	the array occupies 256 KB — eight times larger than a 32 KB L1d cache! Stored
	as a compact []f32 (16 KB), the entire working set sits inside L1d.

	Remember two rules when timing with intrinsics.read_cycle_counter():
	Always take the minimum cycle count across multiple repetitions (because OS
	interrupts only add positive noise), and always consume the final sum in a
	print statement so -o:speed cannot delete the loop via dead-code elimination.
	*/

	// Allocate bloated := make([]Bloated_Entity, 4096) and compact := make([]f32, 4096)
	// with defer delete on both. Initialize bloated[i].pos_x and compact[i] to
	// f32(i % 16) * 0.25. Over 16 repetitions, measure minimum RDTSC cycles
	// summing bloated[i].pos_x vs compact[i], assert both sums match, and print
	// the two min_cycles values and speedup ratio.


	// Observe the L3-to-RAM cliff directly: allocate small_buf := make([]f32, 4096)
	// (16 KB, L1-resident) and huge_buf := make([]f32, 8 * 1024 * 1024) (32 MB,
	// spills L3 into RAM on many CPUs) with defer delete. Fill both with 0.25,
	// time 4,096 sequential reads in small_buf vs 4,096 strided reads spaced by
	// 2048 floats across huge_buf over 16 repetitions, and print cycles per read.
}

stride_and_hardware_prefetching :: proc() {

	/*
	Sequential stride-1 reads let the hardware stream prefetcher pull upcoming
	64-byte cache lines before your loop asks for them. Jumping by 16 f32s
	(64 bytes) on every iteration defeats spatial locality completely: every
	single read lands on a cold cache line and wastes the other 15 floats.

	When your access pattern is irregular but predictable a few steps ahead,
	'intrinsics.prefetch_read_data(&stream[i + 16], 3)' warns the memory
	controller early so the line arrives in L1 before it is needed.
	*/

	// Allocate stream := make([]f32, 16384) (64 KB) with defer delete(stream)
	// and fill every slot with 0.5. Over 16 repetitions, record minimum RDTSC
	// cycles for 4,096 reads in three modes:
	// first, stride-1 sequential reading stream[i];
	// second, stride-16 scattered reading stream[(i * 16) % len(stream)];
	// third, stride-1 with if i + 16 < 4096 { intrinsics.prefetch_read_data(&stream[i + 16], 3) }.
	// Print all three min_cycles counts and checksums.
	//
	// Try uncommenting below to see Odin reject a runtime locality variable:
	// loc: i32 = 3; intrinsics.prefetch_read_data(&stream[0], loc)
}

false_sharing_multithreaded :: proc() {

	/*
	Now watch Multiplier #4 collide with multithreading. Suppose Thread 0
	updates bad[0] and Thread 1 updates bad[1] inside bad: [4]i64. Even though
	each thread touches its own index, both i64s sit inside the same 64-byte
	cache line! Every write forces MESI coherency to invalidate the other core's
	copy and ship the line across the interconnect.

	Under -o:speed, the compiler would hoist 'slot^ += 1' into a register and
	store only once at the end. Using 'intrinsics.volatile_load(slot)' and
	'intrinsics.volatile_store(slot, val + 1)' keeps every iteration as a real
	memory write so you can measure true cache-line bouncing on live threads.
	*/

	// Here is thread.Thread byte size so you can inspect the OS thread descriptor:

	fmt.printfln("size_of(thread.Thread)=%dB | false-sharing test iterations=%d", size_of(thread.Thread), FALSE_SHARING_ITERS)

	// Write two worker procedures outside main:
	// bump_unpadded :: proc(slot: ^i64)
	// bump_padded :: proc(slot: ^Padded_Counter)
	// Inside each, loop for _ in 0..<FALSE_SHARING_ITERS and update slot^ (or
	// &slot.value) using intrinsics.volatile_store(ptr, intrinsics.volatile_load(ptr) + 1).


	// In this section, declare shared_bad: [4]i64 and isolated_good: [4]Padded_Counter.
	// Time spawning 4 threads with thread.create_and_start_with_poly_data(&shared_bad[w], bump_unpadded),
	// waiting with thread.join_multiple(..threads[:]), and destroying each handle.
	// Repeat the exact same 4-thread run using &isolated_good[w] and bump_padded.
	// Measure both runs with time.tick_now() and intrinsics.read_cycle_counter(),
	// verify every counter equals FALSE_SHARING_ITERS, and print the speedup!
	// Try running with: odin run 705_cache_lines_bandwidth_and_false_sharing.odin -file -o:speed


	// Verify the best fix of all: write bump_local :: proc(slot: ^i64) that
	// accumulates local_count: i64 = 0 in a CPU register for FALSE_SHARING_ITERS
	// steps and writes slot^ += local_count once at the end. Time 4 threads
	// writing into a plain [4]i64 array with bump_local to confirm zero cache-line
	// bouncing during the loop.
}

main :: proc() {

	fmt.println("=== 1. Cache lines and #align(64) padding ===")
	cache_lines_and_struct_padding()

	fmt.println("\n=== 2. Working-set size and bandwidth cliffs ===")
	working_set_and_bandwidth_cliffs()

	fmt.println("\n=== 3. Stride patterns and hardware prefetching ===")
	stride_and_hardware_prefetching()

	fmt.println("\n=== 4. Live multithreaded false sharing ===")
	false_sharing_multithreaded()
}
