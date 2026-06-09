import pygame
from typing import TYPE_CHECKING
from pacman.game.scene_manager import Scene
from pacman.resources import resource_path
from pacman.game.sprites import SpriteSheet, StringFont
from pacman.highscores import load_highscores
from pacman.highscores import insert_highscore, save_highscores

if TYPE_CHECKING:
    from pacman.game.game import Game


class GameOverScene(Scene):
    """Display the game-over menu and score entry flow."""

    def __init__(self, game: "Game") -> None:
        """Initialize the game over scene.

        Args:
            game: Shared game object that owns resources, groups, and state.
        """
        super().__init__(game)
        sheet = SpriteSheet(resource_path("ui", "map.gif"), game)
        sheet_skins = SpriteSheet(resource_path("ui", "scores_skins.png"),
                                  game)
        self.background = sheet.get_sprite(0, 167, 208, 144)
        self.background = pygame.transform.scale(
            self.background, (game.logic_width // 2, game.logic_height // 2))
        self.state = "Replay"
        self.phase = "profile_name"
        self.username = ""
        sheet_skins_a = [
            sheet_skins.get_sprite(0, 0, 16, 14),
            sheet_skins.get_sprite(0, 13, 16, 14),
            sheet_skins.get_sprite(0, 26, 16, 14),
            sheet_skins.get_sprite(0, 39, 16, 14),
            sheet_skins.get_sprite(0, 52, 16, 14)
        ]
        self.sheet_skins = {
            "green": pygame.transform.scale(sheet_skins_a[0], (32, 32)),
            "dark": pygame.transform.scale(sheet_skins_a[1], (32, 32)),
            "purple": pygame.transform.scale(sheet_skins_a[2], (32, 32)),
            "blue": pygame.transform.scale(sheet_skins_a[3], (32, 32)),
            "red": pygame.transform.scale(sheet_skins_a[4], (32, 32))
        }
        self.skin_options = [
            "green",
            "dark",
            "purple",
            "blue",
            "red"
        ]
        self.skin_index = 0
        self.skin_color = "green"
        self.score_saved = False

        self.bgm_loop = resource_path("music", "game_over.mp3")
        self.intro_end = pygame.USEREVENT + 1
        self.waiting_for_loop = False
        self.game.sfx['move_menu'].set_volume(0.5)
        self.game.sfx['press_menu'].set_volume(0.5)

    def on_enter(self) -> None:
        """Prepare the scene when it becomes active."""
        self.game.collected_items = {}
        self.game.lives = self.game.config["lives"]
        self.play_theme(self.intro_end)

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
            self._handle_keydown(event)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle one key press event.

        Args:
            event: Event data to handle.
        """
        if self.phase == "menu":
            if event.key == pygame.K_UP:
                self.game.sfx['move_menu'].play()
                if self.state == "Replay":
                    self.state = "main_menu"
                elif self.state == "main_menu":
                    self.state = "Replay"
            elif event.key == pygame.K_DOWN:
                self.game.sfx['move_menu'].play()
                if self.state == "main_menu":
                    self.state = "Replay"
                elif self.state == "Replay":
                    self.state = "main_menu"
            if event.key == pygame.K_RETURN:
                self.game.sfx['press_menu'].play()
                if self.state == "Replay":
                    from pacman.game.scenes import PlayScene
                    self.game.lives = self.game.config["lives"]
                    self.game.in_game_score = 0
                    self.game.scene_manager.change(PlayScene(self.game))
                if self.state == "main_menu":
                    from pacman.game.scenes import MainMenuScene as Menu
                    self.game.lives = self.game.config["lives"]
                    self.game.in_game_score = 0
                    self.game.scene_manager.change(Menu(self.game))

        elif self.phase == "profile_name":
            if not hasattr(event, "unicode"):
                return
            if event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.key == pygame.K_RETURN or\
                    event.key == pygame.K_KP_ENTER:
                if 0 < len(self.username) <= 10:
                    self.game.sfx['press_menu'].play()
                    self.phase = "profile_skin"
            else:
                if len(self.username) < 10\
                        and (event.unicode.isalnum()
                             or event.unicode.isspace()):
                    self.username += event.unicode
                else:
                    self.game.sfx['error'].play()
                    self.game.sfx['error'].set_volume(0.3)
        elif self.phase == "profile_skin":
            if event.key == pygame.K_LEFT:
                if self.skin_color == "green":
                    self.skin_color = "red"
                elif self.skin_color == "dark":
                    self.skin_color = "green"
                elif self.skin_color == "purple":
                    self.skin_color = "dark"
                elif self.skin_color == "blue":
                    self.skin_color = "purple"
                elif self.skin_color == "red":
                    self.skin_color = "blue"
            elif event.key == pygame.K_RIGHT:
                if self.skin_color == "green":
                    self.skin_color = "dark"
                elif self.skin_color == "dark":
                    self.skin_color = "purple"
                elif self.skin_color == "purple":
                    self.skin_color = "blue"
                elif self.skin_color == "blue":
                    self.skin_color = "red"
                elif self.skin_color == "red":
                    self.skin_color = "green"
            elif event.key == pygame.K_RETURN:
                self.phase = "menu"

    def render(self, surface: pygame.Surface) -> None:
        """Draw the current state onto a surface.

        Args:
            surface: Surface that receives drawing operations.
        """
        surface.blit(self.background,
                     (surface.get_width() // 4, surface.get_height() // 4))

        self.game_over(surface)

        self.draw_score(surface)

        self.to_game(surface)

        self.to_main_menu(surface)

        self.save_score(surface)

    def draw_score(self, surface: pygame.Surface) -> None:
        """Draw the final run score at the top of the screen.

        Args:
            surface: Surface that receives drawing operations.
        """
        font = StringFont(surface, resource_path("font", "zelda-gba.ttf"), 40)
        score_text = f"SCORE: {self.game.in_game_score}"
        text_x = surface.get_width() // 2 - font.get_width(score_text) // 2
        font.write(score_text, text_x + 2, 30, (0, 0, 0))
        font.write(score_text, text_x, 28, (255, 255, 255))

    def save_score(self, surface: pygame.Surface) -> None:
        """Persist the current run score.

        Args:
            surface: Surface that receives drawing operations.
        """
        if self.phase == "profile_name":
            font = StringFont(surface,
                              resource_path("font", "zelda-gba.ttf"), 30)
            prompt = "Enter Name:" + self.username
            font.write(prompt,
                       surface.get_width() // 2 - font.get_width(prompt) // 2,
                       surface.get_height() // 2, (255, 255, 255))
        if self.phase == "profile_skin":
            font = StringFont(surface,
                              resource_path("font", "zelda-gba.ttf"), 30)
            prompt = "Choose Skin (Left/Right)"
            font.write(prompt,
                       surface.get_width() // 2 - font.get_width(prompt) // 2,
                       surface.get_height() // 2, (255, 255, 255))
            skin_name = self.skin_color
            skin_image = self.sheet_skins[skin_name]
            surface.blit(skin_image, (
                surface.get_width() // 2 - skin_image.get_width() // 2,
                surface.get_height() // 2 + 20))
        if self.phase == "menu" and not self.score_saved:
            highscores = load_highscores()
            highscores = insert_highscore(
                highscores, self.username,
                self.game.in_game_score,
                self.skin_color,
                self.game.cheat
            )
            save_highscores(highscores)
            self.score_saved = True
            self.game.highscores = load_highscores()

    def to_main_menu(self, surface: pygame.Surface) -> None:
        """Return to the main menu scene.

        Args:
            surface: Surface that receives drawing operations.
        """
        if self.phase == "menu":
            font = StringFont(surface,
                              resource_path("font", "zelda-gba.ttf"), 30)
            len_s = font.get_width("Quit")
            if self.state == "main_menu":
                font.write("> Quit", surface.get_width() // 2 - len_s // 2,
                           surface.get_height() // 2, (255, 255, 255))
            else:
                font.write("Quit", surface.get_width() // 2 - len_s // 2,
                           surface.get_height() // 2, (100, 100, 100))

    def to_game(self, surface: pygame.Surface) -> None:
        """Start or restart gameplay.

        Args:
            surface: Surface that receives drawing operations.
        """
        if self.phase == "menu":
            font = StringFont(surface,
                              resource_path("font", "zelda-gba.ttf"), 30)
            len_s = font.get_width("Replay")
            if self.state == "Replay":
                font.write("> Replay", surface.get_width() // 2 - len_s // 2,
                           surface.get_height() // 2 + 30, (255, 255, 255))
            else:
                font.write("Replay", surface.get_width() // 2 - len_s // 2,
                           surface.get_height() // 2 + 30, (100, 100, 100))

    def game_over(self, surface: pygame.Surface) -> None:
        """Return to the game-over flow.

        Args:
            surface: Surface that receives drawing operations.
        """
        font = StringFont(surface, resource_path("font", "zelda-gba.ttf"), 80)
        len_s = font.get_width("GAME OVER")
        font.write("GAME OVER", surface.get_width() // 2 - len_s // 2,
                   surface.get_height() // 2 - 220, (252, 213, 47))
        font.write("GAME OVER", surface.get_width() // 2 - len_s // 2 + 2,
                   surface.get_height() // 2 - 220, (202, 0, 6))
