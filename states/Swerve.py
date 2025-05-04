# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588
import random
from state import State
from proto import Key

class Swerve(State):
    def __init__(self):
        super().__init__()
        self.moves = {
            (0, -1): Key.UP,    # up
            (0, 1): Key.DOWN,   # down
            (-1, 0): Key.LEFT,  # left
            (1, 0): Key.RIGHT,  # right
        }

    def tick(self, world, internal_state) -> Key:
        try:
            snake_body = world["body"]
            current_head = tuple(map(int, snake_body[0]))
            grid = internal_state.get_map()

            neck = tuple(map(int, snake_body[1]))
            direction = None

            # block in front of the snake
            if current_head[0] == neck[0]:
                direction = (current_head[0], current_head[1] + 1)
            else:
                direction = (current_head[0] + 1, current_head[1])

            move_for_direction = (direction[0] - current_head[0], direction[1] - current_head[1])

            valid_moves = [move for move in self.moves if move != move_for_direction and move != (-move_for_direction[0], -move_for_direction[1])]



            move = random.choice(valid_moves)

            idx = 0
            max_tries = 4
            while idx <= max_tries and (([current_head[0] + move[0], current_head[1] + move[1]]) in snake_body or grid[current_head[0] + move[0]][current_head[1] + move[1]] == 4 or grid[current_head[0] + move[0]][current_head[1] + move[1]] == 5):
                move = random.choice(valid_moves)
                idx += 1

            return self.moves[move]
        except Exception as e:
            return Key.EMPTY

    def on_exit(self, world, internal_state):
        super().on_exit(world, internal_state)
        return Key.EMPTY

    def on_enter(self, world, internal_state):
        super().on_enter(world, internal_state)
        return self.tick(world, internal_state)

            