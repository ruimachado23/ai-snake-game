# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588
from greedy_search import greedy_search
from proto import Key
from typing import List, Tuple


def is_adjacent_wrap(
        pos1: Tuple[int, int],
        pos2: Tuple[int, int],
        width: int,
        height: int,
        wrapping: bool
) -> bool:
    """
    Returns True if pos2 is adjacent to pos1 by 1 cell
    (considering up/down/left/right) with optional wrapping.
    """
    if not wrapping:
        # Normal adjacency
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)
    else:
        # Wrapped adjacency
        # Effective difference in x/y if we allow wrapping around edges
        dx = abs(pos1[0] - pos2[0]) % width
        dy = abs(pos1[1] - pos2[1]) % height

        # For wrapping, the difference in one dimension could be "width - 1" (or "height - 1")
        # which is effectively 1 if we jump around the edge.
        return (
                (dx == 1 and dy == 0) or
                (dx == 0 and dy == 1) or
                (dx == width - 1 and dy == 0) or
                (dx == 0 and dy == height - 1)
        )

class State:
    def tick(self, world, internal_state) -> Key:
        return Key.EMPTY

    def on_enter(self, world, internal_state) -> Key:
        print(f"Entered {self.__class__.__name__}")
        return Key.EMPTY

    def on_exit(self, world, internal_state) -> Key:
        return Key.EMPTY

    def is_move_safe(
        self,
        start: tuple,
        move: tuple,
        snake_body: List[List[int]],
        grid: List[List[int]],
        traverse: List[int],
        heuristic,
    ) -> bool:
        width, height = len(grid), len(grid[0])
        body_set = {tuple(body_pos) for body_pos in snake_body}

        next_pos = ((start[0] + move[0]) % width, (start[1] + move[1]) % height)

        # Check if next position is part of snake body
        return next_pos not in body_set

    def is_adjacent(self, a: tuple, b: tuple) -> bool:
        return abs(a[0] - b[0]) + abs(a[1] - b[0]) == 1

    def move(self, current_head, next_pos, width, height, wrapping):
        """
        Return Key.UP, Key.DOWN, Key.LEFT, Key.RIGHT, or Key.EMPTY
        depending on how to move from current_head to next_pos,
        respecting wrapping if needed.
        """
        if not wrapping:
            dx = next_pos[0] - current_head[0]
            dy = next_pos[1] - current_head[1]
        else:
            # compute a dx/dy in the range -width//2..+width//2, etc.
            dx = (next_pos[0] - current_head[0]) % width
            # If dx is more than half the board, it’s shorter to go the other way
            if dx > width // 2:
                dx -= width

            dy = (next_pos[1] - current_head[1]) % height
            if dy > height // 2:
                dy -= height

        # Now interpret (dx, dy)
        if dx == 1 and dy == 0:
            return Key.RIGHT
        elif dx == -1 and dy == 0:
            return Key.LEFT
        elif dx == 0 and dy == 1:
            return Key.DOWN
        elif dx == 0 and dy == -1:
            return Key.UP
        else:
            # Not a simple adjacent move
            return Key.EMPTY