// Raylib frame renderer and temp-allocated HUD formatting for 980_raylib_arcade_lab.

package main

import "core:fmt"
import rl "vendor:raylib"

/*
Raylib is a C library, so drawing HUD text with rl.DrawText requires a
null-terminated cstring rather than an Odin string. Instead of allocating a
permanent C string on the heap every frame and leaking 60 strings per second,
Odin provides 'fmt.ctprintf'. The 'c' means cstring and the 't' means it
allocates out of context.temp_allocator, which main.odin wipes clean at the end
of every frame with free_all(context.temp_allocator).

Suppose g.score is 300 and 21 invaders remain. Calling:

    hud := fmt.ctprintf("SCORE: %d  INVADERS: %d", g.score, len(g.invaders))

formats a transient null-terminated cstring valid for the current frame without
touching the general-purpose heap allocator. Pairing rl.BeginDrawing() with
'defer rl.EndDrawing()' guarantees the frame always closes cleanly even if a
render branch returns early.
*/

draw_game :: proc(g: ^Game_State) {

	rl.BeginDrawing()
	defer rl.EndDrawing()

	rl.ClearBackground(rl.BLACK)
	rl.DrawText(fmt.ctprintf("SCORE: %d  INVADERS: %d", g.score, len(g.invaders)), 16, 16, 20, rl.RAYWHITE)

	// Draw the player ship at g.player_pos with size rl.Vector2{40, 20} in
	// rl.GREEN using rl.DrawRectangleV.
	// Loop over g.bullets and draw each projectile at b.pos with radius b.radius
	// in rl.YELLOW via rl.DrawCircleV.
	// Loop over g.invaders and draw each inv.rect in rl.RED via rl.DrawRectangleRec.
	// When g.game_over is true, draw a "VICTORY!" banner across the center of
	// the screen with rl.DrawText.
}
