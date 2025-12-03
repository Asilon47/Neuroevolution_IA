from unittest import case
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

MAX_GENS = 2000
SPAWN_FRAMES = 30


def run_simulation():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neuroevolucion")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    trainning = 0
    while True:
        screen.fill(COLOR_BG)
        text_surface = font.render(
            "1: Entrenar | 2: Simular mejor controlador", True, COLOR_TEXT
        )
        screen.blit(
            text_surface,
            (
                WIDTH // 2 - text_surface.get_width() // 2,
                HEIGHT // 2 - text_surface.get_height() // 2,
            ),
        )
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    trainning = 1
                    break
                elif event.key == pygame.K_2:
                    trainning = 2
                    break

        match trainning:
            case 1:
                frame_count = 0
                turbo = 0

                population = Population(size=300, load_file="weights_final.npy")
                obstacles = []
                running = True
                while running:
                    if population.generation > MAX_GENS:
                        print("Generaciones maximas alcanzadas")
                        best_car = max(population.cars, key=lambda c: c.score)
                        best_car.controller.save_model()
                        running = False

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_TAB:
                                turbo = (turbo + 1) % 3

                    if not population.is_extinct():
                        frame_count += 1
                        if frame_count >= SPAWN_FRAMES:
                            obstacles.append(Obstacle())
                            frame_count = 0
                        for obs in obstacles:
                            obs.update()
                        obstacles = [
                            obs for obs in obstacles if not obs.is_off_screen()
                        ]
                        obstacle_rects = [obs.rect for obs in obstacles]

                        population.update(obstacle_rects)

                    else:
                        population.evolve()
                        obstacles = []
                        frame_count = 0
                        if turbo != 1:
                            pygame.time.delay(2000)

                    match turbo:
                        case 0:
                            screen.fill(COLOR_BG)

                            for obs in obstacles:
                                obs.draw(screen)

                            population.draw(screen)

                            alive_count = sum([1 for c in population.cars if c.alive])
                            status = f"Gen: {population.generation} | Vivos: {alive_count} | pulsa TAB para modo rabido"
                            screen.blit(font.render(status, True, COLOR_TEXT), (10, 10))

                            pygame.display.flip()
                            clock.tick(FPS)
                        case 1:
                            if frame_count % 100 == 0:
                                screen.fill((0, 0, 0))
                                status = f"rabido | Gen: {population.generation} | pulsa TAB para modo lider"
                                screen.blit(
                                    font.render(status, True, COLOR_TEXT),
                                    (WIDTH // 2 - 200, HEIGHT // 2),
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
                                status = f"Score: {leader.score:.2f} | pulsa TAB para modo generacion"
                                screen.blit(
                                    font.render(status, True, COLOR_TEXT), (10, 10)
                                )

                            pygame.display.flip()
                            clock.tick(FPS)

                pygame.quit()
            case 2:
                running = True
                while running:
                    population = Population(size=1, load_file="weights_final.npy")
                    leader = population.cars[0]
                    obstacles = []
                    frame_count = 0

                    while running:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False

                        if leader.alive:
                            frame_count += 1
                            if frame_count >= SPAWN_FRAMES:
                                obstacles.append(Obstacle())
                                frame_count = 0
                            for obs in obstacles:
                                obs.update()
                            obstacles = [
                                obs for obs in obstacles if not obs.is_off_screen()
                            ]
                            obstacle_rects = [obs.rect for obs in obstacles]

                            leader.update(obstacle_rects)
                        else:
                            leader.reset()
                            pygame.time.delay(1000)

                        screen.fill(COLOR_BG)

                        for obs in obstacles:
                            obs.draw(screen)

                        leader.draw(screen, show_sensors=True)
                        pygame.draw.rect(screen, COLOR_TARGET, leader.target)

                        status = f"Score: {leader.score:.2f}"
                        screen.blit(font.render(status, True, COLOR_TEXT), (10, 10))

                        pygame.display.flip()
                        clock.tick(FPS)

                    pygame.quit()
            case _:
                print("Opcion no valida")


if __name__ == "__main__":
    run_simulation()
