from enum import Enum
import random
from heapq import heappush, heappop
from collections import deque
from dataclasses import dataclass
from typing import Dict, Optional, TypedDict


class State(Enum):
    """Enumerate the supported enemy AI states."""
    CHASE = "CHASE"
    SCATTER = "SCATTER"
    FRIGHTENED = "FRIGHT"
    EATEN = "EATEN"


class AIDebugEvent(TypedDict):
    """Describe one raw AI debug event."""
    frame: int
    actor: str
    message: str


class AIDebugRow(AIDebugEvent):
    """Describe one render-ready AI debug row."""
    state: str
    color: tuple[int, int, int]


class AIDebugTrace:
    """Collect AI events for in-game and terminal debugging."""

    def __init__(self, enabled: bool = True, max_events: int = 300) -> None:
        """Initialize the AI debug trace.

        Args:
            enabled: Whether debug collection starts enabled.
            max_events: Maximum number of debug events to retain.
        """
        self.enabled = enabled
        self.frame = 0
        self._events: deque[AIDebugEvent] = deque(maxlen=max_events)
        self._last_dump_index = 0

    def begin_frame(self) -> None:
        """Advance the AI debug frame counter."""
        self.frame += 1

    def clear(self) -> None:
        """Remove all buffered AI debug events."""
        self._events.clear()
        self._last_dump_index = 0

    def record(self, actor: str, message: str) -> None:
        """Append one AI debug event.

        Args:
            actor: Identifier of the AI actor.
            message: Debug message to record or inspect.
        """
        if not self.enabled:
            return
        self._events.append({
            "frame": self.frame,
            "actor": actor,
            "message": message,
        })

    def get_lines(self, limit: int = 12) -> list[str]:
        """Return formatted AI debug lines.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            Formatted debug lines.
        """
        if limit <= 0:
            return []
        recent_events = list(self._events)[-limit:]
        return [self.format_event(event) for event in recent_events]

    def get_events(self, limit: int = 12) -> list[AIDebugEvent]:
        """Return recent raw AI debug events.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            Recent debug events.
        """
        if limit <= 0:
            return []
        return list(self._events)[-limit:]

    @staticmethod
    def format_event(event: AIDebugEvent) -> str:
        """Format one AI debug event for display.

        Args:
            event: Event data to handle.

        Returns:
            Formatted debug line.
        """
        return (
            f"[{int(event['frame']):05d}] "
            f"{event['actor']}: {event['message']}"
        )

    @staticmethod
    def state_from_message(message: str) -> State | None:
        """Infer an AI state from a debug message.

        Args:
            message: Debug message to record or inspect.

        Returns:
            Inferred state, or None when no state is found.
        """
        lowered = message.lower()
        if "fright" in lowered:
            return State.FRIGHTENED
        if "scatter" in lowered:
            return State.SCATTER
        if "chase" in lowered:
            return State.CHASE
        if "eaten" in lowered:
            return State.EATEN
        return None

    @staticmethod
    def color_for_state(state: State | None) -> tuple[int, int, int]:
        """Choose a display color for an AI state.

        Args:
            state: AI state to inspect or apply.

        Returns:
            RGB color tuple for display.
        """
        palette = {
            State.CHASE: (90, 210, 255),
            State.SCATTER: (255, 200, 90),
            State.FRIGHTENED: (140, 120, 255),
            State.EATEN: (180, 180, 180),
        }
        if state is None:
            return (230, 255, 180)
        return palette[state]

    def render_rows(
        self,
        limit: int = 12,
    ) -> list[AIDebugRow]:
        """Build render-ready AI debug rows.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            Rows ready for debug rendering.
        """
        rows: list[AIDebugRow] = []
        for event in self.get_events(limit):
            message = str(event["message"])
            state = self.state_from_message(message)
            rows.append({
                "frame": event["frame"],
                "actor": event["actor"],
                "message": message,
                "state": state.value if state else "",
                "color": self.color_for_state(state),
            })
        return rows

    def dump_to_console(self, limit: int = 12) -> list[str]:
        """Print new AI debug events and return their lines.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            Formatted lines that were printed.
        """
        if not self.enabled or limit <= 0:
            return []

        events = list(self._events)
        new_events = events[self._last_dump_index:]
        if not new_events:
            return []

        new_lines = new_events[-limit:]
        for line in new_lines:
            print(self.format_event(line))

        self._last_dump_index = len(events)
        return [self.format_event(line) for line in new_lines]


