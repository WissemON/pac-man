import pygame
from collections import defaultdict
from typing import TYPE_CHECKING, TypeAlias

from pacman.game.ai import AIDebugTrace, EnemyBrain, State
from pacman.game.scene_manager import Scene
from pacman.game.sprites import StringFont
from pacman.game.ui import UiElements
from pacman.game.levels import LEVEL_CLASSES, Level, level_name
from pacman.game.save import save_levels
from pacman.game.scenes.pause import PauseScene
from pacman.resources import resource_path, TILE_SIZE
from pacman.game.sprites import SpriteSheet

if TYPE_CHECKING:
    from pacman.game.game import Game
    from pacman.game.entities import Ennemy

PathCacheKey: TypeAlias = tuple[
    str | None,
    str,
    tuple[int, int],
    tuple[int, int] | None,
    str,
]


class PlayScene(Scene):
    """Run the active gameplay level."""

    def __init__(
        self,
        game: "Game",
        level_class: type[Level] | None = None,
    ) -> None:
        """Initialize the play scene.

        Args:
            game: Shared game object that owns resources, groups, and state.
            level_class: Level class to resolve or instantiate.
        """
        super().__init__(game)
        if level_class is not None:
            self.level_class = level_class
        elif LEVEL_CLASSES:
            self.level_class = LEVEL_CLASSES[0]
        else:
            raise RuntimeError("No level class available")
        self.level: Level | None = None
        self.levels = LEVEL_CLASSES
        self.ui: UiElements | None = None
        self.game.in_game_time = self.game.config["level_max_time"]

        self.frozen = False
        self.respawn_freeze = False
        self.item_gain = False
        self.freeze_timer = 0.0
        self.respawn_freeze_timer = 0.0

        self.show_ai_debug = False
        self.show_ai_overlay = False
        self.show_ai_terminal_debug = False
        self.ai_debug_font: pygame.font.Font | None = None
        self._path_cache: dict[PathCacheKey, list[tuple[int, int]]] = {}

        self.total_gums = 0
        self.total_super_gums = 0
        self.count_gums = 0
        self.count_super_gums = 0

        self.intro_end = pygame.USEREVENT + 1
        self.waiting_for_loop = False

        self.hit = False
        self.win_level = False
        self.start_level = True

        bgm_win = resource_path("music", "win_level.mp3")
        self.bgm_win = pygame.mixer.Sound(bgm_win)
        self.bgm_win.set_volume(0.2)
        self.fade_in_duration_ms = 8000
        self.fade_out_duration_ms = 2000
        self.fade_in = True
        self.alpha = 255.0

        final_stage_sheet = SpriteSheet(
            resource_path("pics", "final_round.png"), game
        )
        final_stage_image = final_stage_sheet.get_sprite(0, 0, 420, 200)
        final_stage_image = pygame.transform.scale(
            final_stage_image,
            (final_stage_image.get_width() *
             self.game._logic_screen.get_width() //
             2000,
             final_stage_image.get_height() *
             self.game._logic_screen.get_height() //
             2000))
        self.final_stage = final_stage_image

    def on_enter(self) -> None:
        """Prepare the scene when it becomes active."""
        self.game.ai_debug_trace = AIDebugTrace(enabled=True, max_events=300)
        if hasattr(self.game, "input_handler"):
            self.game.input_handler.reset()
        self.start_level = True
        self.win_level = False
        self.fade_in = False
        self.alpha = 255.0
        index = self.levels.index(self.level_class)
        level_id = str(index + 1)
        level_cfg = self.game.config["level"][0][level_id]

        width = level_cfg["width"]
        height = level_cfg["height"]

        need_regen = (
            self.game.current_level_id != level_id
            or not self.game.maze_grid
            or len(self.game.maze_grid) != height
            or len(self.game.maze_grid[0]) != width
        )

        if need_regen:
            # Generate a fresh maze for this level.
            # Use the global seed only for the first generation.
            from mazegenerator.mazegenerator import MazeGenerator
            if level_id == "1" and self.game.current_level_id is None:
                seed = self.game.config["seed"]
                maze_gen = MazeGenerator(
                    size=(width, height),
                    seed=seed,
                )
            else:
                maze_gen = MazeGenerator(size=(width, height))

            self.game.update_maze_and_dimensions(maze_gen.maze)
            self.game.current_level_id = level_id

        # Create and initialize the level.
        self.level = self.level_class(self.game, self.game.maze_grid)
        self.level.setup()
        self.level.play_theme(self.intro_end)
        self._path_cache.clear()

        self.total_gums = len(self.game.gums)
        self.total_super_gums = len(self.game.super_gums)
        self.count_gums = 0
        self.count_super_gums = 0

        self.waiting_for_loop = True

        self.ui = UiElements(self.game)
        self.ai_debug_font = pygame.font.Font(resource_path(
            "fonts", "PixelOperator-Bold.ttf"), 15)
        if self.start_level:
            self.freeze_after_respawn(4000)

    def on_exit(self) -> None:
        """Clean up before the scene leaves the stack."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one pygame event for the scene.

        Args:
            event: Event data to handle.
        """
        if self.win_level:
            return
        # Delegate KEYDOWN handling to a helper for clarity and reuse
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)

        # for music
        if event.type == self.intro_end and self.level is not None:
            if self.waiting_for_loop:
                # force loop to stop intro
                pygame.mixer.music.load(self.level.bgm_loop)
                pygame.mixer.music.play(-1)
                self.waiting_for_loop = False

    def _handle_keydown(self, key: int) -> None:
        # for ai DEBUG
        """Handle one key press event.

        Args:
            key: Configuration key to validate.
        """
        if key == pygame.K_F1:
            self.show_ai_overlay = not self.show_ai_overlay
        elif key == pygame.K_F2:
            self.show_ai_terminal_debug = not self.show_ai_terminal_debug
        elif key == pygame.K_F3:
            self.show_ai_debug = not self.show_ai_debug
        elif key == pygame.K_F4:
            self.game.ai_debug_trace.clear()

        # menu pause input is mapped to K_ESCAPE by InputHandler
        elif key == pygame.K_ESCAPE:
            self.game.scene_manager.push(PauseScene(self.game))

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        if self.fade_in:
            fade_step = 255 * dt / self.fade_in_duration_ms
            self.alpha = min(255, self.alpha + fade_step)
        else:
            fade_step = 255 * dt / self.fade_out_duration_ms
            self.alpha = max(0, self.alpha - fade_step)

        if self.game.player.death:
            self.game.player.animate(dt)
            return

        if self.hit:
            self.hit = False
            self._reset_after_player_death()

        if self.game.player.game_over is False and self.game.lives == 0:
            from pacman.game.scenes.game_over import GameOverScene
            self.game.scene_manager.change(GameOverScene(self.game))
            return

        if self.game.in_game_time <= 0:
            from pacman.game.scenes.game_over import GameOverScene
            self.game.scene_manager.change(GameOverScene(self.game))
            return

        if self.game.player.game_over:
            self.game.player.update(dt)
            return

        self.game.ai_debug_trace.begin_frame()
        for enemy in self.game.ennemies:
            enemy.advance_respawn(dt / 1000.0)
        if self.show_ai_overlay:
            self._prime_debug_path_cache()
        if self.show_ai_terminal_debug:
            self.game.ai_debug_trace.dump_to_console(limit=16)
        if self.respawn_freeze:
            self.respawn_freeze_timer -= dt
            if self.respawn_freeze_timer <= 0:
                self.respawn_freeze = False
                self.start_level = False
            return
        if self.frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.frozen = False
                self.item_gain = False
            self.game.player_group.update(dt)
            return
        else:
            keys = pygame.key.get_pressed()
            from pacman.game.entities import Player
            for sprite in self.game.all_sprites:
                if isinstance(sprite, Player):
                    sprite.queue_direction(keys)
                    break

            if len(
                    self.game.gums) == 0 and len(
                    self.game.super_gums) == 0 and self.win_level is False:
                pygame.mixer.music.set_volume(0.0)
                self.bgm_win.play()
                self.win_level = True
                self.fade_in = True
                self.alpha = 0.0
                for enemy in self.game.ennemies:
                    enemy.kill()
                    self.game.sfx['kill'].play()
                    self.game.sfx['kill'].set_volume(0.05)
                self.freeze_for(9000)
                return

            if len(
                    self.game.gums) == 0 and len(
                    self.game.super_gums) == 0 and self.win_level:
                current_level_id = self.game.current_level_id
                if current_level_id is None:
                    raise RuntimeError("Current level id is not set")
                current_level_number = int(current_level_id)

                if current_level_number == 16 and self.game.cheat:
                    from pacman.game.scenes.weird_ending import (
                        WeirdEndingScene,
                    )
                    self.game.in_game_time = self.game.config["level_max_time"]
                    self.game.scene_manager.change(WeirdEndingScene(self.game))
                    return
                elif (
                    current_level_number == 16
                    and self.game.cheat is False
                    and len(self.game.collected_items) < 16
                ):
                    from pacman.game.scenes.win_screen_base import (
                        WinScreenBase,
                    )
                    if not self.game.cheat:
                        save_levels(self.game, current_level_number)
                    self.game.in_game_time = self.game.config["level_max_time"]
                    self.game.scene_manager.change(WinScreenBase(self.game))
                    return
                elif (
                    current_level_number == 16
                    and self.game.cheat is False
                    and len(self.game.collected_items) == 16
                ):
                    if not self.game.cheat:
                        save_levels(self.game, current_level_number + 1)
                    from pacman.game.scenes.true_ending import TrueEndingScene
                    self.game.in_game_time = self.game.config["level_max_time"]
                    self.game.scene_manager.change(TrueEndingScene(self.game))
                    return
                else:
                    if not self.game.cheat:
                        save_levels(self.game, current_level_number)
                    index = self.levels.index(self.level_class)
                    next_scene = PlayScene(self.game, self.levels[index + 1])
                    self.game.in_game_time = self.game.config["level_max_time"]
                    self.game.scene_manager.change(next_scene)
                    return

            self.game.all_sprites.update(dt)

            collected_gums = pygame.sprite.spritecollideany(
                self.game.player, self.game.gums)
            collected_super_gums = pygame.sprite.spritecollideany(
                self.game.player, self.game.super_gums)
            collected_item = pygame.sprite.spritecollideany(
                self.game.player, self.game.special_items)

            if collected_gums:
                collected_gums.collected()

            if collected_super_gums:
                collected_super_gums.collected()
                self.game.player.powered_timer = 8.0
                self.count_super_gums += 1

            if collected_item:
                self.item_gain = True
                collected_item.collected()

            if not self.game.cheat:
                self._handle_enemy_collisions()

        if not self.frozen:
            self.game.in_game_time -= 1 / 120.0
        if self.level is not None:
            self.level.update(dt)

    def freeze_for(self, duration_ms: int) -> None:
        """Freeze scene updates for a fixed duration.

        Args:
            duration_ms: Freeze duration in milliseconds.
        """
        self.frozen = True
        self.freeze_timer = float(duration_ms)

    def freeze_after_respawn(self, duration_ms: int = 2000) -> None:
        """Freeze gameplay after the player respawns.

        Args:
            duration_ms: Freeze duration in milliseconds.
        """
        self.respawn_freeze = True
        self.respawn_freeze_timer = float(duration_ms)

    def _handle_enemy_collisions(self) -> None:
        """Resolve collisions between player and enemies."""
        if not self.game.player or not self.game.ennemies:
            return

        for enemy in self.game.ennemies:
            if self.game.player.hurtbox.colliderect(enemy.hurtbox):
                hits = [enemy]
                break
        else:
            hits = []
        hits = [
            enemy for enemy in hits
            if not getattr(enemy, "is_respawning", False)
        ]
        if not hits:
            return

        player = self.game.player
        for enemy in hits:
            if player.powered:
                self.game.sfx['hit'].play()
                self.game.sfx['hit'].set_volume(0.2)
                self.game.in_game_score += enemy.points
                if hasattr(enemy, "begin_respawn"):
                    respawn_seconds = getattr(
                        enemy.ai.state_controller,
                        "eaten_duration",
                        4.0,
                    )
                    # freeze game for a short moment to emphasize the kill
                    if self.game.joystick:
                        self.game.joystick.rumble(0.1, 0.5, 200)
                    self.freeze_for(500)
                    self.game.sfx['kill'].play()
                    self.game.sfx['kill'].set_volume(0.2)
                    enemy.begin_respawn(int(respawn_seconds * 1000))
                    enemy.ai.trace(
                        f"collision powered -> teleport {enemy.enemy_type}"
                    )
                break

            if self.game.lives > 0:
                self.game.sfx['link_hurt'].play()
                self.game.lives -= 1
                if self.game.joystick:
                    self.game.joystick.rumble(0.1, 0.5, 200)

            if self.game.lives == 0:
                self.game.player.game_over = True
                self.game.sfx['death_link'].play()
                pygame.mixer.music.stop()
                return

            self.hit = True
            break

    def _reset_after_player_death(self) -> None:
        """Reset player and enemies after a death."""
        player = self.game.player
        if not player:
            return

        player.respawn()
        player.powered = False
        player.powered_timer = 8.0

        for enemy in self.game.ennemies:
            enemy.respawn()

        self.frozen = False
        self.freeze_timer = 0.0
        self.freeze_after_respawn(2000)

    def _level_title_font_size(
        self,
        surface: pygame.Surface,
        text: str,
        font_path: str,
    ) -> int:
        """Return the largest title font size that fits the screen.

        Args:
            surface: Surface used to measure the logical screen width.
            text: Level title to render.
            font_path: Path to the font file.

        Returns:
            Font size adapted to the title length and screen width.
        """
        surface_width = int(surface.get_width())
        max_width = int(surface_width * 0.78)
        max_size = max(46, min(72, surface_width // 11))
        min_size = max(28, surface_width // 30)

        for size in range(max_size, min_size - 1, -2):
            font = StringFont(surface, font_path, size)
            if font.get_width(text) <= max_width:
                return size
        return min_size

    def _render_level_title(self, surface: pygame.Surface) -> None:
        """Draw the level title overlay with adaptive sizing.

        Args:
            surface: Surface that receives drawing operations.
        """
        if self.game.current_level_id is None:
            return

        level_id = int(self.game.current_level_id)
        level_index = level_id - 1
        if level_index < 0 or level_index >= len(level_name):
            return

        text = level_name[level_index]
        font_path = resource_path("fonts", "PixelOperator-Bold.ttf")
        font_size = self._level_title_font_size(surface, text, font_path)
        font = StringFont(surface, font_path, font_size)
        text_width = font.get_width(text)
        text_height = font.font.get_height()

        text_x = surface.get_width() // 2 - text_width // 2
        text_y = surface.get_height() // 2 - text_height // 2

        padding_x = max(24, surface.get_width() // 32)
        padding_y = max(12, font_size // 5)
        banner_rect = pygame.Rect(
            text_x - padding_x,
            text_y - padding_y,
            text_width + padding_x * 2,
            text_height + padding_y * 2,
        )
        banner = pygame.Surface(banner_rect.size, pygame.SRCALPHA)
        banner.fill((0, 0, 0, 150))
        surface.blit(banner, banner_rect)
        pygame.draw.rect(surface, (255, 255, 255, 90), banner_rect, 1)

        outline = max(2, font_size // 18)
        font.write(text, text_x + outline, text_y + outline,
                   (0, 0, 0), 160)
        for dx, dy in (
            (-outline, 0),
            (outline, 0),
            (0, -outline),
            (0, outline),
            (-outline, -outline),
            (outline, -outline),
            (-outline, outline),
            (outline, outline),
        ):
            font.write(text, text_x + dx, text_y + dy, (18, 18, 24))
        font.write(text, text_x, text_y, (255, 246, 176))

    def render(self, surface: pygame.Surface) -> None:
        """Draw the current state onto a surface.

        Args:
            surface: Surface that receives drawing operations.
        """
        if self.level is None or self.ui is None:
            return
        self.level.fill_background(surface)
        self.game.decorations.draw(surface)
        self.game.all_sprites.draw(surface)
        self.level.render_special(surface)
        # pygame.draw.rect(surface, (255, 0, 0), self.game.player.hurtbox, 1)
        # for enemy in getattr(self.game, "ennemies", []):
        #     pygame.draw.rect(surface, (255, 0, 255), enemy.hurtbox, 1)
        # redessiner Link pour que le skin 42 soit en dessous
        from pacman.game.entities import Player
        for sprite in self.game.all_sprites:
            if isinstance(sprite, Player):
                surface.blit(sprite.image, sprite.rect)
        self.ui.draw(surface)

        if self.start_level:
            if self.game.current_level_id == "16":
                final_rect = self.final_stage.get_rect(
                    center=(surface.get_width() // 2,
                            surface.get_height() // 2 - 20)
                )
                surface.blit(self.final_stage, final_rect)

        # Render overlay (F1) on top of the game world
        self._render_ai_overlay(surface)
        # Render debug panel or overlay (F3) -- this may be drawn into
        # self._render_ai_debug(surface)

        if self.start_level:
            self._render_level_title(surface)

        # fade in / out black screen
        if self.alpha > 0:
            fade_surface = pygame.Surface(
                (surface.get_width(), surface.get_height()),
                pygame.SRCALPHA
            )
            fade_surface.fill((0, 0, 0, int(self.alpha)))
            surface.blit(fade_surface, (0, 0))

    def _render_ai_overlay(self, surface: pygame.Surface) -> None:
        """Draw enemy targets and paths for debugging.

        Args:
            surface: Surface that receives drawing operations.
        """
        if not self.show_ai_overlay:
            return
        step = TILE_SIZE * 2
        cell_size = max(4, TILE_SIZE // 2)

        def cell_center(grid_x: int, grid_y: int) -> tuple[int, int]:
            """Return the screen center of a maze cell.

            Args:
                grid_x: Horizontal grid coordinate.
                grid_y: Vertical grid coordinate.

            Returns:
                Computed coordinate tuple.
            """
            world_x = self.game.maze_offset_x + TILE_SIZE // 2 + grid_x * step
            world_y = self.game.maze_offset_y + TILE_SIZE // 2 + grid_y * step
            return world_x + step // 2, world_y + step // 2

        for enemy in self.game.ennemies:
            try:
                ai = enemy.ai
                start = ai.position
                target = ai.current_target
                state = ai.state
                # Prefer an enemy-specific color for path rendering
                enemy_type = enemy.enemy_type or ai.enemy_id
                enemy_colors = {
                    'blinky': (255, 0, 0),
                    'pinky': (200, 100, 255),
                    'inky': (90, 210, 255),
                    'clyde': (255, 200, 90),
                }
                enemy_color = None
                if enemy_type is not None:
                    try:
                        enemy_color = enemy_colors.get(str(enemy_type).lower())
                    except Exception:
                        enemy_color = None

                color = (
                    enemy_color
                    if enemy_color is not None
                    else AIDebugTrace.color_for_state(state)
                )

                cache_key = self._build_path_cache_key(
                    enemy=enemy,
                    ai=ai,
                    start=start,
                    target=target,
                    state=state,
                )
                path_positions = self._path_cache.get(cache_key, [])

                # draw path as compact line segments between cell centers
                if path_positions:
                    previous_center = cell_center(*start)
                    for gx, gy in path_positions:
                        current_center = cell_center(gx, gy)
                        pygame.draw.line(
                            surface,
                            color,
                            previous_center,
                            current_center,
                            2,
                        )
                        pygame.draw.circle(surface, color, current_center, 3)
                        previous_center = current_center

                # draw target marker
                if target is not None:
                    cx, cy = cell_center(*target)
                    pygame.draw.line(
                        surface,
                        color,
                        (cx - 6, cy - 6),
                        (cx + 6, cy + 6),
                        2,
                    )
                    pygame.draw.line(
                        surface,
                        color,
                        (cx - 6, cy + 6),
                        (cx + 6, cy - 6),
                        2,
                    )
                    pygame.draw.circle(surface, color, (cx, cy), cell_size, 1)
                    if self.ai_debug_font:
                        label = self.ai_debug_font.render(
                            '[TARGET]', True, (255, 255, 255)
                        )
                        surface.blit(label, (cx + 8, cy - 8))
            except Exception:
                # Don't let debug overlay break the game
                continue

    def _build_path_cache_key(
        self,
        enemy: "Ennemy",
        ai: EnemyBrain,
        start: tuple[int, int],
        target: tuple[int, int] | None,
        state: State,
    ) -> PathCacheKey:
        """Build a cache key for an enemy debug path.

        Args:
            enemy: Enemy sprite being inspected.
            ai: Enemy brain used to choose movement.
            start: Starting grid position.
            target: Target grid position for pathfinding.
            state: AI state to inspect or apply.

        Returns:
            Cache key for the enemy debug path.
        """
        enemy_key = ai.enemy_id or enemy.enemy_type or str(id(enemy))
        state_key = state.value
        level_key = self.game.current_level_id
        return level_key, enemy_key, start, target, state_key

    def _prime_debug_path_cache(self) -> None:
        """Precompute debug paths for all enemies."""
        for enemy in self.game.ennemies:
            ai = enemy.ai
            start = ai.position
            target = ai.current_target
            state = ai.state

            cache_key = self._build_path_cache_key(
                enemy=enemy,
                ai=ai,
                start=start,
                target=target,
                state=state,
            )
            if cache_key in self._path_cache:
                continue
            self._path_cache[cache_key] = self._compute_path_positions(
                enemy=enemy,
                ai=ai,
                start=start,
                target=target,
                state=state,
            )

    def _compute_path_positions(
        self,
        enemy: "Ennemy",
        ai: EnemyBrain,
        start: tuple[int, int],
        target: tuple[int, int] | None,
        state: State,
    ) -> list[tuple[int, int]]:
        """Compute grid positions for an enemy debug path.

        Args:
            enemy: Enemy sprite being inspected.
            ai: Enemy brain used to choose movement.
            start: Starting grid position.
            target: Target grid position for pathfinding.
            state: AI state to inspect or apply.

        Returns:
            Grid positions that make up the debug path.
        """
        behavior = ai.behaviors.get(ai.state)
        if not (
            behavior
            and hasattr(behavior, 'astar_path')
            and target is not None
        ):
            return []

        try:
            moves = behavior.astar_path(start, target)
        except Exception:
            return []

        deltas = {
            'UP': (0, -1),
            'DOWN': (0, 1),
            'LEFT': (-1, 0),
            'RIGHT': (1, 0),
        }
        pos = start
        path_positions: list[tuple[int, int]] = []
        for move in moves:
            dx, dy = deltas.get(move, (0, 0))
            pos = (pos[0] + dx, pos[1] + dy)
            path_positions.append(pos)
        return path_positions

    def _render_ai_debug(self, surface: pygame.Surface) -> None:
        """Draw the AI debug side panel.

        Args:
            surface: Surface that receives drawing operations.
        """
        if not self.show_ai_debug or not self.ai_debug_font:
            return

        rows = self.game.ai_debug_trace.render_rows(limit=16)
        if not rows:
            return

        margin = 8
        line_height = self.ai_debug_font.get_height() + 4
        header_height = self.ai_debug_font.get_height() + 8

        grouped: dict[str, dict[str, str]] = defaultdict(dict)
        for row in rows:
            actor = str(row["actor"])
            if row["state"]:
                grouped[actor]["state"] = str(row["state"])
            grouped[actor]["message"] = str(row["message"])

        header_lines = [
            f"FPS {int(self.game._clock.get_fps())}",
            "AI DEBUG",
            f"F1 pathfinding: {'ON' if self.show_ai_overlay else 'OFF'}",
            f"F2 terminal: {'ON' if self.show_ai_terminal_debug else 'OFF'}",
            f"F3 debug: {'ON' if self.show_ai_debug else 'OFF'}",
            "F4 clear log",
        ]
        header_width = max(
            self.ai_debug_font.size(line)[0] for line in header_lines
        ) + 20

        row_width = 0
        for row in rows:
            line = (
                f"[{int(row['frame']):05d}] {row['actor']}: "
                f"{row['message']}"
            )
            row_width = max(row_width, self.ai_debug_font.size(line)[0] + 20)

        summary_lines: list[str] = []
        for enemy in self.game.ennemies:
            ai = enemy.ai
            actor = ai.enemy_id or enemy.enemy_type
            state_label = ai.state.value
            scatter_total = ai.scatter_round_summary()
            summary = f"{actor}: {state_label} | scatter={scatter_total}"
            summary_lines.append(summary)

        summary_width = 0
        for line in summary_lines:
            summary_width = max(
                summary_width,
                self.ai_debug_font.size(line)[0] + 16,
            )

        width = max(header_width, row_width, summary_width)
        height = (
            header_height * len(header_lines)
            + 8
            + line_height * len(summary_lines)
            + 8
            + line_height * len(rows)
            + 12
        )

        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        # panel.fill((0, 0, 0, 185))
        surface.blit(panel, (margin, margin))

        y = margin + 5
        for index, line in enumerate(header_lines):
            color = (240, 240, 240) if index == 1 else (190, 220, 255)
            if index == 0:
                color = (255, 0, 0)
            # color = (240, 240, 240) if index == 1 else (190, 220, 255)
            text = self.ai_debug_font.render(line, True, color)
            surface.blit(text, (margin + 8, y))
            y += header_height

        y += 2
        separator_width = width - 16
        pygame.draw.line(
            surface,
            (100, 100, 100),
            (margin + 8, y),
            (margin + 8 + separator_width, y),
            1,
        )
        y += 8

        for line in summary_lines:
            if "blinky" in line:
                color = (255, 0, 0)
            elif "pinky" in line:
                color = (200, 100, 255)
            elif "inky" in line:
                color = (90, 210, 255)
            elif "clyde" in line:
                color = (255, 200, 90)
            else:
                color = (255, 230, 170)
            text = self.ai_debug_font.render(
                f"• {line}", True, color
            )
            surface.blit(text, (margin + 8, y))
            y += line_height

        if summary_lines:
            y += 2
            pygame.draw.line(
                surface,
                (100, 100, 100),
                (margin + 8, y),
                (margin + 8 + separator_width, y),
                1,
            )
            y += 8

        for row in rows:
            line = (
                f"[{int(row['frame']):05d}] {row['actor']}: "
                f"{row['message']}"
            )
            state = str(row["state"])
            color = row["color"]
            prefix = f"[{state}] " if state else ""
            text = self.ai_debug_font.render(prefix + line, True, color)
            surface.blit(text, (margin + 8, y))
            y += line_height
