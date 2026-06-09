from typing import Any, Generic, Iterable, Iterator, TypeVar

_T = TypeVar("_T")

SRCALPHA: int
USEREVENT: int
KEYDOWN: int
QUIT: int
HWSURFACE: int
DOUBLEBUF: int

K_UP: int
K_DOWN: int
K_LEFT: int
K_RIGHT: int
K_RETURN: int
K_KP_ENTER: int
K_BACKSPACE: int
K_ESCAPE: int
K_SPACE: int
K_F1: int
K_F2: int
K_F3: int
K_F4: int
K_a: int
K_c: int
K_d: int
K_e: int
K_h: int
K_i: int
K_j: int
K_l: int
K_m: int
K_n: int
K_p: int
K_t: int
K_u: int

ColorValue = object


class Color:
    def __init__(self, value: object) -> None: ...


class Rect:
    x: int
    y: int
    width: int
    height: int
    left: int
    right: int
    top: int
    bottom: int
    centerx: int
    centery: int
    center: tuple[int, int]
    midbottom: tuple[int, int]
    topleft: tuple[int, int]
    size: tuple[int, int]

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

    def copy(self) -> "Rect": ...
    def move(self, x: int | float, y: int | float) -> "Rect": ...
    def colliderect(self, other: "Rect") -> bool: ...
    def collidepoint(self, *args: Any) -> bool: ...


class Surface:
    def __init__(
        self,
        size: tuple[int, int],
        flags: int = 0,
        depth: int = 0,
        masks: object | None = None,
    ) -> None: ...
    def get_width(self) -> int: ...
    def get_height(self) -> int: ...
    def get_size(self) -> tuple[int, int]: ...
    def get_rect(self, **kwargs: Any) -> Rect: ...

    def blit(
        self,
        source: "Surface",
        dest: object,
        area: object | None = None,
        special_flags: int = 0,
    ) -> Rect: ...
    def fill(self, color: object) -> Rect: ...
    def set_colorkey(self, color: object) -> None: ...
    def set_alpha(self, alpha: int) -> None: ...
    def convert(self) -> "Surface": ...
    def convert_alpha(self) -> "Surface": ...
    def copy(self) -> "Surface": ...


class font:
    class Font:
        def __init__(self, filename: str | None, size: int) -> None: ...

        def render(
            self,
            text: str,
            antialias: bool,
            color: object,
        ) -> "Surface": ...
        def size(self, text: str) -> tuple[int, int]: ...
        def get_height(self) -> int: ...

    @staticmethod
    def SysFont(name: str | None, size: int) -> Font: ...


class image:
    @staticmethod
    def load(filename: str) -> Surface: ...


class transform:
    @staticmethod
    def scale(surface: Surface, size: tuple[int, int]) -> Surface: ...
    @staticmethod
    def smoothscale(surface: Surface, size: tuple[int, int]) -> Surface: ...
    @staticmethod
    def flip(surface: Surface, xbool: bool, ybool: bool) -> Surface: ...
    @staticmethod
    def rotate(surface: Surface, angle: float) -> Surface: ...


class mixer:
    class Sound:
        def __init__(self, file: str) -> None: ...
        def set_volume(self, volume: float) -> None: ...
        def play(self, loops: int = 0) -> None: ...
        def stop(self) -> None: ...

    class music:
        @staticmethod
        def load(filename: str) -> None: ...
        @staticmethod
        def play(loops: int = 0) -> None: ...
        @staticmethod
        def stop() -> None: ...
        @staticmethod
        def set_volume(volume: float) -> None: ...
        @staticmethod
        def queue(filename: str) -> None: ...
        @staticmethod
        def set_endevent(event_id: int) -> None: ...


class event:
    class Event:
        type: int
        key: int
        unicode: str
        def __init__(self, type: int, dict: dict[str, object] | None = None,
                     **attributes: object) -> None: ...

    @staticmethod
    def get() -> list[Event]: ...
    @staticmethod
    def post(event: Event) -> None: ...


class key:
    class ScancodeWrapper:
        def __getitem__(self, key: int) -> bool: ...

    @staticmethod
    def get_pressed() -> ScancodeWrapper: ...


class joystick:
    class JoystickType:
        def init(self) -> None: ...
        def get_hat(self, index: int) -> tuple[int, int]: ...
        def get_axis(self, index: int) -> float: ...
        def get_numbuttons(self) -> int: ...
        def get_button(self, index: int) -> bool: ...

        def rumble(
            self,
            low_frequency: float,
            high_frequency: float,
            duration: int,
        ) -> bool: ...

    @staticmethod
    def get_count() -> int: ...
    @staticmethod
    def Joystick(index: int) -> JoystickType: ...


class time:
    class Clock:
        def tick(self, framerate: int = 0) -> int: ...
        def get_fps(self) -> float: ...

    @staticmethod
    def get_ticks() -> int: ...
    @staticmethod
    def delay(milliseconds: int) -> None: ...


class display:
    @staticmethod
    def set_mode(size: tuple[int, int], flags: int = 0) -> Surface: ...
    @staticmethod
    def flip() -> None: ...


class draw:
    @staticmethod
    def rect(
        surface: Surface,
        color: object,
        rect: Rect,
        width: int = 0,
    ) -> Rect: ...

    @staticmethod
    def line(
        surface: Surface,
        color: object,
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        width: int = 1,
    ) -> Rect: ...

    @staticmethod
    def circle(
        surface: Surface,
        color: object,
        center: tuple[int, int],
        radius: int,
        width: int = 0,
    ) -> Rect: ...


class sprite:
    class Sprite:
        image: Surface
        rect: Rect
        def __init__(self, *groups: object) -> None: ...
        def kill(self) -> None: ...

    class LayeredUpdates(Generic[_T]):
        def __init__(self, *sprites: _T) -> None: ...
        def add(self, *sprites: _T) -> None: ...
        def remove(self, *sprites: _T) -> None: ...
        def empty(self) -> None: ...
        def draw(self, surface: Surface) -> list[Rect]: ...
        def update(self, *args: object, **kwargs: object) -> None: ...
        def sprites(self) -> list[_T]: ...
        def __iter__(self) -> Iterator[_T]: ...
        def __len__(self) -> int: ...

    @staticmethod
    def spritecollide(
        sprite: Sprite,
        group: Iterable[_T],
        dokill: bool,
    ) -> list[_T]: ...

    @staticmethod
    def spritecollideany(
        sprite: Sprite,
        group: Iterable[_T],
    ) -> _T | None: ...


def init() -> tuple[int, int]: ...


def quit() -> None: ...
