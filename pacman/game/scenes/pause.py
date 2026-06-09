import pygame
from typing import TYPE_CHECKING
from pacman.game.scene_manager import Scene
from pacman.resources import resource_path
from pacman.game.sprites import SpriteSheet, StringFont
from pacman.game.scenes.main_menu_scene import MainMenuScene as MainMenu

if TYPE_CHECKING:
    from pacman.game.game import Game


class PauseScene(Scene):
    """Display and control the pause overlay."""

    def __init__(self, game: "Game") -> None:
        """Initialize the pause scene.

        Args:
            game: Shared game object that owns resources, groups, and state.
        """
        super().__init__(game)
        sheet = SpriteSheet(resource_path("ui", "map.gif"), game)
        self.background = sheet.get_sprite(0, 167, 208, 144)
        self.background = pygame.transform.scale(
            self.background, (game.logic_width, game.logic_height))
        self.state = "resume"
        self.game.sfx['pause_start'].set_volume(0.5)
        self.game.sfx['pause_exit'].set_volume(0.5)

    def on_enter(self) -> None:
        """Prepare the scene when it becomes active."""
        self.game.sfx['pause_start'].play()

    def on_exit(self) -> None:
        """Clean up before the scene leaves the stack."""
        self.game.sfx['pause_exit'].play()

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one pygame event for the scene.

        Args:
            event: Event data to handle.
        """
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)

    def _handle_keydown(self, key: int) -> None:
        """Handle one key press event.

        Args:
            key: Configuration key to validate.
        """
        if key == pygame.K_ESCAPE:
            self.game.scene_manager.pop()
        if key == pygame.K_UP:
            if self.state == "resume":
                self.game.sfx['move_pause'].play()
                self.state = "main_menu"
            elif self.state == "main_menu":
                self.game.sfx['move_pause'].play()
                self.state = "resume"
        if key == pygame.K_DOWN:
            if self.state == "resume":
                self.game.sfx['move_pause'].play()
                self.state = "main_menu"
            elif self.state == "main_menu":
                self.game.sfx['move_pause'].play()
                self.state = "resume"
        if key == pygame.K_RETURN:
            if self.state == "resume":
                self.game.scene_manager.pop()
            elif self.state == "main_menu":
                self.game.scene_manager.change(MainMenu(self.game))

    def render(self, surface: pygame.Surface) -> None:
        """Draw the current state onto a surface.

        Args:
            surface: Surface that receives drawing operations.
        """
        surface.blit(self.background, (0, 0))

        self.to_game(surface)

        self.to_main_menu(surface)

    def to_game(self, surface: pygame.Surface) -> None:
        """Start or restart gameplay.

        Args:
            surface: Surface that receives drawing operations.
        """
        font = StringFont(surface, resource_path("font", "zelda-gba.ttf"), 30)
        if self.state == "resume":
            len_s = font.get_width("> RESUME")
            font.write("> RESUME", surface.get_width() // 2 - len_s // 2,
                       surface.get_height() // 2 - 30, (255, 255, 255))
        else:
            len_s = font.get_width("RESUME")
            font.write("RESUME", surface.get_width() // 2 - len_s // 2,
                       surface.get_height() // 2 - 30, (100, 100, 100))

    def to_main_menu(self, surface: pygame.Surface) -> None:
        """Return to the main menu scene.

        Args:
            surface: Surface that receives drawing operations.
        """
        font = StringFont(surface, resource_path("font", "zelda-gba.ttf"), 30)
        if self.state == "main_menu":
            len_s = font.get_width("> MAIN MENU")
            font.write("> MAIN MENU", surface.get_width() // 2 - len_s // 2,
                       surface.get_height() // 2, (255, 255, 255))
        else:
            len_s = font.get_width("MAIN MENU")
            font.write("MAIN MENU", surface.get_width() // 2 - len_s // 2,
                       surface.get_height() // 2, (100, 100, 100))
