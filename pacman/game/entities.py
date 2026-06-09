import pygame
import random
import math
from typing import TYPE_CHECKING

from pacman.game.ai import EnemyBrain, State, ChaseContext
from pacman.game.type_defs import GameSprite, SkinAnimation
from pacman.resources import resource_path, TILE_SIZE
from pacman.game.sprites import SpriteSheet

if TYPE_CHECKING:
    from pacman.game.game import Game


class Wall(GameSprite):
    """Represent one collidable maze wall tile."""
    def __init__(
        self,
        game: "Game",
        x: int,
        y: int,
        base_image: pygame.Surface | None = None,
        variants: list[pygame.Surface] | None = None,
    ) -> None:
        """Initialize the wall.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            base_image: Base tile image used to create the sprite.
            variants: Alternate tile images available for variation.
        """
        super().__init__()
        self.game = game
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        if variants is None:
            variants = self.game.wall_variants
        if base_image is None:
            base_image = self.game.wall_base_image

        if base_image is None:
            base_image = pygame.image.load(resource_path(
                '01_level_walls.png')).convert_alpha()
        self.image = base_image.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.game.all_sprites.add(self)
        self.game.walls.add(self)

        self.x = x
        self.y = y

        if variants:
            self.image.blit(random.choice(variants), (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class DecorationBorder(GameSprite):
    """Represent a decorative border tile."""
    def __init__(
        self,
        game: "Game",
        x: int,
        y: int,
        image: pygame.Surface,
    ) -> None:
        """Initialize the decoration border.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            image: Surface used as the sprite image.
        """
        super().__init__()
        self.game = game
        self.image = image
        self.game.decorations.add(self)

        self.rect = self.image.get_rect(midbottom=(x, y))


class DecorationUpDown(GameSprite):
    """Represent a decorative vertical border tile."""
    def __init__(
        self,
        game: "Game",
        x: int,
        y: int,
        image: pygame.Surface,
    ) -> None:
        """Initialize the decoration up down.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            image: Surface used as the sprite image.
        """
        super().__init__()
        self.game = game
        self.image = image
        self.game.decorations.add(self)

        self.rect = self.image.get_rect(midtop=(x, y))


class Ground(GameSprite):
    """Represent one walkable ground tile."""
    def __init__(
        self,
        game: "Game",
        x: int,
        y: int,
        base_image: pygame.Surface | None = None,
        variants: list[pygame.Surface] | None = None,
    ) -> None:
        """Initialize the ground.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            base_image: Base tile image used to create the sprite.
            variants: Alternate tile images available for variation.
        """
        super().__init__()
        self.game = game
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        if variants is None:
            variants = self.game.ground_variants
        if base_image is None:
            base_image = self.game.ground_base_image

        if base_image is None:
            base_image = pygame.image.load(resource_path(
                '01_level_floor.png')).convert_alpha()
        self.image = base_image.copy()
        self.game.all_sprites.add(self)
        self.game.grounds.add(self)

        self.x = x
        self.y = y

        if variants:
            self.image.blit(random.choice(variants), (0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class Player(GameSprite):
    """Represent the player sprite and movement state."""
    def __init__(
        self,
        game: "Game",
        x: int,
        y: int,
        power_color: str,
    ) -> None:
        """Initialize the player.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            power_color: Color used while the player is powered up.
        """
        super().__init__()
        self.game = game
        self.power_color = power_color
        self.cheat = self.game.cheat
        self.game_over = False
        self.time_death = 0.0
        self.death = False
        self.win = False

        x = int(x)
        y = int(y)
        self.current_direction: str | None = None
        self.direction_asked: str | None = None
        self.speed: float = 100.0
        self.vx = 0.0
        self.vy = 0.0

        self.pos_x = float(x)
        self.pos_y = float(y)

        self.spawn_x = int(x)
        self.spawn_y = int(y)
        self.lives = game.config["lives"]
        self.game.all_sprites.add(self)
        self.game.player_group.add(self)

        self.width = TILE_SIZE
        self.height = TILE_SIZE

        self.link_sprite = SpriteSheet(
            resource_path('player', 'minish_cap_sprites.png'), self)
        self.image = self.link_sprite.get_sprite(683, 18, 18, 25)
        self.link = SpriteSheet(resource_path('player', 'walking.png'), self)
        self.animation_loop = 0.0
        self.anim_fps = 30.0
        self.facing = 'DOWN'
        self.win_level_started = False
        self.current_held_item: pygame.Surface | None = None

        self.link_death = [
            self.link_sprite.get_sprite(15, 461, 18, 24),
            self.link_sprite.get_sprite(46, 460, 19, 24),
            self.link_sprite.get_sprite(78, 461, 22, 23),
            self.link_sprite.get_sprite(109, 460, 22, 24),
            self.link_sprite.get_sprite(143, 461, 19, 23),
            self.link_sprite.get_sprite(175, 462, 19, 22),
            self.link_sprite.get_sprite(204, 462, 22, 22),
            self.link_sprite.get_sprite(237, 461, 20, 23),

            self.link_sprite.get_sprite(12, 880, 22, 24),
            self.link_sprite.get_sprite(42, 880, 22, 24),
            self.link_sprite.get_sprite(72, 887, 24, 18),
            self.link_sprite.get_sprite(108, 880, 25, 19),
            self.link_sprite.get_sprite(141, 881, 24, 18),
        ]

        self.up_walking = [
            self.link_sprite.get_sprite(79, 10, 18, 22),
            self.link.get_sprite(7, 37, 18, 23),
            self.link.get_sprite(103, 37, 18, 23),
            self.link.get_sprite(199, 35, 18, 25),
            self.link.get_sprite(295, 35, 18, 25),
            self.link.get_sprite(391, 36, 18, 24),
            self.link.get_sprite(487, 37, 18, 23),
            self.link.get_sprite(615, 37, 18, 23),
            self.link.get_sprite(711, 35, 18, 25),
            self.link.get_sprite(839, 35, 18, 25),
        ]

        self.left_walking = [
            self.link_sprite.get_sprite(49, 10, 19, 23),
            self.link.get_sprite(8, 69, 23, 23),
            self.link.get_sprite(104, 69, 20, 23),
            self.link.get_sprite(198, 67, 20, 25),
            self.link.get_sprite(295, 67, 20, 25),
            self.link.get_sprite(392, 68, 20, 24),
            self.link.get_sprite(488, 69, 23, 23),
            self.link.get_sprite(585, 69, 19, 23),
            self.link.get_sprite(679, 67, 19, 25),
            self.link.get_sprite(776, 67, 19, 25),
            self.link.get_sprite(872, 68, 20, 24),
        ]

        self.down_walking = [
            self.link_sprite.get_sprite(15, 9, 18, 24),
            self.link.get_sprite(7, 100, 18, 24),
            self.link.get_sprite(103, 99, 18, 25),
            self.link.get_sprite(199, 98, 18, 26),
            self.link.get_sprite(295, 98, 18, 25),
            self.link.get_sprite(391, 99, 18, 25),
            self.link.get_sprite(487, 100, 18, 24),
            self.link.get_sprite(583, 99, 18, 25),
            self.link.get_sprite(679, 98, 18, 26),
            self.link.get_sprite(775, 98, 18, 26),
            self.link.get_sprite(871, 99, 18, 25),
        ]

        # Flip left/down walking sprites to build the opposite animations.
        self.right_walking = [
            pygame.transform.flip(f, True, False) for f in self.left_walking
        ]

        sword_gain = SpriteSheet(resource_path(
            'player', 'brandish_00.png'), game)
        self.obtain_sword = [
            sword_gain.get_sprite(2, 36, 22, 24),
            sword_gain.get_sprite(135, 23, 20, 37),
            sword_gain.get_sprite(167, 23, 20, 37),
            sword_gain.get_sprite(199, 23, 22, 37),
            sword_gain.get_sprite(231, 23, 22, 37),
            sword_gain.get_sprite(263, 25, 25, 35),
            sword_gain.get_sprite(295, 24, 24, 36),
            sword_gain.get_sprite(327, 19, 25, 41),
            sword_gain.get_sprite(359, 18, 24, 42),
        ]
        self.powered = False
        self.powered_timer = 8.0
        powered = SpriteSheet(resource_path(
            'player', 'powered_state.png'), game)
        self.powered_up = [
            powered.get_sprite(435, 60, 18, 28),
            powered.get_sprite(467, 61, 18, 28),
            powered.get_sprite(499, 60, 18, 28),
            powered.get_sprite(531, 59, 18, 29),
            powered.get_sprite(563, 59, 18, 29),
            powered.get_sprite(595, 60, 18, 25),
        ]

        self.powered_down = [
            powered.get_sprite(170, 36, 19, 34),
            powered.get_sprite(205, 36, 18, 34),
            powered.get_sprite(237, 36, 18, 34),
            powered.get_sprite(271, 36, 19, 34),
            powered.get_sprite(303, 34, 19, 34),
            powered.get_sprite(335, 36, 19, 33),
        ]

        self.powered_left = [
            powered.get_sprite(670, 5, 29, 23),
            powered.get_sprite(670, 34, 32, 24),
            powered.get_sprite(668, 60, 32, 24),
            powered.get_sprite(668, 100, 29, 24),
            powered.get_sprite(750, 20, 29, 25),
            powered.get_sprite(749, 60, 30, 24),
        ]

        self.powered_right = [
            pygame.transform.flip(f, True, False) for f in self.powered_left
        ]

        win_base = SpriteSheet(resource_path(
            'player', 'base_win.png'), game)
        self.win_base = [
            win_base.get_sprite(0, 0, 42, 55),
            win_base.get_sprite(50, 0, 42, 55),
            win_base.get_sprite(100, 0, 42, 55),
            win_base.get_sprite(150, 0, 42, 55),
            win_base.get_sprite(200, 0, 42, 55),
            win_base.get_sprite(250, 0, 42, 55),
            win_base.get_sprite(300, 0, 42, 55),
            win_base.get_sprite(350, 0, 42, 55),
            win_base.get_sprite(400, 0, 42, 55),
            win_base.get_sprite(450, 0, 42, 55),
            win_base.get_sprite(500, 0, 42, 55),
            win_base.get_sprite(550, 0, 42, 55),
            win_base.get_sprite(600, 0, 42, 55),
            win_base.get_sprite(650, 0, 42, 55),
            win_base.get_sprite(700, 0, 42, 55),
            win_base.get_sprite(750, 0, 42, 55),
            win_base.get_sprite(800, 0, 42, 55),
            win_base.get_sprite(850, 0, 42, 55),
            win_base.get_sprite(900, 0, 42, 55),
            win_base.get_sprite(950, 0, 42, 55),
            win_base.get_sprite(1000, 0, 42, 55),
            win_base.get_sprite(1050, 0, 42, 55),
            win_base.get_sprite(1100, 0, 42, 55),
            win_base.get_sprite(1150, 0, 42, 55),
            win_base.get_sprite(1200, 0, 42, 55),
            win_base.get_sprite(1250, 0, 42, 55),
            win_base.get_sprite(1300, 0, 42, 55),
            win_base.get_sprite(1350, 0, 42, 55),
            win_base.get_sprite(1400, 0, 42, 55),
            win_base.get_sprite(1450, 0, 42, 55),
            win_base.get_sprite(1500, 0, 42, 55),
            win_base.get_sprite(1550, 0, 42, 55),
            win_base.get_sprite(1600, 0, 42, 55),
            win_base.get_sprite(1650, 0, 42, 55),
            win_base.get_sprite(1700, 0, 42, 55),
            win_base.get_sprite(1750, 0, 42, 55),
            win_base.get_sprite(1800, 0, 42, 55),
            win_base.get_sprite(1850, 0, 42, 55),
            win_base.get_sprite(1900, 0, 42, 55),
            win_base.get_sprite(1950, 0, 42, 55),
            win_base.get_sprite(2000, 0, 42, 55),
            win_base.get_sprite(2050, 0, 42, 55),
            win_base.get_sprite(2100, 0, 42, 55),
            win_base.get_sprite(2150, 0, 42, 55),
            win_base.get_sprite(2200, 0, 42, 55),
            win_base.get_sprite(2250, 0, 42, 55),
            win_base.get_sprite(2300, 0, 42, 55),
            win_base.get_sprite(2350, 0, 42, 55),
            win_base.get_sprite(2400, 0, 42, 55),
            win_base.get_sprite(2450, 0, 42, 55),
            win_base.get_sprite(2500, 0, 42, 55),
            win_base.get_sprite(2550, 0, 42, 55),
            win_base.get_sprite(2600, 0, 42, 55),
            win_base.get_sprite(2650, 0, 42, 55),
            win_base.get_sprite(2700, 0, 42, 55),
            win_base.get_sprite(2750, 0, 42, 55),
            win_base.get_sprite(2800, 0, 42, 55),
            win_base.get_sprite(2850, 0, 42, 55),
            win_base.get_sprite(2900, 0, 42, 55),
            win_base.get_sprite(2950, 0, 42, 55),
            win_base.get_sprite(3000, 0, 42, 55),
            win_base.get_sprite(3050, 0, 42, 55),
            win_base.get_sprite(3100, 0, 42, 55),
            win_base.get_sprite(3150, 0, 42, 55),
            win_base.get_sprite(3200, 0, 42, 55),
            win_base.get_sprite(3250, 0, 42, 55),
            win_base.get_sprite(3300, 0, 42, 55),
            win_base.get_sprite(3350, 0, 42, 55),
            win_base.get_sprite(3400, 0, 42, 55),
            win_base.get_sprite(3450, 0, 42, 55),
            win_base.get_sprite(3500, 0, 42, 55),
        ]

        win_blue = SpriteSheet(resource_path('player', 'blue_win.png'), game)
        self.win_blue = [
            win_blue.get_sprite(0, 0, 42, 55),
            win_blue.get_sprite(50, 0, 42, 55),
            win_blue.get_sprite(100, 0, 42, 55),
            win_blue.get_sprite(150, 0, 42, 55),
            win_blue.get_sprite(200, 0, 42, 55),
            win_blue.get_sprite(250, 0, 42, 55),
            win_blue.get_sprite(300, 0, 42, 55),
            win_blue.get_sprite(350, 0, 42, 55),
            win_blue.get_sprite(400, 0, 42, 55),
            win_blue.get_sprite(450, 0, 42, 55),
            win_blue.get_sprite(500, 0, 42, 55),
            win_blue.get_sprite(550, 0, 42, 55),
            win_blue.get_sprite(600, 0, 42, 55),
            win_blue.get_sprite(650, 0, 42, 55),
            win_blue.get_sprite(700, 0, 42, 55),
            win_blue.get_sprite(750, 0, 42, 55),
            win_blue.get_sprite(800, 0, 42, 55),
            win_blue.get_sprite(850, 0, 42, 55),
            win_blue.get_sprite(900, 0, 42, 55),
            win_blue.get_sprite(950, 0, 42, 55),
            win_blue.get_sprite(1000, 0, 42, 55),
            win_blue.get_sprite(1050, 0, 42, 55),
            win_blue.get_sprite(1100, 0, 42, 55),
            win_blue.get_sprite(1150, 0, 42, 55),
            win_blue.get_sprite(1200, 0, 42, 55),
            win_blue.get_sprite(1250, 0, 42, 55),
            win_blue.get_sprite(1300, 0, 42, 55),
            win_blue.get_sprite(1350, 0, 42, 55),
            win_blue.get_sprite(1400, 0, 42, 55),
            win_blue.get_sprite(1450, 0, 42, 55),
            win_blue.get_sprite(1500, 0, 42, 55),
            win_blue.get_sprite(1550, 0, 42, 55),
            win_blue.get_sprite(1600, 0, 42, 55),
            win_blue.get_sprite(1650, 0, 42, 55),
            win_blue.get_sprite(1700, 0, 42, 55),
            win_blue.get_sprite(1750, 0, 42, 55),
            win_blue.get_sprite(1800, 0, 42, 55),
            win_blue.get_sprite(1850, 0, 42, 55),
            win_blue.get_sprite(1900, 0, 42, 55),
            win_blue.get_sprite(1950, 0, 42, 55),
            win_blue.get_sprite(2000, 0, 42, 55),
            win_blue.get_sprite(2050, 0, 42, 55),
            win_blue.get_sprite(2100, 0, 42, 55),
            win_blue.get_sprite(2150, 0, 42, 55),
            win_blue.get_sprite(2200, 0, 42, 55),
            win_blue.get_sprite(2250, 0, 42, 55),
            win_blue.get_sprite(2300, 0, 42, 55),
            win_blue.get_sprite(2350, 0, 42, 55),
            win_blue.get_sprite(2400, 0, 42, 55),
            win_blue.get_sprite(2450, 0, 42, 55),
            win_blue.get_sprite(2500, 0, 42, 55),
            win_blue.get_sprite(2550, 0, 42, 55),
            win_blue.get_sprite(2600, 0, 42, 55),
            win_blue.get_sprite(2650, 0, 42, 55),
            win_blue.get_sprite(2700, 0, 42, 55),
            win_blue.get_sprite(2750, 0, 42, 55),
            win_blue.get_sprite(2800, 0, 42, 55),
            win_blue.get_sprite(2850, 0, 42, 55),
            win_blue.get_sprite(2900, 0, 42, 55),
            win_blue.get_sprite(2950, 0, 42, 55),
            win_blue.get_sprite(3000, 0, 42, 55),
            win_blue.get_sprite(3050, 0, 42, 55),
            win_blue.get_sprite(3100, 0, 42, 55),
            win_blue.get_sprite(3150, 0, 42, 55),
            win_blue.get_sprite(3200, 0, 42, 55),
            win_blue.get_sprite(3250, 0, 42, 55),
            win_blue.get_sprite(3300, 0, 42, 55),
            win_blue.get_sprite(3350, 0, 42, 55),
            win_blue.get_sprite(3400, 0, 42, 55),
            win_blue.get_sprite(3450, 0, 42, 55),
            win_blue.get_sprite(3500, 0, 42, 55),
        ]

        win_yellow = SpriteSheet(resource_path(
            'player', 'yellow_win.png'), game)
        self.win_yellow = [
            win_yellow.get_sprite(0, 0, 42, 55),
            win_yellow.get_sprite(50, 0, 42, 55),
            win_yellow.get_sprite(100, 0, 42, 55),
            win_yellow.get_sprite(150, 0, 42, 55),
            win_yellow.get_sprite(200, 0, 42, 55),
            win_yellow.get_sprite(250, 0, 42, 55),
            win_yellow.get_sprite(300, 0, 42, 55),
            win_yellow.get_sprite(350, 0, 42, 55),
            win_yellow.get_sprite(400, 0, 42, 55),
            win_yellow.get_sprite(450, 0, 42, 55),
            win_yellow.get_sprite(500, 0, 42, 55),
            win_yellow.get_sprite(550, 0, 42, 55),
            win_yellow.get_sprite(600, 0, 42, 55),
            win_yellow.get_sprite(650, 0, 42, 55),
            win_yellow.get_sprite(700, 0, 42, 55),
            win_yellow.get_sprite(750, 0, 42, 55),
            win_yellow.get_sprite(800, 0, 42, 55),
            win_yellow.get_sprite(850, 0, 42, 55),
            win_yellow.get_sprite(900, 0, 42, 55),
            win_yellow.get_sprite(950, 0, 42, 55),
            win_yellow.get_sprite(1000, 0, 42, 55),
            win_yellow.get_sprite(1050, 0, 42, 55),
            win_yellow.get_sprite(1100, 0, 42, 55),
            win_yellow.get_sprite(1150, 0, 42, 55),
            win_yellow.get_sprite(1200, 0, 42, 55),
            win_yellow.get_sprite(1250, 0, 42, 55),
            win_yellow.get_sprite(1300, 0, 42, 55),
            win_yellow.get_sprite(1350, 0, 42, 55),
            win_yellow.get_sprite(1400, 0, 42, 55),
            win_yellow.get_sprite(1450, 0, 42, 55),
            win_yellow.get_sprite(1500, 0, 42, 55),
            win_yellow.get_sprite(1550, 0, 42, 55),
            win_yellow.get_sprite(1600, 0, 42, 55),
            win_yellow.get_sprite(1650, 0, 42, 55),
            win_yellow.get_sprite(1700, 0, 42, 55),
            win_yellow.get_sprite(1750, 0, 42, 55),
            win_yellow.get_sprite(1800, 0, 42, 55),
            win_yellow.get_sprite(1850, 0, 42, 55),
            win_yellow.get_sprite(1900, 0, 42, 55),
            win_yellow.get_sprite(1950, 0, 42, 55),
            win_yellow.get_sprite(2000, 0, 42, 55),
            win_yellow.get_sprite(2050, 0, 42, 55),
            win_yellow.get_sprite(2100, 0, 42, 55),
            win_yellow.get_sprite(2150, 0, 42, 55),
            win_yellow.get_sprite(2200, 0, 42, 55),
            win_yellow.get_sprite(2250, 0, 42, 55),
            win_yellow.get_sprite(2300, 0, 42, 55),
            win_yellow.get_sprite(2350, 0, 42, 55),
            win_yellow.get_sprite(2400, 0, 42, 55),
            win_yellow.get_sprite(2450, 0, 42, 55),
            win_yellow.get_sprite(2500, 0, 42, 55),
            win_yellow.get_sprite(2550, 0, 42, 55),
            win_yellow.get_sprite(2600, 0, 42, 55),
            win_yellow.get_sprite(2650, 0, 42, 55),
            win_yellow.get_sprite(2700, 0, 42, 55),
            win_yellow.get_sprite(2750, 0, 42, 55),
            win_yellow.get_sprite(2800, 0, 42, 55),
            win_yellow.get_sprite(2850, 0, 42, 55),
            win_yellow.get_sprite(2900, 0, 42, 55),
            win_yellow.get_sprite(2950, 0, 42, 55),
            win_yellow.get_sprite(3000, 0, 42, 55),
            win_yellow.get_sprite(3050, 0, 42, 55),
            win_yellow.get_sprite(3100, 0, 42, 55),
            win_yellow.get_sprite(3150, 0, 42, 55),
            win_yellow.get_sprite(3200, 0, 42, 55),
            win_yellow.get_sprite(3250, 0, 42, 55),
            win_yellow.get_sprite(3300, 0, 42, 55),
            win_yellow.get_sprite(3350, 0, 42, 55),
            win_yellow.get_sprite(3400, 0, 42, 55),
            win_yellow.get_sprite(3450, 0, 42, 55),
            win_yellow.get_sprite(3500, 0, 42, 55),
        ]

        win_red = SpriteSheet(resource_path(
            'player', 'red_win.png'), game)
        self.win_red = [
            win_red.get_sprite(0, 0, 42, 55),
            win_red.get_sprite(50, 0, 42, 55),
            win_red.get_sprite(100, 0, 42, 55),
            win_red.get_sprite(150, 0, 42, 55),
            win_red.get_sprite(200, 0, 42, 55),
            win_red.get_sprite(250, 0, 42, 55),
            win_red.get_sprite(300, 0, 42, 55),
            win_red.get_sprite(350, 0, 42, 55),
            win_red.get_sprite(400, 0, 42, 55),
            win_red.get_sprite(450, 0, 42, 55),
            win_red.get_sprite(500, 0, 42, 55),
            win_red.get_sprite(550, 0, 42, 55),
            win_red.get_sprite(600, 0, 42, 55),
            win_red.get_sprite(650, 0, 42, 55),
            win_red.get_sprite(700, 0, 42, 55),
            win_red.get_sprite(750, 0, 42, 55),
            win_red.get_sprite(800, 0, 42, 55),
            win_red.get_sprite(850, 0, 42, 55),
            win_red.get_sprite(900, 0, 42, 55),
            win_red.get_sprite(950, 0, 42, 55),
            win_red.get_sprite(1000, 0, 42, 55),
            win_red.get_sprite(1050, 0, 42, 55),
            win_red.get_sprite(1100, 0, 42, 55),
            win_red.get_sprite(1150, 0, 42, 55),
            win_red.get_sprite(1200, 0, 42, 55),
            win_red.get_sprite(1250, 0, 42, 55),
            win_red.get_sprite(1300, 0, 42, 55),
            win_red.get_sprite(1350, 0, 42, 55),
            win_red.get_sprite(1400, 0, 42, 55),
            win_red.get_sprite(1450, 0, 42, 55),
            win_red.get_sprite(1500, 0, 42, 55),
            win_red.get_sprite(1550, 0, 42, 55),
            win_red.get_sprite(1600, 0, 42, 55),
            win_red.get_sprite(1650, 0, 42, 55),
            win_red.get_sprite(1700, 0, 42, 55),
            win_red.get_sprite(1750, 0, 42, 55),
            win_red.get_sprite(1800, 0, 42, 55),
            win_red.get_sprite(1850, 0, 42, 55),
            win_red.get_sprite(1900, 0, 42, 55),
            win_red.get_sprite(1950, 0, 42, 55),
            win_red.get_sprite(2000, 0, 42, 55),
            win_red.get_sprite(2050, 0, 42, 55),
            win_red.get_sprite(2100, 0, 42, 55),
            win_red.get_sprite(2150, 0, 42, 55),
            win_red.get_sprite(2200, 0, 42, 55),
            win_red.get_sprite(2250, 0, 42, 55),
            win_red.get_sprite(2300, 0, 42, 55),
            win_red.get_sprite(2350, 0, 42, 55),
            win_red.get_sprite(2400, 0, 42, 55),
            win_red.get_sprite(2450, 0, 42, 55),
            win_red.get_sprite(2500, 0, 42, 55),
            win_red.get_sprite(2550, 0, 42, 55),
            win_red.get_sprite(2600, 0, 42, 55),
            win_red.get_sprite(2650, 0, 42, 55),
            win_red.get_sprite(2700, 0, 42, 55),
            win_red.get_sprite(2750, 0, 42, 55),
            win_red.get_sprite(2800, 0, 42, 55),
            win_red.get_sprite(2850, 0, 42, 55),
            win_red.get_sprite(2900, 0, 42, 55),
            win_red.get_sprite(2950, 0, 42, 55),
            win_red.get_sprite(3000, 0, 42, 55),
            win_red.get_sprite(3050, 0, 42, 55),
            win_red.get_sprite(3100, 0, 42, 55),
            win_red.get_sprite(3150, 0, 42, 55),
            win_red.get_sprite(3200, 0, 42, 55),
            win_red.get_sprite(3250, 0, 42, 55),
            win_red.get_sprite(3300, 0, 42, 55),
            win_red.get_sprite(3350, 0, 42, 55),
            win_red.get_sprite(3400, 0, 42, 55),
            win_red.get_sprite(3450, 0, 42, 55),
            win_red.get_sprite(3500, 0, 42, 55),
        ]

        zelda = SpriteSheet(resource_path('player', 'zelda.gif'), game)

        self.zelda_down = [
            zelda.get_sprite(1, 36, 18, 25, (255, 255, 255)),
            zelda.get_sprite(21, 37, 18, 24, (255, 255, 255)),
            zelda.get_sprite(63, 36, 18, 25, (255, 255, 255)),
            zelda.get_sprite(84, 37, 18, 24, (255, 255, 255)),
            zelda.get_sprite(105, 37, 18, 24, (255, 255, 255)),
        ]

        self.zelda_up = [
            zelda.get_sprite(0, 94, 18, 25, (255, 255, 255)),
            zelda.get_sprite(21, 95, 18, 24, (255, 255, 255)),
            zelda.get_sprite(43, 95, 18, 24, (255, 255, 255)),
            zelda.get_sprite(64, 94, 18, 25, (255, 255, 255)),
            zelda.get_sprite(84, 95, 18, 24, (255, 255, 255)),
            zelda.get_sprite(105, 95, 18, 24, (255, 255, 255)),
        ]

        self.zelda_left = [
            zelda.get_sprite(1, 161, 16, 28, (255, 255, 255)),
            zelda.get_sprite(22, 161, 17, 27, (255, 255, 255)),
            zelda.get_sprite(40, 161, 16, 27, (255, 255, 255)),
            zelda.get_sprite(60, 160, 16, 28, (255, 255, 255)),
            zelda.get_sprite(80, 161, 17, 27, (255, 255, 255)),
            zelda.get_sprite(99, 161, 16, 27, (255, 255, 255)),
        ]

        self.zelda_right = [
            pygame.transform.flip(f, True, False) for f in self.zelda_left
        ]

        self.zelda_item = [
            zelda.get_sprite(1, 223, 18, 28, (255, 255, 255)),
            zelda.get_sprite(21, 223, 18, 28, (255, 255, 255)),
            zelda.get_sprite(40, 223, 18, 28, (255, 255, 255)),
        ]

        self.zelda_sword = [
            zelda.get_sprite(188, 291, 44, 43, (255, 255, 255)),
            zelda.get_sprite(236, 291, 44, 43, (255, 255, 255)),
            zelda.get_sprite(283, 291, 44, 43, (255, 255, 255)),
            zelda.get_sprite(329, 291, 44, 43, (255, 255, 255)),
        ]

        zelda_sheet2 = SpriteSheet(resource_path('player', 'zelda2.png'), game)
        self.zelda_powered = [
            zelda_sheet2.get_sprite(15, 712, 18, 23, (16, 128, 88)),
            zelda_sheet2.get_sprite(48, 712, 18, 23, (16, 128, 88)),
            zelda_sheet2.get_sprite(81, 712, 18, 23, (16, 128, 88)),
        ]

        self.zelda_anim = [
            zelda.get_sprite(1, 223, 18, 28, (255, 255, 255)),
            zelda.get_sprite(21, 223, 18, 28, (255, 255, 255)),
            zelda.get_sprite(40, 223, 18, 28, (255, 255, 255)),
        ]

        win = SpriteSheet(resource_path('player', 'win_item.png'), game)
        self.win_item = [
            win.get_sprite(6, 36 - 16, 18, 24 + 16),
            win.get_sprite(166, 34 - 16, 18, 26 + 16),
            win.get_sprite(294, 36 - 16, 18, 24 + 16)
        ]

        self.hitbox = pygame.Rect(
            self.pos_x, self.pos_y, TILE_SIZE, TILE_SIZE
        )
        self.hurtbox = pygame.Rect(
            self.pos_x + TILE_SIZE // 4, self.pos_y + TILE_SIZE // 4,
            TILE_SIZE // 2, TILE_SIZE // 2
        )
        self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)

    def update(self, dt: float = 0) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        delta = dt / 1000.0
        if self.game_over or self.death:
            self.animate(delta)
            return

        self.image.set_alpha(255)
        self.change_direction()

        current_scene = self.game.scene_manager.current_scene()
        if (
            self.current_direction is not None
            and current_scene is not None
            and self.can_move(self.current_direction, delta)
            and not current_scene.frozen
        ):
            self.move_link(self.current_direction)

            self.pos_x += self.vx * delta
            self.pos_y += self.vy * delta

            self.hitbox.x = int(self.pos_x)
            self.hitbox.y = int(self.pos_y)
            self.hurtbox.x = self.hitbox.x + TILE_SIZE // 4
            self.hurtbox.y = self.hitbox.y + TILE_SIZE // 4
        else:
            self.vx = 0.0
            self.vy = 0.0

        self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)
        self.animate(delta)

        # use work surface width (positions are in work_surface coords)
        work_w = getattr(self.game, 'work_width', None)
        if work_w is None:
            work_w = self.game._work_surface.get_width()

        if self.hitbox.centerx < - 15:
            self.hitbox.x = work_w - TILE_SIZE
            self.pos_x = float(self.hitbox.x)
            self.hurtbox.x = self.hitbox.x + TILE_SIZE // 4
            self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)
        elif self.hitbox.centerx > work_w + 15:
            self.hitbox.x = 0
            self.pos_x = float(self.hitbox.x)
            self.hurtbox.x = self.hitbox.x + TILE_SIZE // 4
            self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)

        if self.powered:
            self.powered_timer -= delta
            if self.powered_timer <= 0:
                self.powered = False
                self.powered_timer = 8.0

    def respawn(self) -> None:
        """Reset the sprite to its spawn position."""
        self.hitbox.x = self.spawn_x
        self.hitbox.y = self.spawn_y
        self.hurtbox.x = self.spawn_x
        self.hurtbox.y = self.spawn_y
        self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)
        self.current_direction = None
        self.direction_asked = None
        self.pos_x = float(self.spawn_x)
        self.pos_y = float(self.spawn_y)
        self.vx = 0.0
        self.vy = 0.0
        self.powered = False
        self.powered_timer = 8.0
        self.win_level_started = False

    def move_link(self, direction: str) -> None:
        """Move the player sprite according to input.

        Args:
            direction: Movement direction to evaluate.
        """
        self.vx = 0.0
        self.vy = 0.0

        if direction == 'UP':
            self.vy = -self.speed
            self.facing = 'UP'
        if direction == 'DOWN':
            self.vy = self.speed
            self.facing = 'DOWN'
        if direction == 'LEFT':
            self.vx = -self.speed
            self.facing = 'LEFT'
        if direction == 'RIGHT':
            self.vx = self.speed
            self.facing = 'RIGHT'

    def is_aligned(self, axis: str = "both", tolerance: float = 5.0) -> bool:
        """Check whether the sprite is aligned to the grid.

        Args:
            axis: Axis to test for grid alignment.
            tolerance: Pixel tolerance accepted around the target alignment.

        Returns:
            True when the requested condition is met.
        """
        aligned_x = abs((self.hitbox.x % TILE_SIZE) - 0) <= tolerance or abs(
            (self.hitbox.x % TILE_SIZE) - TILE_SIZE) <= tolerance
        aligned_y = abs((self.hitbox.y % TILE_SIZE) - 0) <= tolerance or abs(
            (self.hitbox.y % TILE_SIZE) - TILE_SIZE) <= tolerance

        if axis == "x":
            return bool(aligned_x)
        if axis == "y":
            return bool(aligned_y)
        return bool(aligned_x and aligned_y)

    def queue_direction(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Queue a requested player direction.

        Args:
            keys: Current keyboard state mapping.
        """
        if keys[pygame.K_UP] or self.game.joystick_direction == 'UP':
            self.direction_asked = 'UP'
        elif keys[pygame.K_DOWN] or self.game.joystick_direction == 'DOWN':
            self.direction_asked = 'DOWN'
        elif keys[pygame.K_LEFT] or self.game.joystick_direction == 'LEFT':
            self.direction_asked = 'LEFT'
        elif keys[pygame.K_RIGHT] or self.game.joystick_direction == 'RIGHT':
            self.direction_asked = 'RIGHT'

    def change_direction(self) -> None:
        """Apply a new movement direction."""
        if self.direction_asked and self.can_move(self.direction_asked, 2)\
                and self.is_aligned('both'):
            self.current_direction = self.direction_asked
            self.direction_asked = None

    def can_move(self, direction: str | None, delta: float) -> bool:
        """Check whether movement is possible in a direction.

        Args:
            direction: Movement direction to evaluate.
            delta: Movement distance in pixels for this frame.

        Returns:
            True when the requested condition is met.
        """
        if direction is None:
            return False

        dx, dy = 0.0, 0.0
        if direction == 'UP':
            dy = -1
        elif direction == 'DOWN':
            dy = 1
        elif direction == 'LEFT':
            dx = -1
        elif direction == 'RIGHT':
            dx = 1

        verify_rect = self.hitbox.move(dx, dy)
        for wall in self.game.walls:
            if verify_rect.colliderect(wall.rect):
                return False
        return True

    def collide_walls(self, direction: str) -> bool:
        """Resolve wall collisions after movement.

        Args:
            direction: Movement direction to evaluate.

        Returns:
            True when the requested condition is met.
        """
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0:
                    self.hitbox.x = hits[0].rect.left - self.hitbox.width
                if self.vx < 0:
                    self.hitbox.x = hits[0].rect.right
                self.vx = 0
                return True
        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0:
                    self.hitbox.y = hits[0].rect.top - self.hitbox.height
                if self.vy < 0:
                    self.hitbox.y = hits[0].rect.bottom
                self.vy = 0
                return True
        return False

    def animate(self, dt: float) -> None:
        """Advance the sprite animation frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        if self.death:
            self.time_death += dt
            last_frame = len(self.link_death) - 1
            self.animation_loop = min(
                self.animation_loop + dt * self.anim_fps, last_frame)
            self.image = self.link_death[math.floor(self.animation_loop)]
            self.rect = self.image.get_rect(
                midbottom=self.hitbox.midbottom)

            if self.time_death >= len(self.link_death) / self.anim_fps:
                self.death = False
                self.time_death = 0.0
            return

        if self.game_over:
            self.time_death += dt
            last_frame = len(self.link_death) - 1
            self.animation_loop = min(
                self.animation_loop + dt * self.anim_fps, last_frame)
            self.image = self.link_death[math.floor(self.animation_loop)]
            self.rect = self.image.get_rect(
                midbottom=self.hitbox.midbottom)

            if self.time_death >= len(self.link_death) / self.anim_fps:
                self.game_over = False
                self.time_death = 0.0
            return

        current_scene = self.game.scene_manager.current_scene()
        if current_scene is not None and current_scene.frozen:
            if current_scene.item_gain and self.current_held_item is not None:
                if self.cheat is False:
                    last_frame = len(self.win_item) - 1
                    self.animation_loop = min(
                        self.animation_loop + dt * self.anim_fps, last_frame)
                    self.image = self.win_item[math.floor(self.animation_loop)]
                    link_frame = self.image.copy()
                    item_rect = self.current_held_item.get_rect(
                        midbottom=(link_frame.get_width() // 2, 16))
                    link_frame.blit(self.current_held_item, item_rect)
                    self.image = link_frame
                    self.rect = self.image.get_rect(
                        midbottom=self.hitbox.midbottom)
                    return
                else:
                    last_frame = len(self.zelda_item) - 1
                    self.animation_loop = min(
                        self.animation_loop + dt * self.anim_fps, last_frame)
                    self.image = self.zelda_item[math.floor(
                        self.animation_loop)]
                    zelda_frame = self.image.copy()
                    item_rect = self.current_held_item.get_rect(
                        midbottom=(zelda_frame.get_width() // 2, 16))
                    zelda_frame.blit(self.current_held_item, item_rect)
                    self.image = zelda_frame
                    self.rect = self.image.get_rect(
                        midbottom=self.hitbox.midbottom)
                    return
            elif current_scene.win_level:
                if not self.win_level_started:
                    self.animation_loop = 0
                    self.win_level_started = True

                if self.cheat:
                    last_frame = len(self.zelda_anim) - 1
                    self.animation_loop = min(
                        self.animation_loop + dt * self.anim_fps, last_frame)
                    self.image = self.zelda_anim[
                        math.floor(self.animation_loop)]
                    self.rect = self.image.get_rect(
                        midbottom=self.hitbox.midbottom)
                    return

                if self.power_color == 'blue':
                    last_frame = len(self.win_blue) - 1
                    self.animation_loop = min(
                        self.animation_loop + dt * self.anim_fps, last_frame)
                    self.image = self.win_blue[math.floor(self.animation_loop)]
                    self.rect = self.image.get_rect(
                        midbottom=self.hitbox.midbottom)
                    return
                elif self.power_color == 'base':
                    last_frame = len(self.win_base) - 1
                    self.animation_loop = min(
                        self.animation_loop + dt * self.anim_fps, last_frame)
                    self.image = self.win_base[math.floor(self.animation_loop)]
                    self.rect = self.image.get_rect(
                        midbottom=self.hitbox.midbottom)
                    return
                elif self.power_color == 'yellow':
                    last_frame = len(self.win_yellow) - 1
                    self.animation_loop = min(
                        self.animation_loop + dt * self.anim_fps, last_frame)
                    self.image = self.win_yellow[math.floor(
                        self.animation_loop)]
                    self.rect = self.image.get_rect(
                        midbottom=self.hitbox.midbottom)
                    return
                elif self.power_color == 'red':
                    last_frame = len(self.win_red) - 1
                    self.animation_loop = min(
                        self.animation_loop + dt * self.anim_fps, last_frame)
                    self.image = self.win_red[math.floor(self.animation_loop)]
                    self.rect = self.image.get_rect(
                        midbottom=self.hitbox.midbottom)
                    return
            else:
                if self.cheat is False:
                    last_frame = len(self.obtain_sword) - 1
                    self.animation_loop = min(
                        self.animation_loop + dt * self.anim_fps, last_frame)
                    self.image = self.obtain_sword[math.floor(
                        self.animation_loop)]
                    self.rect = self.image.get_rect(
                        midbottom=self.hitbox.midbottom)
                    self.powered = True
                    return
                else:
                    last_frame = len(self.zelda_sword) - 1
                    self.animation_loop = min(
                        self.animation_loop + dt * self.anim_fps, last_frame)
                    self.image = self.zelda_sword[
                        math.floor(self.animation_loop)]
                    self.rect = self.image.get_rect(
                        midbottom=self.hitbox.midbottom)
                    self.powered = True
                    return

        if self.facing == 'UP':
            if not self.powered:
                if self.vy == 0:
                    if self.cheat is False:
                        self.image = self.up_walking[0]
                    else:
                        self.image = self.zelda_up[0]
                else:
                    if self.cheat is False:
                        self.animation_loop += dt * self.anim_fps
                        if self.animation_loop >= len(self.up_walking):
                            self.animation_loop = 0
                        self.image = self.up_walking[math.floor(
                            self.animation_loop)]
                    else:
                        self.animation_loop += dt * self.anim_fps
                        if self.animation_loop >= len(self.zelda_up):
                            self.animation_loop = 0
                        self.image = self.zelda_up[math.floor(
                            self.animation_loop)]
            else:
                if self.vy == 0:
                    if self.cheat is False:
                        self.image = self.powered_up[0]
                    else:
                        self.image = self.zelda_powered[0]
                else:
                    if self.cheat is False:
                        self.animation_loop += dt * self.anim_fps
                        if self.animation_loop >= len(self.powered_up):
                            self.animation_loop = 0
                        self.image = self.powered_up[math.floor(
                            self.animation_loop)]
                    else:
                        self.animation_loop += dt * self.anim_fps
                        if self.animation_loop >= len(self.zelda_powered):
                            self.animation_loop = 0
                        self.image = self.zelda_powered[math.floor(
                            self.animation_loop)]

        if self.facing == 'LEFT':
            if not self.powered:
                if self.vx == 0:
                    if self.cheat is False:
                        self.image = self.left_walking[0]
                    else:
                        self.image = self.zelda_left[0]
                else:
                    if self.cheat is False:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.left_walking):
                            self.animation_loop = 0
                        self.image = self.left_walking[math.floor(
                            self.animation_loop)]
                    else:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.zelda_left):
                            self.animation_loop = 0
                        self.image = self.zelda_left[math.floor(
                            self.animation_loop)]
            else:
                if self.vx == 0:
                    if self.cheat is False:
                        self.image = self.powered_left[0]
                    else:
                        self.image = self.zelda_powered[0]
                else:
                    if self.cheat is False:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.powered_left):
                            self.animation_loop = 0
                        self.image = self.powered_left[math.floor(
                            self.animation_loop)]
                    else:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.zelda_powered):
                            self.animation_loop = 0
                        self.image = self.zelda_powered[math.floor(
                            self.animation_loop)]

        if self.facing == 'RIGHT':
            if not self.powered:
                if self.vx == 0:
                    if self.cheat is False:
                        self.image = self.right_walking[0]
                    else:
                        self.image = self.zelda_right[0]
                else:
                    if self.cheat is False:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.right_walking):
                            self.animation_loop = 0
                        self.image = self.right_walking[math.floor(
                            self.animation_loop)]
                    else:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.zelda_right):
                            self.animation_loop = 0
                        self.image = self.zelda_right[math.floor(
                            self.animation_loop)]
            else:
                if self.vx == 0:
                    if self.cheat is False:
                        self.image = self.powered_right[0]
                    else:
                        self.image = self.zelda_powered[0]
                else:
                    if self.cheat is False:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.powered_right):
                            self.animation_loop = 0
                        self.image = self.powered_right[math.floor(
                            self.animation_loop)]
                    else:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.zelda_powered):
                            self.animation_loop = 0
                        self.image = self.zelda_powered[math.floor(
                            self.animation_loop)]
        if self.facing == 'DOWN':
            if not self.powered:
                if self.vy == 0:
                    if self.cheat is False:
                        self.image = self.down_walking[0]
                    else:
                        self.image = self.zelda_down[0]
                else:
                    if self.cheat is False:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.down_walking):
                            self.animation_loop = 0
                        self.image = self.down_walking[math.floor(
                            self.animation_loop)]
                    else:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.zelda_down):
                            self.animation_loop = 0
                        self.image = self.zelda_down[math.floor(
                            self.animation_loop)]
            else:
                if self.vy == 0:
                    if self.cheat is False:
                        self.image = self.powered_down[0]
                    else:
                        self.image = self.zelda_powered[0]
                else:
                    if self.cheat is False:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.powered_down):
                            self.animation_loop = 0
                        self.image = self.powered_down[math.floor(
                            self.animation_loop)]
                    else:
                        self.animation_loop += 0.1
                        if self.animation_loop >= len(self.zelda_powered):
                            self.animation_loop = 0
                        self.image = self.zelda_powered[math.floor(
                            self.animation_loop)]


