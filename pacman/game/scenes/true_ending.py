import pygame
from typing import TYPE_CHECKING
from pacman.game.scene_manager import Scene
from pacman.resources import resource_path
from pacman.game.sprites import SpriteSheet, StringFont
from pacman.highscores import load_highscores
from pacman.highscores import insert_highscore, save_highscores

if TYPE_CHECKING:
    from pacman.game.game import Game


class TrueEndingScene(Scene):
    """Display the true ending sequence."""

    def __init__(self, game: "Game") -> None:
        """Initialize the true ending scene.

        Args:
            game: Shared game object that owns resources, groups, and state.
        """
        super().__init__(game)
        self.state = "1st_text"
        self.phase: str | None = None
        self.alpha = 0.0
        self.timer_text = 0.0
        self.username = ""
        self.score_saved = False
        self.skin_color = "green"

        self.sprite_sheet = SpriteSheet(
            resource_path("pics", "TMC_Credits.png"),
            game)
        glass = self.sprite_sheet.get_sprite(381, 164, 216, 115,
                                             (255, 255, 255))
        self.glass = pygame.transform.scale(
            glass, (glass.get_width() * 3, glass.get_height() * 3))

        sheet_skins = SpriteSheet(resource_path("ui", "scores_skins.png"),
                                  game)
        sheet_skins_a = [
            sheet_skins.get_sprite(0, 0, 16, 14),
            sheet_skins.get_sprite(0, 13, 16, 14),
            sheet_skins.get_sprite(0, 26, 16, 14),
            sheet_skins.get_sprite(0, 39, 16, 14),
            sheet_skins.get_sprite(0, 52, 16, 14),
        ]
        self.sheet_skins = {
            "green": pygame.transform.scale(sheet_skins_a[0], (32, 32)),
            "dark": pygame.transform.scale(sheet_skins_a[1], (32, 32)),
            "purple": pygame.transform.scale(sheet_skins_a[2], (32, 32)),
            "blue": pygame.transform.scale(sheet_skins_a[3], (32, 32)),
            "red": pygame.transform.scale(sheet_skins_a[4], (32, 32)),
        }

    def on_enter(self) -> None:
        """Prepare the scene when it becomes active."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one pygame event for the scene.

        Args:
            event: Event data to handle.
        """
        if event.type == pygame.KEYDOWN:
            if self.phase == "win_screen":
                if event.key == pygame.K_RETURN:
                    self.game.sfx['press_menu'].play()
                self.phase = "profile_name"
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
                        self.game.scene_manager.change(PlayScene(self.game))
                    if self.state == "main_menu":
                        from pacman.game.scenes import MainMenuScene as Menu
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
                    self.state = "main_menu"

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        if self.state == "1st_text":
            self.alpha += dt // 8
            if self.alpha > 255:
                self.alpha = 255
                if self.alpha == 255:
                    self.timer_text += dt
                    if self.timer_text > 3500:
                        self.state = "2nd_text"
                        self.alpha = 0.0
                        self.timer_text = 0.0
                        self.alpha -= dt // 8
                        if self.alpha < 0:
                            self.alpha = 0.0
        elif self.state == "2nd_text":
            self.alpha += dt // 8
            if self.alpha > 255:
                self.alpha = 255
                if self.alpha == 255:
                    self.timer_text += dt
                    if self.timer_text > 3500:
                        self.state = "3rd_text"
                        self.alpha = 0.0
                        self.timer_text = 0.0
        elif self.state == "3rd_text":
            self.alpha += dt // 8
            if self.alpha > 255:
                self.alpha = 255
                if self.alpha == 255:
                    self.timer_text += dt
                    if self.timer_text > 3500:
                        self.state = "profile_name"
                        self.phase = "profile_name"
                        self.alpha = 0.0
                        self.timer_text = 0.0

    def render(self, surface: pygame.Surface) -> None:
        """Draw the current state onto a surface.

        Args:
            surface: Surface that receives drawing operations.
        """
        surface.fill((0, 0, 0))

        surface.blit(self.glass,
                     ((surface.get_width() - self.glass.get_width()) // 2,
                      0))

        self.first_text(surface)
        self.second_text(surface)
        self.third_text(surface)

        self.save_score(surface)
        self.to_game(surface)
        self.to_main_menu(surface)

    def first_text(self, surface: pygame.Surface) -> None:
        """Draw the first true-ending text block.

        Args:
            surface: Surface that receives drawing operations.
        """
        font = StringFont(surface, resource_path(
            "ui", "arcade.ttf"), 40)
        len_s = font.get_width("Thus did Link's quest")
        if self.state == "1st_text":
            font.write("Thus did Link's quest",
                       surface.get_width() // 2 - len_s // 2,
                       surface.get_height() // 2 - 20,
                       (255, 255, 255),
                       self.alpha)
            len_s = font.get_width("come to an end.")
            font.write("come to an end.",
                       surface.get_width() // 2 - len_s // 2,
                       surface.get_height() // 2 + 20,
                       (255, 255, 255),
                       self.alpha)

    def second_text(self, surface: pygame.Surface) -> None:
        """Draw the second true-ending text block.

        Args:
            surface: Surface that receives drawing operations.
        """
        font = StringFont(surface, resource_path(
            "ui", "arcade.ttf"), 40)
        len_s = font.get_width("But surely, this is not the end of Zelda")
        if self.state == "2nd_text":
            font.write("But surely, this is not the end of Zelda",
                       surface.get_width() // 2 - len_s // 2,
                       surface.get_height() // 2 - 20,
                       (255, 255, 255),
                       self.alpha)
            len_s = font.get_width("and Link's adventures in Hyrule.")
            font.write("and Link's adventures in Hyrule.",
                       surface.get_width() // 2 - len_s // 2,
                       surface.get_height() // 2 + 20,
                       (255, 255, 255),
                       self.alpha)

    def third_text(self, surface: pygame.Surface) -> None:
        """Draw the third true-ending text block.

        Args:
            surface: Surface that receives drawing operations.
        """
        font = StringFont(surface, resource_path(
            "ui", "arcade.ttf"), 40)
        len_s = font.get_width("The legend will continue...")
        if self.state == "3rd_text":
            font.write("The legend will continue...",
                       surface.get_width() // 2 - len_s // 2,
                       surface.get_height() // 2 - 20,
                       (255, 255, 255),
                       self.alpha)

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
