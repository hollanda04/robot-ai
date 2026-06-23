# modulo responsavel por definir os obstaculos (paredes) no ambiente e prover funçao de detecçao de colisao

import pygame
import math

class Obstacle:
    #representa uma parede retangural, obstaculo, na area do mapa
    
    def __init__(self, x: float, y: float, width: float, height: float):
        # inicialisa um obstaculo com posisao e dimensao
        self.rect = pygame.Rect(x, y, width, height)

    def collides_with_circle(self, cx: float, cy: float, radius: float) -> bool:
       # checa se o robo circular colide com esta obstaculo retangular
        # acha o menor caminho entre um ponto no retangulo para o centro do circulo
        closest_x = max(self.rect.left, min(cx, self.rect.right))
        closest_y = max(self.rect.top, min(cy, self.rect.bottom))

        # calcula a distancia entre o ponto mais proximo e o centro do circulo
        distance_x = cx - closest_x
        distance_y = cy - closest_y
        distance_squared = (distance_x ** 2) + (distance_y ** 2)

        return distance_squared < (radius ** 2)

    def draw(self, surface: pygame.Surface, color: tuple = (40, 44, 52)):
        # desenha o obstaculo dado a superfice pygame

        pygame.draw.rect(surface, color, self.rect)
        #pequena borda para um toque especial
        pygame.draw.rect(surface, (60, 64, 72), self.rect, 1)
