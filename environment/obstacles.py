import pygame
import math

class Obstacle:
    
    def __init__(self, x: float, y: float, width: float, height: float):
        self.rect = pygame.Rect(x, y, width, height)

    def collides_with_circle(self, cx: float, cy: float, radius: float) -> bool:
        closest_x = max(self.rect.left, min(cx, self.rect.right))
        closest_y = max(self.rect.top, min(cy, self.rect.bottom))
        distance_x = cx - closest_x
        distance_y = cy - closest_y
        distance_squared = (distance_x ** 2) + (distance_y ** 2)

        return distance_squared < (radius ** 2)

    def draw(self, surface: pygame.Surface, color: tuple = (40, 44, 52)):
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (60, 64, 72), self.rect, 1)
