import pygame
import random
from population import Population
from car import CAR_SIZE, WIDTH, HEIGHT, COLOR_BG, COLOR_OBSTACLE, COLOR_TEXT, FPS
from obstacle import Obstacle


def run_simulation():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Phase 4: Neuroevolution")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    population = Population(size=30)
    obstacles = []

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 750)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == SPAWN_EVENT and not population.is_extinct():
                obstacles.append(Obstacle())

        if not population.is_extinct():
            for obs in obstacles:
                obs.update()

            obstacles = [obs for obs in obstacles if not obs.is_off_screen()]
            obstacle_rects = [obs.rect for obs in obstacles]

            alive_count = population.update(obstacle_rects)

        else:
            population.evolve()

            obstacles = []
            pygame.time.delay(500)

        screen.fill(COLOR_BG)
        for obs in obstacles:
            obs.draw(screen)

        population.draw(screen)

        gen_text = f"Gen: {population.generation} | Alive: {alive_count}"
        screen.blit(font.render(gen_text, True, COLOR_TEXT), (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run_simulation()
