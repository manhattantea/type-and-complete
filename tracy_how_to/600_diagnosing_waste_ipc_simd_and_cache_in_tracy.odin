// odin run 600_diagnosing_waste_ipc_simd_and_cache_in_tracy.odin -file

package main

import "base:intrinsics"
import "core:fmt"
import "core:simd"
import "core:time"

/*
Once Tracy's Statistics view (sorted descending by Self Time or MTPC, meaning
Mean Time Per Call) points to your hottest zone, the next question is why that
zone is slow. Dividing minimum elapsed CPU cycles by the item count gives
cycles_per_item, and dividing bytes touched by minimum elapsed nanoseconds gives
effective_gb_per_sec (because 1 GB/s is literally 1 byte per nanosecond).

Together with Tracy's Source, Assembly, and CPU Counter views, those two
numbers separate Casey Muratori's single-core bottlenecks cleanly:
- If cycles_per_item sits above 20 with unexpected allocations or helper calls,
  Multiplier #1 (Waste) is burning cycles outside the real math.
- If waste is gone and cycles_per_item stays high alongside L1d or LLC cache
  misses and bloated struct stride, Multiplier #4 (Caching) is starving ports.
- If cache density is 100% and Assembly shows scalar addss/mulss writing to a
  single accumulator (IPC < 1.0), Multiplier #2 (IPC Stalls) is active.
- Once dependency chains are broken, scalar instructions still leave 75% to
  87.5% of vector width idle until Multiplier #3 (SIMD) packs lanes together.

For raw Odin syntax details on #soa, #align(64), #simd, and loop unrolling, see
../odin_how_to/700_soa_data_layout.odin,
../odin_how_to/705_cache_lines_bandwidth_and_false_sharing.odin,
../odin_how_to/710_simd_vectors.odin, and
../odin_how_to/715_ipc_dependency_chains_and_unrolling.odin.
*/

// 128-byte AoS struct: two full 64-byte cache lines per entity when only x and vx are hot.
Entity_AoS :: struct {
	x, y:    f32,
	vx, vy:  f32,
	padding: [28]f32,
}

// Lean SoA record: #soa[]Entity_SoA splits x, y, vx, vy into four contiguous arrays.
Entity_SoA :: struct {
	x, y:   f32,
	vx, vy: f32,
}

Zone_Diagnosis :: struct {
	name:           string,
	items:          int,
	min_cycles:     u64,
	min_ns:         i64,
	bytes_per_item: int,
}

zone_diagnosis_metrics :: proc() {

	/*
	Why measure BOTH cycles_per_item and effective_gb_per_sec? Because CPU clock
	frequency fluctuates under turbo boost, and bytes per nanosecond reveals
	whether you are actually saturating L1/L2/RAM bandwidth.

	When we compute effective_gb_per_sec := f64(total_bytes) / f64(min_ns), it
	means "how many billions of bytes moved per second" without needing any
	hardcoded GHz constant:

	    Suppose a zone updates 8,192 entities touching 8 bytes each (65,536 B)
	    and its fastest repetition finishes in 2,000 ns (2 microseconds).
	    65,536.0 / 2,000.0 equals 32.77 GB/s! Meanwhile, if the same loop uses
	    128-byte AoS records (1,048,576 B) and takes 25,000 ns, cycles_per_item
	    jumps ~12x and effective useful throughput drops to ~2.6 GB/s.

	Remember to reset mutable arrays before each repetition and take min_cycles
	and min_ns across repetitions, because OS interrupts only add positive noise.
	*/

	t0 := time.tick_now()
	c0 := intrinsics.read_cycle_counter()
	sample_diag := Zone_Diagnosis {
		name           = "Preview_SoA_Zone",
		items          = 1024,
		min_cycles     = 512,
		min_ns         = 160,
		bytes_per_item = 8,
	}
	c1 := intrinsics.read_cycle_counter()
	t1 := time.tick_now()
	probe_ns := max(time.duration_nanoseconds(time.tick_diff(t0, t1)), 1)
	preview_gbps := f64(sample_diag.items * sample_diag.bytes_per_item) / f64(sample_diag.min_ns)
	fmt.printfln(
		"Struct footprints: Entity_AoS=%d B vs Entity_SoA=%d B | Sample %s=%.2f GB/s (probe=%d cyc, %d ns)",
		size_of(Entity_AoS),
		size_of(Entity_SoA),
		sample_diag.name,
		preview_gbps,
		c1 - c0,
		probe_ns,
	)

	// Define print_zone_diagnosis :: proc(d: Zone_Diagnosis) above or inside this
	// scope. Compute cycles_per_item := f64(d.min_cycles) / f64(max(d.items, 1))
	// and effective_gb_per_sec := f64(d.items * d.bytes_per_item) / f64(max(d.min_ns, 1)).
	// Classify the bottleneck from those metrics:
	// - cycles_per_item > 20.0 && d.bytes_per_item <= 16 -> "Multiplier #1 (Waste)"
	// - cycles_per_item > 20.0 && d.bytes_per_item > 16  -> "Multiplier #1/#4 (Waste or AoS Cache)"
	// - d.bytes_per_item > 16                            -> "Multiplier #4 (AoS Cache Stride)"
	// - cycles_per_item > 1.5                            -> "Multiplier #2/#3 (IPC or Scalar)"
	// - otherwise                                        -> "Peak SIMD + Cache"
	// Print d.name, d.min_cycles, cycles_per_item, effective_gb_per_sec, d.bytes_per_item,
	// and the diagnosis label on one aligned line.
}

