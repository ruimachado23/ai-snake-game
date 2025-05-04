# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588
from state import State
from proto import Key


class Idle(State):
    def tick(self, world, internal_state) -> Key:
        return Key.EMPTY

    def on_enter(self, world, internal_state) -> Key:
        return Key.EMPTY

    def on_exit(self, world, internal_state) -> Key:
        return Key.EMPTY
