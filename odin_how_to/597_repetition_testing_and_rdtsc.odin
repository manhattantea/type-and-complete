// odin run 597_repetition_testing_and_rdtsc.odin -file

package main

import "base:intrinsics"
import "core:fmt"
import "core:time"

/*
Once a profiler (Spall or Tracy) points you to a genuine hotspot, you still
need to answer two engineering questions: did your rewrite actually shrink the
hardware cost, and how close is the loop to your CPU's physical throughput
ceiling in bytes per cycle or gigabytes per second?

Casey Muratori's Repetition Testing method (Computer, Enhance! Parts 2 & 3)
runs the exact same workload many times in a row and watches the minimum
observed cost rather than just the average. OS interrupts, page faults, and
power-state shifts only ever add positive stalls to a deterministic CPU loop—
never negative time—so min_cycles converges on the true uninterrupted cost of
the machine code.
*/

Repetition_Stats :: struct {
	min_cycles:    u64,
	max_cycles:    u64,
	total_cycles:  u64,
	runs:          u64,
	bytes_per_run: u64,
}

// Implement record_sample :: proc(stats: ^Repetition_Stats, cycles: u64)
// right here at file scope once you start the first section:
// When stats.runs == 0, initialize stats.min_cycles = cycles and
// stats.max_cycles = cycles. On every subsequent run, update
// stats.min_cycles = min(stats.min_cycles, cycles) and
// stats.max_cycles = max(stats.max_cycles, cycles). Always add
// stats.total_cycles += cycles and increment stats.runs += 1.

rdtsc_and_min_cycles_theory :: proc() {

	/*
	Calling intrinsics.read_cycle_counter() emits a single hardware timestamp
	instruction (RDTSC on x86_64, CNTVCT_EL0 on ARM64) in user space. Pairing
	it with time.tick_now() lets us record both hardware reference cycles and
	nanoseconds so we can convert byte count into GB/s.

	Why trust min_cycles over the mean?

	    Suppose 32 runs produce 31 samples around 4,200 cycles and 1 sample at
	    98,000 cycles because the OS scheduler preempted your thread mid-loop.
	    The average jumps from 4,200 to 7,137 cycles (+70% noise!), whereas
	    min_cycles stays pinned at 4,200—revealing the true loop speed.

	One critical compiler rule when compiling with -o:speed: if your benchmark
	loop computes a sum that is never read afterward, LLVM's dead-code
	elimination (DCE) will erase the entire loop and report ~0 cycles. Always
	fold each run's result into a checksum_sink printed at the end!
	*/

	t0 := time.tick_now()
	c0 := intrinsics.read_cycle_counter()
	anchor := Repetition_Stats{bytes_per_run = 64}
	c1 := intrinsics.read_cycle_counter()
	elapsed_ns := time.duration_nanoseconds(time.tick_since(t0))
	fmt.printfln("RDTSC probe: delta=%d cycles | wall=%d ns | stats=%d B (runs=%d)",
		c1 - c0, elapsed_ns, size_of(Repetition_Stats), anchor.runs)

	// After writing record_sample :: proc(stats: ^Repetition_Stats, cycles: u64),
	// feed five synthetic samples {4200, 4150, 98000, 4180, 4160} into a local
	// Repetition_Stats and print min_cycles, max_cycles, and average cycles to
	// confirm the 98,000-cycle OS spike does not corrupt min_cycles.
}

l1_repetition_and_dce_sink :: proc() {

	/*
	When we compute gigabytes per second using:

	    gb_per_sec := f64(bytes_per_run) / f64(max(min_ns, 1))

	notice the units cancel directly: 1 GB is 10^9 bytes and 1 second is 10^9
	nanoseconds, so bytes divided by nanoseconds equals GB/s with no extra
	scaling constants!

	A 16 KB buffer (2,048 u64 elements) sits comfortably inside a modern CPU's
	~32 KB L1 data cache. Once warmed on pass 0, every element streams straight
	from L1 at peak cache bandwidth.
	*/

	buf := make([]u64, 2048)
	defer delete(buf)
	for i in 0 ..< 8 {
		buf[i] = u64(i + 1)
	}
	fmt.printfln("L1 test slice ready: %d elements (%d KB)",
		len(buf), (len(buf) * size_of(u64)) / 1024)

	// Fill all 2,048 elements of buf with u64(i + 1), and write a file-scope
	// helper sum_u64_slice :: proc(data: []u64) -> u64 that sums every element.


	// Run 32 repetitions over buf[:] tracking stats := Repetition_Stats{bytes_per_run = u64(len(buf) * size_of(u64))},
	// min_ns := max(i64), and checksum_sink: u64. On each iteration:
	// capture t_start := time.tick_now() and c_start := intrinsics.read_cycle_counter(),
	// call local_sum := sum_u64_slice(buf[:]), capture c_end and run_ns, call
	// record_sample(&stats, c_end - c_start), update min_ns = min(min_ns, run_ns),
	// and fold checksum_sink ~= local_sum so -o:speed cannot erase the loop.


	// Compute cycles_per_element := f64(stats.min_cycles) / f64(len(buf)),
	// avg_cycles := f64(stats.total_cycles) / f64(stats.runs), and
	// gb_per_sec := f64(stats.bytes_per_run) / f64(max(min_ns, 1)). Print
	// min_cycles, max_cycles, avg_cycles, cycles_per_element, gb_per_sec, and
	// checksum_sink.
}

l3_cache_sweep_and_bandwidth :: proc() {

	/*
	Now scale the working set up 512x from 16 KB to 8 MB (1,048,576 u64 values).
	Because 8 MB exceeds L1 (~32 KB) and L2 (~512 KB–1 MB), each pass spills
	into shared L3 cache or main RAM. Watching cycles_per_element climb and
	GB/s drop across that exact same sum_u64_slice procedure shows why cache
	residency—not arithmetic—governs data-heavy loops.
	*/

	big_buf := make([]u64, 1024 * 1024)
	defer delete(big_buf)
	big_buf[0] = 1
	big_buf[len(big_buf) - 1] = u64(len(big_buf))
	fmt.printfln("L3/RAM sweep buffer allocated: %d MB (%d bytes)",
		(len(big_buf) * size_of(u64)) / (1024 * 1024), len(big_buf) * size_of(u64))

	// Populate all 1,048,576 elements of big_buf (big_buf[i] = u64(i + 1)),
	// then sweep both slices using the exact same 32-repetition harness:
	// - l1_slice := big_buf[:2048] (16 KB)
	// - l3_slice := big_buf[:]     (8 MB)
	// Keep a single checksum_sink printed at the end so neither sweep is pruned.


	// Print L1 (16 KB) vs L3 (8 MB) side by side: min_cycles, cycles_per_element,
	// and gb_per_sec. Run once with 'odin run 597_repetition_testing_and_rdtsc.odin -file'
	// and once with '-o:speed' to compare debug codegen against optimized codegen!
}

main :: proc() {

	fmt.println("=== 1. RDTSC and min_cycles theory ===")
	rdtsc_and_min_cycles_theory()

	fmt.println("\n=== 2. L1 repetition test and DCE checksum sink ===")
	l1_repetition_and_dce_sink()

	fmt.println("\n=== 3. L1 (16 KB) vs L3 (8 MB) cache sweep and GB/s ===")
	l3_cache_sweep_and_bandwidth()
}
