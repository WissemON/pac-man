import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pacman.game.sprites import SpriteSheet
from pacman.game.type_defs import BiomeAssets, BiomeConfig, SkinAnimation
from pacman.resources import TILE_SIZE, resource_path

if TYPE_CHECKING:
    from pacman.game.game import Game


class Level(ABC):
    """Provide shared setup and helpers for themed levels."""

    bgm_intro: str
    bgm_loop: str
    bgm_cheat: str
    biomes_config: BiomeConfig
    blinky: SkinAnimation
    clyde: SkinAnimation
    inky: SkinAnimation
    pinky: SkinAnimation

    def __init__(self, game: "Game", maze_grid: list[list[int]]) -> None:
        """Initialize the level.

        Args:
            game: Shared game object that owns resources, groups, and state.
            maze_grid: Maze grid used for layout and pathfinding.
        """
        self.item_spawn_delay = 10000.0
        self.item_spawn_timer = 0.0
        self.item_spawned = False
        self.game = game
        self.maze_grid = maze_grid
        self._load_default_enemy_skins()
        self.bgm_cheat = resource_path(
            'music/zelda_theme.mp3')

    def _load_default_enemy_skins(self) -> None:
        """Load the default enemy sprite animations."""
        enemy_sheet = SpriteSheet(resource_path(
            'enemies', 'octorok.gif'), self.game)
        cat_sheet = SpriteSheet(
            resource_path('enemies', 'cats.gif'), self.game)

        if self.game.cheat is False:
            self.blinky = {
                'down': [
                    enemy_sheet.get_sprite(41, 23, 16, 15, (255, 0, 255)),
                    enemy_sheet.get_sprite(11, 23, 16, 15, (255, 0, 255))
                ],
                'up': [
                    enemy_sheet.get_sprite(10, 87, 16, 14, (255, 0, 255)),
                    enemy_sheet.get_sprite(43, 84, 16, 14, (255, 0, 255)),
                ],
                'left': [
                    enemy_sheet.get_sprite(14, 45, 14, 15, (255, 0, 255)),
                    enemy_sheet.get_sprite(41, 45, 16, 14, (255, 0, 255)),
                ],
                'right': [
                    enemy_sheet.get_sprite(14, 64, 14, 15, (255, 0, 255)),
                    enemy_sheet.get_sprite(39, 65, 16, 14, (255, 0, 255))
                ]
            }
        else:
            right = [
                cat_sheet.get_sprite(22, 141, 27, 17),
                cat_sheet.get_sprite(50, 141, 28, 18),
                cat_sheet.get_sprite(79, 141, 28, 17),
                cat_sheet.get_sprite(108, 141, 28, 18)
            ]
            left = [
                pygame.transform.flip(f, True, False) for f in right
            ]
            self.blinky = {
                'down': [
                    cat_sheet.get_sprite(256, 166, 20, 14),
                ],
                'up': [
                    cat_sheet.get_sprite(295, 159, 16, 21),
                ],
                'left': left,
                'right': right
            }

        if self.game.cheat is False:
            self.clyde = {
                'down': [
                    enemy_sheet.get_sprite(157, 72, 16, 15, (255, 0, 255)),
                    enemy_sheet.get_sprite(184, 74, 16, 15, (255, 0, 255))
                ],
                'up': [
                    enemy_sheet.get_sprite(157, 138, 16, 14, (255, 0, 255)),
                    enemy_sheet.get_sprite(186, 139, 16, 14, (255, 0, 255)),
                ],
                'left': [
                    enemy_sheet.get_sprite(156, 95, 14, 15, (255, 0, 255)),
                    enemy_sheet.get_sprite(184, 97, 16, 14, (255, 0, 255)),
                ],
                'right': [
                    enemy_sheet.get_sprite(158, 116, 14, 15, (255, 0, 255)),
                    enemy_sheet.get_sprite(186, 116, 16, 14, (255, 0, 255))
                ]
            }
        else:
            right = [
                cat_sheet.get_sprite(22, 190, 27, 17),
                cat_sheet.get_sprite(50, 189, 28, 18),
                cat_sheet.get_sprite(79, 190, 28, 17),
                cat_sheet.get_sprite(108, 189, 28, 18)
            ]
            left = [
                pygame.transform.flip(f, True, False) for f in right
            ]
            self.clyde = {
                'down': [
                    cat_sheet.get_sprite(256, 215, 20, 14),
                ],
                'up': [
                    cat_sheet.get_sprite(311, 206, 17, 23),
                ],
                'left': left,
                'right': right
            }

        if self.game.cheat is False:
            self.inky = {
                'down': [
                    enemy_sheet.get_sprite(10, 138, 16, 15, (255, 0, 255)),
                    enemy_sheet.get_sprite(44, 138, 16, 15, (255, 0, 255))
                ],
                'up': [
                    enemy_sheet.get_sprite(9, 198, 16, 14, (255, 0, 255)),
                    enemy_sheet.get_sprite(45, 197, 16, 14, (255, 0, 255)),
                ],
                'left': [
                    enemy_sheet.get_sprite(9, 157, 14, 15, (255, 0, 255)),
                    enemy_sheet.get_sprite(43, 159, 16, 14, (255, 0, 255)),
                ],
                'right': [
                    enemy_sheet.get_sprite(11, 177, 14, 15, (255, 0, 255)),
                    enemy_sheet.get_sprite(45, 179, 16, 14, (255, 0, 255))
                ]
            }
        else:
            right = [
                cat_sheet.get_sprite(22, 0, 27, 17),
                cat_sheet.get_sprite(50, 0, 28, 18),
                cat_sheet.get_sprite(79, 0, 28, 17),
                cat_sheet.get_sprite(108, 0, 28, 18)
            ]
            left = [
                pygame.transform.flip(f, True, False) for f in right
            ]
            self.inky = {
                'down': [
                    cat_sheet.get_sprite(90, 44, 18, 19),
                ],
                'up': [
                    cat_sheet.get_sprite(71, 44, 18, 19),
                ],
                'left': left,
                'right': right
            }

        pink = SpriteSheet(resource_path('enemies', 'octorok_pinky.png'),
                           self.game)

        if self.game.cheat is False:
            self.pinky = {
                'down': [
                    pink.get_sprite(0, 0, 16, 15, (255, 0, 255)),
                    pink.get_sprite(35, 0, 16, 15, (255, 0, 255))
                ],
                'up': [
                    pink.get_sprite(0, 60, 16, 14, (255, 0, 255)),
                    pink.get_sprite(36, 59, 16, 14, (255, 0, 255)),
                ],
                'left': [
                    pink.get_sprite(0, 19, 14, 15, (255, 0, 255)),
                    pink.get_sprite(34, 21, 16, 14, (255, 0, 255)),
                ],
                'right': [
                    pink.get_sprite(2, 39, 14, 15, (255, 0, 255)),
                    pink.get_sprite(36, 41, 16, 14, (255, 0, 255))
                ]
            }
        else:
            right = [
                cat_sheet.get_sprite(22, 70, 27, 17),
                cat_sheet.get_sprite(50, 70, 28, 18),
                cat_sheet.get_sprite(79, 70, 28, 17),
                cat_sheet.get_sprite(108, 70, 28, 18)
            ]
            left = [
                pygame.transform.flip(f, True, False) for f in right
            ]
            self.pinky = {
                'down': [
                    cat_sheet.get_sprite(256, 95, 20, 14),
                ],
                'up': [
                    cat_sheet.get_sprite(295, 88, 16, 21),
                ],
                'left': left,
                'right': right
            }

    @abstractmethod
    def setup(self) -> None:
        """Build the level sprites and gameplay objects."""
        pass

    def setup_enemies(self) -> None:
        """Spawn the enemies for the level."""
        return None

    @abstractmethod
    def spawn_random_item(self) -> None:
        """Spawn a special item on a free maze cell."""
        pass

    @abstractmethod
    def fill_background(self, surface: pygame.Surface) -> None:
        """Fill the render surface with the level background.

        Args:
            surface: Surface that receives drawing operations.
        """
        pass

    @abstractmethod
    def render_special(self, surface: pygame.Surface) -> None:
        """Render level-specific overlay visuals.

        Args:
            surface: Surface that receives drawing operations.
        """
        pass

    def reserved_cells(self) -> set[tuple[int, int]]:
        """Return maze cells reserved for starts and enemies.

        Returns:
            Set of reserved maze cells.
        """
        cols = len(self.maze_grid[0])
        rows = len(self.maze_grid)
        reserved = {
            ((cols - 1) // 2, (rows - 1) // 2),  # center cell for Link
            (0, 0),  # super pac gum
            (cols - 1, 0),  # super pac gum
            (0, rows - 1),  # super pac gum
            (cols - 1, rows - 1)  # super pac gum
        }

        for y, maze_row in enumerate(self.maze_grid):
            for x, cell in enumerate(maze_row):
                if cell == 15:
                    reserved.add((x, y))

        return reserved

    def _rect_overlaps_tunnel(
        self,
        x: int,
        y: int,
        margin: int = 24,
    ) -> bool:
        """Provide internal rect overlaps tunnel behavior.

        Args:
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            margin: Pixel distance accepted around tunnel entrances.

        Returns:
            True when the requested condition is met.
        """
        lx, ly = self._grid_to_world(0, len(self.maze_grid) // 2)
        rx, ry = self._grid_to_world(
            len(self.maze_grid[0]) - 1, len(self.maze_grid) // 2)
        return abs(x - lx) < margin and abs(y - ly) < margin\
            or abs(x - rx) < margin and abs(y - ry) < margin

    def _grid_to_world(self, gx: int, gy: int) -> tuple[int, int]:
        """Convert grid coordinates to world pixels.

        Args:
            gx: Horizontal grid coordinate.
            gy: Vertical grid coordinate.

        Returns:
            World pixel coordinates for the cell.
        """
        return (gx * TILE_SIZE * 2 + self.game.maze_offset_x,
                gy * TILE_SIZE * 2 + self.game.maze_offset_y)

    def _grid_to_world_center(self, gx: int, gy: int) -> tuple[int, int]:
        """Convert a grid cell to its world center.

        Args:
            gx: Horizontal grid coordinate.
            gy: Vertical grid coordinate.

        Returns:
            World pixel center for the cell.
        """
        x, y = self._grid_to_world(gx, gy)
        return x + TILE_SIZE, y + TILE_SIZE

    def get_biome_assets(
        self,
        x: int,
        y: int,
        mid_x: float,
        mid_y: float,
    ) -> BiomeAssets:
        """Return cached assets for a biome.

        Args:
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            mid_x: Horizontal midpoint used to choose the biome.
            mid_y: Vertical midpoint used to choose the biome.

        Returns:
            Cached biome asset surfaces.
        """
        if y < mid_y:
            biome = (self.biomes_config['north_west'] if (x < mid_x)
                     else self.biomes_config['north_east'])
        else:
            biome = (self.biomes_config['south_west'] if (x < mid_x)
                     else self.biomes_config['south_east'])
        return biome

    def free_item_spawn_points(self, x: int, y: int) -> bool:
        """Find available cells for item spawning.

        Args:
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.

        Returns:
            Free grid cells suitable for item spawning.
        """
        spawn_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        for group in (
            self.game.gums,
            self.game.walls,
            self.game.player_group,
        ):
            for sprite in group:
                if spawn_rect.colliderect(sprite.rect):
                    return False
        return True

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        if not self.item_spawned:
            self.item_spawn_timer += dt
            # Debug: print timer every second
            # if int(self.item_spawn_timer) % 1000 < dt:
            #     print(f"Item spawn timer: {self.item_spawn_timer}"
            #           f" / {self.item_spawn_delay}")
            if self.item_spawn_timer >= self.item_spawn_delay:
                if not self.game.special_items:
                    self.spawn_random_item()
                    self.item_spawned = True

    def play_theme(self, end_event_id: int) -> None:
        """Start the scene or level music.

        Args:
            end_event_id: Pygame event id fired when intro music ends.
        """
        if not self.game.cheat:
            pygame.mixer.music.set_endevent(end_event_id)
            if hasattr(self, 'bgm_intro'):
                pygame.mixer.music.load(self.bgm_intro)
            else:
                pygame.mixer.music.load(self.bgm_loop)
            pygame.mixer.music.play(0)
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.queue(self.bgm_loop)
        else:
            pygame.mixer.music.set_endevent(end_event_id)
            pygame.mixer.music.load(self.bgm_cheat)
            pygame.mixer.music.play(0)
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.queue(self.bgm_cheat)
