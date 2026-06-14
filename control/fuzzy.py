"""
This module implements a Fuzzy Logic controller for the robot.
It uses custom membership functions and Sugeno-style inference rules
for smooth steering and speed control based on heading error and distance.
"""

import math
from typing import Tuple

class FuzzyController:
    """
    A custom Fuzzy Logic Controller that computes linear and angular velocity.
    Avoids external dependencies like scikit-fuzzy by using custom analytical
    membership functions and Sugeno singleton rule inference.
    """

    def __init__(self, max_v: float = 120.0, max_w: float = 4.0):
        """
        Initializes the Fuzzy controller.
        
        Args:
            max_v (float): Maximum linear velocity.
            max_w (float): Maximum angular velocity.
        """
        self.max_v = max_v
        self.max_w = max_w

    def reset(self):
        """Reset internal state (not needed for static fuzzy rules but keeps interface uniform)."""
        pass

    # --- Membership Functions for Angle Error (e) ---
    def _mu_angle_left(self, e: float) -> float:
        """LN (Left / Negative error): robot needs to steer left (positive angular velocity)."""
        # Peak at -pi, goes to 0 at -0.2
        if e <= -0.4:
            return 1.0
        elif -0.4 < e < 0.0:
            return e / -0.4
        else:
            return 0.0

    def _mu_angle_center(self, e: float) -> float:
        """ZE (Center / Zero error): robot is facing the target."""
        # Triangular peak at 0, goes to 0 at -0.4 and 0.4
        if e <= -0.4 or e >= 0.4:
            return 0.0
        elif -0.4 < e < 0.0:
            return (e + 0.4) / 0.4
        else:  # 0 <= e < 0.4
            return (0.4 - e) / 0.4

    def _mu_angle_right(self, e: float) -> float:
        """LP (Right / Positive error): robot needs to steer right (negative angular velocity)."""
        # Peak at pi, goes to 0 at 0.2
        if e <= 0.0:
            return 0.0
        elif 0.0 < e < 0.4:
            return e / 0.4
        else:
            return 1.0

    # --- Membership Functions for Distance (d) ---
    def _mu_dist_close(self, d: float) -> float:
        """CL (Close): robot is near the waypoint."""
        if d <= 8.0:
            return 1.0
        elif 8.0 < d < 40.0:
            return (40.0 - d) / 32.0
        else:
            return 0.0

    def _mu_dist_medium(self, d: float) -> float:
        """MD (Medium): robot is at moderate distance."""
        if d <= 15.0 or d >= 90.0:
            return 0.0
        elif 15.0 < d <= 40.0:
            return (d - 15.0) / 25.0
        else:  # 40.0 < d < 90.0
            return (90.0 - d) / 50.0

    def _mu_dist_far(self, d: float) -> float:
        """FR (Far): robot is far from the waypoint."""
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
        """
        Computes fuzzy control outputs (v, w) based on current state and target.
        
        Args:
            x (float): Current robot x-coordinate.
            y (float): Current robot y-coordinate.
            theta (float): Current robot heading in radians.
            target_x (float): Target waypoint x-coordinate.
            target_y (float): Target waypoint y-coordinate.
            dt (float): Time step in seconds (not strictly needed for fuzzy, but keeps compatibility).
            
        Returns:
            Tuple[float, float]: (linear_velocity, angular_velocity)
        """
        dx = target_x - x
        dy = target_y - y
        d = math.sqrt(dx**2 + dy**2)
        
        # Target angle
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
        v_turn = 0.15 * self.max_v

        a1 = mu_cl
        a2 = min(mu_md, mu_ze)
        a3 = min(mu_fr, mu_ze)
        a4 = max(mu_ln, mu_lp)

        v_numerator = (a1 * v_slow) + (a2 * v_med) + (a3 * v_fast) + (a4 * v_turn)
        v_denominator = a1 + a2 + a3 + a4

        v = v_numerator / v_denominator if v_denominator > 0 else 0.0

        # Stop completely if distance is extremely small
        if d < 3.0:
            v = 0.0
            w = 0.0

        return v, w
