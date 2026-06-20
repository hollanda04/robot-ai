import math
from typing import Tuple

class PIDController:

    
    def __init__(
        self, 
        kp_theta: float = 6.0, 
        ki_theta: float = 0.02, 
        kd_theta: float = 0.4,
        max_v: float = 120.0,  
        max_w: float = 4.0     
    ):

        self.kp_theta = kp_theta
        self.ki_theta = ki_theta
        self.kd_theta = kd_theta
        self.max_v = max_v
        self.max_w = max_w
        
        
        self.prev_error_theta = 0.0
        self.integral_theta = 0.0

    def reset(self):
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
        if dt <= 0.0:
            return 0.0, 0.0
            
        
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        target_theta = math.atan2(dy, dx)
        
       
        error_theta = target_theta - theta
        error_theta = (error_theta + math.pi) % (2 * math.pi) - math.pi
        
        self.integral_theta += error_theta * dt
        self.integral_theta = max(-5.0, min(self.integral_theta, 5.0))
        
        derivative_theta = (error_theta - self.prev_error_theta) / dt
        self.prev_error_theta = error_theta

        w = (self.kp_theta * error_theta) + (self.ki_theta * self.integral_theta) + (self.kd_theta * derivative_theta)
        w = max(-self.max_w, min(w, self.max_w))
        
        angle_scaling = max(0.0, math.cos(error_theta))  
        
        speed_factor = min(1.0, distance / 30.0)
        v = self.max_v * speed_factor * angle_scaling
        
        if distance < 3.0:
            v = 0.0
            w = 0.0
            
        return v, w
