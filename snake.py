import pygame
import time
import random

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 102)
BLUE = (50, 153, 213)

# display settings
WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# clock - game speed
CLOCK = pygame.time.Clock()
fps = 20

# font style
FONT_STYLE = pygame.font.SysFont(None, 50)
SCORE_FONT = pygame.font.SysFont(None, 35)


# drawing the snake
def draw_snake(snake_block, snake_list):
    for block in snake_list:
        pygame.draw.rect(WINDOW, GREEN, [block[0], block[1], snake_block, snake_block])


# display player's score
def display_score(score):
    value = SCORE_FONT.render("Score: " + str(score), True, YELLOW)
    WINDOW.blit(value, [0, 0])  # draw the score on top of the window


# main game loop
def game_loop():
    game_over = False
    game_close = False

    while not game_over:
        while game_close:
            WINDOW.fill(BLACK)
            message = FONT_STYLE.render("You Lost! Press Q-Quit or C-Play Again", True, RED)
            WINDOW.blit(message, [WIDTH / 6, HEIGHT / 3])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        WINDOW.fill(BLUE)
        pygame.display.update()
        CLOCK.tick(fps)

    pygame.quit()
    quit()


game_loop()
