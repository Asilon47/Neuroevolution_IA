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
    
    
    target_rect = pygame.Rect(WIDTH/2, HEIGHT/2, 30, 30)
    
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
            
            for obs in obstacles: obs.update()
            obstacles = [obs for obs in obstacles if not obs.is_off_screen()]
            obstacle_rects = [obs.rect for obs in obstacles]
            
            
            
            target_eaten = False
            alive_count = 0
            
            for car in population.cars:
                if car.alive:
                    alive_count += 1
                    
                    eaten = car.update(obstacle_rects, target_rect)
                    if eaten:
                        target_eaten = True
            
            
            if target_eaten:
                target_rect.x = random.randint(50, WIDTH-50)
                target_rect.y = random.randint(50, HEIGHT-50)
        
        else:
            
            population.evolve()
            obstacles = [] 
            target_rect.center = (WIDTH/2, HEIGHT/2) 
            pygame.time.delay(200)

        
        screen.fill(COLOR_BG) 
        
        
        pygame.draw.rect(screen, COLOR_TARGET, target_rect)
        
        for obs in obstacles: obs.draw(screen)
        population.draw(screen)
        
        status = f"Gen: {population.generation} | Alive: {alive_count if not population.is_extinct() else 0}"
        screen.blit(font.render(status, True, COLOR_TEXT), (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    run_simulation()