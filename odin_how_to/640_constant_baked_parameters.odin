// odin run 640_constant_baked_parameters.odin -file

package main

import "core:fmt"

/*
Constant value baking mixes ordinary runtime parameters with compile-time
constant parameters prefixed by '$', such as '$clamp_unit: bool' or
'$Mode: Filter_Mode'.

Whenever a caller passes a constant value (like true, false, or .Hard_Clip),
Odin generates a dedicated procedure specialized for that exact constant. Inside
the body, a compile-time 'when' block tests that '$' parameter and strips the
untaken branch completely—no runtime 'if' check, no branch misprediction inside
tight audio, physics, or pixel loops.
*/

scale_baked :: proc(val: f32, $factor: int) -> f32 {

	#assert(factor > 0, "factor must be positive")
	return val * f32(factor)
}

// Write a sample-processing procedure with a baked boolean clamping flag:
// transform_samples :: proc(samples: []f32, gain: f32, $clamp_unit: bool)
// Loop over samples by reference with for &sample in samples, multiply each
// sample *= gain, and inside the loop write a compile-time when clamp_unit
// block calling sample = clamp(sample, -1.0, 1.0).

baked_flags_and_multipliers :: proc() {

	/*
	Because '$clamp_unit: bool' is known at compile time, calling
	transform_samples(buf, 2.0, false) emits a plain multiply loop with zero
	min/max instructions, while passing true bakes the clamp straight in.
	*/

	fmt.printfln("Starter baked scale: %v", scale_baked(2.5, 4))

	// Create raw_samples := [4]f32{0.2, -0.4, 0.8, -0.9} and
	// clamped_samples := raw_samples. Call transform_samples(raw_samples[:], 2.0, false)
	// and transform_samples(clamped_samples[:], 2.0, true), then print both
	// arrays to compare unclamped vs unit-clamped results.


	// Try uncommenting below to confirm a baked $ parameter rejects a runtime
	// boolean variable:
	// runtime_flag := true
	// transform_samples(nil, 1.0, runtime_flag)
}

Filter_Mode :: enum {
	Pass_Through,
	Rectify,
	Hard_Clip,
}

// Write an enum-specialized signal processor over Filter_Mode:
// apply_filter :: proc(samples: []f32, $Mode: Filter_Mode)
// Loop with for &sample in samples and use compile-time branching inside the
// loop:
// - when Mode == .Pass_Through: leave sample untouched
// - else when Mode == .Rectify: set sample = max(sample, 0.0)
// - else when Mode == .Hard_Clip: set sample = clamp(sample, -1.0, 1.0)

enum_mode_specialization :: proc() {

	/*
	Baking an enum parameter '$Mode: Filter_Mode' lets one loop serve multiple
	DSP or shader modes with zero per-sample switch overhead.

	    Suppose signal := [4]f32{-1.5, -0.2, 0.5, 1.8}:
	    Calling apply_filter(signal[:], .Rectify) specializes a tight loop that
	    only emits max(sample, 0.0), producing [0.0, 0.0, 0.5, 1.8].
	*/

	fmt.printfln("Filter modes available: %d", len(Filter_Mode))

	// Declare base_signal := [4]f32{-1.5, -0.2, 0.5, 1.8}, make two copies
	// rectified := base_signal and clipped := base_signal, call
	// apply_filter(rectified[:], .Rectify) and apply_filter(clipped[:], .Hard_Clip),
	// and print both arrays.


	// Write a small verification call to apply_filter(base_signal[:], .Pass_Through)
	// and print base_signal to confirm it remains unchanged.
}

main :: proc() {

	fmt.println("=== 1. Baked flags and multipliers ===")
	baked_flags_and_multipliers()

	fmt.println("\n=== 2. Enum mode specialization ===")
	enum_mode_specialization()
}
