"""
This module implements the Breadth-First Search (BFS) algorithm.
The agent uses BFS to scan the map, locate diamonds, and log visited cells.
"""

import time
from collections import deque
from typing import List, Tuple, Dict

def bfs_find_diamonds(
    grid: List[List[int]], 
    start: Tuple[int, int], 
    diamond_positions: List[Tuple[int, int]]
) -> Dict:
    """
    Performs a Breadth-First Search (BFS) starting from the robot's initial grid position
    to search/discover the coordinates of all diamonds in the maze.
    
    Args:
        grid (List[List[int]]): 2D grid of the map (0 for passage, 1 for wall).
        start (Tuple[int, int]): Starting coordinates (col, row).
        diamond_positions (List[Tuple[int, int]]): The actual positions of diamonds on the map.
        
    Returns:
        Dict: A dictionary containing:
            - 'found_diamonds': List of discovered diamond coordinates in the order found.
            - 'visited_cells': List of coordinates (col, row) visited during the search (for animation/metrics).
            - 'execution_time': Time taken in seconds.
    """
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
        
        # Check if current cell contains a diamond
        if curr in diamonds_set:
            found_diamonds.append(curr)
            # If we've found all spawned diamonds, we can stop the search early
            if len(found_diamonds) == len(diamond_positions):
                break
                
        # Explore neighbors
        for dc, dr in directions:
            neighbor = (curr[0] + dc, curr[1] + dr)
            nc, nr = neighbor
            
            # Check boundaries and if neighbor is walkable (0) and not yet visited
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
