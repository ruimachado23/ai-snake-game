# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588
from state import State


class InternalState:
    def __init__(self):
        self.ticks: int = 0
        self.current_target = None
        self.states: list[State] = []
        self.current_state = None
        self.rocks: list = []
        self.blocked_moves: list = []
        self.traverse = True
        self.target_index = 0
        self.points_reached = 0

    def set_foods(self, foods: list):
        self.foods: list = foods

    def set_map(self, map: list):
        self.map: list = map

    def set_states(self, states: list[State]):
        self.states: list[State] = states

    def get_states(self) -> list[State]:
        return self.states

    def get_foods(self):
        return self.foods

    def get_map(self):
        return self.map

    def get_rocks(self):
        if not self.rocks:
            for i in range(len(self.map)):
                for j in range(len(self.map[i])):
                    if self.map[i][j] == 1:
                        self.rocks.append((i, j))
            return self.rocks
        return self.rocks


class SensorialProcess:
    def __init__(self, layers, internal_state: InternalState):
        self.layers = layers
        self.internal_state: InternalState = internal_state
        self.layers.sort(key=lambda x: x.priority)

    def process_world(self, world):
        self.internal_state.ticks += 1

        # update traverse
        traverse = world.get("traverse", True)
        world["traverse"] = traverse
        self.internal_state.traverse = traverse


        # if the snake has reached the target, remove it from the list - food
        for food in self.internal_state.foods:
            if tuple(world["body"][0]) == food:
                self.internal_state.foods.remove(food)
                if self.internal_state.current_target == food:
                    self.internal_state.current_target = None

        if self.internal_state.ticks > 2:
            for layer in self.layers:
                layer_response = layer.check(world, self.internal_state)

                self.internal_state = layer_response.get_internal_state()

                if layer_response.get_state() is not None:
                    if self.internal_state.current_state == layer_response.get_state():
                        return SensorialResponse(
                            None, world, layer_response.get_internal_state()
                        )
                    self.internal_state.current_state = layer_response.get_state()
                    return layer_response

        return SensorialResponse(
            self.internal_state.states[0], world, self.internal_state
        )


class SensorialResponse:
    def __init__(self, state, world, internal_state: InternalState):
        self.state = state
        self.world = world
        self.internal_state = internal_state

    def get_state(self):
        return self.state

    def get_world(self):
        return self.world

    def get_internal_state(self):
        return self.internal_state


class Layer:
    def __init__(self, priority):
        self.priority = priority

    def check(self, world, internal_state) -> SensorialResponse:
        return SensorialResponse(None, world, internal_state)

    def __str__(self):
        return self.__class__.__name__
