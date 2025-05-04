# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588
from state import State
from proto import Key


class StateMachine:
    def __init__(self, initial_state: State):
        self.state = initial_state
        self.moves = {
            (0, -1): Key.UP,  # up
            (0, 1): Key.DOWN,  # down
            (-1, 0): Key.LEFT,  # left
            (1, 0): Key.RIGHT,  # right
        }

    def change_state(self, state):
        self.state = state

    def tick_state(self, world, internal_state):
        res = self.state.tick(world, internal_state)
        #       if internal_state.ticks > 5 and res == Key.EMPTY:
        #           raise ValueError("No move was made!")
        return res

    def tick_machine(self, sensorial_response):
        if sensorial_response is None:
            raise ValueError("SensorialResponse is None!")

        new_state = sensorial_response.get_state()

        if new_state is not None and new_state != self.state:
            self.state.on_exit(
                sensorial_response.get_world(), sensorial_response.get_internal_state()
            )
            self.change_state(new_state)
            return self.state.on_enter(
                sensorial_response.get_world(), sensorial_response.get_internal_state()
            )
        else:
            return self.tick_state(
                sensorial_response.get_world(), sensorial_response.get_internal_state()
            )

    def __str__(self):
        return self.state.__class__.__name__
