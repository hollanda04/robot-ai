import math
from typing import Tuple

class FuzzyController:


    def __init__(self, max_v: float = 120.0, max_w: float = 4.0):

        self.max_v = max_v
        self.max_w = max_w

    def reset(self):

        pass


    def _mu_angle_left(self, e: float) -> float:

        if e <= -0.4:
            return 1.0
        elif -0.4 < e < 0.0:
            return e / -0.4
        else:
            return 0.0

    def _mu_angle_center(self, e: float) -> float:

        if e <= -0.4 or e >= 0.4:
            return 0.0
        elif -0.4 < e < 0.0:
            return (e + 0.4) / 0.4
        else:  # 0 <= e < 0.4
            return (0.4 - e) / 0.4

    def _mu_angle_right(self, e: float) -> float:
        if e <= 0.0:
            return 0.0
        elif 0.0 < e < 0.4:
            return e / 0.4
        else:
            return 1.0

    def _mu_dist_close(self, d: float) -> float:

        if d <= 8.0:
            return 1.0
        elif 8.0 < d < 40.0:
            return (40.0 - d) / 32.0
        else:
            return 0.0

    def _mu_dist_medium(self, d: float) -> float:

        if d <= 15.0 or d >= 90.0:
            return 0.0
        elif 15.0 < d <= 40.0:
            return (d - 15.0) / 25.0
        else:  # 40.0 < d < 90.0
            return (90.0 - d) / 50.0

    def _mu_dist_far(self, d: float) -> float:

        if d <= 40.0:
            return 0.0
        elif 40.0 < d < 100.0:
            return (d - 40.0) / 60.0
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

        dx = target_x - x
        dy = target_y - y
        d = math.sqrt(dx**2 + dy**2)
        
        
        target_theta = math.atan2(dy, dx)
        
        e = target_theta - theta
        e = (e + math.pi) % (2 * math.pi) - math.pi

       
        mu_ln = self._mu_angle_left(e)   
        mu_ze = self._mu_angle_center(e) 
        mu_lp = self._mu_angle_right(e)  
        
        mu_cl = self._mu_dist_close(d)
        mu_md = self._mu_dist_medium(d)
        mu_fr = self._mu_dist_far(d)

        
        w_numerator = (mu_ln * (-self.max_w)) + (mu_ze * 0.0) + (mu_lp * self.max_w)
        w_denominator = mu_ln + mu_ze + mu_lp
        
        w = w_numerator / w_denominator if w_denominator > 0 else 0.0


        v_slow = 0.10 * self.max_v
        v_med  = 0.60 * self.max_v
        v_fast = 1.00 * self.max_v
        v_turn = 0.15 * self.max_v

        a1 = mu_cl
        a2 = min(mu_md, mu_ze)
        a3 = min(mu_fr, mu_ze)
        a4 = max(mu_ln, mu_lp)

        v_numerator = (a1 * v_slow) + (a2 * v_med) + (a3 * v_fast) + (a4 * v_turn)
        v_denominator = a1 + a2 + a3 + a4

        v = v_numerator / v_denominator if v_denominator > 0 else 0.0

    
        if d < 3.0:
            v = 0.0
            w = 0.0

        return v, w
