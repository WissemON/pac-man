import pygame
from typing import TypedDict


class KeyState(TypedDict):
    """Represent normalized keyboard state for movement controls."""
    pressed: bool
    last_time: int
    last_repeat: int


class InputHandler:
    """Translate keyboard and joystick input into key events."""

    def __init__(self, axis_threshold: float = 0.5,
                 initial_delay: int = 300, repeat_interval: int = 80) -> None:
        """Initialize the input handler.

        Args:
            axis_threshold: Axis value required to count as movement.
            initial_delay: Delay before held joystick input repeats.
            repeat_interval: Delay between repeated joystick inputs.
        """
        self.axis_threshold = axis_threshold
        self.initial_delay = initial_delay
        self.repeat_interval = repeat_interval
        self._state: dict[int, KeyState] = {}
        self._suppress_until_release = False

    def reset(self) -> None:
        """Clear the buffered input state."""
        self._state.clear()
        self._suppress_until_release = True

    def _map_joystick_to_keys(
        self,
        joystick: pygame.joystick.JoystickType,
    ) -> set[int]:
        """Convert joystick axes into key state.

        Args:
            joystick: Joystick instance to read.

        Returns:
            Key constants activated by joystick axes.
        """
        keys: set[int] = set()

        try:
            pad = joystick.get_hat(0)
        except Exception:
            pad = (0, 0)

        if pad != (0, 0):
            if pad[1] == 1:
                keys.add(pygame.K_UP)
            elif pad[1] == -1:
                keys.add(pygame.K_DOWN)
            if pad[0] == 1:
                keys.add(pygame.K_RIGHT)
            elif pad[0] == -1:
                keys.add(pygame.K_LEFT)
            return keys

        try:
            axe_x = joystick.get_axis(0)
            axe_y = joystick.get_axis(1)
        except Exception:
            axe_x = 0.0
            axe_y = 0.0

        if axe_x > self.axis_threshold:
            keys.add(pygame.K_RIGHT)
        elif axe_x < -self.axis_threshold:
            keys.add(pygame.K_LEFT)

        if axe_y > self.axis_threshold:
            keys.add(pygame.K_DOWN)
        elif axe_y < -self.axis_threshold:
            keys.add(pygame.K_UP)

        return keys

    def _map_buttons_to_keys(
        self,
        joystick: pygame.joystick.JoystickType,
    ) -> set[int]:
        """Convert joystick buttons into key state.

        Args:
            joystick: Joystick instance to read.

        Returns:
            Key constants activated by joystick buttons.
        """
        keys: set[int] = set()

        try:
            if joystick.get_numbuttons() > 0 and joystick.get_button(0):
                keys.add(pygame.K_RETURN)
            if joystick.get_numbuttons() > 1 and joystick.get_button(1):
                keys.add(pygame.K_BACKSPACE)
            if joystick.get_numbuttons() > 7 and joystick.get_button(7):
                keys.add(pygame.K_ESCAPE)
        except Exception:
            pass

        return keys

    def get_direction(
        self,
        joystick: pygame.joystick.JoystickType | None,
    ) -> str | None:
        """Return the current primary joystick direction.

        Args:
            joystick: Joystick instance to read.

        Returns:
            Direction name, or None when the joystick is neutral.
        """
        if joystick is None:
            return None

        try:
            pad = joystick.get_hat(0)
        except Exception:
            pad = (0, 0)

        if pad[0] == 1:
            return 'RIGHT'
        if pad[0] == -1:
            return 'LEFT'
        if pad[1] == 1:
            return 'UP'
        if pad[1] == -1:
            return 'DOWN'

        try:
            axe_x = joystick.get_axis(0)
            axe_y = joystick.get_axis(1)
        except Exception:
            return None

        if axe_x > self.axis_threshold:
            return 'RIGHT'
        if axe_x < -self.axis_threshold:
            return 'LEFT'
        if axe_y > self.axis_threshold:
            return 'DOWN'
        if axe_y < -self.axis_threshold:
            return 'UP'

        return None

    def get_key_events(
        self,
        joystick: pygame.joystick.JoystickType | None,
    ) -> list[int]:
        """Build keydown events from keyboard and joystick input.

        Args:
            joystick: Joystick instance to read.

        Returns:
            Synthetic keydown events for this frame.
        """
        if joystick is None:
            return []

        now = pygame.time.get_ticks()
        direction_keys = self._map_joystick_to_keys(joystick)
        button_keys = self._map_buttons_to_keys(joystick)
        emit: list[int] = []

        if self._suppress_until_release:
            if not direction_keys and not button_keys:
                self._suppress_until_release = False
            return emit

        for key in direction_keys:
            st = self._state.get(key)
            if not st or not st.get('pressed'):
                emit.append(key)
                self._state[key] = {
                    'pressed': True,
                    'last_time': now,
                    'last_repeat': now,
                }
            else:
                last_time = st.get('last_time', now)
                last_repeat = st.get('last_repeat', now)
                if now - last_time >= self.initial_delay and \
                        now - last_repeat >= self.repeat_interval:
                    emit.append(key)
                    st['last_repeat'] = now

        for key in button_keys:
            st = self._state.get(key)
            if not st or not st.get('pressed'):
                emit.append(key)
                self._state[key] = {
                    'pressed': True,
                    'last_time': now,
                    'last_repeat': now,
                }

        for key in list(self._state.keys()):
            if key not in direction_keys and key not in button_keys and \
                    self._state[key].get('pressed'):
                self._state[key]['pressed'] = False

        return emit
