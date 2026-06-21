"""
This module implements the A* search algorithm and provides functions to sequence
the traversal from Start -> Diamonds (in optimal order) -> End.
"""

import time
import heapq
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
    num_diamonds = len(diamonds)
    
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

    # Distance lookup helper (in grid steps). Unreachable pairs are float('inf').
    def seg_len(a, b):
        p = path_cache.get((a, b))
        return (len(p) - 1) if p else float('inf')

    # --- Held-Karp DP for the diamond visiting order (TSP with fixed start/end) ---
    # dp[mask][i] = (min cost to start at `start`, visit exactly the diamonds in `mask`,
    #                ending at diamond index i)
    # This replaces the previous O(n!) itertools.permutations brute force with an
    # O(2^d * d^2) dynamic programming approach, which scales far better as the
    # number of diamonds grows.
    dp: Dict[Tuple[int, int], float] = {}
    parent: Dict[Tuple[int, int], Optional[int]] = {}

    for i in range(num_diamonds):
        cost = seg_len(start, diamonds[i])
        dp[(1 << i, i)] = cost
        parent[(1 << i, i)] = None

    full_mask = (1 << num_diamonds) - 1
    for mask in range(1, 1 << num_diamonds):
        for i in range(num_diamonds):
            if not (mask & (1 << i)):
                continue
            state = (mask, i)
            if state not in dp:
                continue
            base_cost = dp[state]
            if base_cost == float('inf'):
                continue
            for j in range(num_diamonds):
                if mask & (1 << j):
                    continue
                new_mask = mask | (1 << j)
                new_cost = base_cost + seg_len(diamonds[i], diamonds[j])
                new_state = (new_mask, j)
                if new_cost < dp.get(new_state, float('inf')):
                    dp[new_state] = new_cost
                    parent[new_state] = i

    # Pick the best final diamond to end the diamond-visiting chain on,
    # accounting for the final hop to `end`.
    best_path_len = float('inf')
    best_last = None
    for i in range(num_diamonds):
        state = (full_mask, i)
        if state in dp and dp[state] != float('inf'):
            total = dp[state] + seg_len(diamonds[i], end)
            if total < best_path_len:
                best_path_len = total
                best_last = i

    # Reconstruct the optimal visiting order from the parent pointers
    best_order_idx: List[int] = []
    if best_last is not None:
        mask = full_mask
        i = best_last
        while i is not None:
            best_order_idx.append(i)
            prev_i = parent[(mask, i)]
            mask &= ~(1 << i)
            i = prev_i
        best_order_idx.reverse()

    best_permutation = tuple(diamonds[i] for i in best_order_idx) if best_order_idx else None

    # Build the segments for the chosen order: start -> d1 -> d2 -> ... -> end
    best_segments = []
    if best_permutation is not None:
        route = [start] + list(best_permutation) + [end]
        valid_route = True
        for k in range(len(route) - 1):
            seg_path = path_cache.get((route[k], route[k + 1]))
            if seg_path is None:
                valid_route = False
                break
            best_segments.append(seg_path)
        if not valid_route:
            best_segments = []
            best_permutation = None

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