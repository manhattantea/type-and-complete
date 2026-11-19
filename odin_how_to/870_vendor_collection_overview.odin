// odin run 870_vendor_collection_overview.odin -file

package main

import "core:c"
import "core:fmt"
import rl "vendor:raylib"
import stbi "vendor:stb/image"

/*
Most systems languages force you through external package managers, CMake
files, or manual C compilation just to load an image or open a window. Odin
ships a curated 'vendor:' collection directly inside the compiler distribution
(<odin_root>/vendor) with pre-configured bindings and prebuilt binaries for
raylib, sdl2, sdl3, glfw, vulkan, OpenGL, directx, wgpu, miniaudio, stb, box2d,
lua, microui, and cgltf.

Importing a vendor library requires zero external build config: the compiler
automatically resolves headers and links platform libraries (WinMM/GDI32 on
Windows, X11/GL/pthread on Linux, Cocoa/IOKit on macOS).

Even better, libraries like vendor:raylib and vendor:stb/image provide pure
headless routines (vectors, colors, collision math, in-memory image header
probing) that run cleanly in CLI tools and CI tests without opening a window.
For a full windowed 60-FPS game loop with a -headless test flag, see
980_raylib_arcade_lab.
*/

headless_raylib_math :: proc() {

	/*
	Raylib's rl.Vector2 is a [2]f32 array in Odin, so .x/.y field access and
	vector arithmetic (enemy_pos - player_pos) work natively without calling
	helper wrappers. Suppose circle A sits at {100, 150} with radius 25 and
	circle B sits at {130, 160} with radius 15: their center distance is ~31.6,
	which is less than 25 + 15 = 40, so rl.CheckCollisionCircles returns true.
	*/

	sample_color := rl.Color{255, 128, 0, 255}
	fmt.printfln("Headless Raylib Color RGBA: %v", sample_color)

	// Declare player_pos := rl.Vector2{100.0, 150.0} and
	// enemy_pos := rl.Vector2{130.0, 160.0}, compute delta := enemy_pos - player_pos,
	// and print player_pos, enemy_pos, and delta with fmt.printfln.


	// Call circles_hit := rl.CheckCollisionCircles(player_pos, 25.0, enemy_pos, 15.0)
	// and print circles_hit (expected: true) with fmt.printfln.


	// Declare raylib_red := rl.Color{230, 41, 55, 255}, convert it via
	// hsv := rl.ColorToHSV(raylib_red), and print hsv.x, hsv.y, hsv.z.


	// Declare obstacle := rl.Rectangle{x = 80, y = 120, width = 60, height = 40},
	// test box_hit := rl.CheckCollisionCircleRec(player_pos, 25.0, obstacle),
	// and print box_hit with fmt.printfln.


	// Test point-in-rectangle and alpha fading without a window:
	// inside := rl.CheckCollisionPointRec(rl.Vector2{100, 140}, obstacle)
	// faded := rl.Fade(raylib_red, 0.5)
	// Print inside and faded with fmt.printfln.
}

stb_image_memory_probe :: proc() {

	/*
	The vendor:stb/image package wraps Sean Barrett's single-header stb_image
	decoder. Because its from-memory procedures operate directly on a [^]u8
	byte buffer, you can inspect or decode embedded image assets without
	touching the filesystem.
	*/

	stbi.set_flip_vertically_on_load(1)
	dummy_bytes := [4]u8{0x00, 0x01, 0x02, 0x03}
	w, h, channels: c.int
	ok := stbi.info_from_memory(&dummy_bytes[0], c.int(len(dummy_bytes)), &w, &h, &channels)
	fmt.printfln("stbi.info_from_memory on 4 dummy bytes: ok=%d, reason=%s", ok, stbi.failure_reason())

	// Build a minimal 1x1 uncompressed TGA header + 1 RGBA pixel in a byte
	// array (18-byte TGA header with image_type=2, width=1, height=1, bpp=32,
	// followed by 4 pixel bytes {0, 255, 0, 255}), probe its dimensions with
	// stbi.info_from_memory, then decode it with:
	// pixels := stbi.load_from_memory(&tga[0], c.int(len(tga)), &w, &h, &channels, 4)
	// Free pixels with defer stbi.image_free(pixels) when non-nil and print the
	// decoded RGBA bytes pixels[0:4]!


	// Check HDR detection on the same byte buffer using
	// is_hdr := stbi.is_hdr_from_memory(&dummy_bytes[0], c.int(len(dummy_bytes)))
	// and print is_hdr (expected: 0) with fmt.printfln.
}

main :: proc() {

	fmt.println("=== 1. Headless Raylib math and collision ===")
	headless_raylib_math()

	fmt.println("\n=== 2. Headless stb/image memory probe ===")
	stb_image_memory_probe()
}
