*This activity has been created as part of the 42 curriculum by wboussah, sizem.*

# Pacman

## Description

Pacman is a Pac-Man-inspired 2D arcade game built with Python and
pygame. The goal of the activity is to recreate the core ideas of Pac-Man:
maze navigation, collectible pac-gums, enemy AI, scoring, lives, a timer,
menus, and persistent highscores.

The project goes beyond a minimal clone by using a Zelda: The Minish Cap
visual theme, multiple levels, custom sprites, music, sound effects, controller
support, several ending screens, cheat handling, and debugging tools for enemy
AI behavior.

## Instructions

### Requirements

- Python 3.13 or newer
- `uv`
- `make`

The project dependencies are declared in `pyproject.toml`:

- `pygame`
- `mazegenerator`

### Installation

Install or synchronize the virtual environment:

```bash
make install
```

This uses `uv sync` and installs the dependencies declared by the project.

### Execution

Run the game with the default configuration:

```bash
make run
```

Equivalent direct command:

```bash
.venv/bin/python pac-man.py config.json
```

The executable entry point is `pac-man.py`, which delegates to
`pacman.main:main`.

### Development Commands

Show available Makefile targets:

```bash
make help
```

Run linting and type checking:

```bash
make lint
make lint-strict
```

Build Python distributions:

```bash
make build
```

Clean Python cache files:

```bash
make clean
```

### Packaging Notes

The project was also tested with PyInstaller for local standalone distribution.
The recommended workflow is to test `onedir` first, then try `onefile` only
after the folder build works.

Example Linux `onedir` command:

```bash
.venv/bin/python -m PyInstaller \
  --name pac-man \
  --onedir \
  --clean \
  --add-data "pacman/assets:pacman/assets" \
  --add-data "pacman/highscores.json:pacman" \
  --add-data "pacman/game/saves/save.txt:pacman/game/saves" \
  --add-data "config.json:." \
  pac-man.py
```

The distributable folder is then:

```text
dist/pac-man/
```

## Configuration

The game uses `config.json` at the repository root. The loader supports normal
JSON and also strips comments before parsing:

- `# line comments`
- `// line comments`
- `/* block comments */`

The configuration is validated in `pacman/config.py`. Invalid or missing values
are replaced with safe defaults.

### Structure

```json
{
  "lives": 3,
  "pacgum": 42,
  "points_per_pacgum": 1,
  "points_per_super_pacgum": 20,
  "points_per_special_item": 30,
  "points_per_ghost": 40,
  "level_max_time": 300,
  "seed": 42,
  "level": [
    {
      "1": {
        "width": 4,
        "height": 4,
        "ai": {
          "scatter_duration": 12.0,
          "chase_duration": 24.0,
          "frightened_duration": 6.0,
          "eaten_duration": 7.0
        }
      }
    }
  ]
}
```

### Keys

| Key | Type | Purpose | Default |
| --- | --- | --- | --- |
| `lives` | integer | Number of player lives. | `3` |
| `pacgum` | integer | Number of pac-gums to place. | `42` |
| `points_per_pacgum` | integer | Score gained for one pac-gum. | `1` |
| `points_per_super_pacgum` | integer | Score gained for one super pac-gum. | `20` |
| `points_per_special_item` | integer | Score gained for one special item. | `30` |
| `points_per_ghost` | integer | Score gained when eating an enemy. | `40` |
| `level_max_time` | integer | Maximum level duration in seconds. | `300` |
| `seed` | integer | Seed used for deterministic first maze generation. | `42` |
| `level` | list | Per-level maze and AI configuration. | All levels get defaults. |

Each level entry contains:

| Key | Type | Purpose | Default |
| --- | --- | --- | --- |
| `width` | integer | Maze width passed to the maze generator. | `14` |
| `height` | integer | Maze height passed to the maze generator. | `14` |
| `ai.scatter_duration` | number | Duration of scatter mode. | `6.0` |
| `ai.chase_duration` | number | Duration of chase mode. | `7.0` |
| `ai.frightened_duration` | number | Duration of frightened mode. | `6.0` |
| `ai.eaten_duration` | number | Duration of eaten/respawn mode. | `7.0` |

## Highscore

Highscores are stored in `pacman/highscores.json` as a JSON object indexed from
`"1"` to `"10"`.

Example entry:

```json
{
  "1": {
    "player_name": "DZ",
    "score": 99002,
    "skin_color": "green",
    "cheat": false
  }
}
```

The highscore system is implemented in `pacman/highscores.py`.

It was intentionally implemented with JSON because:

- it is human-readable during evaluation;
- it is easy to version and inspect;
- it does not require a database dependency;
- it matches the project configuration format.

