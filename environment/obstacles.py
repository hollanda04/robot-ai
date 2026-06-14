"""
This module defines the obstacles (walls) in the environment and provides collision detection functions.
"""

import pygame
import math

class Obstacle:
    """Represents a rectangular wall obstacle in the grid map."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Initializes an obstacle with position and dimensions.
        
        Args:
            x (float): Top-left x-coordinate in pixels.
            y (float): Top-left y-coordinate in pixels.
            width (float): Width in pixels.
            height (float): Height in pixels.
        """
        self.rect = pygame.Rect(x, y, width, height)

    def collides_with_circle(self, cx: float, cy: float, radius: float) -> bool:
        """
        Checks if a circular robot collides with this rectangular obstacle.
        
        Args:
            cx (float): X-coordinate of the circle center.
            cy (float): Y-coordinate of the circle center.
            radius (float): Radius of the circle.
            
        Returns:
            bool: True if they collide, False otherwise.
        """
        # Find the closest point on the rectangle to the circle's center
        closest_x = max(self.rect.left, min(cx, self.rect.right))
        closest_y = max(self.rect.top, min(cy, self.rect.bottom))

        # Calculate distance between closest point and circle center
        distance_x = cx - closest_x
        distance_y = cy - closest_y
        distance_squared = (distance_x ** 2) + (distance_y ** 2)

        return distance_squared < (radius ** 2)

    def draw(self, surface: pygame.Surface, color: tuple = (40, 44, 52)):
        """
        Draws the obstacle on the given Pygame surface.
        
        Args:
            surface (pygame.Surface): The surface to draw on.
            color (tuple): RGB color tuple for the wall.
        """
        pygame.draw.rect(surface, color, self.rect)
        # Subtle border for a premium feel
        pygame.draw.rect(surface, (60, 64, 72), self.rect, 1)
