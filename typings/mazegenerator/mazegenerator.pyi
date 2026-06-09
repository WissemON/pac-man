class MazeGenerator:
    maze: list[list[int]]

    def __init__(
        self,
        size: tuple[int, int],
        seed: int | None = None,
    ) -> None: ...
