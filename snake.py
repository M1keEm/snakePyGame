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
fps = 5
SNAKE_BLOCK = 10  # snake moves 10 pixels at a time

# font style
FONT_STYLE = pygame.font.SysFont("bahnschrift", 40)
SCORE_FONT = pygame.font.SysFont("comicsans", 35)


# drawing the snake
def draw_snake(snake_block, snake_list):
    for block in snake_list:
        pygame.draw.rect(WINDOW, GREEN, [block[0], block[1], snake_block, snake_block])


# display player's score
def display_score(score):
    value = SCORE_FONT.render("Score: " + str(score), True, YELLOW)
    WINDOW.blit(value, [0, 0])  # draw the score on top of the window

def message(msg, color):
    mesg = FONT_STYLE.render(msg, True, color)
    WINDOW.blit(mesg, [WIDTH / 6, HEIGHT / 3])

# main game loop
def game_loop():
    game_over = False
    game_close = False

    # initial snake position
    x1, y1 = WIDTH / 2, HEIGHT / 2
    x1_change, y1_change = 0, 0

    # snake body
    snake_length = 1
    snake_list = []

    # food position
    food_x = round(random.randrange(0, WIDTH - 10) / 10.0) * 10.0
    food_y = round(random.randrange(0, HEIGHT - 10) / 10.0) * 10.0

    while not game_over:
        while game_close:
            WINDOW.fill(BLACK)
            message("You Lost! Press Q-Quit or Space-Play Again", RED)
            display_score(snake_length - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_SPACE:
                        game_loop()
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -SNAKE_BLOCK
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = SNAKE_BLOCK
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -SNAKE_BLOCK
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = SNAKE_BLOCK
                    x1_change = 0

        # check if snake hits the wall
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        # update snake position
        x1 += x1_change
        y1 += y1_change
        WINDOW.fill(BLUE)

        # draw food
        pygame.draw.rect(WINDOW, RED, [food_x + 1, food_y + 1, SNAKE_BLOCK - 1, SNAKE_BLOCK - 1])

        # add snake head to the snake list
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]  # remove the tail of the snake

        # check if snake hits itself
        for block in snake_list[:-1]:
            if block == snake_head:
                game_close = True

        # draw the snake
        draw_snake(SNAKE_BLOCK, snake_list)
        # display current score
        display_score(snake_length - 1)



        pygame.display.update()
        CLOCK.tick(fps)

    pygame.quit()
    quit()


game_loop()