class Ennemy(GameSprite):
    """Represent an enemy sprite driven by AI behavior."""
    def __init__(
        self,
        game: "Game",
        x: int,
        y: int,
        ai: EnemyBrain,
        skin_anim: SkinAnimation,
        enemy_type: str = "enemy",
    ) -> None:
        """Initialize the ennemy.

        Args:
            game: Shared game object that owns resources, groups, and state.
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.
            ai: Enemy brain used to choose movement.
            skin_anim: Animation frames used by the enemy sprite.
            enemy_type: Enemy type label used for behavior and display.
        """
        super().__init__()
        self.skin_anim = skin_anim
        self.animation_loop = 0.0
        self.facing = 'DOWN'
        self.game = game
        self.image = self.skin_anim['down'][0]\
            if 'down' in self.skin_anim else pygame.Surface(
            (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        # Add more enemies by instantiating Ennemy with its own StrategyAI
        # and registering it in this group.
        self.game.all_sprites.add(self)
        self.game.ennemies.add(self)
        self.hitbox = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.hurtbox = pygame.Rect(
            x + TILE_SIZE // 4, y + TILE_SIZE // 4,
            TILE_SIZE // 2, TILE_SIZE // 2
        )
        self.vx = 0.0
        self.vy = 0.0
        self.pos_x = float(x)
        self.pos_y = float(y)
        # Keep speed easy to tune without changing the AI.
        self.speed = 100.0
        self.ai = ai
        self.enemy_type = enemy_type
        self.spawn_x = x
        self.spawn_y = y
        self.spawn_grid = ai.position
        self.current_direction: str | None = None
        self.direction_asked: str | None = None
        # La cible est la prochaine cellule en pixels; l'IA reste en grille.
        self.target_world_x = float(x)
        self.target_world_y = float(y)
        # Tracker l'etat precedent pour detecter le passage a FRIGHTENED
        self.last_ai_state = ai.state
        self.is_respawning = False
        self.respawn_timer = 0.0
        self.points = self.game.config["points_per_ghost"]
        # Directions opposees pour forcer demi-tour instantane
        self.opposite_directions = {'UP': 'DOWN', 'DOWN': 'UP',
                                    'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
        self.chase_play = False

    def respawn(self) -> None:
        """Reset the sprite to its spawn position."""
        self.hitbox.x = self.spawn_x
        self.hitbox.y = self.spawn_y
        self.pos_x = float(self.spawn_x)
        self.pos_y = float(self.spawn_y)
        self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)
        self.current_direction = None
        self.direction_asked = None
        self.target_world_x, self.target_world_y = self._grid_to_world(
            *self.spawn_grid
        )
        self.ai.position = self.spawn_grid
        self.ai.state = self.ai._default_state
        self.ai.state_controller.state_timer = 0.0
        if hasattr(self.ai, "clear_scatter_round_tracking"):
            self.ai.clear_scatter_round_tracking()
        current_behavior = self.ai.behaviors[self.ai.state]
        self.ai.current_target = current_behavior.current_target
        self.ai.current_direction = current_behavior.current_direction
        self.is_respawning = False
        self.respawn_timer = 0.0
        # self.image.set_alpha(126)
        # self.image.fill(self.base_color)

    def begin_respawn(self, duration_ms: int) -> None:
        """Begin the enemy respawn delay.

        Args:
            duration_ms: Freeze duration in milliseconds.
        """
        self.respawn()
        self.is_respawning = True
        self.respawn_timer = duration_ms / 1000.0
        self.image.set_alpha(0)

    def advance_respawn(self, delta: float) -> None:
        """Advance the enemy respawn timer.

        Args:
            delta: Movement distance in pixels for this frame.
        """
        if not self.is_respawning:
            return
        self.respawn_timer = max(0.0, self.respawn_timer - delta)
        if self.respawn_timer > 0:
            return
        self.is_respawning = False
        self.image.set_alpha(255)

    def _world_to_grid(self, x: int, y: int) -> tuple[int, int]:
        """Convert world pixels to a maze grid coordinate.

        Args:
            x: Horizontal coordinate in pixels.
            y: Vertical coordinate in pixels.

        Returns:
            Computed coordinate tuple.
        """
        step = TILE_SIZE * 2
        gx = (x - self.game.maze_offset_x - TILE_SIZE) // step
        gy = (y - self.game.maze_offset_y - TILE_SIZE) // step
        max_x = len(self.game.maze_grid[0]) - 1
        max_y = len(self.game.maze_grid) - 1
        gx = max(0, min(int(gx), max_x))
        gy = max(0, min(int(gy), max_y))
        return gx, gy

    def _grid_to_world(self, gx: int, gy: int) -> tuple[int, int]:
        """Convert grid coordinates to world pixels.

        Args:
            gx: Horizontal grid coordinate.
            gy: Vertical grid coordinate.

        Returns:
            World pixel coordinates for the cell.
        """
        step = TILE_SIZE * 2
        x = self.game.maze_offset_x + TILE_SIZE + gx * step
        y = self.game.maze_offset_y + TILE_SIZE + gy * step
        return x, y

    def _is_on_cell_center(self, tolerance: int = 2) -> bool:
        """Check whether the sprite is centered on a cell.

        Args:
            tolerance: Pixel tolerance accepted around the target alignment.

        Returns:
            True when the requested condition is met.
        """
        step = TILE_SIZE * 2
        rel_x = self.hitbox.x - (self.game.maze_offset_x + TILE_SIZE)
        rel_y = self.hitbox.y - (self.game.maze_offset_y + TILE_SIZE)
        return bool(
            (abs(rel_x % step) <= tolerance or
             abs((rel_x % step) - step) <= tolerance) and
            (abs(rel_y % step) <= tolerance or
             abs((rel_y % step) - step) <= tolerance)
        )

    def update(self, dt: float = 0) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        delta = dt / 1000.0

        if self.is_respawning:
            self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)
            return

        current_scene = self.game.scene_manager.current_scene()
        if current_scene is not None and current_scene.frozen:
            self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)
            return

        state_changed = self.ai.transition_state(
            player_powered=self.game.player.powered,
            delta_seconds=delta,
        )

        # Decide the next grid step only once the enemy reaches its current
        # target cell center.
        if (abs(self.hitbox.x - self.target_world_x) <= 1 and
                abs(self.hitbox.y - self.target_world_y) <= 1):
            self.hitbox.x = int(self.target_world_x)
            self.hitbox.y = int(self.target_world_y)

            current_grid = self._world_to_grid(self.hitbox.x, self.hitbox.y)
            self.ai.position = current_grid
            self.ai.trace(
                f"{self.ai.state.value} pos={current_grid}"
            )
            # self.ai.trace(
            #     f"tick state={self.ai.state.value} "
            #     f"powered={self.game.player.powered} pos={current_grid}"
            # )

            if self.ai.state == State.CHASE and not self.chase_play:
                self.chase_play = True
                self.game.sfx['m'].play()
                self.game.sfx['m'].set_volume(0.1)
            elif self.ai.state != State.CHASE and self.chase_play:
                self.chase_play = False
            # Detecter le passage a FRIGHTENED et forcer demi-tour immediat
            immediate_reversal = False
            if (state_changed and
                    self.ai.state == State.FRIGHTENED):
                # Inverser immediatement la direction et recalculer la cible
                if self.current_direction in self.opposite_directions:
                    opposite_dir = \
                        self.opposite_directions[self.current_direction]
                    # Faire avancer l'IA dans la direction opposee
                    self.ai.change_position(opposite_dir)
                    # Recalculer la cible en pixels
                    self.target_world_x, self.target_world_y = \
                        self._grid_to_world(*self.ai.position)
                    self.current_direction = opposite_dir
                    immediate_reversal = True
                    # self.ai.trace(
                    #     f"frightened immediate_reversal={opposite_dir}"
                    # )

            # Si on vient de forcer un demi-tour, skip la decision IA normale
            # pour la prochaine cellule
            if not immediate_reversal:
                # Build ChaseContext and ask AI to compute the CHASE target
                try:
                    player_grid = self._world_to_grid(
                        self.game.player.hitbox.centerx,
                        self.game.player.hitbox.centery,
                    )

                    # Build all_enemies positions map
                    all_enemies: dict[str, tuple[int, int]] = {}
                    for e in self.game.ennemies:
                        key = e.enemy_type or e.ai.enemy_id
                        if key:
                            all_enemies[str(key).lower()] = e.ai.position

                    # Determine scatter corner if available
                    scatter_corner: tuple[int, int] = self.ai.position
                    scatter_behavior = self.ai.behaviors.get(State.SCATTER)
                    if scatter_behavior and hasattr(scatter_behavior,
                                                    'scatter_corner'):
                        scatter_corner = scatter_behavior.scatter_corner
                    else:
                        eaten_behavior = self.ai.behaviors.get(State.EATEN)
                        scatter_corner = getattr(eaten_behavior,
                                                 'respawn_position',
                                                 self.ai.position)

                    chase_ctx = ChaseContext(
                        enemy_type=self.enemy_type,
                        player_grid=player_grid,
                        player_direction=getattr(
                            self.game.player, 'current_direction', None),
                        enemy_grid=self.ai.position,
                        enemy_scatter_corner=scatter_corner,
                        all_enemies_grid=all_enemies,
                    )

                    target_grid = self.ai.compute_target(chase_ctx)
                except Exception:
                    # Fallback: original behavior (direct player target)
                    target_grid = self._world_to_grid(
                        self.game.player.hitbox.centerx,
                        self.game.player.hitbox.centery,
                    )

                next_direction = self.ai.decision(target_grid)
                previous_grid = self.ai.position
                self.ai.change_position(next_direction)

                if self.ai.position != previous_grid:
                    self.current_direction = next_direction
                    self.facing = self.current_direction
                    self.target_world_x, self.target_world_y = \
                        self._grid_to_world(*self.ai.position)

        # Smooth interpolation toward the current target cell center.
        dx = self.target_world_x - self.hitbox.x
        dy = self.target_world_y - self.hitbox.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            step = self.speed * delta
            if step >= distance:
                self.hitbox.x = int(self.target_world_x)
                self.hitbox.y = int(self.target_world_y)
                self.pos_x = float(self.hitbox.x)
                self.pos_y = float(self.hitbox.y)
                self.hurtbox.x = self.hitbox.x + TILE_SIZE // 4
                self.hurtbox.y = self.hitbox.y + TILE_SIZE // 4
            else:
                ratio = step / distance
                self.pos_x += dx * ratio
                self.pos_y += dy * ratio
                self.hitbox.x = int(self.pos_x)
                self.hitbox.y = int(self.pos_y)
                self.hurtbox.x = self.hitbox.x + TILE_SIZE // 4
                self.hurtbox.y = self.hitbox.y + TILE_SIZE // 4

        self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)
        self.animate()

        if self.hitbox.x < 0:
            self.hitbox.x = self.game._logic_screen.get_width()
        elif self.hitbox.x > self.game._logic_screen.get_width():
            self.hitbox.x = 0

        if self.ai.state == State.FRIGHTENED:
            self.speed = 50.0  # Slow enemies while FRIGHTENED.
        else:
            self.speed = 100.0  # Use normal speed in other modes.

    def move(self, direction: str) -> None:
        """Move the sprite according to its current direction.

        Args:
            direction: Movement direction to evaluate.
        """
        self.vx = 0.0
        self.vy = 0.0

        if direction == 'UP':
            self.vy = -self.speed
            self.facing = 'UP'
        elif direction == 'DOWN':
            self.vy = self.speed
            self.facing = 'DOWN'
        elif direction == 'LEFT':
            self.vx = -self.speed
            self.facing = 'LEFT'
        elif direction == 'RIGHT':
            self.vx = self.speed
            self.facing = 'RIGHT'

    def is_aligned(self, axis: str = "both", tolerance: float = 5.0) -> bool:
        """Check whether the sprite is aligned to the grid.

        Args:
            axis: Axis to test for grid alignment.
            tolerance: Pixel tolerance accepted around the target alignment.

        Returns:
            True when the requested condition is met.
        """
        aligned_x = abs((self.hitbox.x % TILE_SIZE) - 0) <= tolerance or abs(
            (self.hitbox.x % TILE_SIZE) - TILE_SIZE) <= tolerance
        aligned_y = abs((self.hitbox.y % TILE_SIZE) - 0) <= tolerance or abs(
            (self.hitbox.y % TILE_SIZE) - TILE_SIZE) <= tolerance

        if axis == "x":
            return bool(aligned_x)
        if axis == "y":
            return bool(aligned_y)
        return bool(aligned_x and aligned_y)

    def change_direction(self) -> None:
        """Apply a new movement direction."""
        if self.direction_asked is not None:
            if self.direction_asked == 'UP' and not self.collide_walls('y'):
                self.current_direction = 'UP'
                self.direction_asked = None
            if self.direction_asked == 'DOWN' and not self.collide_walls('y'):
                self.current_direction = 'DOWN'
                self.direction_asked = None
            if self.direction_asked == 'LEFT' and not self.collide_walls('x'):
                self.current_direction = 'LEFT'
                self.direction_asked = None
            if self.direction_asked == 'RIGHT' and not self.collide_walls('x'):
                self.current_direction = 'RIGHT'
                self.direction_asked = None

    def can_move(self, direction: str, delta: float) -> bool:
        """Check whether movement is possible in a direction.

        Args:
            direction: Movement direction to evaluate.
            delta: Movement distance in pixels for this frame.

        Returns:
            True when the requested condition is met.
        """
        dx, dy = 0.0, 0.0
        if direction == 'UP':
            dy = -1
        elif direction == 'DOWN':
            dy = 1
        elif direction == 'LEFT':
            dx = -1
        elif direction == 'RIGHT':
            dx = 1

        verify_rect = self.hitbox.move(dx, dy)
        for wall in self.game.walls:
            if verify_rect.colliderect(wall.rect):
                return False
        return True

    def collide_walls(self, direction: str) -> bool:
        """Resolve wall collisions after movement.

        Args:
            direction: Movement direction to evaluate.

        Returns:
            True when the requested condition is met.
        """
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0:
                    self.hitbox.x = hits[0].rect.left - self.hitbox.width
                if self.vx < 0:
                    self.hitbox.x = hits[0].rect.right
                self.vx = 0
                return True
        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0:
                    self.hitbox.y = hits[0].rect.top - self.hitbox.height
                if self.vy < 0:
                    self.hitbox.y = hits[0].rect.bottom
                self.vy = 0
                return True
        return False

    def animate(self) -> None:
        """Advance the sprite animation frame."""
        if self.facing == 'UP':
            self.animation_loop += 0.1
            if self.animation_loop >= len(self.skin_anim['up']):
                self.animation_loop = 0
            self.image = self.skin_anim['up'][math.floor(self.animation_loop)]

        if self.facing == 'LEFT':
            self.animation_loop += 0.1
            if self.animation_loop >= len(self.skin_anim['left']):
                self.animation_loop = 0
            self.image = self.skin_anim['left'][math.floor(
                self.animation_loop)]

        if self.facing == 'RIGHT':
            self.animation_loop += 0.1
            if self.animation_loop >= len(self.skin_anim['right']):
                self.animation_loop = 0
            self.image = self.skin_anim['right'][math.floor(
                self.animation_loop)]

        if self.facing == 'DOWN':
            self.animation_loop += 0.1
            if self.animation_loop >= len(self.skin_anim['down']):
                self.animation_loop = 0
            self.image = self.skin_anim['down'][math.floor(
                self.animation_loop)]
