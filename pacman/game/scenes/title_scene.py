import pygame
from typing import TYPE_CHECKING
from pacman.game.scene_manager import Scene
from pacman.game.scenes.main_menu_scene import MainMenuScene
from pacman.resources import resource_path
from pacman.game.sprites import SpriteSheet, StringFont

if TYPE_CHECKING:
    from pacman.game.game import Game


class TitleScreen(Scene):
    """Display the title screen before the main menu."""

    def __init__(self, game: "Game") -> None:
        """Initialize the title screen.

        Args:
            game: Shared game object that owns resources, groups, and state.
        """
        super().__init__(game)
        sheet = SpriteSheet(resource_path("ui", "title_screen.png"), game)
        self.background = sheet.get_sprite(251, 24, 240, 160)
        self.sword = sheet.get_sprite(273, 236, 191, 98, (112, 216, 248))
        self.logo = sheet.get_sprite(285, 447, 167, 88, (112, 216, 248))
        self.start = sheet.get_sprite(327, 188, 89, 18, (112, 216, 248))

        self.start = pygame.transform.scale(
            self.start, (self.start.get_width() * 2,
                         self.start.get_height() * 2))
        self.sword = pygame.transform.scale(
            self.sword, (self.sword.get_width() * 2,
                         self.sword.get_height() * 2))
        self.logo = pygame.transform.scale(
            self.logo, (self.logo.get_width() * 2,
                        self.logo.get_height() * 2))
        self.background = pygame.transform.scale(
            self.background, (game.logic_width, game.logic_height))

        bg_anim_0 = sheet.get_sprite(6, 24, 240, 160, (112, 216, 248))
        bg_anim_1 = sheet.get_sprite(6, 187, 240, 160, (112, 216, 248))
        bg_anim_2 = sheet.get_sprite(6, 350, 240, 160, (112, 216, 248))
        bg_anim_3 = sheet.get_sprite(6, 513, 240, 160, (112, 216, 248))

        bg_anim_0 = pygame.transform.scale(
            bg_anim_0, (game.logic_width, game.logic_height))
        bg_anim_1 = pygame.transform.scale(
            bg_anim_1, (game.logic_width, game.logic_height))
        bg_anim_2 = pygame.transform.scale(
            bg_anim_2, (game.logic_width, game.logic_height))
        bg_anim_3 = pygame.transform.scale(
            bg_anim_3, (game.logic_width, game.logic_height))

        bg_anim_0.set_alpha(100)
        bg_anim_1.set_alpha(100)
        bg_anim_2.set_alpha(100)
        bg_anim_3.set_alpha(100)

        self.bg_animation_frames = [bg_anim_0, bg_anim_1, bg_anim_2, bg_anim_3]
        self.animation_time = 0.0
        self.animation_logo_t = 0.0
        self.frame_duration = 0.2
        self.current_frame_index = 0

    def on_enter(self) -> None:
        """Prepare the scene when it becomes active."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        # Accept synthetic KEYDOWN events emitted from the InputHandler
        """Handle one pygame event for the scene.

        Args:
            event: Event data to handle.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                pygame.time.delay(1)
                next_scene = MainMenuScene(self.game)
                self.game.scene_manager.change(next_scene)

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        self.start.set_alpha(0)
        self.animation_time += dt / 1000.0
        self.animation_logo_t += dt / 1000.0

        if self.animation_time >= self.frame_duration:
            self.current_frame_index = (
                self.current_frame_index + 1) % len(self.bg_animation_frames)
            self.animation_time -= self.frame_duration

        if self.animation_logo_t >= 0.6:
            self.start.set_alpha(255)
            if self.animation_logo_t >= 1.2:
                self.animation_logo_t = 0.0

    def render(self, surface: pygame.Surface) -> None:
        """Draw the current state onto a surface.

        Args:
            surface: Surface that receives drawing operations.
        """
        surface.blit(self.background, (0, 0))
        surface.blit(
            self.bg_animation_frames[self.current_frame_index], (0, 0))
        surface.blit(self.sword,
                     (surface.get_width() // 2 - self.sword.get_width() // 2,
                      surface.get_height() // 3 - self.sword.get_height() // 2
                      ))
        surface.blit(self.logo,
                     (surface.get_width() // 2 - self.logo.get_width() // 2,
                      surface.get_height() // 3 - self.logo.get_height() // 2))
        surface.blit(self.start,
                     (surface.get_width() // 2 - self.start.get_width() // 2,
                      surface.get_height() * 2 // 3
                      - self.start.get_height() // 2))

        string_tool = StringFont(surface, resource_path(
            "fonts", "minish_cap_font.ttf"), 20)
        string = "2026 - Sizem, Wboussah"
        len_string = string_tool.get_width(string)
        string_tool.write("2026 - Sizem, Wboussah",
                          (surface.get_width() - len_string) // 2,
                          surface.get_height() - 38, (0, 0, 0))
        string_tool.write("2026 - Sizem, Wboussah",
                          (surface.get_width() - len_string) // 2,
                          surface.get_height() - 40, (255, 255, 255))
