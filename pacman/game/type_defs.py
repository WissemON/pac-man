from __future__ import annotations

from typing import TypeAlias, TypedDict

import pygame


class GameSprite(pygame.sprite.Sprite):
    """Define the sprite attributes required by game sprite groups."""
    image: pygame.Surface
    rect: pygame.Rect


JsonValue: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | list["JsonValue"]
    | dict[str, "JsonValue"]
)


AIConfig: TypeAlias = dict[str, float]


class LevelConfig(TypedDict):
    """Describe the validated configuration for a single level."""
    width: int
    height: int
    ai: AIConfig


LevelConfigMap: TypeAlias = dict[str, LevelConfig]


class GameConfig(TypedDict):
    """Describe the validated game configuration structure."""
    lives: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_special_item: int
    points_per_ghost: int
    level_max_time: int
    seed: int
    level: list[LevelConfigMap]


class HighscoreEntry(TypedDict):
    """Describe one persisted highscore entry."""
    player_name: str
    score: int
    skin_color: str
    cheat: bool


SkinAnimation: TypeAlias = dict[str, list[pygame.Surface]]


class BiomeAssets(TypedDict):
    """Group the surfaces used by a level biome."""
    wall_base: pygame.Surface
    ground_base: pygame.Surface
    wall_variants: list[pygame.Surface]
    ground_variants: list[pygame.Surface]


BiomeConfig: TypeAlias = dict[str, BiomeAssets]
