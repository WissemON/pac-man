import pygame
from typing import TYPE_CHECKING
from pacman.game.scene_manager import Scene
from pacman.resources import resource_path
from pacman.game.sprites import SpriteSheet, StringFont
from pacman.highscores import load_highscores
from pacman.highscores import insert_highscore, save_highscores

if TYPE_CHECKING:
    from pacman.game.game import Game


class WinScreenBase(Scene):
    """Provide shared behavior for victory and ending screens."""

    def __init__(self, game: "Game") -> None:
        """Initialize the win screen base.

        Args:
            game: Shared game object that owns resources, groups, and state.
        """
        super().__init__(game)
        self.phase = "win_screen"
        self.state = "Replay"
        self.zelda = SpriteSheet(resource_path("player", "zelda.gif"), game)
        self.link_s = SpriteSheet(
            resource_path("player", "minish_cap_sprites.png"),
            game)

        self.time = 0.0
        self.frame_index = 0
        self.frame_delay = 120
        zelda_anim = [
            self.zelda.get_sprite(1, 222, 18, 29, (255, 255, 255)),
            self.zelda.get_sprite(21, 222, 18, 29, (255, 255, 255)),
            self.zelda.get_sprite(40, 222, 18, 29, (255, 255, 255)),
            self.zelda.get_sprite(60, 222, 18, 29, (255, 255, 255)),
            self.zelda.get_sprite(81, 222, 18, 29, (255, 255, 255)),
            self.zelda.get_sprite(100, 222, 18, 29, (255, 255, 255)),
        ]
        self.zelda_anim = [
            pygame.transform.scale(sprite, (sprite.get_width() * 3,
                                            sprite.get_height() * 3))
            for sprite in zelda_anim
        ]

        link = self.link_s.get_sprite(47, 223, 18, 25)
        self.link = pygame.transform.scale(link, (link.get_width() * 3,
                                                  link.get_height() * 3))

        sheet_skins = SpriteSheet(
            resource_path("ui", "scores_skins.png"), game)
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

        self.bgm_loop = resource_path("music", "credits.mp3")

    def on_enter(self) -> None:
        """Prepare the scene when it becomes active."""
        self.play_theme(pygame.USEREVENT)

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

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        self.time += dt
        if self.time >= self.frame_delay:
            self.time = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.zelda_anim)

    def render(self, surface: pygame.Surface) -> None:
        """Draw the current state onto a surface.

        Args:
            surface: Surface that receives drawing operations.
        """
        surface.fill((0, 0, 0))
        font = StringFont(surface,
                          resource_path("fonts", "zelda-gba.ttf"), 40)

        len_s = font.get_width("SCORE: " + str(self.game.in_game_score)) / 2
        font.write(
            "SCORE: " + str(self.game.in_game_score),
            surface.get_width() // 2 - len_s,
            30,
            (255, 255, 255)
        )

        len_s = font.get_width(
            "ITEMS COLLECTED: " + str(self.game.collected_items)) / 2
        items = len(self.game.collected_items)
        font.write(
            "ITEMS COLLECTED: " + str(items),
            surface.get_width() // 2 - len_s,
            80,
            (255, 255, 255)
        )

        len_s = font.get_width("THANKS LINK, YOU'RE") / 2
        font.write(
            "THANKS LINK, YOU'RE",
            surface.get_width() // 2 - len_s,
            surface.get_height() // 2 - 20,
            (255, 255, 255)
        )
        len_s = font.get_width("THE HERO OF HYRULE.") / 2
        font.write(
            "THE HERO OF HYRULE.",
            surface.get_width() // 2 - len_s,
            surface.get_height() // 2 + 20,
            (255, 255, 255)
        )
        # put here sprites of Zelda and Link (+60 height)
        surface.blit(self.zelda_anim[self.frame_index],
                     (surface.get_width() // 2 - 100,
                      surface.get_height() // 2 + 70))
        surface.blit(self.link,
                     (surface.get_width() // 2,
                      surface.get_height() // 2 + 82))

        len_s = font.get_width("FINALLY,") / 2
        font.write(
            "FINALLY,",
            surface.get_width() // 2 - len_s,
            surface.get_height() // 2 + 160,
            (255, 255, 255)
        )

        len_s = font.get_width("PEACE RETURNS TO HYRULE.") / 2
        font.write(
            "PEACE RETURNS TO HYRULE.",
            surface.get_width() // 2 - len_s,
            surface.get_height() // 2 + 200,
            (255, 255, 255)
        )

        len_s = font.get_width("THIS ENDS THE STORY.") / 2
        font.write(
            "THIS ENDS THE STORY.",
            surface.get_width() // 2 - len_s,
            surface.get_height() // 2 + 300,
            (255, 255, 255)
        )

        self.to_game(surface)

        self.to_main_menu(surface)

        self.save_score(surface)

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
                       surface.get_height() // 3, (255, 255, 255))
        if self.phase == "profile_skin":
            font = StringFont(surface,
                              resource_path("font", "zelda-gba.ttf"), 30)
            prompt = "Choose Skin (Left/Right)"
            font.write(prompt,
                       surface.get_width() // 2 - font.get_width(prompt) // 2,
                       surface.get_height() // 3, (255, 255, 255))
            skin_name = self.skin_color
            skin_image = self.sheet_skins[skin_name]
            surface.blit(skin_image, (
                surface.get_width() // 2 - skin_image.get_width() // 2,
                surface.get_height() // 3 + 20))
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
                           surface.get_height() // 3, (255, 255, 255))
            else:
                font.write("Quit", surface.get_width() // 2 - len_s // 2,
                           surface.get_height() // 3, (100, 100, 100))

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
                           surface.get_height() // 3 + 30, (255, 255, 255))
            else:
                font.write("Replay", surface.get_width() // 2 - len_s // 2,
                           surface.get_height() // 3 + 30, (100, 100, 100))
