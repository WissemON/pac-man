import pygame
import random
from typing import TYPE_CHECKING
from pacman.game.levels.level_base import Level
from pacman.game.sprites import SpriteSheet
from pacman.game.type_defs import GameSprite
from pacman.game.entities import Wall, Ground, DecorationBorder
from pacman.game.entities import Player
from pacman.game.items import PacGumRupee, SuperPacGum, SpecialItem
from pacman.game.ai import State
from pacman.game.levels.enemy_factory import (
    EnemySpec,
    extract_level_ai_config,
    spawn_enemies,
)
from pacman.resources import resource_path, TILE_SIZE

if TYPE_CHECKING:
    from pacman.game.game import Game


class CaveOfFlames(Level):
    """Define the cave of flames themed level."""

    def __init__(self, game: "Game", maze_grid: list[list[int]]) -> None:
        """Initialize the cave of flames.

        Args:
            game: Shared game object that owns resources, groups, and state.
            maze_grid: Maze grid used for layout and pathfinding.
        """
        super().__init__(game, maze_grid)
        self.bgm_intro = resource_path(
            'music/levels/level_05/cave_of_flames_intro.mp3')
        self.bgm_loop = resource_path(
            'music/levels/level_05/cave_of_flames_loop.mp3')
        self.tiles1 = SpriteSheet(resource_path(
            'levels/level_5', 'tiles1.png'), self.game)
        self.tiles2 = SpriteSheet(resource_path(
            'levels/level_5', 'tiles2.png'), self.game)
        item_sheet = SpriteSheet(resource_path(
            'items', 'items.png'), self.game)
        self.special_item = item_sheet.get_sprite(
            112, 195, 16, 16, (192, 192, 255))

    def _load_default_enemy_skins(self) -> None:
        """Load the default enemy sprite animations."""
        enemy_sheet = SpriteSheet(resource_path(
            'enemies', 'helmerauts.png'), self.game)

        self.blinky = {
            'up': [
                enemy_sheet.get_sprite(0, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(16, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(32, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(48, 0, 15, 16, (0, 0, 0))
            ],
            'down': [
                enemy_sheet.get_sprite(64, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(80, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(96, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(112, 0, 15, 16, (0, 0, 0))
            ],
            'left': [
                enemy_sheet.get_sprite(128, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(144, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(160, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(176, 0, 15, 16, (0, 0, 0))
            ],
            'right': [
                enemy_sheet.get_sprite(192, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(208, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(224, 0, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(240, 0, 15, 16, (0, 0, 0))
            ]
        }

        self.clyde = {
            'up': [
                enemy_sheet.get_sprite(0, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(16, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(32, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(48, 32, 15, 16, (0, 0, 0))
            ],
            'down': [
                enemy_sheet.get_sprite(64, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(80, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(96, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(112, 32, 15, 16, (0, 0, 0))
            ],
            'left': [
                enemy_sheet.get_sprite(128, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(144, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(160, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(176, 32, 15, 16, (0, 0, 0))
            ],
            'right': [
                enemy_sheet.get_sprite(192, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(208, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(224, 32, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(240, 32, 15, 16, (0, 0, 0))
            ]
        }

        self.inky = {
            'up': [
                enemy_sheet.get_sprite(0, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(16, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(32, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(48, 16, 15, 16, (0, 0, 0))
            ],
            'down': [
                enemy_sheet.get_sprite(64, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(80, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(96, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(112, 16, 15, 16, (0, 0, 0))
            ],
            'left': [
                enemy_sheet.get_sprite(128, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(144, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(160, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(176, 16, 15, 16, (0, 0, 0))
            ],
            'right': [
                enemy_sheet.get_sprite(192, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(208, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(224, 16, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(240, 16, 15, 16, (0, 0, 0))
            ]
        }

        self.pinky = {
            'up': [
                enemy_sheet.get_sprite(0, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(16, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(32, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(48, 48, 15, 16, (0, 0, 0))
            ],
            'down': [
                enemy_sheet.get_sprite(64, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(80, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(96, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(112, 48, 15, 16, (0, 0, 0))
            ],
            'left': [
                enemy_sheet.get_sprite(128, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(144, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(160, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(176, 48, 15, 16, (0, 0, 0))
            ],
            'right': [
                enemy_sheet.get_sprite(192, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(208, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(224, 48, 15, 16, (0, 0, 0)),
                enemy_sheet.get_sprite(240, 48, 15, 16, (0, 0, 0))
            ]
        }

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        if not self.item_spawned:
            self.item_spawn_timer += dt
            if self.item_spawn_timer >= self.item_spawn_delay:
                if not self.game.special_items:
                    self.spawn_random_item()
                    self.item_spawned = True

    def spawn_random_item(self) -> None:
        """Spawn a special item on a free maze cell."""
        reserved = self.reserved_cells()
        free_points = []

        for y, maze_row in enumerate(self.maze_grid):
            for x, cell in enumerate(maze_row):
                if (x, y) in reserved:
                    continue
                world_x, world_y = self._grid_to_world_center(x, y)
                if self.free_item_spawn_points(world_x, world_y):
                    free_points.append((world_x, world_y))

        if free_points:
            spawn_x, spawn_y = random.choice(free_points)
            SpecialItem(self.game, spawn_x, spawn_y, 112, 195, 16, 16)
            item_spawn_sfx = self.game.sfx['item_spawn']
            item_spawn_sfx.set_volume(0.3)
            item_spawn_sfx.play()

    def setup(self) -> None:
        """Build the level sprites and gameplay objects."""
        self.game.setup_sprites()
        self._setup_maze_theme_assets()
        self.generate_maze()
        self.setup_decorations()
        self.setup_gums(401)
        self.setup_enemies()

    def _setup_maze_theme_assets(self) -> None:
        """Load themed wall and ground assets."""
        self.biomes_config = {
            'north_west': {
                'wall_base': self.tiles1.get_sprite(208, 144, 16, 16),
                'ground_base': self.tiles1.get_sprite(224, 0, 16, 16),
                'wall_variants': [
                    self.tiles1.get_sprite(208, 144, 16, 16),
                    self.tiles1.get_sprite(208, 160, 16, 16),
                    self.tiles1.get_sprite(240, 128, 16, 16),
                    self.tiles1.get_sprite(240, 144, 16, 16),
                ],
                'ground_variants': [
                    self.tiles1.get_sprite(224, 0, 16, 16),
                ]
            },
            'north_east': {
                'wall_base': self.tiles1.get_sprite(80, 48, 16, 16),
                'ground_base': self.tiles1.get_sprite(48, 1200, 16, 16),
                'wall_variants': [
                    self.tiles1.get_sprite(80, 48, 16, 16),
                    self.tiles1.get_sprite(96, 48, 16, 16),
                    self.tiles1.get_sprite(112, 48, 16, 16)
                ],
                'ground_variants': [
                    self.tiles1.get_sprite(48, 1200, 16, 16),
                    self.tiles1.get_sprite(80, 1232, 16, 16),
                ]
            },
            'south_west': {
                'wall_base': self.tiles1.get_sprite(80, 80, 16, 16),
                'ground_base': self.tiles1.get_sprite(224, 0, 16, 16),
                'wall_variants': [
                    self.tiles1.get_sprite(80, 80, 16, 16),
                ],
                'ground_variants': [
                    self.tiles1.get_sprite(224, 0, 16, 16),
                    self.tiles1.get_sprite(224, 80, 16, 16),
                    self.tiles1.get_sprite(240, 80, 16, 16),
                ]
            },
            'south_east': {
                'wall_base': self.tiles1.get_sprite(0, 64, 16, 16),
                'ground_base': self.tiles1.get_sprite(256, 48, 16, 16),
                'wall_variants': [
                    self.tiles1.get_sprite(0, 64, 16, 16),
                    self.tiles1.get_sprite(16, 64, 16, 16),
                ],
                'ground_variants': [
                    self.tiles1.get_sprite(224, 0, 16, 16),
                ]
            }
        }

    def setup_enemies(self) -> None:
        """Spawn the enemies for the level."""
        cols = len(self.maze_grid[0])
        rows = len(self.maze_grid)
        enemy_specs = [
            EnemySpec((0, 0), self.blinky, 'blinky', 'blinky', (0, 0)),
            EnemySpec((cols - 1, 0), self.pinky,
                      'pinky', 'pinky', (cols - 1, 0)),
            EnemySpec((0, rows - 1), self.inky, 'inky', 'inky', (0, rows - 1)),
            EnemySpec((cols - 1, rows - 1), self.clyde,
                      'clyde', 'clyde', (cols - 1, rows - 1))
        ]
        spawn_enemies(
            self.game,
            enemy_specs,
            default_state=State.SCATTER,
            durations_map=extract_level_ai_config(self.game),
        )

    def generate_maze(self) -> None:
        """Create terrain sprites from the maze grid."""
        tunnel_row = len(self.maze_grid) // 2
        left_tunnel_x = 0
        right_tunnel_x = len(self.maze_grid[0]) - 1

        rows = len(self.maze_grid)
        cols = len(self.maze_grid[0])

        mid_x = cols // 2
        mid_y = rows // 2

        for y, maze_row in enumerate(self.maze_grid):
            for x, cell in enumerate(maze_row):
                assets = self.get_biome_assets(x, y, mid_x, mid_y)

                new_x, new_y = self._grid_to_world(x, y)

                is_tunnel_row = y == tunnel_row
                is_left_tunnel = is_tunnel_row and x == left_tunnel_x
                is_right_tunnel = is_tunnel_row and x == right_tunnel_x

                Wall(
                    self.game,
                    new_x,
                    new_y,
                    base_image=assets['wall_base'],
                    variants=assets['wall_variants'])
                Wall(
                    self.game,
                    new_x + TILE_SIZE * 2,
                    new_y + TILE_SIZE * 2,
                    base_image=assets['wall_base'],
                    variants=assets['wall_variants'])
                Wall(
                    self.game,
                    new_x + TILE_SIZE * 2,
                    new_y,
                    base_image=assets['wall_base'],
                    variants=assets['wall_variants'])
                Wall(
                    self.game,
                    new_x,
                    new_y + TILE_SIZE * 2,
                    base_image=assets['wall_base'],
                    variants=assets['wall_variants'])

                if cell & 1:
                    Wall(
                        self.game,
                        new_x + TILE_SIZE,
                        new_y,
                        base_image=assets['wall_base'],
                        variants=assets['wall_variants'])
                else:
                    Ground(
                        self.game,
                        new_x + TILE_SIZE,
                        new_y,
                        base_image=assets['ground_base'],
                        variants=assets['ground_variants'])

                if cell & 2:
                    if not is_right_tunnel:
                        Wall(
                            self.game,
                            new_x + TILE_SIZE * 2,
                            new_y + TILE_SIZE,
                            base_image=assets['wall_base'],
                            variants=assets['wall_variants'])
                else:
                    Ground(
                        self.game,
                        new_x + TILE_SIZE * 2,
                        new_y + TILE_SIZE,
                        base_image=assets['ground_base'],
                        variants=assets['ground_variants'])

                if cell & 4:
                    Wall(
                        self.game,
                        new_x + TILE_SIZE,
                        new_y + TILE_SIZE * 2,
                        base_image=assets['wall_base'],
                        variants=assets['wall_variants'])
                else:
                    Ground(
                        self.game,
                        new_x + TILE_SIZE,
                        new_y + TILE_SIZE * 2,
                        base_image=assets['ground_base'],
                        variants=assets['ground_variants'])

                if cell & 8:
                    if not is_left_tunnel:
                        Wall(
                            self.game,
                            new_x,
                            new_y + TILE_SIZE,
                            base_image=assets['wall_base'],
                            variants=assets['wall_variants'])
                else:
                    Ground(
                        self.game,
                        new_x,
                        new_y + TILE_SIZE,
                        base_image=assets['ground_base'],
                        variants=assets['ground_variants'])

                if is_left_tunnel:
                    Ground(
                        self.game,
                        new_x,
                        new_y + TILE_SIZE,
                        base_image=assets['ground_base'],
                        variants=assets['ground_variants'])
                if is_right_tunnel:
                    Ground(
                        self.game,
                        new_x + TILE_SIZE * 2,
                        new_y + TILE_SIZE,
                        base_image=assets['ground_base'],
                        variants=assets['ground_variants'])

                Ground(
                    self.game,
                    new_x + TILE_SIZE,
                    new_y + TILE_SIZE,
                    base_image=assets['ground_base'],
                    variants=assets['ground_variants'])

        # Center Link in the maze
        cols = len(self.maze_grid[0])
        rows = len(self.maze_grid)
        center_cell_x = (cols - 1) // 2
        center_cell_y = (rows - 1) // 2
        player_x, player_y = self._grid_to_world_center(
            center_cell_x,
            center_cell_y,
        )
        self.game.player = Player(self.game, player_x, player_y, 'base')
        self.game.player.current_held_item = self.special_item

        tunnel_row = len(self.maze_grid) // 2
        self.tunnels = {'left': (0, tunnel_row), 'right': (
            len(self.maze_grid[0]) - 1, tunnel_row)}

        water_sprite = self.tiles1.get_sprite(96, 32, 16, 16)
        bridge_sprite = self.tiles1.get_sprite(224, 0, 16, 16)

        x = 0
        walk_y = 0
        for side, (gx, gy) in self.tunnels.items():
            new_x, new_y = self._grid_to_world(gx, gy)
            walk_y = new_y + TILE_SIZE

            if side == 'left':
                start_x = new_x - TILE_SIZE
                direction = -1
            else:
                start_x = new_x + TILE_SIZE * 3
                direction = 1

            for i in range(2):
                x = start_x + direction * i * TILE_SIZE

                Water(self.game, x, walk_y + TILE_SIZE, water_sprite)
                Bridge(self.game, x, walk_y, bridge_sprite)
                Water(self.game, x, walk_y - TILE_SIZE, water_sprite)

        Water(self.game, x + 16, walk_y - TILE_SIZE,
              self.tiles1.get_sprite(160, 608, 16, 16))
        Bridge(self.game, x + 16, walk_y,
               self.tiles1.get_sprite(192, 624, 16, 16))
        Water(self.game, x + 16, walk_y + TILE_SIZE,
              self.tiles1.get_sprite(160, 640, 16, 16))

        Water(self.game, self.game.maze_offset_x - 48,
              walk_y - TILE_SIZE, self.tiles1.get_sprite(112, 608, 16, 16))
        Bridge(self.game, self.game.maze_offset_x - 48, walk_y,
               self.tiles1.get_sprite(112, 624, 16, 16))
        Water(self.game, self.game.maze_offset_x - 48,
              walk_y + TILE_SIZE, self.tiles1.get_sprite(112, 608, 16, 16))

        Water(self.game, -16,
              walk_y - TILE_SIZE, self.tiles1.get_sprite(112, 608, 16, 16))
        Bridge(self.game, - 16, walk_y,
               self.tiles1.get_sprite(112, 624, 16, 16))
        Water(self.game, -16,
              walk_y + TILE_SIZE, self.tiles1.get_sprite(112, 608, 16, 16))

        Water(self.game, x + 32, walk_y - TILE_SIZE,
              self.tiles1.get_sprite(160, 608, 16, 16))
        Bridge(self.game, x + 32, walk_y,
               self.tiles1.get_sprite(192, 624, 16, 16))
        Water(self.game, x + 32, walk_y + TILE_SIZE,
              self.tiles1.get_sprite(160, 640, 16, 16))

    def setup_decorations(self) -> None:
        """Place static level decorations."""
        cols = len(self.maze_grid[0])
        rows = len(self.maze_grid)

        step = TILE_SIZE * 2 - 7
        dungeon_wall_l = self.tiles1.get_sprite(0, 337, 32, 62)
        dungeon_wall_r = self.tiles1.get_sprite(96, 336, 32, 62)

        left_x = self.game.maze_offset_x - 48
        right_x = self.game.maze_offset_x + self.game.maze_width + 48
        for r in range(0, rows + 20):
            y = self.game.maze_offset_y + r * step + step
            DecorationBorder(self.game, left_x, y - 16, dungeon_wall_l)
            DecorationBorder(self.game, right_x, y - 16, dungeon_wall_r)

        dungeon_wall_up = self.tiles1.get_sprite(0, 272, 62, 32)
        dungeon_wall_down = self.tiles1.get_sprite(0, 304, 62, 32)
        for c in range(0, cols + 7, 2):
            x = self.game.maze_offset_x + c * step + step
            DecorationBorder(self.game, x - 27,
                             self.game.maze_offset_y - 16, dungeon_wall_up)
            DecorationBorder(self.game, x - 27, self.game.maze_offset_y +
                             self.game.maze_height + 48, dungeon_wall_down)

    def setup_gums(self, nb_pac_gums: int) -> None:
        """Place pacgums and special pickups.

        Args:
            nb_pac_gums: Number of pacgums to place in the maze.
        """
        reserved = self.reserved_cells()
        corners = [(0, 0), (len(self.maze_grid[0]) - 1, 0),
                   (0, len(self.maze_grid) - 1), (len(self.maze_grid[0]) - 1,
                                                  len(self.maze_grid) - 1)]
        total_cells = len(self.maze_grid) * len(self.maze_grid[0])
        available_cells = total_cells - len(reserved)
        max_pac_gums = int(available_cells * 0.8)

        for x, y in corners:
            if (x, y) in reserved:
                world_x, world_y = self._grid_to_world_center(x, y)
                SuperPacGum(self.game, world_x, world_y, 5, 195, 16, 16)

        cells_open = []
        for y, maze_row in enumerate(self.maze_grid):
            for x, cell in enumerate(maze_row):
                if x == 15:
                    continue
                if (x, y) in reserved:
                    continue
                world_x, world_y = self._grid_to_world_center(x, y)
                if self.free_item_spawn_points(world_x, world_y):
                    cells_open.append((world_x, world_y))

        # --- Shuffle et placement
        random.shuffle(cells_open)
        for i, (world_x, world_y) in enumerate(cells_open):
            if i >= max_pac_gums or i >= nb_pac_gums:
                break
            PacGumRupee(self.game, world_x, world_y)

    def fill_background(self, surface: pygame.Surface) -> None:
        """Fill the render surface with the level background.

        Args:
            surface: Surface that receives drawing operations.
        """
        pass

    def render_special(self, surface: pygame.Surface) -> None:
        """Render level-specific overlay visuals.

        Args:
            surface: Surface that receives drawing operations.
        """
        top_left_corner = self.tiles2.get_sprite(256, 992, 16, 16)
        top_middle = self.tiles2.get_sprite(304, 992, 16, 16)
        top_right_corner = self.tiles2.get_sprite(368, 992, 16, 16)
        left_middle = self.tiles2.get_sprite(256, 1088, 16, 16)
        bottom_left_corner = self.tiles2.get_sprite(256, 1104, 16, 16)
        bottom_middle = self.tiles2.get_sprite(272, 1104, 16, 16)
        bottom_right_corner = self.tiles2.get_sprite(368, 1104, 16, 16)
        right_middle = self.tiles2.get_sprite(368, 1088, 16, 16)

        corner_left_to_bottom = self.tiles1.get_sprite(192, 1472, 16, 16)
        corner_bottom_to_left = self.tiles1.get_sprite(192, 1456, 16, 16)
        corner_bottom_to_right = pygame.transform.flip(
            corner_bottom_to_left, True, False)
        corner_right_to_bottom = pygame.transform.flip(
            corner_left_to_bottom, True, False)
        corner_top_to_right = corner_bottom_to_right
        middle_01 = self.tiles1.get_sprite(0, 1456, 16, 16)
        middle_02 = self.tiles1.get_sprite(0, 1472, 16, 16)

        tiles_42 = [
            [
                top_left_corner, top_middle, top_right_corner,
                left_middle, middle_01, right_middle,
                left_middle, middle_02, right_middle,
            ],
            [top_left_corner, top_middle, top_middle,
                left_middle, middle_01, middle_02,
                bottom_left_corner, bottom_middle, bottom_middle],
            [top_middle, top_middle, top_middle,
                middle_02, middle_01, middle_02,
                bottom_middle, bottom_middle, corner_left_to_bottom],
            [top_middle, top_middle, top_right_corner,
                middle_02, middle_01, right_middle,
                corner_left_to_bottom, middle_01, right_middle],

            [left_middle, middle_01, right_middle,
                left_middle, middle_02, right_middle,
                left_middle, middle_01, right_middle],
            [corner_left_to_bottom, middle_01, right_middle,
                left_middle, middle_02, right_middle,
                corner_bottom_to_left, middle_01, right_middle],

            [left_middle, middle_01, corner_top_to_right,
                left_middle, middle_02, middle_01,
                bottom_left_corner, bottom_middle, bottom_middle],
            [corner_top_to_right, top_middle, top_middle,
                middle_01, middle_02, middle_01,
                bottom_middle, bottom_middle, corner_left_to_bottom,],
            [top_middle, top_middle, top_right_corner,
                middle_01, middle_02, right_middle,
                corner_left_to_bottom, middle_01, right_middle],
            [top_left_corner, top_middle, top_middle,
                left_middle, middle_01, middle_02,
                left_middle, middle_02, corner_right_to_bottom],
            [top_middle, top_middle, bottom_left_corner,
                middle_02, middle_01, middle_02,
                corner_right_to_bottom, bottom_middle, bottom_middle],
            [corner_bottom_to_left, middle_01, right_middle,
                middle_02, middle_01, right_middle,
                bottom_middle, bottom_middle, bottom_right_corner],

            [corner_left_to_bottom, middle_01, right_middle,
                left_middle, middle_02, right_middle,
                left_middle, middle_01, right_middle],
            [left_middle, middle_01, corner_right_to_bottom,
                left_middle, middle_02, right_middle,
                left_middle, middle_01, corner_top_to_right],

            [left_middle, middle_01, right_middle,
                left_middle, middle_02, right_middle,
                bottom_left_corner, bottom_middle, bottom_right_corner],
            [left_middle, middle_01, corner_top_to_right,
                left_middle, middle_02, middle_01,
                bottom_left_corner, bottom_middle, bottom_middle],
            [corner_top_to_right, top_middle, corner_top_to_right,
                middle_01, middle_02, middle_01,
                bottom_middle, bottom_middle, bottom_middle],
            [top_middle, top_middle, top_right_corner,
                middle_01, middle_02, right_middle,
                bottom_middle, bottom_middle, bottom_right_corner]
        ]
        # on sait il y a combien de 15 pour dessiner 42 donc on dessine sur
        # l'ordre
        fifty_index = 0
        for y, maze_row in enumerate(self.maze_grid):
            for x, cell in enumerate(maze_row):
                if cell == 15 and len(tiles_42) > fifty_index:
                    new_x = x * TILE_SIZE * 2 + self.game.maze_offset_x
                    new_y = y * TILE_SIZE * 2 + self.game.maze_offset_y

                    block = tiles_42[fifty_index]

                    for sprite_inx in range(9):
                        row = sprite_inx // 3
                        col = sprite_inx % 3

                        sprite_x = new_x + col * TILE_SIZE
                        sprite_y = new_y + row * TILE_SIZE
                        surface.blit(block[sprite_inx], (sprite_x, sprite_y))
                    fifty_index += 1


class Water(GameSprite):
    """Represent a water tile that participates in level collision."""
    def __init__(
        self,
        game: "Game",
        x: int,
        y: int,
        image: pygame.Surface,
    ) -> None:
        """Initialize the water.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            image: Surface used as the sprite image.
        """
        super().__init__()
        self.game = game
        self.image = image
        self.game.all_sprites.add(self)
        self.game.walls.add(self)
        self.rect = self.image.get_rect(topleft=(x, y))


class Bridge(GameSprite):
    """Represent a bridge tile drawn over level terrain."""
    def __init__(
        self,
        game: "Game",
        x: int,
        y: int,
        image: pygame.Surface,
    ) -> None:
        """Initialize the bridge.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            image: Surface used as the sprite image.
        """
        super().__init__()
        self.game = game
        self.image = image
        self.game.all_sprites.add(self)
        self.rect = self.image.get_rect(topleft=(x, y))
