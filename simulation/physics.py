"""
This module handles the kinematic equations of the robot (unicycle model)
and resolves wall collisions to allow smooth sliding movement.
"""

import math
from typing import List, Tuple
from environment.obstacles import Obstacle

def check_collision_at(
    x: float, 
    y: float, 
    radius: float, 
    obstacles: List[Obstacle]
) -> bool:
    """Checks if a circle at (x, y) with a given radius collides with any obstacles."""
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
    """
    Updates kinematics and resolves collisions using a sliding response.
    
    Args:
        x (float): Current x position.
        y (float): Current y position.
        theta (float): Current heading in radians.
        v (float): Linear velocity.
        w (float): Angular velocity.
        radius (float): Robot physical radius.
        obstacles (List[Obstacle]): List of obstacles in the environment.
        dt (float): Time step in seconds.
        
    Returns:
        Tuple[float, float, float]: (final_x, final_y, final_theta)
    """
    # 1. Update heading first (steering has no direct spatial collision)
    next_theta = theta + w * dt
    next_theta = (next_theta + math.pi) % (2 * math.pi) - math.pi
    
    # 2. Try to move in both directions (full step)
    dx = v * math.cos(theta) * dt
    dy = v * math.sin(theta) * dt
    
    target_x = x + dx
    target_y = y + dy
    
    # Check if full step is collision-free
    if not check_collision_at(target_x, target_y, radius, obstacles):
        return target_x, target_y, next_theta
        
    # Sliding resolution: Try moving only in X-axis
    if not check_collision_at(target_x, y, radius, obstacles):
        return target_x, y, next_theta
        
    # Sliding resolution: Try moving only in Y-axis
    if not check_collision_at(x, target_y, radius, obstacles):
        return x, target_y, next_theta
        
    # Locked: Collision in all sliding directions, freeze position
    return x, y, next_theta