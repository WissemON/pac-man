# Acceptance Test Plan

The table below lists the main acceptance areas, the test approach, current status, and evidence source.

| Feature / Requirement | Acceptance test | Status | Evidence |
| --- | --- | --- | --- |
| Project can be installed and run from Makefile | make install / make run | Pass | Makefile card in Trello; Makefile commits on 2026-04-25 and later. |
| JSON config loads with defaults and comment stripping | Run with config.json, malformed/missing values fall back safely | Pass | Config cards in Done; config commits on 2026-04-26, 2026-05-23. |
| Maze renders with walls/ground and level assets | Start game and verify maze display | Pass | Rendering Maze and Making Levels cards in Done. |
| Player movement and wall collisions work | Move in four directions, collide with walls and tunnels | Pass | Player movement card in Done; entities/play_scene churn. |
| Pacgums, super pacgums, and special items score correctly | Collect items and observe score/power-up state | Pass | Adding Pac-Gums card in Done; pacgums commit 069d03a. |
| Enemy AI provides distinct behaviors | Observe chase/scatter/frightened/eaten states and debug panel | Pass | Ghosts Ennemies and Debug panel cards in Done. |
| Main menu, title screen, pause, and game-over flows work | Navigate screens with keyboard/controller | Pass | UI cards in Done; menu/pause/game-over commits. |
| Win/true/weird endings collect player name and skin | Finish levels and validate end screen flow | Pass | Win Screen card in Done; ending commits on 2026-05-21. |
| Highscores persist after a valid top-10 score | Insert score, save JSON, reload menu | Fixed/Pass | Save bug fixed in commit 7d3eecc. |
| Controller plug/unplug works during runtime | Connect/disconnect controller and observe SFX/status | Pass | Controller commits on 2026-05-26 and 2026-06-04. |
| Code quality checks pass | flake8 and mypy --strict | Pass | mypy strict commit 8799efa; docstrings commit e1e8cc3. |
| Standalone distribution path investigated | Nuitka attempted, PyInstaller selected as practical route | Mitigated | Packaging investigation documented in blocking points. |

## Regression Checks Used During Final Hardening

- `flake8 .`
- `mypy . --strict`
- `python -m compileall pacman`
- Manual gameplay checks through `make run`
- Packaging smoke test with PyInstaller `onedir`
