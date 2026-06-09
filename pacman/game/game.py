import pygame
from typing import TYPE_CHECKING

from pacman.game.sprites import SpriteSheet, StringFont
from pacman.game.scene_manager import SceneManager
from pacman.game.scenes import PlayScene, TitleScreen
from pacman.resources import resource_path, TILE_SIZE, SCALE, PAD_X, PAD_Y
from pacman.game.input import InputHandler
from pacman.game.type_defs import GameConfig, GameSprite, HighscoreEntry

if TYPE_CHECKING:
    from pacman.game.ai import AIDebugTrace
    from pacman.game.entities import Ennemy, Ground, Player
    from pacman.game.items import PacGumRupee, SpecialItem, SuperPacGum


class Game(pygame.sprite.Sprite):
    """Coordinate pygame resources, global state, and the main loop."""
    def __init__(
        self,
        config: GameConfig,
        highscores: list[HighscoreEntry],
        maze_grid: list[list[int]] | None = None,
    ) -> None:
        """Initialize the game.

        Args:
            config: Configuration mapping to read from.
            highscores: Highscore entries to read or update.
            maze_grid: Maze grid used for layout and pathfinding.
        """
        super().__init__()
        pygame.init()
        self.joystick: pygame.joystick.JoystickType | None = None
        self.connected = False
        self.input_handler = InputHandler()
        self.joystick_direction: str | None = None
        self._running = True
        self.delta_time = 0.0
        self.maze_grid: list[list[int]] = maze_grid or []
        self.config = config
        self.highscores = highscores

        # track which level the current maze was generated for
        self.current_level_id: str | None = None
        self.cheat = False

        self.in_game_score = 0
        self.in_game_time: float = float(config['level_max_time'])

        # initialize maze-related dimensions and surfaces
        self.logic_width = 840
        self.logic_height = 840
        self.maze_offset_x = PAD_X
        self.maze_offset_y = PAD_Y
        self.maze_width = 0
        self.maze_height = 0
        self.work_width = self.logic_width
        self.work_height = self.logic_height
        self.work_scale = 1.0
        if maze_grid is not None:
            self.update_maze_and_dimensions(maze_grid)

        # Create one logical render surface and one display surface.
        # Reserve logical pixels for the debug side panel.
        self.DEBUG_PANEL_WIDTH = 320
        self._logic_screen = pygame.Surface(
            (self.logic_width, self.logic_height)
        )
        self._render_surface = self._logic_screen
        # Dedicated logical debug surface.
        self._debug_screen = pygame.Surface(
            (self.DEBUG_PANEL_WIDTH, self.logic_height)
        )
        self._work_surface = pygame.Surface((self.work_width,
                                             self.work_height))
        self._display_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        self._display_size = self._get_display_size(False)
        self._display_screen = pygame.display.set_mode(
            self._display_size,
            self._display_flags,
        )
        self._clock = pygame.time.Clock()

        self.images: dict[str, pygame.Surface] = {}
        self.wall_base_image: pygame.Surface | None = None
        self.wall_variants: list[pygame.Surface] | None = None
        self.ground_base_image: pygame.Surface | None = None
        self.ground_variants: list[pygame.Surface] | None = None

        self.string = StringFont(self._logic_screen, resource_path(
            'fonts', 'minish_cap_font.ttf'), 10)

        # Initialize the scene manager.
        self.scene_manager = SceneManager()
        self.collected_items: dict["SpecialItem", bool] = {}
        self.sfx: dict[str, pygame.mixer.Sound] = {
            'gum_collect': pygame.mixer.Sound(
                resource_path('music/sfx', 'rupee.wav')),
            'super_gum_collect': pygame.mixer.Sound(
                resource_path('music/sfx', 'sword_obtain.wav')),
            'item_collect': pygame.mixer.Sound(
                resource_path('music/sfx', 'item_obtained.wav')),
            'item_spawn': pygame.mixer.Sound(
                resource_path('music/sfx', 'item_spawn.wav')),
            'press_menu': pygame.mixer.Sound(
                resource_path('music/sfx', 'press_menu.mp3')),
            'move_menu': pygame.mixer.Sound(
                resource_path('music/sfx', 'move_menu.mp3')),
            'exit_item': pygame.mixer.Sound(
                resource_path('music/sfx', 'exit_menu.mp3')),
            'pause_start': pygame.mixer.Sound(
                resource_path('music/sfx', 'pause_start.wav')),
            'pause_exit': pygame.mixer.Sound(
                resource_path('music/sfx', 'pause_exit.wav')),
            'connected_controller': pygame.mixer.Sound(
                resource_path('music/sfx', 'connected_controller.wav')),
            'disconnected_controller': pygame.mixer.Sound(
                resource_path('music/sfx', 'disconnected_controller.wav')),
            'move_pause': pygame.mixer.Sound(
                resource_path('music/sfx', 'pause_move.wav')),
            'death_link': pygame.mixer.Sound(
                resource_path('music/sfx', 'death_link.mp3')),
            'link_hurt': pygame.mixer.Sound(
                resource_path('music/sfx', 'link_hurt.wav')),
            'cheat_activate': pygame.mixer.Sound(
                resource_path('music/sfx', 'cheat_activated.wav')),
            'juliette': pygame.mixer.Sound(
                resource_path('music', 'juliette.mp3')),
            'pacman': pygame.mixer.Sound(
                resource_path('music', 'pacman_start.mp3')),
            'm': pygame.mixer.Sound(
                resource_path('music/sfx', 'm.mp3')),
            'hit': pygame.mixer.Sound(
                resource_path('music/sfx', 'enemy_hit.wav')),
            'kill': pygame.mixer.Sound(
                resource_path('music/sfx', 'enemy_kill.wav')),
            'question': pygame.mixer.Sound(
                resource_path('music/sfx', 'question.wav')),
            'error': pygame.mixer.Sound(
                resource_path('music/sfx', 'error.wav')),
        }
        self.lives = config['lives']
        self.enemies_spawn_points: list[tuple[int, int]] = []
        self.player: Player
        self.ai_debug_trace: AIDebugTrace

    def on_init(self) -> None:
        """Initialize the game application."""
        self._running = True
        self.load_images()
        self.setup_sprites()
        # Start on the title screen before entering gameplay.
        self.scene_manager.change(TitleScreen(self))
        pygame.display.flip()

    def on_event(self, event: pygame.event.Event) -> None:
        """Handle one pygame event.

        Args:
            event: Event data to handle.
        """
        if event.type == pygame.QUIT:
            self._running = False
        # Forward all events to the scene manager.
        self.scene_manager.handle_event(event)

    def on_loop(self, dt: float) -> None:
        # Update the active scene.
        """Advance the game loop by one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        if pygame.joystick.get_count() == 0 and self.connected:
            self.connected = False
            self.joystick = None
            self.sfx['disconnected_controller'].play()
            self.sfx['disconnected_controller'].set_volume(0.1)
        if pygame.joystick.get_count() == 1 and not self.joystick:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.connected = True
            self.sfx['connected_controller'].play()
            self.sfx['connected_controller'].set_volume(0.1)
        self.scene_manager.update(dt)

    def render_image(self, image: str, x: int, y: int) -> None:
        """Draw a named image on the render surface.

        Args:
            image: Surface used as the sprite image.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
        """
        self._render_surface.blit(self.images[image], (x, y))

    def on_render(self) -> None:
        # Prepare the logical screen for rendering
        """Render the current frame to the display."""
        self._logic_screen.fill((0, 0, 0))

        current_scene = self.scene_manager.current_scene()

        # Render the active scene once into the appropriate logical surface
        if isinstance(current_scene, PlayScene):
            # For gameplay we render to the work surface then blit onto logic
            self._work_surface.fill((0, 0, 0))
            self._render_surface = self._work_surface
            self.scene_manager.render(self._work_surface)

            if self.work_scale != 1.0:
                scaled_work = pygame.transform.scale(
                    self._work_surface,
                    (int(self.work_width * self.work_scale),
                     int(self.work_height * self.work_scale)),
                )
                x = (self.logic_width - scaled_work.get_width()) // 2
                y = (self.logic_height - scaled_work.get_height()) // 2
                self._logic_screen.blit(scaled_work, (x, y))
            else:
                self._logic_screen.blit(self._work_surface, (0, 0))
        else:
            # Menus and title screens render directly to logic surface
            self._render_surface = self._logic_screen
            self.scene_manager.render(self._logic_screen)

        # Determine whether side debug panel is enabled and ensure display mode
        debug_enabled = bool(getattr(current_scene, 'show_ai_debug', False))
        self._ensure_display_mode(debug_enabled)

        # Render debug panel into its logical surface if requested
        debug_renderer = getattr(current_scene, "_render_ai_debug", None)
        if debug_enabled and callable(debug_renderer):
            self._debug_screen.fill((0, 0, 0))
            try:
                debug_renderer(self._debug_screen)
            except Exception:
                # Don't let debug rendering break the main render
                pass

        # Scale the composed logical game surface once for display
        scaled_game = pygame.transform.scale(
            self._logic_screen,
            (int(self.logic_width * SCALE), int(self.logic_height * SCALE)),
        )

        self._display_screen.fill((0, 0, 0))
        self._display_screen.blit(scaled_game, (0, 0))

        # If debug side panel is enabled, scale and blit it to the right
        if debug_enabled:
            scaled_debug = pygame.transform.scale(
                self._debug_screen,
                (
                    int(self.DEBUG_PANEL_WIDTH * SCALE),
                    int(self.logic_height * SCALE),
                ),
            )
            self._display_screen.blit(
                scaled_debug,
                (int(self.logic_width * SCALE), 0),
            )
        pygame.display.flip()

    def _get_display_size(self, debug_enabled: bool) -> tuple[int, int]:
        """Compute the pygame display size.

        Args:
            debug_enabled: Whether the debug panel is currently visible.

        Returns:
            Display size in pixels.
        """
        width = self.logic_width
        if debug_enabled:
            width += self.DEBUG_PANEL_WIDTH
        return int(width * SCALE), int(self.logic_height * SCALE)

    def _ensure_display_mode(self, debug_enabled: bool) -> None:
        """Recreate the display when the size changes.

        Args:
            debug_enabled: Whether the debug panel is currently visible.
        """
        display_size = self._get_display_size(debug_enabled)
        if display_size == self._display_size:
            return
        self._display_size = display_size
        self._display_screen = pygame.display.set_mode(
            self._display_size,
            self._display_flags,
        )

    def on_cleanup(self) -> None:
        """Release pygame resources before shutdown."""
        pygame.quit()

    def update_maze_and_dimensions(self, maze_grid: list[list[int]]) -> None:
        """Store a maze grid and refresh derived dimensions.

        Args:
            maze_grid: Maze grid used for layout and pathfinding.
        """
        self.maze_grid = maze_grid
        self.maze_width = len(self.maze_grid[0]) * TILE_SIZE * 2 + TILE_SIZE
        self.maze_height = len(self.maze_grid) * TILE_SIZE * 2 + TILE_SIZE

        # Surface de travail (maze + padding)
        self.work_width = self.maze_width + PAD_X * 2
        self.work_height = self.maze_height + PAD_Y * 2

        # Scale work_surface so it fits inside logic_screen.
        self.work_scale = min(
            self.logic_width / max(1, self.work_width),
            self.logic_height / max(1, self.work_height)
        )

        # Working surface at the real maze size with padding.
        self._work_surface = pygame.Surface(
            (self.work_width, self.work_height))

    def on_execute(self) -> None:
        """Run the main pygame loop."""
        self.on_init()

        while self._running:
            dt = self._clock.tick(120)
            self.delta_time = dt / 1000.0  # pour convertir les ms en secondes

            for event in pygame.event.get():
                self.on_event(event)

            if self.joystick is not None:
                self.joystick_direction = self.input_handler.get_direction(
                    self.joystick)

                # Emit synthetic KEYDOWN events for UI consumption
                try:
                    keys = self.input_handler.get_key_events(self.joystick)
                    for k in keys:
                        ev = pygame.event.Event(pygame.KEYDOWN, {'key': k})
                        pygame.event.post(ev)
                except Exception:
                    # Keep gameplay functioning even if joystick polling fails
                    pass
            else:
                self.joystick_direction = None

            self.on_loop(dt)
            self.on_render()

        self.on_cleanup()

    def setup_sprites(self) -> None:
        """Create the sprite groups used by gameplay."""
        self.all_sprites: pygame.sprite.LayeredUpdates[GameSprite]
        self.walls: pygame.sprite.LayeredUpdates[GameSprite]
        self.ennemies: pygame.sprite.LayeredUpdates["Ennemy"]
        self.gums: pygame.sprite.LayeredUpdates["PacGumRupee"]
        self.super_gums: pygame.sprite.LayeredUpdates["SuperPacGum"]
        self.grounds: pygame.sprite.LayeredUpdates["Ground"]
        self.player_group: pygame.sprite.LayeredUpdates["Player"]
        self.decorations: pygame.sprite.LayeredUpdates[GameSprite]
        self.special_items: pygame.sprite.LayeredUpdates["SpecialItem"]

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.walls = pygame.sprite.LayeredUpdates()
        self.ennemies = pygame.sprite.LayeredUpdates()
        self.gums = pygame.sprite.LayeredUpdates()
        self.super_gums = pygame.sprite.LayeredUpdates()
        self.grounds = pygame.sprite.LayeredUpdates()
        self.player_group = pygame.sprite.LayeredUpdates()
        self.decorations = pygame.sprite.LayeredUpdates()
        self.special_items = pygame.sprite.LayeredUpdates()

    def load_images(self) -> None:
        """Load shared image assets into memory."""
        self.images['flowers'] = SpriteSheet(
            resource_path('levels/level_1', 'south_hyrule_field.png'),
            self).get_sprite(377, 449, 17, 16)
        self.images['floor_01'] = SpriteSheet(
            resource_path('levels/level_1', 'south_hyrule_field.png'),
            self).get_sprite(122, 152, 16, 16)
