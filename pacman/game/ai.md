# AI architecture

This document describes the enemy AI implemented in
`pacman/game/ai.py` and how it is used by the game entities.

## Class diagram

```text
                              AIDebugTrace
                                   ^
                                   |
        +--------------------------+--------------------------+
        |                          |                          |
        v                          v                          v
   StrategyAI              EnemyStateController           EnemyBrain
   pathfinding             timed state changes            state router
   decisions                                             target routing
        ^
        |
        +-- ScatterAI
        +-- ChaseAI
        +-- FrightenedAI
        +-- EatenAI

   ChaseContext  --------->  EnemyBrain.compute_target()
```

## AI states

The `State` enum defines the four supported enemy states:

- `CHASE`: the enemy moves toward a computed chase target.
- `SCATTER`: the enemy alternates between its scatter corner and the maze
  center.
- `FRIGHTENED`: the enemy chooses random movement while avoiding immediate
  reversal when possible.
- `EATEN`: the enemy returns to its respawn/scatter position.

## Debug data

### `AIDebugEvent`

Typed dictionary used to store one raw debug event:

- `frame`: debug frame counter.
- `actor`: enemy or AI actor identifier.
- `message`: recorded debug message.

### `AIDebugRow`

Typed dictionary used by the rendering layer. It extends `AIDebugEvent` with:

- `state`: inferred state label.
- `color`: RGB color associated with the inferred state.

### `AIDebugTrace`

Collects AI debug events without relying on scattered `print()` calls.

Key responsibilities:

- Keep a bounded `deque` of recent AI events.
- Increment a frame counter with `begin_frame()`.
- Record events with `record()`.
- Return raw events with `get_events()`.
- Return formatted strings with `get_lines()` and `format_event()`.
- Build render-ready rows with `render_rows()`.
- Dump new events to the console with `dump_to_console()`.

## State controller

### `EnemyStateController`

Handles timed transitions between enemy states.

Internal fallback timings are:

```text
scatter_duration    = 6.0 seconds
chase_duration      = 7.0 seconds
frightened_duration = 6.0 seconds
eaten_duration      = 3.0 seconds
```

These values are used only when no valid `durations_map` reaches the
controller. In normal level spawning, `enemy_factory.extract_level_ai_config()`
passes level timings to `EnemyBrain`.

Transition rules:

- `EATEN` has priority until its timer expires, then returns to the default
  state.
- `FRIGHTENED` starts when the player is powered and remains time-boxed.
- `SCATTER` and `CHASE` alternate automatically when the default state allows
  cycling.
- If cycling is disabled, the controller keeps returning the default state.

The main method is:

```python
next_state(current_state, player_powered, delta_seconds)
```

## Shared strategy behavior

### `StrategyAI`

Base class used by all concrete AI behaviors.

Main responsibilities:

- Convert the integer maze grid into direction tokens with `stringify_maze()`.
- Check bounds with `is_in_bounds()`.
- List legal moves with `next_move()`.
- Compute neighboring cells with `get_neighbors()`.
- Find paths with `astar_path()`.
- Select a pathfinding direction with `default_pathfinding()`.
- Apply movement with `change_position()`.
- Dispatch generic behavior decisions with `decision()`.

`default_pathfinding()` first tries A*. If no path is found, it falls back to a
local greedy move that avoids an immediate U-turn unless no other move exists.

## Concrete strategies

### `ScatterAI`

Implements scatter behavior.

- Starts by targeting the enemy scatter corner.
- Finds a walkable center cell near the geometric center of the maze.
- Alternates between the scatter corner and the center.
- Changes target only when the current target is reached exactly.

### `ChaseAI`

Implements chase movement.

It receives an already computed target position and moves toward it with the
shared pathfinding logic.

### `FrightenedAI`

Implements frightened movement.

- Chooses a random legal direction.
- Avoids immediate reversal when another valid move exists.
- Keeps the current direction if no move is available.

### `EatenAI`

Implements eaten movement.

It ignores the incoming target and pathfinds back to its `respawn_position`.
In the current setup, that respawn position is initialized from the enemy
scatter corner.

## Enemy brain

### `EnemyBrain`

`EnemyBrain` is the main orchestrator attached to each enemy sprite.

It owns:

- One `EnemyStateController`.
- One behavior instance for each state.
- A unified current position.
- A unified current direction.
- A unified current target.
- Scatter round tracking fields used for debug and timing display.

