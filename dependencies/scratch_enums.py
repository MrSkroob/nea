from enum import Enum


class Coordinates:
    def __init__(self, x: int | float, y: int | float) -> None:
        self.x = x
        self.y = y


class Effect(Enum):
    COLOR = 0
    FISHEYE = 1
    WHIRL = 2
    PIXELATE = 3
    MOSAIC = 4
    BRIGHTNESS = 5
    GHOST = 6


class AttributeEvent(Enum):
    LOUDNESS = 0
    TIMER = 1


class Stop(Enum):
    ALL = 0
    THIS_SCRIPT = 1
    OTHER_SCRIPTS_IN_SPRITE = 2


class KeyCode(Enum):
    SPACE = 0
    UP_ARROW = 1
    DOWN_ARROW = 2
    RIGHT_ARROW = 3
    LEFT_ARROW = 4
    ANY = 5
    A = 6
    B = 7
    C = 8
    D = 9
    E = 10
    F = 11
    G = 12
    H = 13
    I = 14
    J = 15
    K = 16
    L = 17
    N = 18
    M = 19
    O = 20
    P = 21
    Q = 22
    R = 23
    S = 24
    T = 25
    U = 26
    V = 27
    W = 28
    X = 29
    Y = 30
    Z = 31
    ONE = 32
    TWO = 33
    THREE = 34
    FOUR = 35
    FIVE = 36
    SIX = 37
    SEVEN = 38
    EIGHT = 39
    NINE = 40
    ZERO = 41


class Layer(Enum):
    FRONT = 0
    BACK = 1


class LayerDirection(Enum):
    FORWARD = 0
    BACKWARD = 1


class Position(Enum):
    RANDOM_POSITION = 0
    MOUSE_POINTER = 1


class RotationStyle(Enum):
    LEFT_RIGHT = 0
    DONT_ROTATE = 1
    ALL_AROUND = 2
