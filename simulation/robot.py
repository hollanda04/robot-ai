# modulo responsavel por definir a classe robo, responsavel pelo estado do agente, a ativação dos controles pid e fuzzy, responsavel pelo rastreamento de caminho e dos registros telemetricos

import math
from typing import List, Tuple, Dict
from control.pid import PIDController
from control.fuzzy import FuzzyController
from control.base_controller import BaseController
from simulation.physics import move_with_collision_check
from environment.map import MazeMap

class Robot:
    # representa o agente robor na simulaçao e e responsavel pelas mesmas informações ditas no começo

    def __init__(self, x: float, y: float, theta: float = 0.0):
        # inicializa o robo
        
        self.start_x = x # posiçao inical em pixels
        self.start_y = y # -
        self.start_theta = theta # orientação inicial em radianos
        
        self.x = x
        self.y = y
        self.theta = theta
        
        self.radius = 12.0  # raio fisico para colisão com a parede
        self.speed = 0.0
        self.omega = 0.0
        
        # Controles
        self.controllers: Dict[str, BaseController] = {
            'PID': PIDController(),
            'Fuzzy': FuzzyController()
        }
        self.controller_type = 'PID'  # controle padrao
        
        # rastreamento de percusso
        self.waypoints: List[Tuple[float, float]] = []  # cordenadas em pixel
        self.current_waypoint_idx = 0
        
        # estado de gameplay
        self.diamonds_collected: List[Tuple[int, int]] = []
        self.finished = False
        
        # registro telemetrico
        self.telemetry = []

    @property
    def active_controller(self) -> BaseController:
        #retorna o estado de ativação atual do controle
        return self.controllers[self.controller_type]

    def reset(self):
        # reinicia o robo para ascondiçoes iniciais e dos registros
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
        #corverte o campo/area para pixels marcadores e marca eles para o robo
        
        self.reset()
        self.waypoints = [map_obj.grid_to_world(col, row) for col, row in grid_path]

    def switch_controller(self, controller_type: str):
        #muda de controle e reinicia o seu estado
        if controller_type in self.controllers:
            self.controller_type = controller_type
            self.controllers[controller_type].reset()

    def update(self, dt: float, map_obj: MazeMap, elapsed_time: float):
        #atualiza o movimento, marcadores, coleta de diamantes e registros de telemetria para o robo
        if self.finished or not self.waypoints:
            self.speed = 0.0
            self.omega = 0.0
            return

        # 1. pega os alvos atuais dos marcadores
        target_x, target_y = self.waypoints[self.current_waypoint_idx]
        
        # 2. checa se ele chegou ao marcado atual
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
        
        # 3. chama o controle ativo para computar a velocidade (polymorphic dispatch) 
        self.speed, self.omega = self.active_controller.compute_control(
            self.x, self.y, self.theta, target_x, target_y, dt
        )

        # 4. plica a atualizaçao cinetica com a checagem de colisao
        self.x, self.y, self.theta = move_with_collision_check(
            self.x, self.y, self.theta,
            self.speed, self.omega,
            self.radius, map_obj.obstacles, dt
        )

        # 5. Checa se o diamante foi coletado
        # Checa a proximidade de qualquer diamante nao coletado no mapa
        curr_grid_pos = map_obj.world_to_grid(self.x, self.y)
        for d_pos in list(map_obj.diamonds):
            d_x, d_y = map_obj.grid_to_world(d_pos[0], d_pos[1])
            dist_to_diamond = math.sqrt((d_x - self.x)**2 + (d_y - self.y)**2)
            
            # se o robo esta perto do diamante ele ira coletalo
            if dist_to_diamond < (self.radius + 15.0):
                if d_pos not in self.diamonds_collected:
                    self.diamonds_collected.append(d_pos)
                    map_obj.diamonds.remove(d_pos)  # o remove do map e disaparece

        # 6. registra telemetria para analise posterior
        # Calcula o erro de rumo para as metricas
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
