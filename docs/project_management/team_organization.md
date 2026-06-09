# Team Organization

The Trello export lists two board members. Git history contains several aliases; the mapping below is inferred from Trello names and commit aliases.

| Person / aliases | Observed responsibilities | Evidence |
| --- | --- | --- |
| Wissem Boussaha / wboussah / Wissem | Gameplay screens, assets integration, level themes, endings, polish, refactor, quality/doc pass. | Trello member + Git aliases inferred from commits. |
| Sid IZEM / Sid Ahmed / sizem | Configuration, Makefile/package setup, AI, enemy logic, debug tooling, controller/input work, integrations. | Trello member + Git aliases inferred from commits. |

## Decision Process

- Trello cards were used to define and track feature areas.
- Git commits and merges show incremental integration from feature branches into the main branch.
- Technical decisions were made by testing implementation feasibility: for example, AI debug tooling was added after pathfinding became difficult to inspect, and PyInstaller was preferred after Nuitka standalone failed locally.

## Issue Handling

- Bugs were fixed through focused commits, for example debug pathfinding, menu/pause resets, cheat mode, and the highscore save bug.
- Larger duplication issues were handled by refactoring common level logic into `level_base.py` and enemy spawning into `enemy_factory.py`.

## Git Author Alias Evidence

| Author alias | Commits |
| --- | --- |
| wboussah | 37 |
| Sid Ahmed | 26 |
| sizem | 8 |
| Sid IZEM | 3 |
| Wissem | 1 |