class EnemyStateController:
    """Manage timed transitions between enemy AI states."""

    def __init__(self, default_state: State,
                 durations_map: dict[str, float] | None = None) -> None:
        """Initialize the enemy state controller.

        Args:
            default_state: Initial AI state for the behavior.
            durations_map: AI duration overrides for the enemies.
        """
        self.default_state = default_state
        self.state_timer = 0.0
        self.enable_cycle = default_state in (State.SCATTER, State.CHASE)
        self.scatter_duration = 6.0
        self.chase_duration = 7.0
        self.frightened_duration = 6.0
        self.eaten_duration = 3.0
        self._apply_durations(durations_map)

    def _apply_durations(self, durations_map: dict[str, float] | None) -> None:
        """Apply configured state durations to the controller.

        Args:
            durations_map: AI duration overrides for the enemies.
        """
        if not isinstance(durations_map, dict):
            return

        scatter = durations_map.get("scatter_duration")
        chase = durations_map.get("chase_duration")
        frightened = durations_map.get("frightened_duration")
        eaten = durations_map.get("eaten_duration")

        try:
            if scatter is not None:
                self.scatter_duration = float(scatter)
            if chase is not None:
                self.chase_duration = float(chase)
            if frightened is not None:
                self.frightened_duration = float(frightened)
            if eaten is not None:
                self.eaten_duration = float(eaten)
        except (TypeError, ValueError):
            # Keep defaults if config values are malformed.
            return

    def next_state(self, current_state: State,
                   player_powered: bool,
                   delta_seconds: float) -> State:
        """Choose the next enemy AI state.

        Args:
            current_state: Current AI state before transition.
            player_powered: Whether the player is currently powered up.
            delta_seconds: Elapsed frame time in seconds.

        Returns:
            Next AI state to use.
        """
        if current_state == State.EATEN:
            self.state_timer += delta_seconds
            if self.state_timer >= self.eaten_duration:
                self.state_timer = 0.0
                return self.default_state
            return State.EATEN

        # FRIGHTENED has priority while powered, but remains time-boxed.
        if player_powered and current_state != State.FRIGHTENED:
            self.state_timer = 0.0
            return State.FRIGHTENED

        if current_state == State.FRIGHTENED:
            self.state_timer += delta_seconds
            if (not player_powered or
                    self.state_timer >= self.frightened_duration):
                self.state_timer = 0.0
                return self.default_state
            return State.FRIGHTENED

        if not self.enable_cycle:
            return self.default_state

        if current_state not in (State.SCATTER, State.CHASE):
            self.state_timer = 0.0
            return self.default_state

        self.state_timer += delta_seconds
        if (current_state == State.SCATTER and
                self.state_timer >= self.scatter_duration):
            self.state_timer = 0.0
            return State.CHASE

        if (current_state == State.CHASE and
                self.state_timer >= self.chase_duration):
            self.state_timer = 0.0
            return State.SCATTER

        return current_state


