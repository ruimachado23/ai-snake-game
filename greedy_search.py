# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588

from heapq import heappush, heappop
from typing import List, Tuple
from collections import deque
from proto import Key

moves = {
    (0, -1): Key.UP,    # up
    (0, 1): Key.DOWN,   # down
    (-1, 0): Key.LEFT,  # left
    (1, 0): Key.RIGHT,  # right
}

def wrapped_manhattan_distance(
        pos1: Tuple[int, int],
        pos2: Tuple[int, int],
        width: int,
        height: int,
        traverse: bool
) -> int:
    """
    Manhattan distance that accounts for wrapping if `traverse` is True.
    If wrapping is enabled, distance is the min of direct vs wrapped around.
    """
    dx = abs(pos1[0] - pos2[0])
    dy = abs(pos1[1] - pos2[1])

    if traverse:
        dx = min(dx, width - dx)
        dy = min(dy, height - dy)

    return dx + dy

def get_path_length_to(
    pos: Tuple[int, int], came_from: dict, start: Tuple[int, int]
) -> int:
    """Calculate the number of moves needed to reach a position from the start."""
    length = 0
    current = pos
    while current != start:
        length += 1
        current = came_from[current]
    return length


def is_neck_collision(
    current_pos: Tuple[int, int], next_pos: Tuple[int, int], snake_body: List[List[int]]
) -> bool:
    """Check if moving to next_pos would collide with the snake's neck (second segment)."""
    if len(snake_body) < 2:
        return False

    # The neck is the second segment of the snake (index 1)
    neck_pos = tuple(snake_body[1])
    return next_pos == neck_pos


def get_neighbors(
    pos: Tuple[int, int], snake_body: List[List[int]], grid, traverse
) -> List[Tuple[int, int]]:
    """Get valid neighboring positions."""
    # Standard moves: up, down, left, right
    possible_moves = {(0, -1), (0, 1), (-1, 0), (1, 0)}

    neighbors = []
    for dx, dy in possible_moves:
        new_pos = (pos[0] + dx, pos[1] + dy)

        if traverse:
            new_pos = (new_pos[0] % len(grid), new_pos[1] % len(grid[0]))
        else:
            if not (0 <= new_pos[0] < len(grid) and 0 <= new_pos[1] < len(grid[0])):
                continue

        if is_valid_position(new_pos, snake_body, grid, traverse):
            neighbors.append(new_pos)
    return neighbors


def is_valid_position(
    pos: Tuple[int, int],
    snake_body: List[List[int]],
    grid: List[List[int]],
    traverse: bool,
) -> bool:
    """Check if a position is valid for the snake to move to."""
    if not isinstance(grid, list) or not grid:
        return False

    if traverse:
        # Wrap around if 'traverse' is True
        adjusted_x = pos[0] % len(grid)
        adjusted_y = pos[1] % len(grid[0])
    else:
        adjusted_x, adjusted_y = pos
        # Check out of bounds
        if (
            adjusted_x < 0
            or adjusted_x >= len(grid)
            or adjusted_y < 0
            or adjusted_y >= len(grid[0])
        ):
            return False

    # Collisions with grid elements (walls, obstacles, other snakes, no-go zones):
    cell_value = grid[adjusted_x][adjusted_y]
    if traverse:
        if cell_value in (4, 5):
            return False
    # check for walls, obstacles, other snakes, no-go zones, or if its going against the edge of the grid
    else:
        if cell_value in (1, 4, 5) or adjusted_x < 0 or adjusted_x >= len(grid) or adjusted_y < 0 or adjusted_y >= len(grid[0]):
            return False

    if [adjusted_x, adjusted_y] in snake_body:
        return False

    return True


def can_reach_tail(
    snake_body_after_move: List[List[int]],
    grid: List[List[int]],
    traverse: bool
) -> bool:

    if len(snake_body_after_move) <= 1:
        return True  # A snake of length 1 trivially can "reach" its tail

    from collections import deque

    head = tuple(snake_body_after_move[0])
    tail = tuple(snake_body_after_move[-1])

    visited = set()
    visited.add(head)
    queue = deque([head])

    while queue:
        current = queue.popleft()
        if current == tail:
            return True  # Found path to tail

        # Explore neighbors (same logic but we must allow going onto 'tail')
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = current[0] + dx, current[1] + dy

            if traverse:
                nx = nx % len(grid)
                ny = ny % len(grid[0])

            # Check boundaries if not wrap-around
            if not traverse:
                if nx < 0 or nx >= len(grid) or ny < 0 or ny >= len(grid[0]):
                    continue

            # If the next cell is the tail itself, we can move there
            # Otherwise, ensure it's not in the body
            if (nx, ny) == tail or [nx, ny] not in snake_body_after_move:
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                    cell_value = grid[nx][ny]
                    if traverse and cell_value in (4, 5):
                        continue
                    if not traverse and cell_value in (1, 4, 5):
                        continue

                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

    return False


def greedy_search(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    snake_body: List[List[int]],
    map: List[List[int]],
    traverse,
    tail_check=False,
    custom_heuristic=wrapped_manhattan_distance,
) -> List[Tuple[int, int]]:

    if not map or not isinstance(map[0], list):
        raise ValueError("Map must be a non-empty 2D list")

    width, height = len(map), len(map[0])

    # check if goal is in 5 or 4
    if map[goal[0]][goal[1]] == 4 or map[goal[0]][goal[1]] == 5:
        return None
    
    def heuristic(a, b):
        return custom_heuristic(a, b, width, height, traverse)

    frontier = []
    heappush(frontier, (heuristic(start, goal), start))

    # A dictionary to store where each node came from (for path reconstruction)
    came_from = {start: None}

    # A set to track visited positions
    visited = set()
    visited.add(start)

    # Prevent infinite loops
    max_iterations = len(map) * len(map[0])
    iterations = 0

    path_found = False
    while frontier and iterations < max_iterations:
        iterations += 1

        _, current = heappop(frontier)

        if current == goal:
            path_found = True
            break

        # Explore neighbors
        for next_pos in get_neighbors(current, snake_body, map, traverse):
            if next_pos in visited:
                continue

            # First check for immediate neck collision
            if is_neck_collision(current, next_pos, snake_body):
                continue

            if next_pos in [tuple(body_part) for body_part in snake_body[2:]]:
                idx = snake_body.index(list(next_pos))
                cells_till_tail = len(snake_body) - 1 - idx
                cells_till_current = get_path_length_to(current, came_from, start) + 1

                if cells_till_tail >= cells_till_current - 1:
                    continue

            visited.add(next_pos)
            came_from[next_pos] = current
            heappush(frontier, (heuristic(next_pos, goal), next_pos))

    if not path_found or goal not in came_from:
        print(f"No path found to goal {goal}")
        return []

    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()

    if iterations >= max_iterations:
        print("Path search exceeded maximum iterations")
        return []

    if tail_check:

        xg, yg = goal
        # If it's a fruit => we add the new head but keep the tail
        if map[xg][yg] == 2:
            # New snake body is new head + old body
            new_body = [list(goal)] + snake_body
        else:
            # Normal move => new head + old body minus the last segment
            new_body = [list(goal)] + snake_body[:-1]

        if not can_reach_tail(new_body, map, traverse):
            return []
    # ------------------------------------------------------

    return path
