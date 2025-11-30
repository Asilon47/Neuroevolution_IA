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
LASER_DISTANCE = 200


def get_distance(sensor_angle, car_x, car_y, obstacles_rects):
    """
    Casts a ray to find the distance to the nearest wall OR obstacle.
    """
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


class Obstacle:
    def __init__(self):
        self.width = CAR_SIZE
        self.height = CAR_SIZE
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.speed = random.randint(3, 10)

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

        self.controller = NeuralNetwork(8, 8, 2)

        self.reset()

    def get_data(self):
        """
        Normalize sensor readings for the Neural Network.
        Raw Distance: 0 to 300
        Normalized:   1.0 (Close/Danger) to 0.0 (Far/Safe)
        """
        inputs = []
        for dist, point in self.radars:
            val = 1 - (dist / LASER_DISTANCE)
            inputs.append(val)

        if len(inputs) == 0:
            return [0, 0, 0, 0, 0]

        return inputs

    def reset(self):
        self.x, self.y = WIDTH / 2, HEIGHT / 2
        self.angle = 0
        self.speed = 0
        self.alive = True
        self.rect.center = (self.x, self.y)
        self.distance_traveled = 0

    def drive(self):
        """Replaces keyboard input with Neural Network output"""

        inputs = self.get_data()

        outputs = self.controller.forward(inputs)

        turn_val = outputs[0]
        speed_val = outputs[1]

        self.angle -= turn_val * 5

        if speed_val > 0:
            self.speed = speed_val * 5
        else:
            self.speed = 0

    def update(self, obstacles_rects):
        if not self.alive:
            return

        self.radars = []
        for offset in [-180, -135, -60, -30, 0, 30, 60, 135]:
            check_angle = self.angle + offset
            dist, point = get_distance(check_angle, self.x, self.y, obstacles_rects)
            self.radars.append((dist, point))

        self.drive()

        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.speed
        dy = math.sin(rad) * self.speed
        self.x += dx
        self.y -= dy
        self.distance_traveled += math.hypot(dx, dy)

        if self.x > WIDTH or self.x < 0 or self.y > HEIGHT or self.y < 0:
            self.alive = False

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))

        if self.rect.collidelist(obstacles_rects) != -1:
            self.alive = False

    def draw(self, screen):
        for dist, point in self.radars:
            color = (0, 255, 0) if dist > 60 else (255, 0, 0)

            pygame.draw.line(
                screen,
                color,
                (int(self.x), int(self.y)),
                (int(point[0]), int(point[1])),
                1,
            )
            pygame.draw.circle(screen, color, (int(point[0]), int(point[1])), 3)

        screen.blit(self.image, self.rect)


def run_simulation():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Phase 2: Dynamic Obstacle Avoidance")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    car = Car()
    obstacles = []

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 500)

    start_ticks = pygame.time.get_ticks()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == SPAWN_EVENT and car.alive:
                obstacles.append(Obstacle())

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not car.alive:
                    car.reset()
                    obstacles = []
                    start_ticks = pygame.time.get_ticks()

        if car.alive:
            for obs in obstacles:
                obs.update()

            obstacles = [obs for obs in obstacles if not obs.is_off_screen()]
            obstacle_rects = [obs.rect for obs in obstacles]

            car.update(obstacle_rects)

        screen.fill(COLOR_BG)

        for obs in obstacles:
            obs.draw(screen)

        car.draw(screen)

        if car.alive:
            seconds = (pygame.time.get_ticks() - start_ticks) / 1000

            time_text = f"Tim: {seconds:.1f}s | Dist: {int(car.distance_traveled)}"
            color = COLOR_TEXT
        else:
            time_text = "Choque - Pulsa SPACE"
            color = (255, 50, 50)

        text_surf = font.render(time_text, True, color)
        screen.blit(text_surf, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run_simulation()
