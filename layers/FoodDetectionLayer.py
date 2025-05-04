# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588
from sensory_process import Layer, SensorialResponse


class FoodDetectionLayer(Layer):
    def __init__(self):
        self.priority = 1

    def check(self, world, internal_state) -> SensorialResponse:
        sight = world.get("sight", {})

        def manhattan_distance(point1, point2):
            return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

        # find foods
        chase_super = (len(sight) // 2) < 5
        for y_str, row in sight.items():
            y = int(y_str)
            for x_str, value in row.items():
                x = int(x_str)

                traverse = world.get("traverse", [])

                if (value == 2) or (not traverse and value == 3) or (chase_super and value == 3):
                    food_position = (y, x)
                    if food_position not in internal_state.get_foods():
                        internal_state.foods.append(food_position)
                        head = world.get("body", [])[0]
                        # sort the food positions by distance to the snake's head
                        internal_state.foods = sorted(
                            internal_state.foods,
                            key=lambda food: manhattan_distance(head, food),
                        )

        if internal_state.get_foods():
            if internal_state.current_target is None:
                # sort the food positions by distance to the snake's head
                internal_state.current_target = internal_state.get_foods()[0]
            return SensorialResponse(
                internal_state.get_states()[1], world, internal_state
            )
        return SensorialResponse(None, world, internal_state)
