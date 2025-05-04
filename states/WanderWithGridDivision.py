
# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588


import random
from greedy_search import greedy_search
from proto import Key
from state import State
from typing import Tuple, List


class WanderWithGridDivision(State):
    def __init__(self):
        self.grid = None
        self.grid_h = 0
        self.grid_w = 0
        self.path = []
        self.moves = {
            (0, -1): Key.UP,  # up
            (0, 1): Key.DOWN,  # down
            (-1, 0): Key.LEFT,  # left
            (1, 0): Key.RIGHT,  # right
        }
        self.goal = None
        self.grid_sections = {}
        self.section_visited_points = {}
        self.current_section_points = {}
        self.last_visited_sections = [] 
        self.current_section = None
        self.counts_traverse = False
        self.num_sections = 20
        self.heuristic_grid = []
        self.heuristic_decay = 1


    def on_enter(self, world, internal_state) -> Key:
        return self.tick(world, internal_state)

    def divide_grid_into_sections(self):
        width, height = len(self.grid), len(self.grid[0])
        self.grid_w = width
        self.grid_h = height
        padding = 2

        section_width = width // 3
        section_height = height // 4

        section_id = 0
        self.grid_sections = {}
        self.section_visited_points = {}
        self.current_section_points = {}

        for i in range(4):
            for j in range(3): 
                start_x = j * section_width
                start_y = i * section_height
                
                section_points = []
                for x in range(start_x, start_x + section_width, 3):
                    for y in range(start_y, start_y + section_height, 3):
                        if x < width and y < height: 
                            section_points.append((x, y))

                self.grid_sections[section_id] = section_points
                self.section_visited_points[section_id] = set()
                section_id += 1
        self.heuristic_grid = [[0 for _ in range(height)] for _ in range(width)]
        return self.grid_sections



    def get_next_section_goal(self, jump_esction=False) -> Tuple[int, int]:
        """Select the next point to visit in current section or move to new section."""
        # If we need a new section or have visited all 3 points in current section

        if (self.current_section is None or 
            len(self.section_visited_points[self.current_section]) >= 2 or
            self.current_section not in self.current_section_points) or jump_esction:
            
            available_sections = [
                section_id for section_id in self.grid_sections.keys()
                if section_id not in self.last_visited_sections
            ]

            if not available_sections:
                self.last_visited_sections = []
                available_sections = list(self.grid_sections.keys())

            self.current_section = random.choice(available_sections)

            first_point = random.choice(self.grid_sections[self.current_section])
            second_point = None
            distance_to_first = 0

            while distance_to_first < 8:
                second_point = random.choice(self.grid_sections[self.current_section])
                distance_to_first = abs(first_point[0] - second_point[0]) + abs(first_point[1] - second_point[1])

            self.current_section_points[self.current_section] = [first_point, second_point]

            self.section_visited_points[self.current_section] = set()
            
            self.last_visited_sections.append(self.current_section)
            if len(self.last_visited_sections) == len(self.grid_sections):
                [self.last_visited_sections.pop(0) for i in range(4)]

        available_points = [
            point for point in self.current_section_points[self.current_section]
            if point not in self.section_visited_points[self.current_section]
        ]

        next_point = random.choice(available_points)
        self.section_visited_points[self.current_section].add(next_point)


        return next_point

    def tick(self, world, internal_state) -> Key:
        super().tick(world, internal_state)
        self.grid = internal_state.get_map()

        snake_body = world["body"]
        start = tuple(snake_body[0])

        if not self.grid_sections:
            self.divide_grid_into_sections()

        self.update_heuristic_grid()

        if not self.goal or start == self.goal:
            self.goal = self.get_next_section_goal()

        self.path = None
        attempts = 0
        index = 0
        max_attempts = 2  
        max_max_attempts = 10 

        while not self.path and index < max_max_attempts:
            jump_section = False
            if attempts >= max_attempts:
                jump_section = True
                attempts = 0

            self.path = greedy_search(
                start,
                self.goal,
                snake_body,
                self.grid,
                world["traverse"],
                tail_check=True,
                custom_heuristic=self.manhattan_distance,
            )

            if not self.path:
                self.goal = self.get_next_section_goal(jump_section)
                attempts += 1
                index += 1
        
        if not self.path:
            snake_body = world["body"]
            head_x, head_y = snake_body[0]

            valid_moves = []
            for (dx, dy), move_key in self.moves.items():
                nx, ny = head_x + dx, head_y + dy

                if not internal_state.traverse:
                    if (nx < 0 or nx >= self.grid_w or ny < 0 or ny >= self.grid_h):
                        continue

                if internal_state.traverse:
                    nx %= self.grid_w
                    ny %= self.grid_h

                cell_value = self.grid[nx][ny]
                if internal_state.traverse:
                    # Disallow stepping on snake or no-go (4 or 5)
                    if cell_value in (4, 5):
                        continue
                else:
                    # Disallow stepping on walls(1), obstacles(3), snakes(4), no-go(5)
                    if cell_value in (1, 3, 4, 5):
                        continue

                # Also ensure we are not colliding with our own snake body
                # (except the very tail, which will move)
                if [nx, ny] in snake_body[:-1]:
                    continue

                # If we reached here, it's a valid fallback move
                valid_moves.append(move_key)

            if valid_moves:
                # Return any valid move (or pick randomly if you prefer)
                return random.choice(valid_moves)

            # If no fallback was possible, do nothing
            return Key.EMPTY
            

        # Follow the path
        next_position = self.path.pop(0)

        # Update the heuristic grid for visited positions and their neighbors
        pos_x, pos_y = next_position
        for i in range(-6, 7):
            for j in range(-6, 7):
                neighbor_x = pos_x + i
                neighbor_y = pos_y + j
                if 0 <= neighbor_x < self.grid_w and 0 <= neighbor_y < self.grid_h:
                    # Add higher penalty for the exact position and decrease for neighbors
                    distance = abs(i) + abs(j)
                    if distance == 0:
                        penalty = 10  # Higher penalty for visited position
                    else:
                        penalty = 5 / (distance + 1)  # Decreasing penalty for neighbors
                    self.heuristic_grid[neighbor_x][neighbor_y] += penalty

        move = self.move(start, next_position, self.grid_w, self.grid_h, internal_state.traverse)

        return move

    def update_heuristic_grid(self):
        """Apply decay to all heuristic values."""
        for i in range(self.grid_w):
            for j in range(self.grid_h):
                self.heuristic_grid[i][j] *= self.heuristic_decay  

    def manhattan_distance(self, a: Tuple[int, int], b: Tuple[int, int], width, height, traverse) -> int:
        """Calculate the Manhattan distance between two points with heuristic adjustment."""
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])

        if traverse:
            dx = min(dx, width - dx)
            dy = min(dy, height - dy)
        base_distance = dx + dy
        # Increase the weight of the heuristic penalty
        heuristic_penalty = self.heuristic_grid[b[0]][b[1]] * 2
        return base_distance + heuristic_penalty
