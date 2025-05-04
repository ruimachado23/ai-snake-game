
# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588

from sensory_process import Layer, SensorialResponse


class WanderLayer(Layer):
    def __init__(self):
        self.priority = 99

    def check(self, world, internal_state) -> SensorialResponse:
        return SensorialResponse(internal_state.get_states()[2], world, internal_state)
