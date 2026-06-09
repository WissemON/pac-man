# Blocking Points and Conflicts

| Blocking point | Observed issue | Resolution / mitigation |
| --- | --- | --- |
| Nuitka standalone segfault | A compiled hello-world binary also crashed with Fedora Python 3.13/Nuitka standalone. | Switched guidance toward PyInstaller and kept evidence out of source tree. |
| Highscore save appeared broken | Game-over scene reset score before saving, so score 0 was dropped from top 10. | Moved score reset to replay/menu transition and validated save_highscores directly. |
| Score/lives reset timing | Some resets happened in endings/game-over instead of scene entry/exit boundaries. | Centralized resets in main menu and removed deprecated ending resets. |
| AI/pathfinding visibility | Enemy movement issues were hard to diagnose without visual feedback. | Added debug panel, visual tracer, and scatter timer. |
| Level duplication | Many level classes repeated the same setup formulas and collision helpers. | Introduced shared Level helpers and factories. |

## Merge / Collaboration Notes

Git history includes several merge commits from `main`, `improvements`, and `new_improvements`. This indicates parallel work and integration steps. No unresolved conflict artifact is kept in the final tree; conflict risk was managed by merging branches and continuing feature-specific fixes.

