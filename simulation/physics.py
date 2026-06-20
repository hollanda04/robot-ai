import math
from typing import List, Tuple
from environment.obstacles import Obstacle

def update_kinematics(
    x: float,
    y: float,
    theta: float,
    v: float,
    w: float,
    dt: float
) -> Tuple[float, float, float]:

    new_theta = theta + w * dt
    new_theta = (new_theta + math.pi) % (2 * math.pi) - math.pi
    
    dx = v * math.cos(theta) * dt
    dy = v * math.sin(theta) * dt
    
    new_x = x + dx
    new_y = y + dy
    
    return new_x, new_y, new_theta

def check_collision_at(
    x: float, 
    y: float, 
    radius: float, 
    obstacles: List[Obstacle]
) -> bool:
    for obs in obstacles:
        if obs.collides_with_circle(x, y, radius):
            return True
    return False

def move_with_collision_check(
    x: float,
    y: float,
    theta: float,
    v: float,
    w: float,
    radius: float,
    obstacles: List[Obstacle],
    dt: float
) -> Tuple[float, float, float]:
    next_theta = theta + w * dt
    next_theta = (next_theta + math.pi) % (2 * math.pi) - math.pi
    
    dx = v * math.cos(theta) * dt
    dy = v * math.sin(theta) * dt
    
    target_x = x + dx
    target_y = y + dy
    
    if not check_collision_at(target_x, target_y, radius, obstacles):
        return target_x, target_y, next_theta
        
    if not check_collision_at(target_x, y, radius, obstacles):
        return target_x, y, next_theta
        
    if not check_collision_at(x, target_y, radius, obstacles):
        return x, target_y, next_theta
        
    return x, y, next_theta
