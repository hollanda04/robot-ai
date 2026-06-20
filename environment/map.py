import random
from typing import List, Tuple
from environment.obstacles import Obstacle

class MazeMap:
    
    def __init__(self, cols: int = 19, rows: int = 15, cell_size: int = 40, offset_y: int = 100):
        self.cols = cols if cols % 2 != 0 else cols + 1
        self.rows = rows if rows % 2 != 0 else rows + 1
        self.cell_size = cell_size
        self.offset_y = offset_y

        self.grid = [[1 for _ in range(self.rows)] for _ in range(self.cols)]
        self.start_grid = (1, 1)
        self.end_grid = (self.cols - 2, self.rows - 2)
        
        self.diamonds = []
        self.obstacles = []
        
        self.generate_maze()
        self.spawn_diamonds()
        self.create_obstacles()

    def generate_maze(self):

        self.grid = [[1 for _ in range(self.rows)] for _ in range(self.cols)]
        
        stack = []
        start_col, start_row = self.start_grid
        self.grid[start_col][start_row] = 0
        stack.append((start_col, start_row))
        
        while stack:
            curr_col, curr_row = stack[-1]

            neighbors = []
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            
            for dc, dr in directions:
                nc, nr = curr_col + dc, curr_row + dr
                if 0 < nc < self.cols - 1 and 0 < nr < self.rows - 1:
                    if self.grid[nc][nr] == 1:
                        neighbors.append((nc, nr))
            
            if neighbors:
                next_col, next_row = random.choice(neighbors)
                mid_col = curr_col + (next_col - curr_col) // 2
                mid_row = curr_row + (next_row - curr_row) // 2
                
                self.grid[mid_col][mid_row] = 0
                self.grid[next_col][next_row] = 0
                
                stack.append((next_col, next_row))
            else:
                stack.pop()
                
        self.grid[self.start_grid[0]][self.start_grid[1]] = 0
        self.grid[self.end_grid[0]][self.end_grid[1]] = 0
        
        loop_factor = 0.08
        for col in range(2, self.cols - 2):
            for row in range(2, self.rows - 2):
                if self.grid[col][row] == 1:
                    if self.grid[col-1][row] == 0 and self.grid[col+1][row] == 0:
                        if random.random() < loop_factor:
                            self.grid[col][row] = 0
                    elif self.grid[col][row-1] == 0 and self.grid[col][row+1] == 0:
                        if random.random() < loop_factor:
                            self.grid[col][row] = 0

    def spawn_diamonds(self):
        self.diamonds = []
        num_diamonds = random.randint(1, 3)
        valid_cells = []
        for col in range(1, self.cols - 1):
            for row in range(1, self.rows - 1):
                if self.grid[col][row] == 0 and (col, row) != self.start_grid and (col, row) != self.end_grid:
                    valid_cells.append((col, row))
        if len(valid_cells) >= num_diamonds:
            self.diamonds = random.sample(valid_cells, num_diamonds)
        else:
            self.diamonds = valid_cells[:num_diamonds]

    def create_obstacles(self):
        self.obstacles = []
        for col in range(self.cols):
            for row in range(self.rows):
                if self.grid[col][row] == 1:
                    x, y = self.grid_to_world(col, row)
                    self.obstacles.append(
                        Obstacle(
                            x - self.cell_size / 2, 
                            y - self.cell_size / 2, 
                            self.cell_size, 
                            self.cell_size
                        )
                    )

    def grid_to_world(self, col: int, row: int) -> Tuple[float, float]:
        x = col * self.cell_size + self.cell_size / 2
        y = row * self.cell_size + self.cell_size / 2 + self.offset_y
        return x, y

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        col = int(x // self.cell_size)
        row = int((y - self.offset_y) // self.cell_size)
        col = max(0, min(col, self.cols - 1))
        row = max(0, min(row, self.rows - 1))
        return col, row

    def is_valid_cell(self, col: int, row: int) -> bool:
        return 0 <= col < self.cols and 0 <= row < self.rows and self.grid[col][row] == 0
        
    def get_width(self) -> int:
        return self.cols * self.cell_size

    def get_height(self) -> int:
        return self.rows * self.cell_size + self.offset_y
