import pygame
import random
from population import Population
from car import CAR_SIZE, WIDTH, HEIGHT, COLOR_BG, COLOR_OBSTACLE, COLOR_TEXT, FPS, COLOR_TARGET
from obstacle import Obstacle


def run_simulation():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neuroevolution: Target Pursuit")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    population = Population(size=50)
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
            # Actualizar Obstaculos
            for obs in obstacles: obs.update()
            obstacles = [obs for obs in obstacles if not obs.is_off_screen()]
            obstacle_rects = [obs.rect for obs in obstacles]
            
            # Actualizar Población (Ya no pasamos target_rect)
            population.update(obstacle_rects)
        
        else:
            # Evolucionar
            population.evolve()
            obstacles = [] 
            pygame.time.delay(200)

        # --- DIBUJADO ---
        screen.fill(COLOR_BG) 
        
        # Dibujar Obstaculos
        for obs in obstacles: obs.draw(screen)
        
        # Dibujar Coches
        population.draw(screen)
        
        # --- NUEVO: Dibujar SOLO el objetivo del mejor coche vivo ---
        leader = population.get_best_car()
        if leader is not None:
            # Dibujamos su objetivo en verde
            pygame.draw.rect(screen, COLOR_TARGET, leader.target)
            # Opcional: Dibujar una marca sobre el líder para identificarlo
            pygame.draw.circle(screen, (255, 255, 255), leader.rect.center, 5)

        # UI
        alive_count = sum([1 for c in population.cars if c.alive])
        status = f"Gen: {population.generation} | Alive: {alive_count}"
        screen.blit(font.render(status, True, COLOR_TEXT), (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    run_simulation()