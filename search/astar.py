"""
This module implements the A* search algorithm and provides functions to sequence
the traversal from Start -> Diamonds (in optimal order) -> End.
"""

import time
import heapq
import itertools
from typing import List, Tuple, Dict, Optional

def astar_search(
    grid: List[List[int]], 
    start: Tuple[int, int], 
    goal: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """
    Performs A* search to find the shortest path from start to goal.
    
    Args:
        grid (List[List[int]]): 2D grid map (0 = walkable, 1 = wall).
        start (Tuple[int, int]): Start grid coordinates (col, row).
        goal (Tuple[int, int]): Goal grid coordinates (col, row).
        
    Returns:
        Optional[List[Tuple[int, int]]]: List of coordinates representing the path,
                                         or None if no path exists.
    """
    cols = len(grid)
    rows = len(grid[0])
    
    # Manhattan distance heuristic
    def heuristic(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    # Priority queue: stores (f_score, g_score, current_node, path)
    # g_score is the cost to reach the node. f_score = g_score + heuristic
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start, [start]))
    
    # Track the minimum g_score to each node
    g_scores = {start: 0}
    
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    while open_set:
        f, g, curr, path = heapq.heappop(open_set)
        
        if curr == goal:
            return path
            
        # If we found a shorter path to curr already, skip
        if g > g_scores.get(curr, float('inf')):
            continue
            
        for dc, dr in directions:
            neighbor = (curr[0] + dc, curr[1] + dr)
            nc, nr = neighbor
            
            if 0 <= nc < cols and 0 <= nr < rows and grid[nc][nr] == 0:
                tentative_g = g + 1  # grid step cost is 1
                
                if tentative_g < g_scores.get(neighbor, float('inf')):
                    g_scores[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor, path + [neighbor]))
                    
    return None

def calculate_optimal_route(
    grid: List[List[int]], 
    start: Tuple[int, int], 
    diamonds: List[Tuple[int, int]], 
    end: Tuple[int, int]
) -> Dict:
    """
    Computes A* paths between Start, Diamonds, and End, and evaluates all 
    permutations of diamond visitations to find the global minimum distance path.
    
    Args:
        grid (List[List[int]]): 2D grid map.
        start (Tuple[int, int]): Start grid coordinate.
        diamonds (List[Tuple[int, int]]): Discovered diamond coordinates.
        end (Tuple[int, int]): End grid coordinate.
        
    Returns:
        Dict: A dictionary containing:
            - 'complete_path': Concentrated list of grid coordinates for the optimized route.
            - 'segments': List of individual path segments (e.g., Start->D1, D1->D2, etc.).
            - 'execution_time': Total A* and routing planning time in seconds.
            - 'ordered_targets': List of targets in the optimal visit order.
    """
    start_time = time.perf_counter()
    
    # If no diamonds, just find path from start to end
    if not diamonds:
        path = astar_search(grid, start, end)
        end_time = time.perf_counter()
        return {
            'complete_path': path or [],
            'segments': [path] if path else [],
            'execution_time': end_time - start_time,
            'ordered_targets': [end]
        }

    # Precalculate A* paths between all pairs in {start, d1, d2, d3, end}
    # Nodes list
    nodes = [start] + list(diamonds) + [end]
    n = len(nodes)
    
    # Memoization dictionary for A* paths: key is (from, to)
    path_cache = {}
    
    # Run A* for necessary pairs
    # Note: We need Start -> D_i, D_i -> D_j, and D_i -> End
    # Let's compute all combinations
    for i in range(n):
        for j in range(n):
            if i != j:
                # We can run A* and cache it
                p = astar_search(grid, nodes[i], nodes[j])
                path_cache[(nodes[i], nodes[j])] = p

    # Evaluate permutations of diamonds
    best_path_len = float('inf')
    best_permutation = None
    best_complete_path = []
    best_segments = []

    # Get all permutations of diamonds
    diamond_perms = list(itertools.permutations(diamonds))
    
    for perm in diamond_perms:
        current_route = [start] + list(perm) + [end]
        valid_route = True
        total_len = 0
        route_segments = []
        
        # Calculate route length
        for k in range(len(current_route) - 1):
            from_node = current_route[k]
            to_node = current_route[k+1]
            seg_path = path_cache.get((from_node, to_node))
            
            if seg_path is None:
                valid_route = False
                break
            
            route_segments.append(seg_path)
            # Subtract 1 to avoid double counting joint nodes in length calculation
            total_len += len(seg_path) - 1
            
        if valid_route and total_len < best_path_len:
            best_path_len = total_len
            best_permutation = perm
            best_segments = route_segments

    # Concatenate segments into one continuous path without repeating joint nodes
    complete_path = []
    if best_segments:
        complete_path.extend(best_segments[0])
        for seg in best_segments[1:]:
            complete_path.extend(seg[1:])  # Skip first node as it's the same as previous segment's last

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    ordered_targets = list(best_permutation) + [end] if best_permutation else [end]

    return {
        'complete_path': complete_path,
        'segments': best_segments,
        'execution_time': execution_time,
        'ordered_targets': ordered_targets
    }
