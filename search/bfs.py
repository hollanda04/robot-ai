import time
from collections import deque
from typing import List, Tuple, Dict

def bfs_find_diamonds(
    grid: List[List[int]], 
    start: Tuple[int, int], 
    diamond_positions: List[Tuple[int, int]]
) -> Dict:

    start_time = time.perf_counter()
    
    cols = len(grid)
    rows = len(grid[0])
    
    queue = deque([start])
    visited = set([start])
    
    visited_cells_ordered = []
    found_diamonds = []
    diamonds_set = set(diamond_positions)
    
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    while queue:
        curr = queue.popleft()
        visited_cells_ordered.append(curr)
        
        if curr in diamonds_set:
            found_diamonds.append(curr)
            if len(found_diamonds) == len(diamond_positions):
                break
                
        for dc, dr in directions:
            neighbor = (curr[0] + dc, curr[1] + dr)
            nc, nr = neighbor
            
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
