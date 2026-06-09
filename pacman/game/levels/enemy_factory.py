from dataclasses import dataclass
from typing import TYPE_CHECKING

from pacman.game.ai import EnemyBrain, State
from pacman.game.entities import Ennemy
from pacman.game.type_defs import AIConfig, SkinAnimation
from pacman.resources import TILE_SIZE

if TYPE_CHECKING:
    from pacman.game.game import Game


@dataclass(frozen=True)
class EnemySpec:
    """Describe how to spawn one level enemy."""
    spawn_grid: tuple[int, int]
    skin_anim: SkinAnimation
    enemy_type: str
    enemy_id: str
    scatter_corner: tuple[int, int]


def _default_ai_config() -> AIConfig:
    """Return default AI timing values.

    Returns:
        Default AI duration mapping.
    """
    return {
        "scatter_duration": 6.0,
        "chase_duration": 7.0,
        "frightened_duration": 6.0,
        "eaten_duration": 7.0,
    }


def extract_level_ai_config(game: "Game") -> AIConfig:
    """Read AI timings for the current level.

    Args:
        game: Shared game object that owns resources, groups, and state.

    Returns:
        AI duration mapping for the current level.
    """
    level_map = game.config["level"][0]
    level_id = game.current_level_id

    if level_id is None:
        level_id = next(iter(level_map.keys()), None)

    if level_id is None:
        return _default_ai_config()

    level_cfg = level_map.get(str(level_id))
    if level_cfg is None:
        return _default_ai_config()
    return level_cfg["ai"]


def grid_to_world(game: "Game", gx: int, gy: int) -> tuple[int, int]:
    """Convert a maze grid coordinate to world pixels.

    Args:
        game: Shared game object that owns resources, groups, and state.
        gx: Horizontal grid coordinate.
        gy: Vertical grid coordinate.

    Returns:
        World pixel coordinate at the center of the cell.
    """
    cell_size = TILE_SIZE * 2
    center_offset = TILE_SIZE

    return (
        gx * cell_size + game.maze_offset_x + center_offset,
        gy * cell_size + game.maze_offset_y + center_offset,
    )


def spawn_enemies(
    game: "Game",
    enemy_specs: list[EnemySpec],
    default_state: State = State.SCATTER,
    durations_map: AIConfig | None = None,
) -> list[Ennemy]:
    """Instantiate enemies from spawn specifications.

    Args:
        game: Shared game object that owns resources, groups, and state.
        enemy_specs: Enemy spawn definitions to instantiate.
        default_state: Initial AI state for the behavior.
        durations_map: AI duration overrides for the enemies.

    Returns:
        Spawned enemy sprites.
    """
    durations_map = durations_map or extract_level_ai_config(game)
    spawn_points: list[tuple[int, int]] = []
    spawned_enemies: list[Ennemy] = []

    for index, spec in enumerate(enemy_specs, start=1):
        spawn_x, spawn_y = grid_to_world(game, *spec.spawn_grid)
        spawn_points.append((spawn_x, spawn_y))
        spawned_enemies.append(
            Ennemy(
                game,
                spawn_x,
                spawn_y,
                EnemyBrain(
                    game.maze_grid,
                    spec.spawn_grid,
                    spec.scatter_corner,
                    default_state=default_state,
                    debug_trace=game.ai_debug_trace,
                    enemy_id=spec.enemy_id or f'E{index}',
                    durations_map=durations_map,
                ),
                spec.skin_anim,
                enemy_type=spec.enemy_type,
            )
        )

    game.enemies_spawn_points = spawn_points
    return spawned_enemies