Key methods:

- `transition_state(player_powered, delta_seconds)`: updates the active state.
- `compute_target(context)`: computes the chase target for the current enemy.
- `decision(target_position)`: asks the active behavior for the next direction.
- `change_position(move)`: applies a legal movement to the active behavior.
- `scatter_round_summary()`: returns scatter timing information for debug
  display.

When the active state changes, `EnemyBrain` keeps the shared position and
direction synchronized across the behavior instances.

## Chase targeting

### `ChaseContext`

`ChaseContext` bundles the information needed to compute a chase target:

- `enemy_type`: enemy behavior type, such as `blinky`, `pinky`, `inky`, or
  `clyde`.
- `player_grid`: player position in maze coordinates.
- `player_direction`: current player direction.
- `enemy_grid`: current enemy position in maze coordinates.
- `enemy_scatter_corner`: enemy scatter corner.
- `all_enemies_grid`: current grid positions for all enemies.

### Target rules

The actual targeting logic currently lives in `EnemyBrain.compute_target()`.
The `Blinky`, `Pinky`, `Inky`, and `Clyde` classes still exist in the file, but
they are only empty placeholders at the moment.

#### Blinky

```text
target = player position
```

#### Pinky

```text
target = player position + 4 tiles in the player direction
```

#### Inky

```text
p_ahead = player position + 2 tiles in the player direction
target = p_ahead + (blinky position - player position)
```

If Blinky cannot be found in `all_enemies_grid`, Inky falls back to `p_ahead`.

#### Clyde

```text
if manhattan_distance(clyde, player) > 8:
    target = player position
else:
    target = clyde scatter corner
```

Every computed target is clamped to the maze bounds when possible.

## Runtime flow

The enemy sprite update loop in `pacman/game/entities.py` uses the AI in this
order:

1. Convert frame time from milliseconds to seconds.
2. Call `EnemyBrain.transition_state(player_powered, delta_seconds)`.
3. When the enemy reaches its current cell center, synchronize the AI grid
   position.
4. If the enemy just entered `FRIGHTENED`, force an immediate reversal when
   possible.
5. Build a `ChaseContext` from the player, the current enemy, and all enemies.
6. Call `EnemyBrain.compute_target(chase_context)`.
7. Call `EnemyBrain.decision(target_grid)`.
8. Call `EnemyBrain.change_position(next_direction)`.
9. Convert the new grid target back to world coordinates for smooth movement.

## Configured durations

AI timings are not hardcoded per maze size in this document anymore.

Each level can provide an `ai` configuration mapping with:

```json
{
  "scatter_duration": 6.0,
  "chase_duration": 7.0,
  "frightened_duration": 6.0,
  "eaten_duration": 7.0
}
```

The values are loaded through `pacman/game/levels/enemy_factory.py` and passed
to each `EnemyBrain`. If no level configuration is available, the factory uses
the values shown above. If malformed values still reach `EnemyStateController`,
the controller keeps its internal fallback timings.

## Scatter Duration Reference

This table is kept as a personal reference for observed scatter travel times.
It is not the source of truth for runtime AI timings. The actual state durations
come from the level `ai` configuration described above.

```text
size    blinky      pinky       inky        clyde
4       2.53        3.11        1.85        1.21
5       2.50        3.76        2.50        5.03
6       3.78        3.14        4.39        2.47
7       3.74        3.74        7.47        2.79
8       6.30        4.44        5.64        7.47
9       6.31        5.07        6.27        6.26
10      7.59        5.69        5.66        5.03
11      7.55        8.75        7.53        6.25
12      7.60        6.95        8.22        7.57
13      11.31       7.55        8.81        10.02
14      8.21        8.86        17.71       13.29
15      10.00       11.37       11.35       11.33
16      10.69       16.43       8.85        10.67
17      15.22       16.64       10.21       11.42
18      12.48       11.93       20.67       17.58
19      16.45       16.52       12.63       12.62
20      17.18       17.82       16.54       17.20
```

## Notes

- The scatter duration table is kept for reference only because current timings
  are driven by level configuration.
- `Blinky`, `Pinky`, `Inky`, and `Clyde` can later become real strategy
  classes, but the current implementation centralizes their target formulas in
  `EnemyBrain.compute_target()`.
- The AI works in maze grid coordinates. Rendering and interpolation are
  handled by the entity layer.
