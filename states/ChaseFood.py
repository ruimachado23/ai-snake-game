
# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588

import random
from greedy_search import greedy_search
from proto import Key
from state import State, is_adjacent_wrap
from typing import Tuple, List


class ChaseFood(State):
    def __init__(self):
        super().__init__()
        self.path = None
        self.sight = None
        self.current_target = None
        self.food_positions = [] 
        self.moves = {
            (0, -1): Key.UP,  
            (0, 1): Key.DOWN, 
            (-1, 0): Key.LEFT,
            (1, 0): Key.RIGHT,
        }

    def on_enter(self, world, internal_state) -> Key:
        super().on_enter(world, internal_state)
        self.path = None
        if internal_state.get_foods():
            self.food_positions = internal_state.get_foods()

        if internal_state.current_target:
            self.current_target = internal_state.current_target
        return self.tick(world, internal_state)

    def tick(self, world, internal_state) -> Key:
        super().tick(world, internal_state)
        try:
            self.food_positions = internal_state.get_foods()
            self.grid = internal_state.get_map()
            self.sight = world["sight"]
            snake_body = world["body"]

            current_head = tuple(map(int, snake_body[0]))

            if not self.path or not self.current_target:
                if not self.food_positions:
                    return self.get_fallback_move(world, internal_state)

                self.current_target = min(
                    self.food_positions,
                    key=lambda food: self.manhattan_distance(current_head, food),
                )

                self.path = greedy_search(
                    start=current_head,
                    goal=self.current_target,
                    snake_body=snake_body,
                    map=self.grid,
                    traverse=world["traverse"],
                    tail_check=True,
                )

                if not self.path:
                    self.food_positions.remove(self.current_target)
                    self.current_target = None
                    return self.get_fallback_move(world, internal_state)

            if self.path:
                next_pos = self.path[0]

                self.path = greedy_search(
                    start=current_head,
                    goal=self.current_target,
                    snake_body=snake_body,
                    map=self.grid,
                    traverse=world["traverse"],
                    tail_check=True,
                )
                if not self.path:
                    self.food_positions.remove(self.current_target)
                    self.current_target = None
                    return self.get_fallback_move(world, internal_state)

                next_pos = self.path[0]

                move = self.move(current_head, next_pos, width=len(self.grid), height=len(self.grid[0]), wrapping=world["traverse"])
                if move:
                    self.path.pop(0)
                    return move

            self.food_positions = []
            self.current_target = None
            return self.get_fallback_move(world, internal_state)

        except Exception as e:
            print(f"Error in tick(): {e}")
            import traceback
            traceback.print_exc()
            return Key.EMPTY

    def on_exit(self, world, internal_state) -> Key:
        super().on_exit(world, internal_state)
        self.path = None
        self.current_target = None
        self.tick_count = 0
        self.food_positions = []
        return Key.EMPTY

    def manhattan_distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two points."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_fallback_move(self, world, internal_state) -> Key:
        print("Attempting to find a fallback move.")
        snake_body = world["body"]
        head_x, head_y = snake_body[0]

        valid_moves = []
        for (dx, dy), move_key in self.moves.items():
            nx, ny = head_x + dx, head_y + dy

            if internal_state.traverse:
                nx %= len(self.grid)
                ny %= len(self.grid[0])
            else:
                if nx < 0 or nx >= len(self.grid) or ny < 0 or ny >= len(self.grid[0]):
                    continue

            cell_value = self.grid[nx][ny]
            if internal_state.traverse:
                if cell_value in (4, 5):
                    continue
            else:
                if cell_value in (1, 3, 4, 5):
                    continue

            if [nx, ny] in snake_body[:-1]:
                continue

            valid_moves.append(move_key)

        if valid_moves:
            chosen_move = random.choice(valid_moves)
            print(f"Fallback move selected: {chosen_move}")
            return chosen_move

        print("No valid fallback moves available. Returning Key.EMPTY.")
        return Key.EMPTY

