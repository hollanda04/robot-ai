# modulo responsavel pela geraçao do labirinto, locaçao do ponto de inicio/fim, e surgimento de diamantes. ele gera um labirinto em uma area quadriculada onde as areas podem ser vazia ou uma parede obstaculo

import random
from typing import List, Tuple
from environment.obstacles import Obstacle

class MazeMap:
    #classe responsavel pela geração e mantimento da area do labirinto para a simulaçao. garantindo que o labirinto e conectado, possue local de inicio/fim e gera diamantes aleatoriamente
    def __init__(self, cols: int = 19, rows: int = 15,cell_size: int = 40, offset_y: int = 100):
        #inicializa o mapa do labirinto

        # garante que as dimensoes sejam impares para garantir um bom percurso e bordas
        self.cols = cols if cols % 2 != 0 else cols + 1
        self.rows = rows if rows % 2 != 0 else rows + 1
        self.cell_size = cell_size
        self.offset_y = offset_y
        
        # Grid representation: 1 = Wall, 0 = Passage
        self.grid = [[1 for _ in range(self.rows)] for _ in range(self.cols)]
        
        # posiçao de inicio e fim (in grid coordinates)
        self.start_grid = (1, 1)
        self.end_grid = (self.cols - 2, self.rows - 2)
        
        self.diamonds = []
        self.obstacles = []
        
        # Genera o layout do labirinto
        self.generate_maze()
        self.spawn_diamonds()
        self.create_obstacles()

    def generate_maze(self):
        #gera um labirinto usando um algoritmo DFS, aleatoriamente removendo algumas paredes para criar loops alternativos

        # Reset grid to walls
        self.grid = [[1 for _ in range(self.rows)] for _ in range(self.cols)]
        
        stack = []
        start_col, start_row = self.start_grid
        self.grid[start_col][start_row] = 0
        stack.append((start_col, start_row))
        
        while stack:
            curr_col, curr_row = stack[-1]
            
            # acha visinhos nao visitados em uma distancia de 2
            neighbors = []
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            
            for dc, dr in directions:
                nc, nr = curr_col + dc, curr_row + dr
                if 0 < nc < self.cols - 1 and 0 < nr < self.rows - 1:
                    if self.grid[nc][nr] == 1:
                        neighbors.append((nc, nr))
            
            if neighbors:
                # escolhe um vizinho nao escolhido aleatoriamente
                next_col, next_row = random.choice(neighbors)
                # Cria um percurso pela area entre eles
                mid_col = curr_col + (next_col - curr_col) // 2
                mid_row = curr_row + (next_row - curr_row) // 2
                
                self.grid[mid_col][mid_row] = 0
                self.grid[next_col][next_row] = 0
                
                stack.append((next_col, next_row))
            else:
                stack.pop()
                
        # garante que o inicio e o fim estejam abertos
        self.grid[self.start_grid[0]][self.start_grid[1]] = 0
        self.grid[self.end_grid[0]][self.end_grid[1]] = 0
        
        # Loop factor: abre algumas paredes para garantir multiplas rotas ( criando disafios para o algotmo de navegaçao/A* )
        # procura por areas da parade que separa duas passagens e a torna em uma passagem por meio de uma probabilidade
        loop_factor = 0.08
        for col in range(2, self.cols - 2):
            for row in range(2, self.rows - 2):
                if self.grid[col][row] == 1:
                    # Checa separaçao horizontal
                    if self.grid[col-1][row] == 0 and self.grid[col+1][row] == 0:
                        if random.random() < loop_factor:
                            self.grid[col][row] = 0
                    # Checa separaçao vertical
                    elif self.grid[col][row-1] == 0 and self.grid[col][row+1] == 0:
                        if random.random() < loop_factor:
                            self.grid[col][row] = 0

    def spawn_diamonds(self):
        #gera de 1 a 5 diamantes aleatoria mente em espaços disponives do percurso
        self.diamonds = []
        num_diamonds = random.randint(1, 5)
        
        # reune todas as areas de passagem validas (expcluindo o inicio e fim)
        valid_cells = []
        for col in range(1, self.cols - 1):
            for row in range(1, self.rows - 1):
                if self.grid[col][row] == 0 and (col, row) != self.start_grid and (col, row) != self.end_grid:
                    valid_cells.append((col, row))
        
        # escolhe aleatoriamente um posiçao para os diamantes
        if len(valid_cells) >= num_diamonds:
            self.diamonds = random.sample(valid_cells, num_diamonds)
        else:
            self.diamonds = valid_cells[:num_diamonds]

    def create_obstacles(self):
         #cria um instancia de obstaculos para todas as paredes na areas do campo? perimetro
        self.obstacles = []
        for col in range(self.cols):
            for row in range(self.rows):
                if self.grid[col][row] == 1:
                    x, y = self.grid_to_world(col, row)
                    # cria um obstaculo centrado ao redor do world coordinate offset 
                    self.obstacles.append(
                        Obstacle(
                            x - self.cell_size / 2, 
                            y - self.cell_size / 2, 
                            self.cell_size, 
                            self.cell_size
                        )
                    )

    def grid_to_world(self, col: int, row: int) -> Tuple[float, float]:
        # converte codernadas da areas para coordenadas de centro do mundo (pixels) 
        x = col * self.cell_size + self.cell_size / 2
        y = row * self.cell_size + self.cell_size / 2 + self.offset_y
        return x, y

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        #converte coordernada de mundo (pixels) para indeces de area
        col = int(x // self.cell_size)
        row = int((y - self.offset_y) // self.cell_size)
        # Clamp to grid bounds
        col = max(0, min(col, self.cols - 1))
        row = max(0, min(row, self.rows - 1))
        return col, row

    def is_valid_cell(self, col: int, row: int) -> bool:
        # checa se uma area esta entre o limite e se e uma passahgem
        return 0 <= col < self.cols and 0 <= row < self.rows and self.grid[col][row] == 0
        
    def get_width(self) -> int:
        # retorna a largura do mapa em pixels
        return self.cols * self.cell_size

    def get_height(self) -> int:
        # retorna a altura do mapa em pixels com um adicional para concideram o HUD
        return self.rows * self.cell_size + self.offset_y
