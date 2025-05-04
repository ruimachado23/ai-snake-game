
# Guilherme Rosa - 113968
# Rui Machado - 113765
# Henrique Teixeira 114588

from typing import Tuple
from proto import Key
from sensory_process import Layer, SensorialResponse
from states.Swerve import Swerve

class SurvivalLayer(Layer):
    def __init__(self):
        super().__init__(0)
        self.priority = 0
        self.grid = None
        self.buffer_distance = 3  

    def check(self, world, internal_state) -> SensorialResponse:
        super().check(world, internal_state)

        self.grid = internal_state.get_map()
        if not self.grid or "sight" not in world:
            return SensorialResponse(None, world, internal_state)

        self.mark_other_snakes_on_map(world)
        return self.check_take_action(world, internal_state) 


    def check_take_action(self, world, internal_state) -> SensorialResponse:
        # if snake is in danger, return the move to avoid it

        if self.grid is None:
            return SensorialResponse(None, world, internal_state)
        
        snake_body = world["body"]
        current_head = tuple(map(int, snake_body[0]))

        neck = tuple(map(int, snake_body[1]))
        block_in_front = None

        # block in front of the snake
        if current_head[0] == neck[0]:
            block_in_front = (current_head[0], current_head[1] + 1)
        else:
            block_in_front = (current_head[0] + 1, current_head[1])

        #check in bounds
        if block_in_front[0] < 0 or block_in_front[0] >= len(self.grid) or block_in_front[1] < 0 or block_in_front[1] >= len(self.grid[0]):
            return SensorialResponse(None, world, internal_state)

        if self.grid[block_in_front[0]][block_in_front[1]] == 5 or self.grid[block_in_front[0]][block_in_front[1]] == 4:
            return SensorialResponse(internal_state.get_states()[3], world, internal_state)
        else:
            return SensorialResponse(None, world, internal_state)

        


    def mark_other_snakes_on_map(self, world):
        """Mark enemy snake as 4, then expand around it by distance=3 with marker 5."""
        width = len(self.grid)
        height = len(self.grid[0])
        for x in range(width):
            for y in range(height):
                if self.grid[x][y] in (4, 5):
                    self.grid[x][y] = 0

        our_body_positions = {
            (int(seg[0]), int(seg[1])) for seg in world["body"]
        }

        sight = world["sight"]
        for row_str, row_info in sight.items():
            ex = int(row_str)
            for col_str, value in row_info.items():
                ey = int(col_str)
                if value == 4:  
                    if (ex, ey) not in our_body_positions:
                        self.grid[ex][ey] = 4

        for x in range(width):
            for y in range(height):
                if self.grid[x][y] == 4:
                    self.mark_no_go_zone_around(x, y, self.buffer_distance)

    def mark_no_go_zone_around(self, ex, ey, dist=3):
        """Mark all cells within manhattan distance dist of (ex, ey) as 5."""
        width = len(self.grid)
        height = len(self.grid[0])

        for dx in range(-dist, dist + 1):
            for dy in range(-dist, dist + 1):
                if abs(dx) + abs(dy) <= dist:
                    nx = ex + dx
                    ny = ey + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if self.grid[nx][ny] in (0, 2):  
                            self.grid[nx][ny] = 5

    def __str__(self):
        return self.__class__.__name__
