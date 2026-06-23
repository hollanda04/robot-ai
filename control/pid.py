#modulo responsavel pelo controle do PID para controlar a direçao e velocidade do robo para os marcadores

import math
from typing import Tuple
from control.base_controller import BaseController

class PIDController(BaseController):
    #controle pid que determina os comandos de velocidade angular e linear para um piloto robo diferencial para seguir um percurso

    def __init__(
        self, 
        kp_theta: float = 6.0, 
        ki_theta: float = 0.02, 
        kd_theta: float = 0.4,
        max_v: float = 120.0,  # Max pixels por segundo
        max_w: float = 4.0     # Max radians por segundo
    ):
        #inicializa o controle pid
        self.kp_theta = kp_theta # ganho proporcional para erro de direçao
        self.ki_theta = ki_theta # ganho integra para erro de direçao
        self.kd_theta = kd_theta # ganho derivado para erro de direçao
        self.max_v = max_v # velocidade linear maxima permitida 
        self.max_w = max_w # velocidade angular maxima permitida
        
        # controle de estado variavel
        self.prev_error_theta = 0.0
        self.integral_theta = 0.0

    def reset(self):
        # reinicia o estado de erro da derivada e integral
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
        # computa o controle dos inputs (v,w) baseado no estado e alvo do robor
        if dt <= 0.0:
            return 0.0, 0.0
            
        # 1. calcula a distancia e angulo do alvo
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        target_theta = math.atan2(dy, dx)
        
        # 2. erro angular (normalized to [-pi, pi])
        error_theta = target_theta - theta
        error_theta = (error_theta + math.pi) % (2 * math.pi) - math.pi
        
        # 3. logica PID logic para velocidade angular (w)
        # termo integra com anti-windup (clamp integral)
        self.integral_theta += error_theta * dt
        self.integral_theta = max(-5.0, min(self.integral_theta, 5.0))
        
        # termo derivativo
        derivative_theta = (error_theta - self.prev_error_theta) / dt
        self.prev_error_theta = error_theta
        
        # Controla sinal para velocidade angular
        w = (self.kp_theta * error_theta) + (self.ki_theta * self.integral_theta) + (self.kd_theta * derivative_theta)
        # Clamp angular velocity
        w = max(-self.max_w, min(w, self.max_w))
        
        # 4. controla logica para velocidade linear (v) 
        # se erro de direçao e grande, desacelere ou pare para mudar de direçao no lugar
        # previne que o robo tenha overshooting dos marcadores em curvas fechadas
        angle_scaling = max(0.0, math.cos(error_theta))  # Scale speed with cos(error)
        
        #controle proporcional de velocidade baseada em distancia
        # desacelera quando se aproxima do alvo (within 30 pixels)
        speed_factor = min(1.0, distance / 30.0)
        v = self.max_v * speed_factor * angle_scaling
        
        # para completamente se a distancia e extremamente pequena
        if distance < 3.0:
            v = 0.0
            w = 0.0
            
        return v, w