When a new score is saved:

1. Existing highscores are loaded and validated.
2. The player name must be 1 to 10 characters.
3. Only alphanumeric characters and spaces are accepted.
4. The new score is inserted.
5. The list is sorted in descending score order.
6. Only the best 10 scores are kept.
7. The `cheat` flag is saved to make cheated runs visible.

## Maze Generation

The assigned A-Maze-ing package is used through:

```python
from mazegenerator.mazegenerator import MazeGenerator
```

At the start of a level, `PlayScene` reads the configured `width` and `height`
for the current level and asks `MazeGenerator` to create a maze grid. The first
level uses the configured global `seed` so the first maze can be deterministic.
Later levels can be regenerated with their own current configuration.

The generated grid is stored in `Game.maze_grid`. Each level class receives
this grid and translates it into pygame sprites:

- wall tiles;
- walkable ground tiles;
- pac-gums and super pac-gums;
- special items;
- enemy spawn positions;
- player spawn position;
- decorative level-specific sprites.

Shared helpers in `pacman/game/levels/level_base.py` convert grid coordinates
to world coordinates and provide common collision/spawn utilities.

## Implementation

The implementation is split around a scene-based pygame architecture.

Main technical elements:

- pygame manages rendering, input, audio, sprites, surfaces, and collisions.
- `SceneManager` manages the active scene stack.
- `PlayScene` owns the gameplay loop for the current level.
- `Level` subclasses define the visual theme and layout behavior of each level.
- `EnemyBrain` routes enemy behavior through Pac-Man-like AI states.
- `InputHandler` normalizes keyboard and controller input.
- `UiElements` draws score, lives, items, and timer.
- `SpriteSheet` extracts sprites from image sheets.
- `StringFont` centralizes text rendering.
- JSON files persist configuration, highscores, and unlocked levels.

The project was hardened late in development with:

- `flake8`
- `mypy --strict`
- complete function/class docstrings
- focused refactors for shared level behavior
- PyInstaller packaging tests

## General Software Architecture

```text
pac-man.py
└── pacman/main.py
    ├── pacman/config.py
    ├── pacman/highscores.py
    └── pacman/game/game.py
        ├── SceneManager
        │   ├── TitleScreen
        │   ├── MainMenuScene
        │   ├── PlayScene
        │   ├── PauseScene
        │   ├── GameOverScene
        │   ├── WinScreenBase
        │   ├── TrueEndingScene
        │   └── WeirdEndingScene
        ├── Level subclasses
        │   ├── HyruleField
        │   ├── MinishWoods
        │   ├── CaveOfFlames
        │   ├── WindRuins
        │   └── ...
        ├── Entities
        │   ├── Player
        │   ├── Ennemy
        │   ├── Wall
        │   └── Ground
        ├── Items
        │   ├── PacGumRupee
        │   ├── SuperPacGum
        │   └── SpecialItem
        ├── AI
        │   ├── EnemyBrain
        │   ├── StrategyAI
        │   ├── ChaseAI
        │   ├── ScatterAI
        │   ├── FrightenedAI
        │   └── EatenAI
        └── UI / sprites / input helpers
```

### Module Overview

| Module | Responsibility |
| --- | --- |
| `pacman/main.py` | Program entry point. Loads config and highscores. |
| `pacman/config.py` | Comment-tolerant JSON loading and validation. |
| `pacman/highscores.py` | Highscore loading, validation, insertion, and saving. |
| `pacman/resources.py` | Stable asset path helper. |
| `pacman/game/game.py` | Global pygame resources, loop, display, and game state. |
| `pacman/game/scene_manager.py` | Scene lifecycle and stack management. |
| `pacman/game/scenes/` | Menu, gameplay, pause, game-over, and ending screens. |
| `pacman/game/levels/` | Level themes, maze-to-sprite generation, enemy setup. |
| `pacman/game/entities.py` | Player, enemies, walls, ground, decorations. |
| `pacman/game/items.py` | Collectibles and score items. |
| `pacman/game/ai.py` | Enemy pathfinding and behavior state machine. |
| `pacman/game/input.py` | Keyboard/controller input normalization. |
| `pacman/game/ui.py` | In-game HUD drawing. |
| `pacman/game/sprites.py` | Sprite sheet extraction and text rendering helpers. |

## Features

- Maze generation with the A-Maze-ing package.
- 16 themed levels.
- Pac-gums, super pac-gums, special items, score, lives, and timer.
- Four enemy behavior states: chase, scatter, frightened, eaten.
- Debug panel and visual tracer for enemy AI.
- Title screen, main menu, pause menu, game-over flow, win/ending screens.
- Persistent highscores with name, score, skin color, and cheat flag.
- Controller support with plug/unplug detection.
- Cheat mode and hidden interactions.
- Music and sound effects.
- Strict typing and style checks.