class StrategyAI:
    """Provide shared pathfinding behavior for enemy strategies."""
    def __init__(self, grid: list[list[int]], position: tuple[int, int],
                 target_position: tuple[int, int],
                 default_state: State = State.CHASE,
                 debug_trace: AIDebugTrace | None = None,
                 actor_name: str = "enemy") -> None:
        """Initialize the strategy AI.

        Args:
            grid: Maze grid used for navigation.
            position: Current grid position.
            target_position: Target grid position.
            default_state: Initial AI state for the behavior.
            debug_trace: Optional debug trace collector.
            actor_name: Name used for debug trace entries.
        """
        self.grid = grid
        if grid:
            self.str_maze = self.stringify_maze(grid)
        self.scatter_target = target_position
        self.current_target = target_position
        self.current_position = position
        self.opp_directions = {"UP": "DOWN",
                               "LEFT": "RIGHT", "DOWN": "UP", "RIGHT": "LEFT"}
        initial_moves = self.next_move()
        self.current_direction: str = random.choice(
            initial_moves) if initial_moves else "UP"
        self._default_state: State = default_state
        self._state: State = default_state
        self._previous_state: State = default_state
        self.state_timer: int = 0
        self.edible_timer: int = 0
        self.debug_trace = debug_trace
        self.actor_name = actor_name

    def is_in_bounds(self, position: tuple[int, int]) -> bool:
        """Check whether a grid position is inside the maze.

        Args:
            position: Current grid position.

        Returns:
            True when the position is inside the maze.
        """
        x, y = position
        if y < 0 or y >= len(self.str_maze):
            return False
        if x < 0 or x >= len(self.str_maze[y]):
            return False
        return True

    @property
    def position(self) -> tuple[int, int]:
        """Perform position behavior.

        Returns:
            Current grid position.
        """
        return self.current_position

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        """Perform position behavior.

        Args:
            value: Raw value to normalize or apply.
        """
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError("Position must be a tuple of (x, y)")
        self.current_position = value

    @property
    def target(self) -> tuple[int, int]:
        """Perform target behavior.

        Returns:
            Current target grid position.
        """
        return self.current_target

    @target.setter
    def target(self, value: tuple[int, int]) -> None:
        """Perform target behavior.

        Args:
            value: Raw value to normalize or apply.
        """
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError("Target must be a tuple of (x, y)")
        self.current_target = value

    @staticmethod
    def distance2_to_target(pos1: tuple[int, int],
                            pos2: tuple[int, int]) -> float:
        """Perform distance2 to target behavior.

        Args:
            pos1: First grid position.
            pos2: Second grid position.

        Returns:
            Squared distance to the current target.
        """
        return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2

    @property
    def state(self) -> State:
        """Perform state behavior.

        Returns:
            Current AI state.
        """
        return self._state

    @state.setter
    def state(self, value: State) -> None:
        """Perform state behavior.

        Args:
            value: Raw value to normalize or apply.
        """
        if not isinstance(value, State):
            raise ValueError(
                "State must be an instance of State enum")
        previous_state = self._state
        # Central point for gameplay-driven strategy changes.
        # This covers item pickup, player collision, respawn, and similar
        # cases.
        self._state = value
        self._previous_state = previous_state
        if value == State.SCATTER and previous_state != State.SCATTER:
            # Return to the original corner when entering SCATTER again.
            self.current_target = self.scatter_target

    @staticmethod
    def stringify_maze(grid: list[list[int]]) -> list[list[str]]:
        """Convert an integer maze grid into pathfinding tokens.

        Args:
            grid: Maze grid used for navigation.

        Returns:
            Maze converted to pathfinding tokens.
        """
        walls = ['0', 'N', 'E', 'NE', 'S',
                 'NS', 'ES', 'NES', 'W', 'NW',
                 'EW', 'NEW', 'SW', 'NSW', 'ESW', 'NESW']
        all_directions = ['N', 'W', 'S', 'E']
        grid_directions = []
        for row in grid:
            line = []
            for cell in row:
                blocked_walls = set(walls[cell])
                # Keep the directions that are not blocked by a wall.
                s = ''.join(direction for direction in all_directions
                            if direction not in blocked_walls)
                line.append(s)
            grid_directions.append(line)
        return grid_directions

    def next_move(self) -> list[str]:
        """Choose the next direction toward the current target.

        Returns:
            Direction chosen for the next move.
        """
        if not self.is_in_bounds(self.position):
            return []
        directions = self.str_maze[self.position[1]][self.position[0]]
        possible_moves = []
        for d in directions:
            if d == 'N':
                possible_moves.append("UP")
            elif d == 'W':
                possible_moves.append("LEFT")
            elif d == 'S':
                possible_moves.append("DOWN")
            elif d == 'E':
                possible_moves.append("RIGHT")
        filtered_moves = []
        for move in possible_moves:
            if self.is_in_bounds(self.get_new_position(move)):
                filtered_moves.append(move)
        return filtered_moves

    def get_new_position(self, move: str) -> tuple[int, int]:
        """Return the grid position reached by one move.

        Args:
            move: Direction name to evaluate.

        Returns:
            Grid position after the move.
        """
        x, y = self.current_position
        if move == "UP":
            return (x, y - 1)
        elif move == "LEFT":
            return (x - 1, y)
        elif move == "DOWN":
            return (x, y + 1)
        elif move == "RIGHT":
            return (x + 1, y)
        return self.current_position

    def manhattan_distance(self, pos1: tuple[int, int],
                           pos2: tuple[int, int]) -> int:
        """Compute Manhattan distance between two grid positions.

        Args:
            pos1: First grid position.
            pos2: Second grid position.

        Returns:
            Manhattan distance between positions.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_neighbors(self, pos: tuple[int, int])\
            -> list[tuple[tuple[int, int], str]]:
        """Return valid neighboring maze positions and directions.

        Args:
            pos: Grid position to inspect.

        Returns:
            Walkable neighboring positions and directions.
        """
        if not self.is_in_bounds(pos):
            return []

        neighbors = []
        x, y = pos
        directions_str = self.str_maze[y][x]

        for d in directions_str:
            if d == 'N':
                neighbor = (x, y - 1)
                move = "UP"
            elif d == 'W':
                neighbor = (x - 1, y)
                move = "LEFT"
            elif d == 'S':
                neighbor = (x, y + 1)
                move = "DOWN"
            elif d == 'E':
                neighbor = (x + 1, y)
                move = "RIGHT"
            else:
                continue

            if self.is_in_bounds(neighbor):
                neighbors.append((neighbor, move))

        return neighbors

    def astar_path(self, start: tuple[int, int],
                   goal: tuple[int, int]) -> list[str]:
        """Find a shortest path through the maze with A*.

        Args:
            start: Starting grid position.
            goal: Goal grid position.

        Returns:
            Path from start to goal, or an empty path.
        """
        if start == goal:
            return []

        # Priority queue: (f_score, counter, position)
        counter = 0
        open_set: list[tuple[int, int, tuple[int, int]]] = []
        heappush(open_set, (0, counter, start))
        counter += 1

        # Track visited and costs
        came_from: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
        g_score = {start: 0}

        visited = set()

        while open_set:
            _, _, current = heappop(open_set)

            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                # Reconstruct path
                path = []
                pos = current
                while pos in came_from:
                    prev_pos, move = came_from[pos]
                    path.append(move)
                    pos = prev_pos
                return path[::-1]

            # Explore neighbors using get_neighbors
            neighbors = self.get_neighbors(current)

            for neighbor, move in neighbors:
                if neighbor in visited:
                    continue

                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = (current, move)
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + \
                        self.manhattan_distance(neighbor, goal)
                    heappush(open_set, (f_score, counter, neighbor))
                    counter += 1

        return []  # No path found

    def default_pathfinding(self, target_position: tuple[int, int]) -> str:
        # Use A* pathfinding to move towards the target
        """Choose a pathfinding direction toward a target.

        Args:
            target_position: Target grid position.

        Returns:
            Direction chosen by pathfinding.
        """
        path = self.astar_path(self.current_position, target_position)
        if path:
            return path[0]
        # Fallback to local greedy if no path found
        possible_moves = self.next_move()
        if not possible_moves:
            return self.current_direction
        # Avoid an immediate U-turn unless it is the only available option.
        reverse_dir = self.opp_directions.get(self.current_direction)
        non_reverse_moves = [m for m in possible_moves if m != reverse_dir]
        if non_reverse_moves:
            possible_moves = non_reverse_moves
        # Choose move that reduces distance
        best_move = possible_moves[0]
        best_distance = self.distance2_to_target(
            self.get_new_position(best_move), target_position)
        for move in possible_moves[1:]:
            new_pos = self.get_new_position(move)
            dist = self.distance2_to_target(new_pos, target_position)
            if dist < best_distance:
                best_distance = dist
                best_move = move
        return best_move

    def chase_decision(self, target_position: tuple[int, int]) -> str:
        # Use A* pathfinding to move towards the target
        """Choose a direction for chase behavior.

        Args:
            target_position: Target grid position.

        Returns:
            Direction name selected by the behavior.
        """
        return self.default_pathfinding(target_position)

    def scatter_decision(self, target_position: tuple[int, int]) -> str:
        # SCATTER alternates between the start corner and the maze center.
        """Choose a direction for scatter behavior.

        Args:
            target_position: Target grid position.

        Returns:
            Direction name selected by the behavior.
        """
        center_position = (len(self.str_maze[0]) // 2, len(self.str_maze) // 2)

        if self.current_target not in (self.scatter_target, center_position):
            self.current_target = self.scatter_target

        # Treat the target as reached when it is very close.
        # Manhattan distance <= 2 absorbs small alignment imprecision.
        distance_to_target = self.manhattan_distance(
            self.current_position, self.current_target)
        if distance_to_target <= 2:
            if self.current_target == self.scatter_target:
                self.current_target = center_position
            else:
                self.current_target = self.scatter_target

        return self.default_pathfinding(self.current_target)

    def frightened_decision(self, target_position: tuple[int, int]) -> str:
        """Choose a direction for frightened behavior.

        Args:
            target_position: Target grid position.

        Returns:
            Direction name selected by the behavior.
        """
        possible_moves = self.next_move()
        if not possible_moves:
            return self.current_direction
        return random.choice(possible_moves)

    def eaten_decision(self, target_position: tuple[int, int]) -> str:
        # Use A* pathfinding to move towards the respawn point
        """Choose a direction for eaten behavior.

        Args:
            target_position: Target grid position.

        Returns:
            Direction name selected by the behavior.
        """
        return self.default_pathfinding(target_position)

    def decision(self, target_position: tuple[int, int]) -> str:
        """Choose the next movement direction.

        Args:
            target_position: Target grid position.

        Returns:
            Direction chosen by the behavior.
        """
        if self.current_position == target_position:
            return self.current_direction  # No move needed
        if self.state == State.CHASE:
            return self.chase_decision(target_position)
        elif self.state == State.SCATTER:
            return self.scatter_decision(target_position)
        elif self.state == State.FRIGHTENED:
            return self.frightened_decision(target_position)
        elif self.state == State.EATEN:
            return self.eaten_decision(target_position)
        else:
            return self.current_direction

    def change_position(self, move: str) -> None:
        """Update the strategy position from a movement direction.

        Args:
            move: Direction name to evaluate.
        """
        legal_moves = self.next_move()
        if move not in legal_moves:
            return
        self.position = self.get_new_position(move)
        self.current_direction = move

    def move(self, target_position: tuple[int, int]) -> bool:
        """Move the sprite according to its current direction.

        Args:
            target_position: Target grid position.

        Returns:
            True when the requested condition is met.
        """
        move = self.decision(target_position)
        old_position = self.current_position
        self.change_position(move)
        if self.current_position == old_position:
            if self.debug_trace:
                self.debug_trace.record(
                    self.actor_name,
                    f"blocked at {self.current_position} (requested {move})",
                )
            return False
        if self.debug_trace:
            self.debug_trace.record(
                self.actor_name,
                f"moved {move} to {self.current_position}",
            )
        return True


class ScatterAI(StrategyAI):
    """Implement scatter behavior that alternates between targets."""

    def __init__(self, grid: list[list[int]], position: tuple[int, int],
                 scatter_corner: tuple[int, int],
                 debug_trace: AIDebugTrace | None = None,
                 actor_name: str = "enemy") -> None:
        """Initialize the scatter AI.

        Args:
            grid: Maze grid used for navigation.
            position: Current grid position.
            scatter_corner: Scatter target corner for the enemy.
            debug_trace: Optional debug trace collector.
            actor_name: Name used for debug trace entries.
        """
        super().__init__(
            grid,
            position,
            scatter_corner,
            State.SCATTER,
            debug_trace=debug_trace,
            actor_name=actor_name,
        )
        self.scatter_corner = scatter_corner
        self.center_position = self._find_walkable_center()
        self.current_target = scatter_corner
        self._state = State.SCATTER

    def _find_walkable_center(self) -> tuple[int, int]:
        """Find a walkable maze cell near the grid center.

        Returns:
            Walkable grid coordinate near the maze center.
        """
        center_x = len(self.str_maze[0]) // 2
        center_y = len(self.str_maze) // 2
        walkable_cells = [
            (x, y)
            for y, row in enumerate(self.str_maze)
            for x, directions in enumerate(row)
            if directions
        ]
        return min(
            walkable_cells,
            key=lambda cell: self.distance2_to_target(
                cell, (center_x, center_y))
        )

    def scatter_decision(self, target_position: tuple[int, int]) -> str:
        """Choose a direction for scatter behavior.

        Args:
            target_position: Target grid position.

        Returns:
            Direction name selected by the behavior.
        """
        if self.current_target not in (self.scatter_corner,
                                       self.center_position):
            self.current_target = self.scatter_corner

        # Change target only after the current one is reached exactly.
        if self.current_position == self.current_target:
            if self.current_target == self.scatter_corner:
                self.current_target = self.center_position
            else:
                self.current_target = self.scatter_corner

        return self.default_pathfinding(self.current_target)

    def decision(self, target_position: tuple[int, int]) -> str:
        """Choose the next movement direction.

        Args:
            target_position: Target grid position.

        Returns:
            Direction chosen by the behavior.
        """
        return self.scatter_decision(target_position)


class ChaseAI(StrategyAI):
    """Implement the enemy chase behavior."""

    def decision(self, target_position: tuple[int, int]) -> str:
        """Choose the next movement direction.

        Args:
            target_position: Target grid position.

        Returns:
            Direction chosen by the behavior.
        """
        return self.default_pathfinding(target_position)


class FrightenedAI(StrategyAI):
    """Implement frightened enemy movement behavior."""

    def decision(self, target_position: tuple[int, int]) -> str:
        """Choose the next movement direction.

        Args:
            target_position: Target grid position.

        Returns:
            Direction chosen by the behavior.
        """
        possible_moves = self.next_move()
        if not possible_moves:
            return self.current_direction

        reverse_dir = self.opp_directions.get(self.current_direction)
        non_reverse_moves = [m for m in possible_moves if m != reverse_dir]
        if non_reverse_moves:
            possible_moves = non_reverse_moves
        return random.choice(possible_moves)


class EatenAI(StrategyAI):
    """Implement respawn-seeking behavior for eaten enemies."""

    def __init__(self, grid: list[list[int]], position: tuple[int, int],
                 target_position: tuple[int, int],
                 default_state: State = State.EATEN,
                 respawn_position: tuple[int, int] | None = None,
                 debug_trace: AIDebugTrace | None = None,
                 actor_name: str = "enemy") -> None:
        """Initialize the eaten AI.

        Args:
            grid: Maze grid used for navigation.
            position: Current grid position.
            target_position: Target grid position.
            default_state: Initial AI state for the behavior.
            respawn_position: Grid position used as the respawn target.
            debug_trace: Optional debug trace collector.
            actor_name: Name used for debug trace entries.
        """
        super().__init__(
            grid,
            position,
            target_position,
            default_state,
            debug_trace=debug_trace,
            actor_name=actor_name,
        )
        self.respawn_position = respawn_position or position

    def decision(self, target_position: tuple[int, int]) -> str:
        """Choose the next movement direction.

        Args:
            target_position: Target grid position.

        Returns:
            Direction chosen by the behavior.
        """
        return self.default_pathfinding(self.respawn_position)


class EnemyBrain:
    """Route enemy decisions through the active AI state."""

    def __init__(
        self,
        grid: list[list[int]],
        position: tuple[int, int],
        scatter_corner: tuple[int, int],
        default_state: State = State.SCATTER,
        debug_trace: AIDebugTrace | None = None,
        enemy_id: str = "enemy",
        durations_map: dict[str, float] | None = None,
    ) -> None:
        """Initialize the enemy brain.

        Args:
            grid: Maze grid used for navigation.
            position: Current grid position.
            scatter_corner: Scatter target corner for the enemy.
            default_state: Initial AI state for the behavior.
            debug_trace: Optional debug trace collector.
            enemy_id: Debug identifier for the enemy.
            durations_map: AI duration overrides for the enemies.
        """
        self._default_state = default_state
        self._state = default_state
        self.debug_trace = debug_trace
        self.enemy_id = enemy_id
        self.state_controller = EnemyStateController(
            default_state=default_state,
            durations_map=durations_map,
        )

        self.behaviors = {
            State.CHASE: ChaseAI(grid, position, scatter_corner,
                                 State.CHASE,
                                 debug_trace=debug_trace,
                                 actor_name=enemy_id),
            State.SCATTER: ScatterAI(
                grid,
                position,
                scatter_corner,
                debug_trace=debug_trace,
                actor_name=enemy_id,
            ),
            State.FRIGHTENED: FrightenedAI(
                grid,
                position,
                scatter_corner,
                State.FRIGHTENED,
                debug_trace=debug_trace,
                actor_name=enemy_id,
            ),
            State.EATEN: EatenAI(
                grid,
                position,
                scatter_corner,
                State.EATEN,
                respawn_position=scatter_corner,
                debug_trace=debug_trace,
                actor_name=enemy_id,
            ),
        }

        self.current_position = position
        self.current_direction = self.behaviors[self._state].current_direction
        self.current_target = self.behaviors[self._state].current_target
        self.opp_directions = self.behaviors[self._state].opp_directions
        self._scatter_round_index = 0
        self._scatter_round_elapsed = 0.0
        self._scatter_round_last_total: float | None = None
        self._scatter_round_phase: str | None = None
        # If we start already in SCATTER, begin tracking the round immediately
        if self._state == State.SCATTER:
            self._start_scatter_round_tracking()

    def trace(self, message: str) -> None:
        """Record one debug message for this enemy.

        Args:
            message: Debug message to record or inspect.
        """
        if self.debug_trace:
            self.debug_trace.record(self.enemy_id, message)

    def clear_scatter_round_tracking(self) -> None:
        """Reset scatter round tracking state."""
        self._scatter_round_index = 0
        self._scatter_round_elapsed = 0.0
        self._scatter_round_phase = None

    def scatter_round_elapsed_text(self) -> str:
        """Return elapsed scatter round time for display.

        Returns:
            Elapsed scatter time formatted for display.
        """
        if self._state == State.SCATTER and self._scatter_round_phase:
            return f"{self._scatter_round_elapsed:.2f}s"
        return "-"

    def scatter_round_last_total_text(self) -> str:
        """Return previous scatter round time for display.

        Returns:
            Previous scatter total formatted for display.
        """
        if self._scatter_round_last_total is not None:
            return f"{self._scatter_round_last_total:.2f}s"
        return "-"

    def scatter_round_summary(self) -> str:
        """Return a compact scatter round summary.

        Returns:
            Compact scatter timing summary.
        """
        return (
            f"{self.scatter_round_elapsed_text()} "
            f"({self.scatter_round_last_total_text()})"
        )

    def _start_scatter_round_tracking(self) -> None:
        """Start tracking a scatter round."""
        self._scatter_round_index = 1
        self._scatter_round_elapsed = 0.0
        self._scatter_round_phase = "to_center"

        scatter_behavior = self.behaviors.get(State.SCATTER)
        if isinstance(scatter_behavior, ScatterAI):
            self.trace(
                f"scatter_round#{self._scatter_round_index} start "
                f"origin={scatter_behavior.scatter_corner} "
                f"center={scatter_behavior.center_position}"
            )

    def _advance_scatter_round_timer(self, delta_seconds: float) -> None:
        """Advance the scatter round timer.

        Args:
            delta_seconds: Elapsed frame time in seconds.
        """
        if self._state == State.SCATTER and self._scatter_round_phase:
            self._scatter_round_elapsed += delta_seconds

    def _update_scatter_round_tracking(self, behavior: StrategyAI) -> None:
        """Update scatter round phase tracking.

        Args:
            behavior: Strategy behavior to synchronize.
        """
        if self._state != State.SCATTER:
            return
        if not isinstance(behavior, ScatterAI):
            return
        if self._scatter_round_phase == "to_center":
            if (behavior.current_position == behavior.center_position and
                    behavior.current_target == behavior.scatter_corner):
                self.trace(
                    f"scatter_round#{self._scatter_round_index} center "
                    f"elapsed={self._scatter_round_elapsed:.2f}s "
                    f"pos={behavior.current_position}"
                )
                self._scatter_round_phase = "to_corner"
        elif self._scatter_round_phase == "to_corner":
            if (behavior.current_position == behavior.scatter_corner and
                    behavior.current_target == behavior.center_position):
                total = self._scatter_round_elapsed
                self._scatter_round_last_total = total
                self.trace(
                    f"scatter_round#{self._scatter_round_index} complete "
                    f"total={total:.2f}s "
                    f"corner={behavior.current_position}"
                )
                # Also emit a concise terminal-friendly trace for quick reading
                self.trace(f"scatter_round_total={total:.2f}s")
                self._scatter_round_index += 1
                self._scatter_round_elapsed = 0.0
                self._scatter_round_phase = "to_center"

    @property
    def state(self) -> State:
        """Perform state behavior.

        Returns:
            Current AI state.
        """
        return self._state

    @state.setter
    def state(self, value: State) -> None:
        """Perform state behavior.

        Args:
            value: Raw value to normalize or apply.
        """
        if not isinstance(value, State):
            raise ValueError("State must be an instance of State enum")
        self._state = value

    @property
    def position(self) -> tuple[int, int]:
        """Perform position behavior.

        Returns:
            Current grid position.
        """
        return self.current_position

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        """Perform position behavior.

        Args:
            value: Raw value to normalize or apply.
        """
        self.current_position = value
        for behavior in self.behaviors.values():
            behavior.position = value

    def _sync_behavior(self, behavior: StrategyAI) -> None:
        """Copy shared state into the active behavior.

        Args:
            behavior: Strategy behavior to synchronize.
        """
        behavior.position = self.current_position
        behavior.current_direction = self.current_direction
        behavior.current_target = self.current_target
        behavior.state = self._state

    def _copy_behavior(self, behavior: StrategyAI) -> None:
        """Copy state between two behavior strategies.

        Args:
            behavior: Strategy behavior to synchronize.
        """
        self.current_position = behavior.position
        self.current_direction = behavior.current_direction
        self.current_target = behavior.current_target

    def transition_state(self, player_powered: bool,
                         delta_seconds: float) -> bool:
        """Switch the enemy brain to a new AI state.

        Args:
            player_powered: Whether the player is currently powered up.
            delta_seconds: Elapsed frame time in seconds.

        Returns:
            True when the requested condition is met.
        """
        next_state = self.state_controller.next_state(
            current_state=self._state,
            player_powered=player_powered,
            delta_seconds=delta_seconds,
        )
        if next_state == self._state:
            self._advance_scatter_round_timer(delta_seconds)
            return False
        previous_state = self._state
        self._state = next_state
        self._previous_state = previous_state
        self.trace(f"state {previous_state.value} -> {next_state.value}")
        if next_state == State.SCATTER:
            self._start_scatter_round_tracking()
        else:
            self.clear_scatter_round_tracking()
        return True

    def decision(self, target_position: tuple[int, int]) -> str:
        """Choose the next movement direction.

        Args:
            target_position: Target grid position.

        Returns:
            Direction chosen by the behavior.
        """
        behavior = self.behaviors[self._state]
        self._sync_behavior(behavior)
        move = behavior.decision(target_position)
        self._copy_behavior(behavior)
        self._update_scatter_round_tracking(behavior)
        self.trace(
            f"decision={move} target={target_position}"
        )
        # self.trace(
        #     f"decision={move} state={self._state.value} "
        #     f"pos={self.current_position} target={target_position}"
        # )
        return move

    def change_position(self, move: str) -> None:
        """Update the strategy position from a movement direction.

        Args:
            move: Direction name to evaluate.
        """
        behavior = self.behaviors[self._state]
        self._sync_behavior(behavior)
        before = behavior.position
        behavior.change_position(move)
        self._copy_behavior(behavior)
        if self.current_position == before:
            self.trace(f"blocked move={move} at {self.current_position}")
            return
        self.trace(f"move={move} -> {self.current_position}")

    @staticmethod
    def _offset_in_direction(pos: tuple[int, int], direction: Optional[str],
                             n: int) -> tuple[int, int]:
        """Offset a grid position in a direction.

        Args:
            pos: Grid position to inspect.
            direction: Movement direction to evaluate.
            n: Number of cells to offset.

        Returns:
            Offset grid position.
        """
        if not direction:
            return pos
        x, y = pos
        if direction == 'UP':
            return (x, y - n)
        if direction == 'DOWN':
            return (x, y + n)
        if direction == 'LEFT':
            return (x - n, y)
        if direction == 'RIGHT':
            return (x + n, y)
        return pos

    def compute_target(self, context: 'ChaseContext') -> tuple[int, int]:
        """Compute the chase target for an enemy.

        Args:
            context: Chase context used to compute the target.

        Returns:
            Target grid position for chase behavior.
        """
        etype = context.enemy_type.lower()
        player = context.player_grid
        # Default return player
        target = player

        if etype == 'blinky':
            target = player

        elif etype == 'pinky':
            target = self._offset_in_direction(
                player, context.player_direction, 4)

        elif etype == 'inky':
            p_ahead = self._offset_in_direction(
                player, context.player_direction, 2)
            # try to find blinky in provided dict (case-insensitive)
            blinky_pos = None
            for k, v in context.all_enemies_grid.items():
                if str(k).lower().startswith('blinky')\
                        or str(k).lower().startswith('b'):
                    blinky_pos = v
                    break
            if blinky_pos is None:
                # fallback to player itself
                target = p_ahead
            else:
                vec = _vec_sub(blinky_pos, player)
                target = _vec_add(p_ahead, vec)

        elif etype == 'clyde':
            # If far from player (>8 tiles) chase
            # otherwise go to scatter corner
            dist = abs(context.enemy_grid[0] - player[0]) + \
                abs(context.enemy_grid[1] - player[1])
            if dist > 8:
                target = player
            else:
                target = context.enemy_scatter_corner

        # Clamp to maze bounds if possible
        try:
            maze = self.behaviors[State.CHASE].str_maze
            target = _clamp_to_bounds(target, maze)
        except Exception:
            pass

        # self.trace(f"compute_target {context} -> {target}")
        return target


@dataclass
class ChaseContext:
    """Bundle player and enemy positions for chase targeting."""
    enemy_type: str
    player_grid: tuple[int, int]
    player_direction: Optional[str]
    enemy_grid: tuple[int, int]
    enemy_scatter_corner: tuple[int, int]
    all_enemies_grid: Dict[str, tuple[int, int]]

    def __repr__(self) -> str:  # simple repr for debug traces
        """Return a developer-friendly chase context string.

        Returns:
            String representation for debugging.
        """
        return (
            f"ChaseContext(type={self.enemy_type}, player={self.player_grid}, "
            f"dir={self.player_direction}, enemy={self.enemy_grid})"
        )


def _clamp_to_bounds(
    pos: tuple[int, int],
    maze: list[list[str]],
) -> tuple[int, int]:
    """Clamp a grid coordinate inside the maze bounds.

    Args:
        pos: Grid position to inspect.
        maze: Tokenized maze used by pathfinding.

    Returns:
        Clamped grid coordinate.
    """
    x, y = pos
    max_y = len(maze) - 1
    max_x = len(maze[0]) - 1 if maze else x
    x = max(0, min(x, max_x))
    y = max(0, min(y, max_y))
    return x, y


def _vec_sub(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    """Subtract two grid vectors.

    Args:
        a: First grid vector.
        b: Second grid vector.

    Returns:
        Vector difference.
    """
    return (a[0] - b[0], a[1] - b[1])


def _vec_add(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    """Add two grid vectors.

    Args:
        a: First grid vector.
        b: Second grid vector.

    Returns:
        Vector sum.
    """
    return (a[0] + b[0], a[1] + b[1])


class Blinky():
    """Compute Blinky chase targets."""
    pass  # top right corner


class Pinky():
    """Compute Pinky chase targets."""
    pass  # top left corner


class Inky():
    """Compute Inky chase targets."""
    pass  # bottom right corner


class Clyde():
    """Compute Clyde chase targets."""
    pass  # bottom left corner
