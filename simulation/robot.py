"""
This module defines the Robot class, which maintains the agent's state,
invokes the active controller (PID or Fuzzy), handles path tracking,
and logs telemetry metrics.
"""

import math
from typing import List, Tuple, Dict
from control.pid import PIDController
from control.fuzzy import FuzzyController
from control.base_controller import BaseController
from simulation.physics import move_with_collision_check
from environment.map import MazeMap

class Robot:
    """
    Represents the explorer robot agent in the simulation.
    Manages kinematic state, path tracking, collision handling,
    and telemetry logging.
    """

    def __init__(self, x: float, y: float, theta: float = 0.0):
        """
        Initializes the Robot.
        
        Args:
            x (float): Initial x position in pixels.
            y (float): Initial y position in pixels.
            theta (float): Initial orientation in radians.
        """
        self.start_x = x
        self.start_y = y
        self.start_theta = theta
        
        self.x = x
        self.y = y
        self.theta = theta
        
        self.radius = 12.0  # Physical radius for wall collisions
        self.speed = 0.0
        self.omega = 0.0
        
        # Controllers (any object implementing BaseController can be plugged in here)
        self.controllers: Dict[str, BaseController] = {
            'PID': PIDController(),
            'Fuzzy': FuzzyController()
        }
        self.controller_type = 'PID'  # Default controller
        
        # Path tracking
        self.waypoints: List[Tuple[float, float]] = []  # In pixel coordinates
        self.current_waypoint_idx = 0
        
        # Gameplay states
        self.diamonds_collected: List[Tuple[int, int]] = []
        self.finished = False
        
        # Telemetry log
        self.telemetry = []

    @property
    def active_controller(self) -> BaseController:
        """Returns the currently active controller instance."""
        return self.controllers[self.controller_type]

    def reset(self):
        """Resets the robot to its starting conditions and clears logs."""
        self.x = self.start_x
        self.y = self.start_y
        self.theta = self.start_theta
        self.speed = 0.0
        self.omega = 0.0
        self.current_waypoint_idx = 0
        self.diamonds_collected = []
        self.finished = False
        self.telemetry = []
        for controller in self.controllers.values():
            controller.reset()

    def set_path(self, grid_path: List[Tuple[int, int]], map_obj: MazeMap):
        """
        Converts grid path to pixel waypoints and sets them for the robot.
        
        Args:
            grid_path (List[Tuple[int, int]]): Path coordinates in grid index format.
            map_obj (MazeMap): Map object for coordinate conversions.
        """
        self.reset()
        self.waypoints = [map_obj.grid_to_world(col, row) for col, row in grid_path]

    def switch_controller(self, controller_type: str):
        """Switches the active controller type and resets its internal state."""
        if controller_type in self.controllers:
            self.controller_type = controller_type
            self.controllers[controller_type].reset()

    def update(self, dt: float, map_obj: MazeMap, elapsed_time: float):
        """
        Updates the robot's movement, waypoints, diamond collection,
        and logs telemetry metrics.
        
        Args:
            dt (float): Time step in seconds.
            map_obj (MazeMap): Map environment object.
            elapsed_time (float): Current elapsed simulation time in seconds.
        """
        if self.finished or not self.waypoints:
            self.speed = 0.0
            self.omega = 0.0
            return

        # 1. Get current target waypoint
        target_x, target_y = self.waypoints[self.current_waypoint_idx]
        
        # 2. Check if we reached the current waypoint
        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_target = math.sqrt(dx**2 + dy**2)
        
        # Waypoint acceptance threshold (e.g. 10 pixels)
        # If it's the final waypoint, we want to be closer (e.g. 5 pixels)
        is_last = (self.current_waypoint_idx == len(self.waypoints) - 1)
        threshold = 5.0 if is_last else 12.0
        
        if dist_to_target < threshold:
            if is_last:
                self.finished = True
                self.speed = 0.0
                self.omega = 0.0
                return
            else:
                self.current_waypoint_idx += 1
                target_x, target_y = self.waypoints[self.current_waypoint_idx]
        
        # 3. Call active controller to compute velocity inputs (polymorphic dispatch)
        self.speed, self.omega = self.active_controller.compute_control(
            self.x, self.y, self.theta, target_x, target_y, dt
        )

        # 4. Apply kinematics update with collision checks
        self.x, self.y, self.theta = move_with_collision_check(
            self.x, self.y, self.theta,
            self.speed, self.omega,
            self.radius, map_obj.obstacles, dt
        )

        # 5. Check for diamond collection
        # Check proximity to any uncollected diamond on the map
        curr_grid_pos = map_obj.world_to_grid(self.x, self.y)
        for d_pos in list(map_obj.diamonds):
            d_x, d_y = map_obj.grid_to_world(d_pos[0], d_pos[1])
            dist_to_diamond = math.sqrt((d_x - self.x)**2 + (d_y - self.y)**2)
            
            # If robot is close to a diamond, collect it
            if dist_to_diamond < (self.radius + 15.0):
                if d_pos not in self.diamonds_collected:
                    self.diamonds_collected.append(d_pos)
                    map_obj.diamonds.remove(d_pos)  # Remove from map so it disappears

        # 6. Log telemetry for later analysis
        # Calculate current heading error for metrics
        t_theta = math.atan2(target_y - self.y, target_x - self.x)
        err_theta = t_theta - self.theta
        err_theta = (err_theta + math.pi) % (2 * math.pi) - math.pi
        
        self.telemetry.append({
            'time': elapsed_time,
            'x': self.x,
            'y': self.y,
            'speed': self.speed,
            'omega': self.omega,
            'angle_error_deg': math.degrees(err_theta),
            'controller': self.controller_type,
            'dist_to_waypoint': dist_to_target
        })