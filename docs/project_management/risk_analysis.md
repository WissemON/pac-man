# Risk Analysis

| Risk | Impact | Probability | Mitigation | Status |
| --- | --- | --- | --- | --- |
| Scope growth from Pac-Man clone to themed adventure game | High | Medium | Prioritize mandatory mechanics first, then add themed levels/endings incrementally. | Mitigated by Trello cards and later refactor. |
| AI behavior complexity and pathfinding regressions | High | Medium | Add debug panel, visual tracer, scatter timer, and path cache diagnostics. | Mitigated by AI debug cards and commits. |
| Large number of level files causing duplication | Medium | High | Move shared logic to level_base.py and enemy_factory.py. | Mitigated by factorization commits. |
| Config/highscore file corruption or invalid values | Medium | Medium | Validate JSON, clamp defaults, validate highscore entries. | Mostly mitigated; save bug fixed late. |
| Controller-specific regressions | Medium | Medium | Normalize joystick input and test plug/unplug at runtime. | Mitigated by input module and controller commits. |
| Packaging/native dependency failures | Medium | High | Test standalone packaging late, keep Makefile run path as reference, switch to PyInstaller when Nuitka failed. | Mitigated by packaging decision. |
| Merge conflicts and branch drift | Medium | Medium | Use Git merges from main/new_improvements and resolve feature branches frequently. | Managed through merge commits. |
