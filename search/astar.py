import time
import heapq
import itertools
from typing import List, Tuple, Dict, Optional

def astar_search(
    grid: List[List[int]], 
    start: Tuple[int, int], 
    goal: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:

    cols = len(grid)
    rows = len(grid[0])
    
    def heuristic(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start, [start]))
    
    g_scores = {start: 0}
    
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    while open_set:
        f, g, curr, path = heapq.heappop(open_set)
        
        if curr == goal:
            return path
            
        if g > g_scores.get(curr, float('inf')):
            continue
            
        for dc, dr in directions:
            neighbor = (curr[0] + dc, curr[1] + dr)
            nc, nr = neighbor
            
            if 0 <= nc < cols and 0 <= nr < rows and grid[nc][nr] == 0:
                tentative_g = g + 1  
                
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

    start_time = time.perf_counter()
    
    if not diamonds:
        path = astar_search(grid, start, end)
        end_time = time.perf_counter()
        return {
            'complete_path': path or [],
            'segments': [path] if path else [],
            'execution_time': end_time - start_time,
            'ordered_targets': [end]
        }

    nodes = [start] + list(diamonds) + [end]
    n = len(nodes)
    
    path_cache = {}
    
    for i in range(n):
        for j in range(n):
            if i != j:
                p = astar_search(grid, nodes[i], nodes[j])
                path_cache[(nodes[i], nodes[j])] = p

    best_path_len = float('inf')
    best_permutation = None
    best_complete_path = []
    best_segments = []

    diamond_perms = list(itertools.permutations(diamonds))
    
    for perm in diamond_perms:
        current_route = [start] + list(perm) + [end]
        valid_route = True
        total_len = 0
        route_segments = []
        
        for k in range(len(current_route) - 1):
            from_node = current_route[k]
            to_node = current_route[k+1]
            seg_path = path_cache.get((from_node, to_node))
            
            if seg_path is None:
                valid_route = False
                break
            
            route_segments.append(seg_path)
            total_len += len(seg_path) - 1
            
        if valid_route and total_len < best_path_len:
            best_path_len = total_len
            best_permutation = perm
            best_segments = route_segments

    complete_path = []
    if best_segments:
        complete_path.extend(best_segments[0])
        for seg in best_segments[1:]:
            complete_path.extend(seg[1:]) 

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    ordered_targets = list(best_permutation) + [end] if best_permutation else [end]

    return {
        'complete_path': complete_path,
        'segments': best_segments,
        'execution_time': execution_time,
        'ordered_targets': ordered_targets
    }
