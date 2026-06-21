"""
This module implements a Proporcional-Integral-Derivative (PID) controller 
for controlling the robot's steering and speed toward waypoints.
"""

import math
from typing import Tuple
from control.base_controller import BaseController

class PIDController(BaseController):
    """
    A PID controller that determines linear and angular velocity commands
    for a differential drive robot to follow a path.
    """
    
    def __init__(
        self, 
        kp_theta: float = 6.0, 
        ki_theta: float = 0.02, 
        kd_theta: float = 0.4,
        max_v: float = 120.0,  # Max pixels per second
        max_w: float = 4.0     # Max radians per second
    ):
        """
        Initializes the PID controller.
        
        Args:
            kp_theta (float): Proportional gain for heading error.
            ki_theta (float): Integral gain for heading error.
            kd_theta (float): Derivative gain for heading error.
            max_v (float): Maximum allowed linear velocity.
            max_w (float): Maximum allowed angular velocity.
        """
        self.kp_theta = kp_theta
        self.ki_theta = ki_theta
        self.kd_theta = kd_theta
        self.max_v = max_v
        self.max_w = max_w
        
        # Controller state variables
        self.prev_error_theta = 0.0
        self.integral_theta = 0.0

    def reset(self):
        """Resets the integral and derivative state variables."""
        self.prev_error_theta = 0.0
        self.integral_theta = 0.0

    def compute_control(
        self, 
        x: float, 
        y: float, 
        theta: float, 
        target_x: float, 
        target_y: float, 
        dt: float
    ) -> Tuple[float, float]:
        """
        Computes the control inputs (v, w) based on the robot's state and target.
        
        Args:
            x (float): Current robot x-coordinate.
            y (float): Current robot y-coordinate.
            theta (float): Current robot heading in radians.
            target_x (float): Target waypoint x-coordinate.
            target_y (float): Target waypoint y-coordinate.
            dt (float): Time step in seconds.
            
        Returns:
            Tuple[float, float]: (linear_velocity, angular_velocity)
        """
        if dt <= 0.0:
            return 0.0, 0.0
            
        # 1. Calculate distance and angle to target
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        target_theta = math.atan2(dy, dx)
        
        # 2. Angle Error (normalized to [-pi, pi])
        error_theta = target_theta - theta
        error_theta = (error_theta + math.pi) % (2 * math.pi) - math.pi
        
        # 3. PID logic for angular velocity (w)
        # Integral term with anti-windup (clamp integral)
        self.integral_theta += error_theta * dt
        self.integral_theta = max(-5.0, min(self.integral_theta, 5.0))
        
        # Derivative term
        derivative_theta = (error_theta - self.prev_error_theta) / dt
        self.prev_error_theta = error_theta
        
        # Control signal for angular velocity
        w = (self.kp_theta * error_theta) + (self.ki_theta * self.integral_theta) + (self.kd_theta * derivative_theta)
        # Clamp angular velocity
        w = max(-self.max_w, min(w, self.max_w))
        
        # 4. Control logic for linear velocity (v)
        # If heading error is large, slow down or stop to turn in place
        # This prevents the robot from overshooting waypoints in sharp turns
        angle_scaling = max(0.0, math.cos(error_theta))  # Scale speed with cos(error)
        
        # Proportional control for speed based on distance
        # Slow down as we approach the target (within 30 pixels)
        speed_factor = min(1.0, distance / 30.0)
        v = self.max_v * speed_factor * angle_scaling
        
        # Stop completely if distance is extremely small
        if distance < 3.0:
            v = 0.0
            w = 0.0
            
        return v, w