## Project Management

The activity was managed with a Trello board and Git history. A dedicated
project management evidence directory is available here:

[docs/project_management/README.md](docs/project_management/README.md)

It includes:

- project timeline and Gantt view;
- Kanban tracking from the Trello export;
- actual progress compared to the timeline;
- Git activity summary;
- project analysis and associated choices;
- risk analysis and mitigations;
- team organization;
- acceptance test plan;
- blocking points and conflicts;
- raw evidence files.

## Resources

### Main Documentation and Tutorials

- pygame documentation: <https://www.pygame.org/docs/>
- pygame animation discussion/example:
  <https://www.reddit.com/r/pygame/comments/vmioj0/what_is_the_best_way_to_handle_animation_i_mean/>
- pygame maze/collision and `Sprite` class discussion:
  <https://stackoverflow.com/questions/19015150/creating-a-maze-in-python-pygame-but-not-sure-how-to-make-walls>
- pygame input wrapper example: <https://www.pygame.org/wiki/InputWrapper>
- Image resizing with Python/pygame-related workflow:
  <https://blog.pythonlibrary.org/2017/10/12/how-to-resize-a-photo-with-python/>
- Additional Python maze collision guide:
  <https://electronstudio.github.io/pygame-zero-book/chapters/maze.html>
- Link sprite size reference for Minish Cap:
  <https://forum.solarus-games.org/en/index.php?topic=1061.0>
- pygame text/font tutorial:
  <https://medium.com/@amit25173/pygame-fonts-guide-for-beginners-e2ec8bf7671c>
- pygame tutorial playlist:
  <https://www.youtube.com/playlist?list=PLkkm3wcQHjT7gn81Wn-e78cAyhwBW3FIc>
- Wrap-around maze behavior:
  <https://www.youtube.com/watch?v=NzCulpYC0p8>
- Pause menu tutorial:
  <https://youtu.be/cyn8Q_C0KUs?si=TNXVhTTjpWvD61_g>
- Pac-Man ghost AI explanation:
  <https://youtu.be/ataGotQ7ir8?si=Fhl5BzF6l88vB8q8>
- Text input in game:
  <https://www.youtube.com/watch?v=Rvcyf4HsWiw>
- Main menu selection tutorial:
  <https://www.youtube.com/watch?v=bmRFi7-gy5Y&list=PLVFWKkB2K-TnsGDz7xrN27IpCU5I1bery&index=2>
- GBA sprite ripping discussion:
  <https://www.reddit.com/r/romhacking/comments/1c6dsok/hey_how_do_i_rip_sprites_from_a_gba_game/>
- PyInstaller usage for pygame:
  <https://pyinstaller.readthedocs.io/en/stable/usage.html#pygame>

### Tools Used for Assets

- SpriteFusion, used to draw tiles and quickly prototype map ideas:
  <https://www.spritefusion.com/>
- Photopea, used to inspect, cut, and create sprites:
  <https://www.photopea.com/>
- AudioMass, used for audio cutting/editing:
  <https://audiomass.co/>

### Credits

- Sprite rip credits: EternalLight, Sonikku, Whispy, Robbydude, Barrubary,
  Nemu.
- Zelda GBA font by `aztecwarrior28`.
- The FontStruction "Zelda GBA"
  (<https://fontstruct.com/fontstructions/show/1968814>) by `aztecwarrior28`
  is licensed under a Creative Commons Attribution Share Alike license:
  <http://creativecommons.org/licenses/by-sa/3.0/>.
- Additional reference videos:
  - <https://youtu.be/4BURZ5WTIKg?si=wzGxM7gVqZ-tXn_B>
  - <https://youtu.be/MRalNWVSqrc?si=9p0Fzg1_UZ8Q7QwG>
- Project visual reference note: `!bed_defait.png`.

### AI Usage

AI assistance was used as a development support tool, not as a replacement for
implementation ownership. It helped with:

- explaining pygame patterns and debugging approaches;
- reviewing code structure and suggesting refactor priorities;
- generating and refining docstrings;
- helping migrate the codebase toward `mypy --strict`;
- diagnosing packaging attempts with Nuitka and PyInstaller;
- drafting project management documentation from Trello and Git evidence;
- improving README structure and wording.

The actual game behavior, asset integration decisions, level design choices,
and final code ownership remained with the project team.


### Special Thanks

Special thanks to our peers vgiroud (sprites advices and feedback), rboughan (testing and feedback), big thanks to nhairabe(final testing and feedback) and mberraho, jorth, bhanicotte... (the night squad).
