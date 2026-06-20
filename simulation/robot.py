import math
from typing import List, Tuple, Dict
from control.pid import PIDController
from control.fuzzy import FuzzyController
from simulation.physics import move_with_collision_check
from environment.map import MazeMap

class Robot:

    def __init__(self, x: float, y: float, theta: float = 0.0):

        self.start_x = x
        self.start_y = y
        self.start_theta = theta
        
        self.x = x
        self.y = y
        self.theta = theta
        
        self.radius = 12.0  
        self.speed = 0.0
        self.omega = 0.0
        
        self.pid = PIDController()
        self.fuzzy = FuzzyController()
        self.controller_type = 'PID'  
        
        self.waypoints: List[Tuple[float, float]] = []  
        self.current_waypoint_idx = 0
        
        self.diamonds_collected: List[Tuple[int, int]] = []
        self.finished = False
        
        self.telemetry = []

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.theta = self.start_theta
        self.speed = 0.0
        self.omega = 0.0
        self.current_waypoint_idx = 0
        self.diamonds_collected = []
        self.finished = False
        self.telemetry = []
        self.pid.reset()
        self.fuzzy.reset()

    def set_path(self, grid_path: List[Tuple[int, int]], map_obj: MazeMap):
        self.reset()
        self.waypoints = [map_obj.grid_to_world(col, row) for col, row in grid_path]

    def switch_controller(self, controller_type: str):
        if controller_type in ['PID', 'Fuzzy']:
            self.controller_type = controller_type
            if controller_type == 'PID':
                self.pid.reset()
            else:
                self.fuzzy.reset()

    def update(self, dt: float, map_obj: MazeMap, elapsed_time: float):

        if self.finished or not self.waypoints:
            self.speed = 0.0
            self.omega = 0.0
            return

        target_x, target_y = self.waypoints[self.current_waypoint_idx]
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_target = math.sqrt(dx**2 + dy**2)
        
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

        if self.controller_type == 'PID':
            self.speed, self.omega = self.pid.compute_control(
                self.x, self.y, self.theta, target_x, target_y, dt
            )
        else: 
            self.speed, self.omega = self.fuzzy.compute_control(
                self.x, self.y, self.theta, target_x, target_y, dt
            )

        self.x, self.y, self.theta = move_with_collision_check(
            self.x, self.y, self.theta,
            self.speed, self.omega,
            self.radius, map_obj.obstacles, dt
        )

        curr_grid_pos = map_obj.world_to_grid(self.x, self.y)
        for d_pos in list(map_obj.diamonds):
            d_x, d_y = map_obj.grid_to_world(d_pos[0], d_pos[1])
            dist_to_diamond = math.sqrt((d_x - self.x)**2 + (d_y - self.y)**2)
            
            if dist_to_diamond < (self.radius + 15.0):
                if d_pos not in self.diamonds_collected:
                    self.diamonds_collected.append(d_pos)
                    map_obj.diamonds.remove(d_pos)  

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
