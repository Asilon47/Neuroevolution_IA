import pygame
import math
import random
from controller import NeuralNetwork

WIDTH, HEIGHT = 800, 600
FPS = 60
CAR_SIZE = 20
COLOR_BG = (30, 30, 30)
COLOR_CAR = (255, 255, 0)
COLOR_OBSTACLE = (255, 50, 50)
COLOR_TEXT = (255, 255, 255)
LASER_DISTANCE = 400
COLOR_TARGET = (0, 255, 0)


def get_distance(sensor_angle, car_x, car_y, obstacles_rects):
    max_dist = LASER_DISTANCE
    rad = math.radians(sensor_angle)
    end_x = car_x + math.cos(rad) * max_dist
    end_y = car_y - math.sin(rad) * max_dist

    closest_dist = max_dist
    closest_point = (end_x, end_y)

    ray_line = ((float(car_x), float(car_y)), (float(end_x), float(end_y)))

    for rect in obstacles_rects:
        clip = rect.clipline(ray_line)
        if clip:
            point_x, point_y = clip[0]
            dist = math.hypot(point_x - car_x, point_y - car_y)
            if dist < closest_dist:
                closest_dist = dist
                closest_point = (point_x, point_y)

    return closest_dist, closest_point


class Car:
    def __init__(self):
        self.width = CAR_SIZE
        self.height = CAR_SIZE / 2

        self.original_image = pygame.Surface((self.width, self.height))
        self.original_image.set_colorkey((0, 0, 0))
        self.original_image.fill((0, 0, 0))
        pygame.draw.rect(
            self.original_image, COLOR_CAR, (0, 0, self.width, self.height)
        )

        pygame.draw.rect(
            self.original_image, (0, 0, 255), (self.width - 5, 0, 5, self.height)
        )

        self.image = self.original_image
        self.rect = self.image.get_rect()

        self.radars = []

        self.controller = NeuralNetwork(10, 64, 2)

        self.target = pygame.Rect(0, 0, 30, 30)
        self.spawn_target()

        self.reset()

    def get_data(self):
        inputs = []
        for dist, point in self.radars:
            val = 1 - (dist / LASER_DISTANCE)
            inputs.append(val)

        tx, ty = self.target.center
        dx = tx - self.x
        dy = self.y - ty

        target_rad = math.atan2(dy, dx)
        target_deg = math.degrees(target_rad)

        delta_angle = (target_deg - self.angle) % 360
        if delta_angle > 180:
            delta_angle -= 360

        inputs.append(delta_angle / 180)

        dist_to_target = math.hypot(dx, dy)
        inputs.append(min(dist_to_target / 600, 1))

        if len(inputs) == 0:
            return [0] * 10
        return inputs

    def spawn_target(self):
        self.target.x = random.randint(50, WIDTH - 50)
        self.target.y = random.randint(50, HEIGHT - 50)

    def reset(self):
        self.x, self.y = WIDTH / 2, HEIGHT / 2
        self.angle = 0
        self.speed = 0
        self.alive = True
        self.rect.center = (self.x, self.y)
        self.score = 0
        self.prev_dist_to_target = None
        self.spawn_target()

    def drive(self):
        inputs = self.get_data()
        outputs = self.controller.forward(inputs)

        turn_val = outputs[0]
        speed_val = outputs[1]

        self.angle -= turn_val * 15
        if speed_val > 0:
            self.speed = speed_val * 20
        else:
            self.speed = 0

    def update(self, obstacles_rects):
        if not self.alive:
            return

        self.radars = []
        is_too_close = False
        for offset in [-180, -135, -60, -30, 0, 30, 60, 135]:
            check_angle = self.angle + offset
            dist, point = get_distance(check_angle, self.x, self.y, obstacles_rects)
            self.radars.append((dist, point))
            if dist < 75:
                is_too_close = True

        if is_too_close:
            self.score -= 0.5

        curr_dist = math.hypot(
            self.target.centerx - self.x, self.target.centery - self.y
        )
        if self.prev_dist_to_target is not None:
            difference = self.prev_dist_to_target - curr_dist
            self.score += difference * 0.1
        self.prev_dist_to_target = curr_dist

        self.drive()

        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y -= math.sin(rad) * self.speed

        if self.x > WIDTH or self.x < 0 or self.y > HEIGHT or self.y < 0:
            self.alive = False
            self.score -= 20
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))

        if self.rect.colliderect(self.target):
            self.score += 100
            self.spawn_target()

        if self.rect.collidelist(obstacles_rects) != -1:
            self.alive = False
            self.score -= 20

    def draw(self, screen, show_sensors=False):
        if show_sensors:
            for dist, point in self.radars:
                color = (0, 255, 0) if dist > 75 else (255, 0, 0)

                pygame.draw.line(
                    screen,
                    color,
                    (int(self.x), int(self.y)),
                    (int(point[0]), int(point[1])),
                    1,
                )
                pygame.draw.circle(screen, color, (int(point[0]), int(point[1])), 3)

        screen.blit(self.image, self.rect)
