import pygame
import math
import random
from car import CAR_SIZE, WIDTH, HEIGHT, COLOR_BG, COLOR_OBSTACLE, COLOR_TEXT, FPS


class Obstacle:
    def __init__(self):
        self.width = CAR_SIZE
        self.height = CAR_SIZE
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.speed = random.randint(3, 13)

        side = random.randint(0, 3)

        if side == 0:
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = -30
            self.vel_x, self.vel_y = 0, self.speed
        elif side == 1:
            self.rect.x = WIDTH + 30
            self.rect.y = random.randint(0, HEIGHT)
            self.vel_x, self.vel_y = -self.speed, 0
        elif side == 2:
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = HEIGHT + 30
            self.vel_x, self.vel_y = 0, -self.speed
        elif side == 3:
            self.rect.x = -30
            self.rect.y = random.randint(0, HEIGHT)
            self.vel_x, self.vel_y = self.speed, 0

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_OBSTACLE, self.rect)

    def is_off_screen(self):
        return (
            self.rect.x < -50
            or self.rect.x > WIDTH + 50
            or self.rect.y < -50
            or self.rect.y > HEIGHT + 50
        )
