import pygame


class SpriteSheet:
    """Load sprites from a sheet image."""
    def __init__(self, filename: str, game: object) -> None:
        """Initialize the sprite sheet.

        Args:
            filename: Path to the file to load.
            game: Shared game object that owns resources, groups, and state.
        """
        self.game = game
        self.sprite_sheet = pygame.image.load(filename).convert_alpha()

    def get_sprite(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        colorkey: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        """Extract one sprite surface from the sheet.

        Args:
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            width: Width in pixels or grid cells, depending on context.
            height: Height in pixels or grid cells, depending on context.
            colorkey: Optional transparent color key.

        Returns:
            Extracted sprite surface.
        """
        if colorkey is not None:
            sprite = pygame.Surface((width, height)).convert()
            sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
            sprite.set_colorkey(colorkey)
            # couleur_reelle = sprite.get_at((0, 0))
        else:
            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite


class StringFont:
    """Render text onto a pygame surface."""
    def __init__(
        self,
        game: pygame.Surface,
        filename: str | None,
        size: int = 30,
    ) -> None:
        """Initialize the string font.

        Args:
            game: Shared game object that owns resources, groups, and state.
            filename: Path to the file to load.
            size: Requested maze size as width and height.
        """
        try:
            self.font = pygame.font.Font(filename, size)
        except Exception:
            self.font = pygame.font.SysFont(None, size)
        self.game_screen = game

    def write(self,
              text: str,
              x: int | float,
              y: int | float,
              color: str | tuple[int, int, int],
              alpha: int | float = 255
              ) -> None:
        # accept color as name or RGB tuple
        """Render text to the target surface.

        Args:
            text: Text content to process or draw.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            color: Text or debug color to use.
            alpha: Opacity applied to rendered text.
        """
        try:
            col = pygame.Color(color) if isinstance(color, str) else color
        except Exception:
            col = (255, 255, 255)
        text_surface = self.font.render(str(text), True, col)
        if alpha < 255:
            text_surface.set_alpha(int(alpha))
        self.game_screen.blit(text_surface, (int(x), int(y)))

    def get_width(self, text: str) -> int:
        """Measure rendered text width.

        Args:
            text: Text content to process or draw.

        Returns:
            Rendered text width in pixels.
        """
        return int(self.font.size(str(text))[0])
