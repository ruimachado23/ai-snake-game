# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588
from enum import Enum


class Key(Enum):
    UP = "w", (0, 1)
    DOWN = "s", (0, -1)
    LEFT = "a", (-1, 0)
    RIGHT = "d", (1, 0)
    SPACE = " ", (0, 0)
    EMPTY = "", (0, 0)

    def __iter__(self):
        return self

    def __next__(self):
        return self
