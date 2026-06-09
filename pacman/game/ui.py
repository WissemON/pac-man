import pygame
from typing import TYPE_CHECKING

# from pygame.locals import *
from pacman.game.sprites import SpriteSheet, StringFont
from pacman.resources import resource_path, HEART_SCALE

if TYPE_CHECKING:
    from pacman.game.game import Game


class UiElements(pygame.sprite.Sprite):
    """Draw the gameplay heads-up display."""
    def __init__(self, game: "Game") -> None:
        """Initialize the UI elements.

        Args:
            game: Shared game object that owns resources, groups, and state.
        """
        super().__init__()
        self.game = game
        self.heart_image: pygame.Surface | None = None
        self.rupee_image: pygame.Surface | None = None
        self.blue_rupee: pygame.Surface | None = None
        self.red_rupee: pygame.Surface | None = None
        self.big_rupee: pygame.Surface | None = None
        self.load_heart_sprite()

    def load_heart_sprite(self) -> None:
        """Load one heart UI sprite."""
        sheet = SpriteSheet(resource_path('ui', 'hud.png'), self.game)
        sheet_rupees = SpriteSheet(resource_path('ui', 'rupee_icon.png'),
                                   self.game)
        img = sheet.get_sprite(7, 8, 9, 8)
        if HEART_SCALE != 1:
            w = int(img.get_width() * HEART_SCALE)
            h = int(img.get_height() * HEART_SCALE)
            self.heart_image = pygame.transform.scale(img, (w, h))
        else:
            self.heart_image = img

        self.rupee_image = sheet.get_sprite(195, 147, 10, 10)
        self.blue_rupee = sheet_rupees.get_sprite(19, 3, 10, 10)
        self.red_rupee = sheet_rupees.get_sprite(35, 3, 10, 10)
        self.big_rupee = sheet_rupees.get_sprite(48, 0, 14, 14)

    def draw(self, screen: pygame.Surface) -> None:
        # main entrypoint to draw all UI elements onto the provided surface
        """Draw all gameplay UI elements.

        Args:
            screen: Surface that receives UI drawing.
        """
        self.draw_hearts(screen)
        self.draw_rupees(screen)
        self.draw_items(screen)
        self.draw_time(screen)
        self.draw_level(screen)

    def _draw_wrapped_images(
        self,
        screen: pygame.Surface,
        images: list[pygame.Surface],
        start_x: int,
        start_y: int,
        max_x: int,
        spacing_x: int,
        spacing_y: int,
    ) -> None:
        """Draw images and wrap to the next line at a maximum x position.

        Args:
            screen: Surface that receives UI drawing.
            images: Images to draw in order.
            start_x: First horizontal drawing position.
            start_y: First vertical drawing position.
            max_x: Horizontal limit before wrapping.
            spacing_x: Horizontal spacing between images.
            spacing_y: Vertical spacing between rows.
        """
        x = start_x
        y = start_y
        row_height = 0

        for image in images:
            image_width = image.get_width()
            image_height = image.get_height()

            if x > start_x and x + image_width > max_x:
                x = start_x
                y += row_height + spacing_y
                row_height = 0

            screen.blit(image, (x, y))
            x += image_width + spacing_x
            row_height = max(row_height, image_height)

    def draw_level(self, screen: pygame.Surface) -> None:
        """Draw the current level id.

        Args:
            screen: Surface that receives UI drawing.
        """
        if self.game.current_level_id is None:
            return

        font = StringFont(screen, resource_path(
            'fonts', 'PixelOperator-Bold.ttf'), 28)
        text = f'LEVEL {self.game.current_level_id}'
        text_width = font.get_width(text)
        text_height = font.font.get_height()
        x = screen.get_width() // 2 - text_width // 2
        y = 10
        padding_x = 12
        padding_y = 4
        background = pygame.Rect(
            x - padding_x,
            y - padding_y,
            text_width + padding_x * 2,
            text_height + padding_y * 2,
        )
        banner = pygame.Surface(background.size, pygame.SRCALPHA)
        banner.fill((0, 0, 0, 150))
        screen.blit(banner, background)
        pygame.draw.rect(screen, (255, 255, 255, 95), background, 1)
        font.write(text, x + 2, y + 2, (0, 0, 0))
        font.write(text, x, y, (255, 246, 176))

    def draw_hearts(self, screen: pygame.Surface) -> None:
        """Draw the player life hearts.

        Args:
            screen: Surface that receives UI drawing.
        """
        if self.heart_image is None:
            return

        hearts = self.game.lives

        heart_images = [self.heart_image for _ in range(hearts)]
        self._draw_wrapped_images(
            screen,
            heart_images,
            start_x=50,
            start_y=15,
            max_x=screen.get_width() // 2,
            spacing_x=0,
            spacing_y=2,
        )

    def draw_rupees(self, screen: pygame.Surface) -> None:
        """Draw the score rupee counter.

        Args:
            screen: Surface that receives UI drawing.
        """
        if self.rupee_image is None:
            return

        font_score = StringFont(screen,
                                resource_path('fonts',
                                              'minish_cap_font.ttf'), 8)
        rupee_skin = self.rupee_image
        if self.game.in_game_score >= 4000 and self.big_rupee is not None:
            rupee_skin = self.big_rupee
        elif self.game.in_game_score >= 2500 and self.red_rupee is not None:
            rupee_skin = self.red_rupee
        elif self.game.in_game_score >= 1000 and self.blue_rupee is not None:
            rupee_skin = self.blue_rupee

        screen.blit(rupee_skin, (screen.get_width() - 85,
                                 screen.get_height() - 36))

        text = f'{self.game.in_game_score}'
        font_score.write(
            text, screen.get_width() - 70,
            screen.get_height() - 40, (0, 0, 0))
        font_score.write(
            text, screen.get_width() - 71,
            screen.get_height() - 40,
            (255, 255, 255))

    def draw_items(self, screen: pygame.Surface) -> None:
        """Draw collected special items.

        Args:
            screen: Surface that receives UI drawing.
        """
        item_images = [item.image for item in self.game.collected_items]
        self._draw_wrapped_images(
            screen,
            item_images,
            start_x=50,
            start_y=screen.get_height() - 40,
            max_x=screen.get_width() // 2,
            spacing_x=2,
            spacing_y=2,
        )

    def draw_time(self, screen: pygame.Surface) -> None:
        """Draw the remaining time.

        Args:
            screen: Surface that receives UI drawing.
        """
        font = StringFont(screen, resource_path(
            'fonts', 'minish_cap_font.ttf'), 8)

        time = f'{int(self.game.in_game_time)}'
        font.write(time, screen.get_width() - 70,
                   14, (0, 0, 0))
        font.write(time, screen.get_width() - 70,
                   15, (255, 255, 255))
