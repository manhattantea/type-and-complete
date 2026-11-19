// Arcade game state and zero-heap simulation logic for 980_raylib_arcade_lab.

package main

import rl "vendor:raylib"

/*
Game_State keeps every active bullet and invader inside fixed-capacity
stack-backed dynamic arrays ([dynamic; 32]Bullet and [dynamic; 24]Invader).
Unlike a heap [dynamic]T, a fixed-capacity [dynamic; N]T stores its backing
buffer inline inside Game_State, so appending or removing entities during the
60-FPS loop triggers zero heap allocations and zero fragmentation.

When removing dead bullets or hit invaders, 'unordered_remove(&arr, i)' swaps
the element at index i with the final element and shrinks len(arr) by 1 in
constant time without shifting the rest of the array.

Suppose bullets holds [B0, B1, B2, B3] and you walk backward from i = 3 down
to 0. If B1 leaves the screen and you call unordered_remove(&bullets, 1), B3
moves into slot 1, leaving [B0, B3, B2]—and since slot 3 was already checked on
the previous iteration, decrementing i to 0 visits B0 next without skipping B3.
*/

SCREEN_WIDTH  :: 800
SCREEN_HEIGHT :: 600

Bullet :: struct {
	pos:    rl.Vector2,
	vel_y:  f32,
	radius: f32,
}

Invader :: struct {
	rect:  rl.Rectangle,
	speed: f32,
	alive: bool,
}

Game_State :: struct {
	player_pos: rl.Vector2,
	bullets:    [dynamic; 32]Bullet,
	invaders:   [dynamic; 24]Invader,
	score:      int,
	game_over:  bool,
}

init_game :: proc(g: ^Game_State) {

	g^ = {}
	g.player_pos = rl.Vector2{f32(SCREEN_WIDTH) * 0.5 - 20, f32(SCREEN_HEIGHT) - 50}

	// Populate g.invaders with 24 enemies arranged in 3 rows of 8 columns.
	// Loop row in 0..<3 and col in 0..<8, compute evenly spaced x and y
	// coordinates inside the 800x600 playfield, and append an Invader with
	// rect = rl.Rectangle{x, y, 40, 24}, speed = 70.0, and alive = true into
	// &g.invaders.
}

// Write update_game :: proc(g: ^Game_State, dt: f32, headless := false)
// Return immediately if g.game_over is true.
// When !headless, poll rl.IsKeyDown(.LEFT) / rl.IsKeyDown(.A) and
// rl.IsKeyDown(.RIGHT) / rl.IsKeyDown(.D) to shift g.player_pos.x at
// 300.0 * dt clamped to 0..=f32(SCREEN_WIDTH - 40). When
// rl.IsKeyPressed(.SPACE) is true and len(g.bullets) < cap(g.bullets), append
// a Bullet at {g.player_pos.x + 20, g.player_pos.y} with vel_y = -480.0 and
// radius = 5.0 into &g.bullets.
// Walk backward over g.bullets with: for i := len(g.bullets) - 1; i >= 0; i -= 1
// Advance g.bullets[i].pos.y += g.bullets[i].vel_y * dt, and remove off-screen
// shots (g.bullets[i].pos.y < 0) via unordered_remove(&g.bullets, i).
// Move each invader's rect.x by inv.speed * dt (reversing speed when hitting
// the left or right screen edges), then check each bullet against each invader
// with rl.CheckCollisionCircleRec(b.pos, b.radius, inv.rect): on hit, remove
// both invader and bullet via unordered_remove, add 100 to g.score, and set
// g.game_over = true once len(g.invaders) == 0.
