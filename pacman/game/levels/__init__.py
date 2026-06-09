from pacman.game.levels.level_base import Level
from pacman.game.levels.hyrule_field import HyruleField
from pacman.game.levels.minish_woods import MinishWoods
from pacman.game.levels.deepwood_shrine import DeepwoodShrine
from pacman.game.levels.mount_crenel import MountCrenel
from pacman.game.levels.cave_of_flames import CaveOfFlames
from pacman.game.levels.castor_wilds import CastorWilds
from pacman.game.levels.wind_ruins import WindRuins
from pacman.game.levels.fortress_winds import FortressWinds
from pacman.game.levels.cave import Cave
from pacman.game.levels.temple_of_droplets import TempleDroplets
from pacman.game.levels.royal_valley import RoyalValley
from pacman.game.levels.cloud_tops import CloudTops
from pacman.game.levels.palace_of_winds import PalaceOfWinds
from pacman.game.levels.dark_hyrule_castle import DarkHyruleCastle
from pacman.game.levels.vaati_battle import VaatiBattle
from pacman.game.levels.final_battle import FinalBattle

__all__ = [
    'Level',
    'HyruleField',
    'MinishWoods',
    'DeepwoodShrine',
    'MountCrenel',
    'CaveOfFlames',
    'CastorWilds',
    'WindRuins',
    'FortressWinds',
    'Cave',
    'TempleDroplets',
    'RoyalValley',
    'CloudTops',
    'PalaceOfWinds',
    'DarkHyruleCastle',
    'VaatiBattle',
    'FinalBattle',
]

# Ordered list of level classes for centralised mapping (index -> level id)
LEVEL_CLASSES: list[type[Level]] = [
    HyruleField,
    MinishWoods,
    DeepwoodShrine,
    MountCrenel,
    CaveOfFlames,
    CastorWilds,
    WindRuins,
    FortressWinds,
    Cave,
    TempleDroplets,
    RoyalValley,
    CloudTops,
    PalaceOfWinds,
    DarkHyruleCastle,
    VaatiBattle,
    FinalBattle,
]


level_name: list[str] = [
    'Hyrule Field',
    'Minish Woods',
    'Deepwood Shrine',
    'Mount Crenel',
    'Cave of Flames',
    'Castor Wilds',
    'Wind Ruins',
    'Fortress Winds',
    'Cave',
    'Temple of Droplets',
    'Royal Valley',
    'Cloud Tops',
    'Palace of Winds',
    'Dark Hyrule Castle',
    'Vaati Battle',
    'Final Battle',
]


def level_class_to_id(level_class: type[Level]) -> str:
    """Resolve the config id for a level class.

    Args:
        level_class: Level class to resolve or instantiate.

    Returns:
        One-based config id for the level class.
    """
    try:
        idx = LEVEL_CLASSES.index(level_class)
        return str(idx + 1)
    except ValueError:
        return ''


def level_id_to_class(level_id: str) -> type[Level] | None:
    """Resolve a level class from a config id.

    Args:
        level_id: String identifier of the level.

    Returns:
        Matching level class, or None when unknown.
    """
    try:
        idx = int(level_id) - 1
        if 0 <= idx < len(LEVEL_CLASSES):
            return LEVEL_CLASSES[idx]
    except Exception:
        pass
    return None
