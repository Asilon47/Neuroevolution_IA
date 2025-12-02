import pygame
import random
from population import Population
from car import (
    CAR_SIZE,
    WIDTH,
    HEIGHT,
    COLOR_BG,
    COLOR_OBSTACLE,
    COLOR_TEXT,
    FPS,
    COLOR_TARGET,
)
from obstacle import Obstacle

MAX_GENS = 200
SPAWN_RATE = 450


def run_simulation():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neuroevolution: Target Pursuit")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    frame_count = 0
    turbo = 0

    population = Population(size=1000)
    obstacles = []

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, SPAWN_RATE)

    running = True
    while running:
        if population.generation > MAX_GENS:
            print("Generaciones máximas alcanzadas")
            best_car = max(population.cars, key=lambda c: c.score)
            best_car.controller.save_model()
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == SPAWN_EVENT and not population.is_extinct():
                obstacles.append(Obstacle())
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    turbo = (turbo + 1) % 3

        if not population.is_extinct():
            frame_count += 1
            if frame_count >= (SPAWN_RATE // 2):
                obstacles.append(Obstacle())
                frame_count = 0
            for obs in obstacles:
                obs.update()
            obstacles = [obs for obs in obstacles if not obs.is_off_screen()]
            obstacle_rects = [obs.rect for obs in obstacles]

            population.update(obstacle_rects)

        else:
            population.evolve()
            obstacles = []
            frame_count = 0
            if turbo != 0:
                pygame.time.delay(500)

        match turbo:
            case 0:
                screen.fill(COLOR_BG)

                for obs in obstacles:
                    obs.draw(screen)

                population.draw(screen)

                alive_count = sum([1 for c in population.cars if c.alive])
                status = f"Gen: {population.generation} | Vivos: {alive_count} | Presiona TAB para modo rabido"
                screen.blit(font.render(status, True, COLOR_TEXT), (10, 10))

                pygame.display.flip()
                clock.tick(FPS)
            case 1:
                if frame_count % 100 == 0:
                    screen.fill((0, 0, 0))
                    status = f"rabido | Gen: {population.generation} | Presiona TAB para modo lider"
                    screen.blit(
                        font.render(status, True, COLOR_TEXT), (WIDTH // 2, HEIGHT // 2)
                    )
                    pygame.display.flip()

            case 2:
                screen.fill(COLOR_BG)

                for obs in obstacles:
                    obs.draw(screen)

                leader = population.get_best_car()
                if leader is not None:
                    leader.draw(screen, show_sensors=True)
                    pygame.draw.rect(screen, COLOR_TARGET, leader.target)
                    status = (
                        f"Score: {leader.score:.2f} | Presiona TAB para modo generacion"
                    )
                    screen.blit(font.render(status, True, COLOR_TEXT), (10, 10))

                pygame.display.flip()
                clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run_simulation()
