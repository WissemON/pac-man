from typing import TYPE_CHECKING

import pygame
from pacman.game.sprites import SpriteSheet
from pacman.game.type_defs import GameSprite
from pacman.resources import resource_path

if TYPE_CHECKING:
    from pacman.game.game import Game


class PacGumRupee(GameSprite):
    """Represent a collectible rupee that awards pacgum points."""

    def __init__(self, game: "Game", x: int, y: int) -> None:
        """Initialize the pac gum rupee.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
        """
        super().__init__()
        sheet = SpriteSheet(resource_path('items', 'green_rupee.png'), game)
        self.image = sheet.get_sprite(0, 0, 16, 16)
        self.game = game
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.game.all_sprites.add(self)
        self.game.gums.add(self)

        self.is_collected = False
        self.points = self.game.config["points_per_pacgum"]
        self.pos_y = float(y)
        self.animation_duration = 0.1
        self.speed_y = 300.0

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        if self.is_collected:
            delta = dt / 1000.0

            self.pos_y -= self.speed_y * delta
            self.rect.y = int(self.pos_y)

            self.animation_duration -= delta
            if self.animation_duration <= 0:
                self.kill()

    def collected(self) -> None:
        """Mark the item as collected and apply its effects."""
        if not self.is_collected:
            self.is_collected = True
            gum_collect_sfx = self.game.sfx['gum_collect']
            gum_collect_sfx.set_volume(0.1)
            gum_collect_sfx.play()
            self.game.in_game_score += self.points
            # rajouter le son plus tard ici


class SuperPacGum(GameSprite):
    """Represent a collectible item that powers up the player."""

    def __init__(self, game: "Game", x: int, y: int, x_rip: int, y_rip:
                 int, x_size_rip: int, y_size_rip: int) -> None:
        """Initialize the super pac gum.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            x_rip: Source x coordinate in the sprite sheet.
            y_rip: Source y coordinate in the sprite sheet.
            x_size_rip: Source sprite width in pixels.
            y_size_rip: Source sprite height in pixels.
        """
        super().__init__()
        self.game = game
        sheet = SpriteSheet(resource_path('items', 'items.png'), game)
        self.image = sheet.get_sprite(x_rip, y_rip, x_size_rip, y_size_rip,
                                      (192, 192, 255))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.points = self.game.config["points_per_super_pacgum"]
        self.game.all_sprites.add(self)
        self.game.super_gums.add(self)
        self.is_collected = False

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        if self.is_collected:
            self.kill()
            current_scene = self.game.scene_manager.current_scene()
            if current_scene is not None:
                current_scene.freeze_for(800)

    def collected(self) -> None:
        """Mark the item as collected and apply its effects."""
        if not self.is_collected:
            self.is_collected = True
            self.game.in_game_score += self.points
            # Convenient point for enemy strategy changes after pickup.
            super_gum_sfx = self.game.sfx['super_gum_collect']
            super_gum_sfx.set_volume(0.2)
            super_gum_sfx.play()


class SpecialItem(GameSprite):
    """Represent a level item collected for bonus points."""

    def __init__(self, game: "Game", x: int, y: int, x_rip: int, y_rip: int,
                 x_size_rip: int, y_size_rip: int,
                 is_final: bool | None = None,
                 item: pygame.Surface | None = None) -> None:
        """Initialize the special item.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            x_rip: Source x coordinate in the sprite sheet.
            y_rip: Source y coordinate in the sprite sheet.
            x_size_rip: Source sprite width in pixels.
            y_size_rip: Source sprite height in pixels.
            is_final: Whether the item uses final-stage artwork.
            item: Optional custom item image.
        """
        super().__init__()
        if not is_final:
            sheet = SpriteSheet(resource_path('items', 'items.png'), game)
            self.image = sheet.get_sprite(x_rip, y_rip, x_size_rip, y_size_rip,
                                          (192, 192, 255))
        else:
            sheet = SpriteSheet(resource_path('ui', 'file_select.png'), game)
            self.image = sheet.get_sprite(x_rip, y_rip, x_size_rip, y_size_rip,
                                          (167, 167, 227))

        if item:
            self.image = item

        self.game = game
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.game.all_sprites.add(self)
        self.game.special_items.add(self)
        self.is_collected = False
        self.points = self.game.config["points_per_special_item"]

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        if self.is_collected:
            self.kill()
            current_scene = self.game.scene_manager.current_scene()
            if current_scene is not None:
                current_scene.freeze_for(800)

    def collected(self) -> None:
        """Mark the item as collected and apply its effects."""
        self.is_collected = True

        special_item_sfx = self.game.sfx['item_collect']
        special_item_sfx.set_volume(0.2)
        special_item_sfx.play()
        self.game.in_game_score += self.points

        self.game.collected_items[self] = True
