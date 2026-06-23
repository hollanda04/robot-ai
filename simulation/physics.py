# modulo responsavel pelas equações cineticas do robo e colisao de objetos/parede

import math
from typing import List, Tuple
from environment.obstacles import Obstacle

def check_collision_at(
    x: float, 
    y: float, 
    radius: float, 
    obstacles: List[Obstacle]
) -> bool:
    # checa se as coordenadas do robo em um raio predeterminado colidiram com algum obstaculo
    for obs in obstacles:
        if obs.collides_with_circle(x, y, radius):
            return True
    return False

def move_with_collision_check(
    x: float, # posiçao
    y: float, # -
    theta: float, # diraçao em radianos
    v: float, # velocidade linear
    w: float, # velocidade angular
    radius: float, # raio fisico do robo
    obstacles: List[Obstacle], #lista de obstaculos no ambiente
    dt: float # tempo gasto em segundos
) -> Tuple[float, float, float]:
# atualiza a cinematica e interpreta a colisão
   
    # 1. atualiza a direção primeiro
    next_theta = theta + w * dt
    next_theta = (next_theta + math.pi) % (2 * math.pi) - math.pi
    
    # 2. tenta se mover em mabas as direções
    dx = v * math.cos(theta) * dt
    dy = v * math.sin(theta) * dt
    
    target_x = x + dx
    target_y = y + dy
    
    # Checa se o movimento esta livre de colisão
    if not check_collision_at(target_x, target_y, radius, obstacles):
        return target_x, target_y, next_theta
        
    # Sliding resolution: tenta-se mover apenas pelo eixo x
    if not check_collision_at(target_x, y, radius, obstacles):
        return target_x, y, next_theta
        
    # Sliding resolution: tenta-se mover apenas pelo eixo y
    if not check_collision_at(x, target_y, radius, obstacles):
        return x, target_y, next_theta
        
    # Locked: colisão em todas as direções
    return x, y, next_theta
