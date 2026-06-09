import pygame
import webbrowser
from typing import TYPE_CHECKING, TypedDict
from pacman.game.scene_manager import Scene
from pacman.highscores import load_highscores
from pacman.resources import resource_path
from pacman.game.sprites import SpriteSheet, StringFont
from pacman.game.save import load_levels

if TYPE_CHECKING:
    from pacman.game.game import Game


class MenuAnim(TypedDict):
    """Store animation state for one main menu panel."""
    target_x: float
    current_x: float
    y: float


class MainMenuScene(Scene):
    """Display and control the main menu."""

    def __init__(self, game: "Game") -> None:
        """Initialize the main menu scene.

        Args:
            game: Shared game object that owns resources, groups, and state.
        """
        super().__init__(game)
        self.highscores = game.highscores
        sheet = SpriteSheet(resource_path("ui", "file_select.png"), game)
        self.font = StringFont(
            game._logic_screen,
            resource_path("fonts", "PixelOperator-Bold.ttf"),
            30,
        )

        bg_0 = sheet.get_sprite(2, 668, 240, 160)
        bg_1 = sheet.get_sprite(243, 668, 240, 160)
        bg_3 = sheet.get_sprite(2, 829, 240, 160)
        bg_4 = sheet.get_sprite(243, 829, 240, 160)

        bg_0 = pygame.transform.scale(
            bg_0, (game.logic_width, game.logic_height))
        bg_1 = pygame.transform.scale(
            bg_1, (game.logic_width, game.logic_height))
        bg_3 = pygame.transform.scale(
            bg_3, (game.logic_width, game.logic_height))
        bg_4 = pygame.transform.scale(
            bg_4, (game.logic_width, game.logic_height))

        cheater = SpriteSheet(resource_path("enemies", "cucoos.png"), game)
        self.cheater = cheater.get_sprite(55, 85, 10, 11, (255, 255, 255))
        self.cheater = pygame.transform.scale(
            self.cheater, (int(self.cheater.get_width() * 1.5),
                           int(self.cheater.get_height() * 1.5)))

        self.bg_animation_frames = [bg_0, bg_1, bg_3, bg_4]
        self.animation_time = 0.0
        self.frame_duration = 0.8
        self.current_frame_index = 0

        center_x = game.logic_width // 2 - 69
        start_x = -200

        self.menu_items: dict[str, MenuAnim] = {
            "Start": {
                "target_x": center_x,
                "current_x": start_x,
                "y": game.logic_height // 2 - 25
            },
            "Scores": {
                "target_x": center_x,
                "current_x": start_x,
                "y": game.logic_height // 2 + 35
            },
            "Help": {
                "target_x": center_x,
                "current_x": start_x,
                "y": game.logic_height // 2 + 95
            },
            "Pics": {
                "target_x": center_x,
                "current_x": start_x,
                "y": game.logic_height // 2 + 155
            },
            "Exit": {
                "target_x": center_x,
                "current_x": start_x,
                "y": game.logic_height // 2 + 215
            },
        }
        self.slide_speed = 0.12

        button = sheet.get_sprite(2, 32, 69, 26, (167, 167, 227))
        button_select = sheet.get_sprite(2, 62, 69, 26, (167, 167, 227))
        button_press = sheet.get_sprite(255, 122, 69, 26, (167, 167, 227))

        button_select = pygame.transform.scale(
            button_select, (button_select.get_width() * 2,
                            button_select.get_height() * 2))
        button = pygame.transform.scale(
            button, (button.get_width() * 2, button.get_height() * 2))
        button_press = pygame.transform.scale(
            button_press, (button_press.get_width() * 2,
                           button_press.get_height() * 2))
        self.button = button
        self.button_select = button_select
        self.button_press = button_press

        cursor_0 = sheet.get_sprite(2, 116, 16, 16, (167, 167, 227))
        cursor_1 = sheet.get_sprite(19, 116, 16, 16, (167, 167, 227))
        cursor_2 = sheet.get_sprite(36, 116, 16, 16, (167, 167, 227))
        cursor_3 = sheet.get_sprite(53, 116, 16, 16, (167, 167, 227))
        cursor_4 = sheet.get_sprite(70, 116, 16, 16, (167, 167, 227))
        cursor_5 = sheet.get_sprite(87, 116, 16, 16, (167, 167, 227))
        cursor_6 = sheet.get_sprite(104, 116, 16, 16, (167, 167, 227))

        cursor_0 = pygame.transform.scale(
            cursor_0, (cursor_0.get_width() * 2, cursor_0.get_height() * 2))
        cursor_1 = pygame.transform.scale(
            cursor_1, (cursor_1.get_width() * 2, cursor_1.get_height() * 2))
        cursor_2 = pygame.transform.scale(
            cursor_2, (cursor_2.get_width() * 2, cursor_2.get_height() * 2))
        cursor_3 = pygame.transform.scale(
            cursor_3, (cursor_3.get_width() * 2, cursor_3.get_height() * 2))
        cursor_4 = pygame.transform.scale(
            cursor_4, (cursor_4.get_width() * 2, cursor_4.get_height() * 2))
        cursor_5 = pygame.transform.scale(
            cursor_5, (cursor_5.get_width() * 2, cursor_5.get_height() * 2))
        cursor_6 = pygame.transform.scale(
            cursor_6, (cursor_6.get_width() * 2, cursor_6.get_height() * 2))

        self.cursor_frames = [cursor_0, cursor_1,
                              cursor_2, cursor_3, cursor_4, cursor_5, cursor_6]
        self.frame = 0
        self.anim_cursor_time = 0.0
        self.frame_cursor = 0.2
        self.state = "Start"

        description = sheet.get_sprite(255, 92, 220, 22, (167, 167, 227))
        description = pygame.transform.scale(
            description,
            (description.get_width() * 2, description.get_height() * 2))
        self.description = description

        box = sheet.get_sprite(255, 188, 228, 124, (167, 167, 227))
        box = pygame.transform.rotate(box, 90)
        box = pygame.transform.scale(
            box, (box.get_width() * 2, box.get_height() * 2))
        self.box = box

        box_help_s = sheet.get_sprite(2, 324, 124, 92, (167, 167, 227))
        box_help_s = pygame.transform.scale(
            box_help_s, (box_help_s.get_width() * 4,
                         box_help_s.get_height() * 4))
        self.box_help_s = box_help_s

        box_x = int(
            self.game.logic_width // 2 - self.box_help_s.get_width() // 2 - 10)
        box_y = self.game.logic_height // 2 - self.box_help_s.get_height() // 2
        self.help_anim: MenuAnim = {
            "target_x": box_x,
            "current_x": self.game.logic_width + 200,
            "y": box_y
        }

        self.pics_anim: MenuAnim = {
            "target_x": box_x,
            "current_x": self.game.logic_width + 200,
            "y": box_y
        }

        self.score_anim: MenuAnim = {
            "target_x": (
                self.game.logic_width - self.box.get_width()) // 2,
            "current_x": (
                self.game.logic_width + 200),
            "y": self.game.logic_height // 2 + 35
        }
        sheet_icon = SpriteSheet(resource_path("ui", "scores_skins.png"), game)
        self.icons = {
            "green": [
                sheet_icon.get_sprite(0, 0, 16, 14),
                sheet_icon.get_sprite(18, 0, 16, 14),
            ],
            "dark": [
                sheet_icon.get_sprite(0, 13, 16, 14),
                sheet_icon.get_sprite(18, 13, 16, 14),
            ],
            "purple": [
                sheet_icon.get_sprite(0, 26, 16, 14),
                sheet_icon.get_sprite(18, 26, 16, 14),
            ],
            "blue": [
                sheet_icon.get_sprite(0, 39, 16, 14),
                sheet_icon.get_sprite(18, 39, 16, 14),
            ],
            "red": [
                sheet_icon.get_sprite(0, 52, 16, 14),
                sheet_icon.get_sprite(18, 52, 16, 14),
            ]
        }

        levels_pics_to_scale = [
            SpriteSheet(resource_path("pics", "TMC_1.png"),
                        game).get_sprite(0, 0, 1000, 1875),
            SpriteSheet(resource_path("pics", "TMC_2.png"),
                        game).get_sprite(0, 0, 1000, 1333),
            SpriteSheet(resource_path("pics", "TMC_3.png"),
                        game).get_sprite(0, 0, 886, 1044),
            SpriteSheet(resource_path("pics", "TMC_4.png"),
                        game).get_sprite(0, 0, 886, 1045),
            SpriteSheet(resource_path("pics", "TMC_5.png"),
                        game).get_sprite(0, 0, 886, 1202),
            SpriteSheet(resource_path("pics", "TMC_6.png"),
                        game).get_sprite(0, 0, 600, 400),
            SpriteSheet(resource_path("pics", "TMC_7.png"),
                        game).get_sprite(0, 0, 1000, 730),
            SpriteSheet(resource_path("pics", "TMC_8.png"),
                        game).get_sprite(0, 0, 1000, 665),
            SpriteSheet(resource_path("pics", "TMC_9.png"),
                        game).get_sprite(0, 0, 1000, 1514),
            SpriteSheet(resource_path("pics", "TMC_10.png"),
                        game).get_sprite(0, 0, 886, 1202),
            SpriteSheet(resource_path("pics", "TMC_11.png"),
                        game).get_sprite(0, 0, 1000, 1151),
            SpriteSheet(resource_path("pics", "TMC_12.png"),
                        game).get_sprite(0, 0, 1000, 1200),
            SpriteSheet(resource_path("pics", "TMC_13.png"),
                        game).get_sprite(0, 0, 1000, 1333),
            SpriteSheet(resource_path("pics", "TMC_14.png"),
                        game).get_sprite(0, 0, 1000, 1333),
            SpriteSheet(resource_path("pics", "TMC_15.png"),
                        game).get_sprite(0, 0, 1000, 1435),
            SpriteSheet(resource_path("pics", "TMC_16.png"),
                        game).get_sprite(0, 0, 1000, 1474),
            SpriteSheet(resource_path("pics", "TMC_17.png"),
                        game).get_sprite(0, 0, 1000, 700),
        ]

        max_width = self.box_help_s.get_width() - 60
        max_height = self.box_help_s.get_height() - 80
        self.levels_pics = [
            pygame.transform.scale(pic,
                                   (int(pic.get_width() * min(
                                       max_width / pic.get_width(),
                                       max_height / pic.get_height())),
                                    int(pic.get_height() * min(
                                        max_width / pic.get_width(),
                                        max_height / pic.get_height())))
                                   ) for pic in levels_pics_to_scale
        ]
        self.i_state = 0

        self.bgm_loop = resource_path("music", "file_select.mp3")
        self.intro_end = pygame.USEREVENT + 1
        self.waiting_for_loop = False
        self.game.sfx['move_menu'].set_volume(0.2)
        self.game.sfx['press_menu'].set_volume(0.2)
        self.game.sfx['exit_item'].set_volume(0.2)

        self.cheat_code = [
            'UP',
            'UP',
            "DOWN",
            'DOWN',
            'LEFT',
            'RIGHT',
            'LEFT',
            'RIGHT',
        ]

        self.secret_seq = [
            'j',
            'u',
            'l',
            'i',
            'e',
            't',
            't',
            'e',
        ]

        self.pac_man_code = [
            'p',
            'a',
            'c',
            'm',
            'a',
            'n',
        ]

        self.m_code = [
            'm',
            'e',
            'h',
            'd',
            'i'
        ]
        m_sheet = SpriteSheet(resource_path("pics", "m.jpg"), game)
        self.m_image = m_sheet.get_sprite(0, 0, 3072, 4096)
        self.m_image = self._scale_secret_image(self.m_image)
        self.m_image_timer = 0.0
        self.m_image_duration = 0.5

        self.input_history: list[str] = []
        self.max_buffer_size = max(
            len(self.cheat_code),
            len(self.secret_seq),
            len(self.pac_man_code),
            len(self.m_code),
        )

        self.sprite_sheet = SpriteSheet(
            resource_path("pics", "TMC_Credits.png"),
            game)
        glass = self.sprite_sheet.get_sprite(381, 164, 216, 115,
                                             (255, 255, 255))
        self.glass = pygame.transform.scale(
            glass, (glass.get_width() * 2, glass.get_height() * 2))

        self.save_level = 0

    def _gallery_max_index(self) -> int:
        """Return the last visible gallery index.

        Returns:
            Maximum gallery index currently reachable.
        """
        unlocked_count = max(self.save_level, 0)
        return min(max(unlocked_count - 1, 0), len(self.levels_pics) - 1)

    def on_enter(self) -> None:
        """Prepare the scene when it becomes active."""
        self.game.collected_items = {}
        self.game.lives = self.game.config["lives"]
        self.game.in_game_score = 0
        self.save_level = load_levels()
        self.highscores = load_highscores()
        self.game.cheat = False
        self.play_theme(self.intro_end)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one pygame event for the scene.

        Args:
            event: Event data to handle.
        """
        if event.type == self.intro_end:
            if self.waiting_for_loop:
                # force loop to stop intro
                pygame.mixer.music.load(self.bgm_loop)
                pygame.mixer.music.play(-1)
                self.waiting_for_loop = False

        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle one key press event.

        Args:
            event: Event data to handle.
        """
        current_input: str | None = None

        if event.key == pygame.K_UP:
            current_input = 'UP'
            if self.state == "Start":
                self.game.sfx['move_menu'].play()
                self.state = "Exit"
            elif self.state == "Scores":
                self.game.sfx['move_menu'].play()
                self.state = "Start"
            elif self.state == "Help":
                self.game.sfx['move_menu'].play()
                self.state = "Scores"
            elif self.state == "Pics":
                self.game.sfx['move_menu'].play()
                self.state = "Help"
            elif self.state == "Exit":
                self.game.sfx['move_menu'].play()
                self.state = "Pics"
        elif event.key == pygame.K_DOWN:
            current_input = 'DOWN'
            if self.state == "Start":
                self.game.sfx['move_menu'].play()
                self.state = "Scores"
            elif self.state == "Scores":
                self.game.sfx['move_menu'].play()
                self.state = "Help"
            elif self.state == "Help":
                self.game.sfx['move_menu'].play()
                self.state = "Pics"
            elif self.state == "Pics":
                self.game.sfx['move_menu'].play()
                self.state = "Exit"
            elif self.state == "Exit":
                self.game.sfx['move_menu'].play()
                self.state = "Start"
        elif event.key == pygame.K_RIGHT:
            current_input = 'RIGHT'
            if self.state == "Pics_Pressed":
                max_index = self._gallery_max_index()
                self.i_state = (self.i_state + 1) % (max_index + 1)
        elif event.key == pygame.K_LEFT:
            current_input = 'LEFT'
            if self.state == "Pics_Pressed":
                max_index = self._gallery_max_index()
                self.i_state = (self.i_state - 1) % (max_index + 1)
        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            if self.state == "Start":
                # from pacman.game.scenes import true_ending
                # from pacman.game.scenes import weird_ending
                from pacman.game.scenes.play_scene import PlayScene
                self.game.sfx['press_menu'].play()
                self.state = "Start_Pressed"
                next_scene = PlayScene(self.game)
                # next_scene = true_ending.TrueEndingScene(self.game)
                # next_scene = weird_ending.WeirdEndingScene(self.game)
                self.game.scene_manager.change(next_scene)
            elif self.state == "Scores":
                self.game.sfx['press_menu'].play()
                self.state = "Scores_Pressed"
            elif self.state == "Help":
                self.game.sfx['press_menu'].play()
                self.state = "Help_Pressed"
            elif self.state == "Pics":
                self.game.sfx['press_menu'].play()
                self.i_state = self._gallery_max_index()
                self.state = "Pics_Pressed"
            elif self.state == "Exit":
                self.game.sfx['press_menu'].play()
                pygame.quit()
                exit()
        if event.key == pygame.K_BACKSPACE:
            if self.state == "Scores_Pressed":
                self.game.sfx['exit_item'].play()
                self.state = "Scores"
            if self.state == "Help_Pressed":
                self.game.sfx['exit_item'].play()
                self.state = "Help"
            if self.state == "Pics_Pressed":
                self.game.sfx['exit_item'].play()
                self.state = "Pics"

        if event.key in [
            pygame.K_j,
            pygame.K_u,
            pygame.K_l,
            pygame.K_i,
            pygame.K_e,
            pygame.K_t,
            pygame.K_a,
            pygame.K_p,
            pygame.K_c,
            pygame.K_m,
            pygame.K_n,
            pygame.K_h,
            pygame.K_d,
        ]:
            current_input = event.unicode
        if current_input is not None:
            self.input_history.append(current_input)
            if len(self.input_history) > self.max_buffer_size:
                self.input_history.pop(0)

            self.check_cheat_code()

    def check_cheat_code(self) -> None:
        """Activate cheat mode when the code is entered."""
        if self.input_history == self.cheat_code:
            self.game.sfx['cheat_activate'].play()
            self.game.sfx['cheat_activate'].set_volume(0.2)
            self.game.cheat = True

        if self.input_history[-len(self.secret_seq):] == self.secret_seq:
            self.game.sfx['juliette'].play()

            webbrowser.open("https://www.quiveutepouseryacim.fr/")

        if self.pac_man_code == self.input_history[-len(self.pac_man_code):]:
            self.game.sfx['pacman'].play()

            webbrowser.open("https://freepacman.org/")

        if self.m_code == self.input_history[-len(self.m_code):]:
            self.game.sfx['m'].play()
            self.m_image_timer = self.m_image_duration

    def _scale_secret_image(self, image: pygame.Surface) -> pygame.Surface:
        """Scale the secret image so it fits inside the menu screen.

        Args:
            image: Secret image to scale.

        Returns:
            Scaled image that fits on the logical screen.
        """
        max_width = int(self.game.logic_width * 0.85)
        max_height = int(self.game.logic_height * 0.85)
        scale = min(
            max_width / image.get_width(),
            max_height / image.get_height(),
            1.0,
        )
        size = (
            max(1, int(image.get_width() * scale)),
            max(1, int(image.get_height() * scale)),
        )
        return pygame.transform.smoothscale(image, size)

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        seconds = dt / 1000.0
        self.animation_time += seconds
        self.anim_cursor_time += seconds
        self.m_image_timer = max(0.0, self.m_image_timer - seconds)

        # for the cursor animation
        if self.anim_cursor_time >= self.frame_cursor:
            self.frame = (self.frame + 1) % len(self.cursor_frames)
            self.anim_cursor_time -= self.frame_cursor

        # for the background animation
        if self.animation_time >= self.frame_duration:
            self.current_frame_index = (
                self.current_frame_index + 1) % len(self.bg_animation_frames)
            self.animation_time -= self.frame_duration

        # slide animation for menu items
        if self.state in ["Start", "Scores", "Help", "Pics", "Exit"]:
            for name, data in self.menu_items.items():
                diff = data["target_x"] - data["current_x"]

                if abs(diff) > 0.1:
                    data["current_x"] += diff * self.slide_speed
                else:
                    data["current_x"] = data["target_x"]
        else:
            for name, data in self.menu_items.items():
                diff = -200 - data["current_x"]

                if abs(diff) > 0.1:
                    data["current_x"] += diff * self.slide_speed
                else:
                    data["current_x"] = -200

        # slide animation for scores box
        if self.state == "Scores_Pressed":
            diff = self.score_anim["target_x"] - self.score_anim["current_x"]
            if abs(diff) > 0.1:
                self.score_anim["current_x"] += diff * self.slide_speed
            else:
                self.score_anim["current_x"] = self.score_anim["target_x"]
        else:
            diff = self.game.logic_width + 200 - self.score_anim["current_x"]
            if abs(diff) > 0.1:
                self.score_anim["current_x"] += diff * self.slide_speed
            else:
                self.score_anim["current_x"] = self.game.logic_width + 200

        # slide animation for help box
        if self.state == "Help_Pressed":
            diff = self.help_anim["target_x"] - self.help_anim["current_x"]
            if abs(diff) > 0.1:
                self.help_anim["current_x"] += diff * self.slide_speed
            else:
                self.help_anim["current_x"] = self.help_anim["target_x"]
        else:
            diff = self.game.logic_width + 200 - self.help_anim["current_x"]
            if abs(diff) > 0.1:
                self.help_anim["current_x"] += diff * self.slide_speed
            else:
                self.help_anim["current_x"] = self.game.logic_width + 200

        # slide animation for pics box
        if self.state == "Pics_Pressed":
            diff = self.pics_anim["target_x"] - self.pics_anim["current_x"]
            if abs(diff) > 0.1:
                self.pics_anim["current_x"] += diff * self.slide_speed
            else:
                self.pics_anim["current_x"] = self.pics_anim["target_x"]
        else:
            diff = self.game.logic_width + 200 - self.pics_anim["current_x"]
            if abs(diff) > 0.1:
                self.pics_anim["current_x"] += diff * self.slide_speed
            else:
                self.pics_anim["current_x"] = self.game.logic_width + 200

    def render(self, surface: pygame.Surface) -> None:
        """Draw the current state onto a surface.

        Args:
            surface: Surface that receives drawing operations.
        """
        surface.blit(
            self.bg_animation_frames[self.current_frame_index], (0, 0))

        # cheat mode message
        if self.game.cheat:
            cheat_msg = "CHEAT MODE ACTIVATED (NO COLLISIONS)"
            font = StringFont(surface, resource_path(
                "fonts", "PixelOperator-Bold.ttf"), 40)
            len_s = font.get_width(cheat_msg)
            surface.blit(self.description, ((
                surface.get_width() - self.description.get_width()) // 2, 0))
            font.write(cheat_msg, (surface.get_width() -
                       len_s) // 2 + 28,
                       surface.get_height() // 3,
                       (255, 51, 51))
            font.write(cheat_msg, (surface.get_width() -
                       len_s) // 2 + 29,
                       surface.get_height() // 3,
                       (255, 255, 255))

        # true ending menu
        if self.save_level == 17:
            center_x = self.game.logic_width // 2 - self.glass.get_width() // 2
            center_y = self.game.logic_height // 3 - 238
            surface.blit(self.glass, (center_x, center_y))

        # start
        self.start(surface)

        # scores
        self.scores(surface)

        # help
        self.help(surface)

        # gallery
        self.pics(surface)

        # exit
        self.exit(surface)

        # scores box
        self.box_scores(surface)

        # help box
        self.box_help(surface)

        # gallery box
        self.box_pics(surface)

        if self.m_image_timer > 0.0:
            image_rect = self.m_image.get_rect(
                center=(surface.get_width() // 2, surface.get_height() // 2)
            )
            surface.blit(self.m_image, image_rect)

    def box_help(self, surface: pygame.Surface) -> None:
        """Draw the help panel.

        Args:
            surface: Surface that receives drawing operations.
        """
        box_x = self.help_anim["current_x"]
        box_y = self.help_anim["y"]
        surface.blit(self.box_help_s, (box_x, box_y))
        desc = StringFont(surface, resource_path(
            "fonts", "PixelOperator-Bold.ttf"), 40)
        if self.state == "Help_Pressed":
            len_s = desc.get_width("DISPLAY INSTRUCTIONS")
            surface.blit(self.description, ((
                surface.get_width() - self.description.get_width()) // 2, 0))
            desc.write("DISPLAY INSTRUCTIONS", (surface.get_width() -
                       len_s) // 2 + 4, -5, (8, 136, 248))
            desc.write("DISPLAY INSTRUCTIONS", (surface.get_width() -
                       len_s) // 2 + 5, -5, (216, 248, 232))

        font = StringFont(surface, None, 25)
        instructions = [
            "Use ARROW KEYS to move or stick for the joystick",
            "Press A (controller) or ENTER to select an option.",
            "Press B (controller) or BACKSPACE to go back.",
            "",
            "In-game, press ESCAPE or START (controller) to pause.",
            "Avoid the monsters! (Unless you have a sword!)",
            "Collect all the rupees and swords to win!",
            "",
            "The more levels you clear, the more pics you obtain!",
            "",
            "                  Get the true ending... if you can!"
        ]
        for i, line in enumerate(instructions):
            font.write(line, box_x + 20, box_y + 32 + i * 30, (216, 248, 232))

    def box_pics(self, surface: pygame.Surface) -> None:
        """Draw the picture gallery panel.

        Args:
            surface: Surface that receives drawing operations.
        """
        levels_completed = self.save_level
        box_x = self.pics_anim["current_x"]
        box_y = self.pics_anim["y"]
        surface.blit(self.box_help_s, (box_x, box_y))

        if self.state == "Pics_Pressed":
            desc = StringFont(surface, resource_path(
                "fonts", "PixelOperator-Bold.ttf"), 40)
            len_s = desc.get_width("VIEW THE GALLERY")
            surface.blit(self.description, ((
                surface.get_width() - self.description.get_width()) // 2, 0))
            desc.write("VIEW THE GALLERY", (surface.get_width() -
                       len_s) // 2 + 9, -5, (8, 136, 248))
            desc.write("VIEW THE GALLERY", (surface.get_width() -
                       len_s) // 2 + 10, -5, (216, 248, 232))

        if levels_completed == 0:
            font = StringFont(surface, resource_path(
                "fonts", "PixelOperator-Bold.ttf"), 25)
            font.write("No pics obtained yet!", box_x +
                       150, box_y + 150, (216, 248, 232))
        else:
            self.i_state = min(self.i_state, self._gallery_max_index())
            font = StringFont(surface, resource_path(
                "fonts", "PixelOperator-Bold.ttf"), 35)
            font.write(f"{levels_completed} / {len(self.levels_pics)}",
                       box_x + 25, box_y + 20, (216, 248, 232))
            if levels_completed == 17:
                font.write("COMPLETED", box_x + 175, box_y, (0, 0, 0))
                font.write("COMPLETED", box_x + 175 +
                           2, box_y + 2, (255, 255, 51))
            pic = self.levels_pics[self.i_state]
            x_adjust = (self.box_help_s.get_width() - pic.get_width()) // 2
            surface.blit(pic, (box_x + x_adjust, box_y + 40))

    def box_scores(self, surface: pygame.Surface) -> None:
        """Draw the highscore panel.

        Args:
            surface: Surface that receives drawing operations.
        """
        highscores = self.highscores
        box_x = int(self.score_anim["current_x"])
        box_y = surface.get_height() // 2 - self.box.get_height() // 2
        box_w = self.box.get_width()

        font = StringFont(surface, None, 25)

        surface.blit(self.box, (box_x, box_y))
        if self.state == "Scores_Pressed":
            desc = StringFont(surface, resource_path(
                "fonts", "PixelOperator-Bold.ttf"), 40)
            len_s = desc.get_width("SHOW HIGHSCORES")
            surface.blit(self.description, ((
                surface.get_width() - self.description.get_width()) // 2, 0))
            desc.write("SHOW HIGHSCORES", (surface.get_width() -
                       len_s) // 2 + 1, -5, (216, 248, 232))
        box_left = box_x
        box_right = box_x + box_w

        for i, player in enumerate(highscores, start=1):
            name = player["player_name"]
            score_str = str(player["score"])
            skin_color = player["skin_color"]
            cheated = player['cheat']
            y = box_y + 40 + (i - 1) * 40

            rank_str = f"{i}."
            rank_x = box_left + 40 - font.get_width(rank_str)
            font.write(rank_str, rank_x, y, (216, 248, 232))

            font.write(name, box_left + 45, y, (216, 248, 232))

            score_width = font.get_width(score_str)
            font.write(score_str, box_right -
                       45 - score_width, y, (216, 248, 232))

            icon = self.icons[skin_color][0]\
                if player["score"] > 0 else self.icons[skin_color][1]

            if cheated:
                icon = self.cheater

            icon_x = box_right - 40
            surface.blit(icon, (icon_x, y))

    def start(self, surface: pygame.Surface) -> None:
        """Start gameplay from the menu.

        Args:
            surface: Surface that receives drawing operations.
        """
        data = self.menu_items["Start"]
        x = data["current_x"]
        y = data["y"]

        font = StringFont(surface, resource_path(
            "fonts", "PixelOperator-Bold.ttf"), 46)

        if self.state == "Start":
            surface.blit(self.cursor_frames[self.frame], (x - 25, y + 10))
            surface.blit(self.button_select, (x, y))
            font.write("START", x + 20, y, (255, 255, 255))

            len_s = font.get_width("START A NEW GAME")
            desc = StringFont(surface, resource_path(
                "fonts", "PixelOperator-Bold.ttf"), 40)
            surface.blit(self.description, ((
                surface.get_width() - self.description.get_width()) // 2, 0))
            desc.write("START A NEW GAME", (surface.get_width() -
                       len_s) // 2 + 28, -5, (8, 136, 248))
            desc.write("START A NEW GAME", (surface.get_width() -
                       len_s) // 2 + 29, -5, (216, 248, 232))
        elif self.state == "Start_Pressed":
            surface.blit(self.button_press, (x, y))
            font.write("START", x + 23, y, (255, 255, 255))
        else:
            surface.blit(self.button, (x, y))
            font.write("START", x + 20, y, (168, 248, 184))

    def scores(self, surface: pygame.Surface) -> None:
        """Open the score panel.

        Args:
            surface: Surface that receives drawing operations.
        """
        data = self.menu_items["Scores"]
        x = data["current_x"]
        y = data["y"]

        font = StringFont(surface, resource_path(
            "fonts", "PixelOperator-Bold.ttf"), 39)
        if self.state == "Scores":
            surface.blit(self.cursor_frames[self.frame], (x - 25, y + 10))
            surface.blit(self.button_select, (x, y))
            font.write("SCORES", x + 21, y + 5, (255, 255, 255))

            desc = StringFont(surface, resource_path(
                "fonts", "PixelOperator-Bold.ttf"), 40)
            len_s = desc.get_width("SHOW HIGHSCORES")
            surface.blit(self.description, ((
                surface.get_width() - self.description.get_width()) // 2, 0))
            desc.write("SHOW HIGHSCORES", (surface.get_width() -
                       len_s) // 2 + 1, -5, (216, 248, 232))
        else:
            surface.blit(self.button, (x, y))
            font.write("SCORES", x + 21, y + 5, (168, 248, 184))

    def help(self, surface: pygame.Surface) -> None:
        """Open the help panel.

        Args:
            surface: Surface that receives drawing operations.
        """
        data = self.menu_items["Help"]
        x = data["current_x"]
        y = data["y"]

        font = StringFont(surface, resource_path(
            "fonts", "PixelOperator-Bold.ttf"), 46)
        if self.state == "Help":
            surface.blit(self.cursor_frames[self.frame], (x - 25, y + 10))
            surface.blit(self.button_select, (x, y))
            font.write("HELP", x + 30, y, (255, 255, 255))

            desc = StringFont(surface, resource_path(
                "fonts", "PixelOperator-Bold.ttf"), 40)
            len_s = desc.get_width("DISPLAY INSTRUCTIONS")
            surface.blit(self.description, ((
                surface.get_width() - self.description.get_width()) // 2, 0))
            desc.write("DISPLAY INSTRUCTIONS", (surface.get_width() -
                       len_s) // 2 + 4, -5, (8, 136, 248))
            desc.write("DISPLAY INSTRUCTIONS", (surface.get_width() -
                       len_s) // 2 + 5, -5, (216, 248, 232))
        else:
            surface.blit(self.button, (x, y))
            font.write("HELP", x + 30, y, (168, 248, 184))

    def pics(self, surface: pygame.Surface) -> None:
        """Open the picture gallery panel.

        Args:
            surface: Surface that receives drawing operations.
        """
        data = self.menu_items["Pics"]
        x = data["current_x"]
        y = data["y"]

        font = StringFont(surface, resource_path(
            "fonts", "PixelOperator-Bold.ttf"), 46)
        if self.state == "Pics":
            surface.blit(self.cursor_frames[self.frame], (x - 25, y + 10))
            surface.blit(self.button_select, (x, y))
            font.write("PICS", x + 35, y, (255, 255, 255))

            desc = StringFont(surface, resource_path(
                "fonts", "PixelOperator-Bold.ttf"), 40)
            len_s = desc.get_width("VIEW THE GALLERY")
            surface.blit(self.description, ((
                surface.get_width() - self.description.get_width()) // 2, 0))
            desc.write("VIEW THE GALLERY", (surface.get_width() -
                       len_s) // 2 + 9, -5, (8, 136, 248))
            desc.write("VIEW THE GALLERY", (surface.get_width() -
                       len_s) // 2 + 10, -5, (216, 248, 232))
        else:
            surface.blit(self.button, (x, y))
            font.write("PICS", x + 35, y, (168, 248, 184))

    def exit(self, surface: pygame.Surface) -> None:
        """Leave the game from the menu.

        Args:
            surface: Surface that receives drawing operations.
        """
        data = self.menu_items["Exit"]
        x = data["current_x"]
        y = data["y"]

        font = StringFont(surface, resource_path(
            "fonts", "PixelOperator-Bold.ttf"), 46)
        if self.state == "Exit":
            surface.blit(self.description, ((
                surface.get_width() - self.description.get_width()) // 2, 0))
            surface.blit(self.cursor_frames[self.frame], (x - 25, y + 10))
            surface.blit(self.button_select, (x, y))
            font.write("EXIT", x + 35, y, (255, 255, 255))

            len_s = font.get_width("QUIT THE GAME")
            desc = StringFont(surface, resource_path(
                "fonts", "PixelOperator-Bold.ttf"), 40)
            surface.blit(self.description, ((
                surface.get_width() - self.description.get_width()) // 2, 0))
            desc.write("QUIT THE GAME", (surface.get_width() -
                       len_s) // 2 + 21, -5, (8, 136, 248))
            desc.write("QUIT THE GAME", (surface.get_width() -
                       len_s) // 2 + 22, -5, (216, 248, 232))
        else:
            surface.blit(self.button, (x, y))
            font.write("EXIT", x + 35, y, (168, 248, 184))
