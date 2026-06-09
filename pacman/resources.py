from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PACKAGE_DIR / "assets"
TILE_SIZE = 16
SCALE = 1.5
PAD_X = 48
PAD_Y = 48
HEART_SCALE = 2


def resource_path(*parts: str) -> str:
    """Build an absolute path to an asset resource.

    Args:
        parts: Path components below the assets directory.

    Returns:
        Absolute path to the requested asset.
    """
    return str(ASSETS_DIR.joinpath(*parts))
