"""
This module defines the common interface shared by all robot controllers
(PID and Fuzzy), so that Robot can treat them polymorphically.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class BaseController(ABC):
    """
    Abstract interface for a waypoint-following controller.
    Any controller plugged into Robot must implement reset() and
    compute_control() with this exact signature.
    """

    @abstractmethod
    def reset(self) -> None:
        """Resets any internal state (integrators, previous errors, etc.)."""
        raise NotImplementedError

    @abstractmethod
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
        Computes control outputs (linear velocity, angular velocity) to drive
        the robot from (x, y, theta) towards (target_x, target_y).

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
        raise NotImplementedError
