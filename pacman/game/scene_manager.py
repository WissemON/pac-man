import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pacman.game.game import Game


class Scene(ABC):
    """Provide the common lifecycle API for scenes."""

    bgm_loop: str

    def __init__(self, game: "Game") -> None:
        """Initialize the scene.

        Args:
            game: Shared game object that owns resources, groups, and state.
        """
        self.game = game
        self.frozen = False
        self.item_gain = False
        self.win_level = False

    def on_enter(self) -> None:
        """Prepare the scene when it becomes active."""
        pass

    def on_resume(self) -> None:
        """Resume the scene after an overlay closes."""
        pass

    def on_pause(self) -> None:
        """Pause the scene while another scene is on top."""
        pass

    def on_exit(self) -> None:
        """Clean up before the scene leaves the stack."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one pygame event for the scene.

        Args:
            event: Event data to handle.
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Draw the current state onto a surface.

        Args:
            surface: Surface that receives drawing operations.
        """
        pass

    def play_theme(self, end_event_id: int) -> None:
        """Start the scene or level music.

        Args:
            end_event_id: Pygame event id fired when intro music ends.
        """
        pygame.mixer.music.set_endevent(end_event_id)
        pygame.mixer.music.load(self.bgm_loop)
        pygame.mixer.music.play(0)
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.queue(self.bgm_loop)

    def freeze_for(self, duration_ms: int) -> None:
        """Freeze scene updates for a fixed duration.

        Args:
            duration_ms: Freeze duration in milliseconds.
        """
        return None


class SceneManager:
    """Manage the active scene stack."""

    def __init__(self) -> None:
        """Initialize the scene manager."""
        self.stack: list[tuple[Scene, bool]] = []

    def current_scene(self) -> Scene | None:
        """Return the scene at the top of the stack.

        Returns:
            Active scene, or None when the stack is empty.
        """
        if not self.stack:
            return None
        return self.stack[-1][0]

    def push(self, scene: Scene, replace: bool = False) -> None:
        """Push a scene on top of the current one.

        Args:
            scene: Scene instance to push or activate.
            replace: Whether the current scene is being replaced.
        """
        current = self.current_scene()
        if current:
            if replace:
                current.on_exit()
            else:
                current.on_pause()
        self.stack.append((scene, replace))
        scene.on_enter()

    def pop(self) -> Scene | None:
        """Remove the top scene and resume the previous one.

        Returns:
            Removed scene, or None when the stack was empty.
        """
        if not self.stack:
            return None

        scene, replaced = self.stack.pop()
        scene.on_exit()

        current = self.current_scene()
        if current:
            if not replaced:
                current.on_resume()
            else:
                current.on_enter()

        return scene

    def change(self, scene: Scene) -> None:
        """Replace the stack with a new scene.

        Args:
            scene: Scene instance to push or activate.
        """
        while self.stack:
            self.pop()
        self.push(scene, replace=True)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one pygame event for the scene.

        Args:
            event: Event data to handle.
        """
        current = self.current_scene()
        if current:
            current.handle_event(event)

    def update(self, dt: float) -> None:
        """Advance state for one frame.

        Args:
            dt: Elapsed frame time in milliseconds.
        """
        current = self.current_scene()
        if current:
            current.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Draw the current state onto a surface.

        Args:
            surface: Surface that receives drawing operations.
        """
        current = self.current_scene()
        if current:
            current.render(surface)
