#modulo responsavel pela implementaçao do algoritmo BFS. o agente usa o bfs para escanear o mapa, localizar diamantes e registrar as areas visitadas

import time
from collections import deque
from typing import List, Tuple, Dict

def bfs_find_diamonds(
    grid: List[List[int]], 
    start: Tuple[int, int], 
    diamond_positions: List[Tuple[int, int]]
) -> Dict:
    # performa o BFS começando pela posiçao inicial do robo para procura/descobrir as coordenadas de todos os diamante no labirinto
    start_time = time.perf_counter()
    
    cols = len(grid)
    rows = len(grid[0])
    
    queue = deque([start])
    visited = set([start])
    
    visited_cells_ordered = []
    found_diamonds = []
    diamonds_set = set(diamond_positions)
    
    # Standard 4-connectivity directions (up, down, left, right)
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    while queue:
        curr = queue.popleft()
        visited_cells_ordered.append(curr)
        
        # Checa se a area atual possui um diamante
        if curr in diamonds_set:
            found_diamonds.append(curr)
            # se todos os diamantes forem encontrados a busca e finalizada mais cedo
            if len(found_diamonds) == len(diamond_positions):
                break
                
        # Explora os visinhos
        for dc, dr in directions:
            neighbor = (curr[0] + dc, curr[1] + dr)
            nc, nr = neighbor
            
            # Checa os limites e obseva se os vizinhos possuem passagem(0) ou se ja foram visitados
            if 0 <= nc < cols and 0 <= nr < rows:
                if grid[nc][nr] == 0 and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return {
        'found_diamonds': found_diamonds,
        'visited_cells': visited_cells_ordered,
        'execution_time': execution_time
    }