isolated_multiplier_stages :: proc() {

	/*
	If your first baseline mixes heap allocations, bloated AoS structs, AND a
	serial accumulator into one procedure, Tracy cannot show how much each
	multiplier contributed on its own. Isolating five clean stages lets you watch
	one bottleneck disappear at a time:

	- Stage 1 (step_aos_waste): adds per-item formatting via fmt.aprintf plus
	  delete inside the loop (Multiplier #1 Waste -> >20 cycles/item).
	- Stage 2 (step_aos_clean): strips the waste so only 128-byte AoS stride
	  remains (isolates Multiplier #4 Cache Waste).
	- Stage 3 (step_soa_serial): switches to #soa[]Entity_SoA so x and vx pack at
	  100% cache density, while keeping ONE serial total += aos_or_soa.x[i] chain
	  (isolates Multiplier #2 IPC Stalls).
	- Stage 4 (step_soa_ipc_4x): breaks the single dependency chain into four
	  independent accumulators s0..s3 stepping by i += 4 under #no_bounds_check
	  (a directive telling Odin to skip per-index bounds checks inside a proven
	  i + 4 <= n loop).
	- Stage 5 (step_soa_simd): processes 4 contiguous floats per lane with
	  #simd[4]f32, simd.fma(vx_v, dt_v, x_v), and direct vector stores using
	  intrinsics.unaligned_store((^#simd[4]f32)(&soa.x[i]), nx) instead of copying
	  lanes through simd.to_array!

	Suppose stack_x := [4]f32{1, 2, 3, 4} and stack_vx := [4]f32{10, 20, 30, 40}.
	Loading both into #simd[4]f32, running nx := simd.fma(vx_v, dt_v, x_v), and
	calling intrinsics.unaligned_store((^#simd[4]f32)(&stack_x[0]), nx) writes all
	4 updated floats back to memory in one vector store instruction.
	*/

	// Starter direct-vector-store demonstration so you see the exact syntax:
	stack_x := [4]f32{1.0, 2.0, 3.0, 4.0}
	stack_vx := [4]f32{10.0, 20.0, 30.0, 40.0}
	dt_v := #simd[4]f32{0.016, 0.016, 0.016, 0.016}
	x_v := simd.from_slice(#simd[4]f32, stack_x[:])
	vx_v := simd.from_slice(#simd[4]f32, stack_vx[:])
	nx_v := simd.fma(vx_v, dt_v, x_v)
	intrinsics.unaligned_store((^#simd[4]f32)(&stack_x[0]), nx_v)
	fmt.printfln("Direct #simd[4]f32 store anchor: x=%v | lane_sum=%.3f", stack_x, simd.reduce_add_ordered(nx_v))

	// Write Stage 1 (Multiplier #1 Waste):
	// Define step_aos_waste :: proc(aos: []Entity_AoS, dt: f32) -> f32
	// Inside the 0..<len(aos) loop, build label := fmt.aprintf("e_%d", i), check
	// len(label) > 0 before updating aos[i].x += aos[i].vx * dt and accumulating
	// total += aos[i].x, then delete(label). Notice how that single per-entity
	// heap allocation swamps the actual floating-point math in Tracy!


	// Write Stage 2 (Multiplier #4 Cache Stride isolated):
	// Define step_aos_clean :: proc(aos: []Entity_AoS, dt: f32) -> f32
	// Remove fmt.aprintf and delete completely, keeping the same aos[i].x += aos[i].vx * dt
	// update and single total accumulator over []Entity_AoS.


	// Write Stage 3 (Multiplier #2 Serial IPC isolated from Cache):
	// Define step_soa_serial :: proc(soa: #soa[]Entity_SoA, dt: f32) -> f32
	// Loop 0..<len(soa) updating soa.x[i] += soa.vx[i] * dt and summing into ONE
	// scalar total: f32 so cache density is 100% while the dependency chain remains.


	// Write Stage 4 (Multiplier #2 IPC fixed via 4-way unrolling):
	// Define step_soa_ipc_4x :: proc(soa: #soa[]Entity_SoA, dt: f32) -> f32
	// Maintain four independent accumulators s0, s1, s2, s3: f32, step i += 4
	// under #no_bounds_check while i + 4 <= len(soa), handle any tail elements
	// into s0, and return (s0 + s1) + (s2 + s3).


	// Write Stage 5 (Multiplier #3 SIMD with direct vector loads and stores):
	// Define step_soa_simd :: proc(soa: #soa[]Entity_SoA, dt: f32) -> f32
	// Broadcast dt_vec := #simd[4]f32(dt) and keep two vector accumulators v0, v1: #simd[4]f32.
	// Step i += 8 under #no_bounds_check: load x and vx at [i:i+4] and [i+4:i+8] via
	// simd.from_slice(#simd[4]f32, soa.x[i:i+4]), compute nx0 := simd.fma(vx0, dt_vec, x0),
	// write directly back with intrinsics.unaligned_store((^#simd[4]f32)(&soa.x[i]), nx0)
	// (no simd.to_array copy!), accumulate into v0 and v1, handle any < 8 tail
	// elements in scalar, and return simd.reduce_add_ordered(v0 + v1) + tail_sum.


	// Benchmark all 5 stages over N = 8_192 entities (32 repetitions each):
	// Allocate aos := make([]Entity_AoS, 8_192) (defer delete(aos)) and
	// soa := make(#soa[]Entity_SoA, 8_192) (defer delete_soa(soa)).
	// Reset initial x positions before EVERY repetition so repeated dt steps do not
	// drift! Capture both min_cycles (intrinsics.read_cycle_counter) and min_ns
	// (time.tick_now / time.tick_diff). Assert all 5 returned sums match within
	// 1e-2, print the checksum sink so -o:speed keeps every loop alive, and call
	// print_zone_diagnosis on all 5 stages (AoS uses bytes_per_item = 128, SoA uses 8).
}

l1_l2_l3_working_set_sweep :: proc() {

	/*
	Running a benchmark only at 1,024 entities (16 KB SoA / 128 KB AoS) hides one
	of the biggest clues in Tracy: the cache-hierarchy cliff!
	Typical x86_64/ARM64 cores hold roughly ~32 KB in L1d (~4-cycle hit),
	~512 KB–1 MB in L2 (~12–15 cycles), and ~16–32 MB in shared L3 (~40–60 cycles)
	before hitting main RAM (~200+ cycles).

	Suppose your SoA pass reads and writes 8 bytes per entity (x and vx) while
	AoS pulls 128 bytes per entity:
	- At 1,024 items: SoA active columns take 8 KB (L1d); AoS takes 128 KB (L2).
	- At 16,384 items: SoA takes 128 KB (L2); AoS takes 2 MB (L3).
	- At 131,072 items: SoA takes 1 MB (L2/L3 edge); AoS takes 16 MB (L3/RAM).
	- At 1,048,576 items: SoA takes 8 MB (L3); AoS takes 128 MB (Main RAM!).

	Sweeping across those four working-set sizes shows effective_gb_per_sec drop
	stepwise as the data spills out of each cache level.
	*/

	sweep_counts := [4]int{1_024, 16_384, 131_072, 1_048_576}
	fmt.println("Working-set footprint preview (AoS 128 B/item vs SoA active x+vx 8 B/item):")
	for n in sweep_counts {
		aos_kb := f64(n * size_of(Entity_AoS)) / 1024.0
		soa_active_kb := f64(n * 8) / 1024.0
		fmt.printfln("  N=%7d -> AoS=%8.1f KB | SoA_active=%7.1f KB", n, aos_kb, soa_active_kb)
	}

	// Run a working-set sweep over sweep_counts := [4]int{1_024, 16_384, 131_072, 1_048_576}:
	// For each n, allocate temporary aos and soa buffers (freeing at the end of each
	// iteration with delete(aos) and delete_soa(soa)), benchmark 8 repetitions of
	// step_aos_clean vs step_soa_simd (resetting x before each repetition and
	// taking min_cycles + min_ns), assert checksum parity within 1e-1, and print
	// cycles_per_item and effective_gb_per_sec for both AoS and SoA at each N!
	// Run with -o:speed to see the L1 -> L2 -> L3 -> RAM throughput cliff clearly.
}

main :: proc() {

	fmt.println("=== 1. Tracy zone diagnosis metrics (cycles/item and GB/s) ===")
	zone_diagnosis_metrics()

	fmt.println("\n=== 2. Isolating Multipliers #1, #4, #2, and #3 ===")
	isolated_multiplier_stages()

	fmt.println("\n=== 3. L1 / L2 / L3 working-set sweep ===")
	l1_l2_l3_working_set_sweep()
}
