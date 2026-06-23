#modulo responsavel por implementar o controlador fuzzy do robo, utilizando funçoes de pertinencia customizadas e regras de inferencia estilo Sugeno para controle suave de velocidade e direcao baseado no erro de direçao e distancia.

import math
from typing import Tuple
from control.base_controller import BaseController

class FuzzyController(BaseController):
    # um controle de logica fuzzy customizado que calcula a velocidade linear e angular. Evita dependencias externas como scikit-fuzzy usando funçoes de pertinencia analiticas customizadas e inferencia de regras singleton estilo Sugeno.    

    def __init__(self, max_v: float = 120.0, max_w: float = 4.0):
        #inicializa o controlador fuzzy
        self.max_v = max_v
        self.max_w = max_w

    def reset(self):
        # resta o estado interno (não necessário para regras fuzzy estáticas, mas mantém a interface uniforme).
        pass

    # --- Membership Functions for Angle Error (e) ---
    def _mu_angle_left(self, e: float) -> float:
        #LN (Left / Negative error): o robo precisa virar para a esquerda (velocidade angular positiva).
        # Peak at -pi, goes to 0 at -0.2
        if e <= -0.4:
            return 1.0
        elif -0.4 < e < 0.0:
            return e / -0.4
        else:
            return 0.0

    def _mu_angle_center(self, e: float) -> float:
        #ze (center / zero error): o robo esta apontando para o alvo.
        # Triangular peak at 0, goes to 0 at -0.4 and 0.4
        if e <= -0.4 or e >= 0.4:
            return 0.0
        elif -0.4 < e < 0.0:
            return (e + 0.4) / 0.4
        else:  # 0 <= e < 0.4
            return (0.4 - e) / 0.4

    def _mu_angle_right(self, e: float) -> float:
        #LP (Right / Positive error): o robo precisa virar para a direita (velocidade angular negativa).
        # Peak at pi, goes to 0 at 0.2
        if e <= 0.0:
            return 0.0
        elif 0.0 < e < 0.4:
            return e / 0.4
        else:
            return 1.0

    # --- Membership Functions for Distance (d) ---
    def _mu_dist_close(self, d: float) -> float:
        #CL (Close): o robo esta proximo do waypoint.
        if d <= 5.0:
            return 1.0
        elif 5.0 < d < 18.0:
            return (18.0 - d) / 13.0
        else:
            return 0.0

    def _mu_dist_medium(self, d: float) -> float:
        #MD (Medium): o robo esta a uma distancia moderada.
        if d <= 18.0 or d >= 110.0:
            return 0.0
        elif 18.0 < d <= 60.0:
            return (d - 18.0) / 42.0
        else:  # 60.0 < d < 110.0
            return (110.0 - d) / 50.0

    def _mu_dist_far(self, d: float) -> float:
        #FR (Far): o robo esta longe do waypoint.
        if d <= 55.0:
            return 0.0
        elif 55.0 < d < 120.0:
            return (d - 55.0) / 65.0
        else:
            return 1.0

    def compute_control(
        self, 
        x: float, 
        y: float, 
        theta: float, 
        target_x: float, 
        target_y: float, 
        dt: float
    ) -> Tuple[float, float]:
        # computa as saídas do controlador fuzzy (v, w) com base no estado atual e no alvo.
        
        dx = target_x - x
        dy = target_y - y
        d = math.sqrt(dx**2 + dy**2)
        
        # angulo alvo
        target_theta = math.atan2(dy, dx)
        
        # Heading error normalized to [-pi, pi]
        e = target_theta - theta
        e = (e + math.pi) % (2 * math.pi) - math.pi

        # Fuzzify inputs
        mu_ln = self._mu_angle_left(e)   # steering left
        mu_ze = self._mu_angle_center(e) # straight
        mu_lp = self._mu_angle_right(e)  # steering right
        
        mu_cl = self._mu_dist_close(d)
        mu_md = self._mu_dist_medium(d)
        mu_fr = self._mu_dist_far(d)

        # --- Rule Inference & Defuzzification (Sugeno style) ---
        
        # 1. Steering output (w) rules:
        # Rule 1: IF e is Left (LN) THEN w is Max Right (negative)
        # Note: If target is to the left of the robot (negative error), the robot needs to turn left.
        # Let's clarify: math.atan2 gives the absolute angle. If target_theta = 0 and robot theta = pi/2 (pointing up),
        # error e = 0 - pi/2 = -pi/2 (Negative/LN). To orient towards 0, the robot must turn right (negative angular velocity w).
        # So: LN (Negative Error) => w should be Negative (Turn Right).
        # LP (Positive Error) => w should be Positive (Turn Left).
        # Let's verify: target_theta = pi/2 (pointing up) and robot theta = 0 (pointing right).
        # error e = pi/2 - 0 = +pi/2 (Positive/LP). Robot must turn left (positive w). Correct!
        #
        # So:
        # - LN (Negative error) => Turn Right (w = -max_w)
        # - ZE (Zero error)     => Go Straight (w = 0)
        # - LP (Positive error) => Turn Left (w = +max_w)
        
        w_numerator = (mu_ln * (-self.max_w)) + (mu_ze * 0.0) + (mu_lp * self.max_w)
        w_denominator = mu_ln + mu_ze + mu_lp
        
        w = w_numerator / w_denominator if w_denominator > 0 else 0.0

        # 2. Linear speed (v) rules:
        # We define rules for speed depending on distance and heading error.
        # Rule V1: IF dist is Close (CL) THEN speed is Slow (v_slow = 0.1 * max_v)
        # Rule V2: IF dist is Medium (MD) AND error is ZE THEN speed is Medium (v_med = 0.6 * max_v)
        # Rule V3: IF dist is Far (FR) AND error is ZE THEN speed is Fast (v_fast = 1.0 * max_v)
        # Rule V4: IF error is NOT ZE (LN or LP) THEN speed is Slow (v_slow_turn = 0.15 * max_v)

        v_slow = 0.10 * self.max_v
        v_med  = 0.60 * self.max_v
        v_fast = 1.00 * self.max_v
        v_turn = 0.35 * self.max_v

        a1 = mu_cl
        a2 = min(mu_md, mu_ze)
        a3 = min(mu_fr, mu_ze)
        a4 = max(mu_ln, mu_lp)

        v_numerator = (a1 * v_slow) + (a2 * v_med) + (a3 * v_fast) + (a4 * v_turn)
        v_denominator = a1 + a2 + a3 + a4

        v = v_numerator / v_denominator if v_denominator > 0 else 0.0

        # para completamente se a distancia for extremamente pequena
        if d < 3.0:
            v = 0.0
            w = 0.0

        return v, w
