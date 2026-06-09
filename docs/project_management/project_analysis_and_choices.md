# Project Analysis and Associated Choices

The project evolved from a basic Pac-Man implementation into a themed 2D game with multiple levels, menus, endings, AI states, controller support, persistent scores, and quality gates.

## Main Choices

| Choice | Rationale |
| --- | --- |
| pygame | Chosen as the game framework because the activity is a 2D arcade game with direct sprite/input/audio needs. |
| uv + Makefile | uv manages reproducible dependencies, while Makefile exposes install/run/lint/build commands required by the activity. |
| JSON config/highscores | Simple persistent format, readable during evaluation, easy to validate and version. |
| Scene stack architecture | Separates gameplay, menu, pause, title, game-over, and ending screens. |
| Level subclasses plus Level base | Allows themed levels while moving common behavior into shared helpers. |
| EnemyBrain + strategy classes | Keeps Pac-Man-like AI states explicit and debuggable. |
| Strict typing late in project | Used mypy --strict after feature completion to reduce regression risk without slowing early prototyping. |

## Architecture Summary

- `pacman/main.py` starts the game and loads configuration/highscores.
- `pacman/game/game.py` owns global pygame resources and the scene manager.
- `pacman/game/scene_manager.py` manages scene transitions and overlays.
- `pacman/game/scenes/` separates title, menu, play, pause, game-over, and endings.
- `pacman/game/levels/` separates level themes while sharing logic through `level_base.py`.
- `pacman/game/ai.py` contains enemy state/strategy logic.
- `pacman/highscores.py` and `pacman/game/save.py` handle persistence.

