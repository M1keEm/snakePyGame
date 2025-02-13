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
WIDTH, HEIGHT = 600, 400
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# clock - game speed
CLOCK = pygame.time.Clock()
fps = 20
SNAKE_BLOCK = 20  # snake moves 10 pixels at a time

# font style
FONT_STYLE = pygame.font.SysFont("bahnschrift", 40)
SCORE_FONT = pygame.font.SysFont("comicsans", 35)
MENU_FONT = pygame.font.SysFont("comicsansms", 50)

MENU_BACKGROUND = pygame.image.load("resources/menu_background.png")
MENU_BACKGROUND = pygame.transform.scale(MENU_BACKGROUND, (WIDTH, HEIGHT))

APPLE_IMG = pygame.image.load("resources/apple.png")
APPLE_IMG = pygame.transform.scale(APPLE_IMG, (20, 20))

def main_menu():
    menu = True
    while menu:
        # WINDOW.fill(BLACK)
        WINDOW.blit(MENU_BACKGROUND, (0, 0))
        message("Welcome to Snake Game!", WHITE, -50, MENU_FONT)
        message("Press SPACE to play", WHITE, 0)
        message("Press Q/ESCAPE to quit", WHITE, 50)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_loop()
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-1, 1)  # Random horizontal velocity
        self.vy = random.uniform(-1, 1)  # Random vertical velocity
        self.lifespan = 30  # Number of frames the particle will live

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifespan -= 1

    def draw(self):
        if self.lifespan > 0:
            pygame.draw.circle(WINDOW, self.color, (int(self.x), int(self.y)), 1)


# drawing the snake
def draw_snake(snake_block, snake_list, eye_state, direction, eating):
    for i, block in enumerate(snake_list):
        pygame.draw.rect(WINDOW, GREEN, [block[0], block[1], snake_block, snake_block])

        # draw eyes on the head of the snake
        if i == len(snake_list) - 1:  # check if it's the head
            head_x, head_y = block[0], block[1]
            eye_radius = 4  # radius of the eye
            eye_offset = 5  # distance from the edge of the head

            # determine the direction of the snake
            if direction == "RIGHT":
                eye1_pos = (head_x + snake_block - eye_offset, head_y + eye_offset)
                eye2_pos = (head_x + snake_block - eye_offset, head_y + snake_block - eye_offset)
            elif direction == "LEFT":
                eye1_pos = (head_x + eye_offset, head_y + eye_offset)
                eye2_pos = (head_x + eye_offset, head_y + snake_block - eye_offset)
            elif direction == "DOWN":
                eye1_pos = (head_x + eye_offset, head_y + snake_block - eye_offset)
                eye2_pos = (head_x + snake_block - eye_offset, head_y + snake_block - eye_offset)
            elif direction == "UP":
                eye1_pos = (head_x + eye_offset, head_y + eye_offset)
                eye2_pos = (head_x + snake_block - eye_offset, head_y + eye_offset)

            # draw the eyes
            if eye_state:
                pygame.draw.circle(WINDOW, BLACK, eye1_pos, eye_radius)
                pygame.draw.circle(WINDOW, BLACK, eye2_pos, eye_radius)
            else:
                # draw smaller eyes
                pygame.draw.circle(WINDOW, BLACK, eye1_pos, eye_radius // 1.5)
                pygame.draw.circle(WINDOW, BLACK, eye2_pos, eye_radius // 1.5)

            if eating:
                if direction == "RIGHT":
                    pygame.draw.rect(WINDOW, RED, [head_x + snake_block, head_y + snake_block // 2 - 2, 4, 4])
                elif direction == "LEFT":
                    pygame.draw.rect(WINDOW, RED, [head_x - 4, head_y + snake_block // 2 - 2, 4, 4])
                elif direction == "DOWN":
                    pygame.draw.rect(WINDOW, RED, [head_x + snake_block // 2 - 2, head_y + snake_block, 4, 4])
                elif direction == "UP":
                    pygame.draw.rect(WINDOW, RED, [head_x + snake_block // 2 - 2, head_y - 4, 4, 4])


# display player's score
def display_score(score):
    value = SCORE_FONT.render("Score: " + str(score), True, YELLOW)
    WINDOW.blit(value, [0, 0])  # draw the score on top of the window


def message(msg, color, y_offset=0, font=None):
    if font is None:
        font = FONT_STYLE

    # text wrapping
    words = msg.split(' ')
    lines = []
    current_line = ''
    for word in words:
        # check if adding the word to the current line will exceed the width of the window
        test_line = current_line + ' ' + word if current_line else word
        test_width, _ = font.size(test_line)  # get the width of the text, ignore the height
        if test_width > WIDTH - 40:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)  # add the last line

    # calculate the y position of the text and center it
    total_height = len(lines) * font.get_height()
    y_start = (HEIGHT - total_height) / 2 + y_offset

    # draw the text
    for i, line in enumerate(lines):
        test_surface = font.render(line, True, color)
        text_rect = test_surface.get_rect(center=(WIDTH / 2, y_start + i * font.get_height()))
        WINDOW.blit(test_surface, text_rect)


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
    food_x = round(random.randrange(0, WIDTH - 20) / 20.0) * 20.0
    food_y = round(random.randrange(0, HEIGHT - 20) / 20.0) * 20.0

    # eye animation logic
    eye_state = True  # True for open, False for closed
    last_blink_time = pygame.time.get_ticks()
    blink_interval = random.randint(500, 1500)  # Random interval between 300ms and 800ms

    # track the snake's direction
    direction = "RIGHT"  # initial direction

    # eating animation logic
    eating = False  # True if the snake is eating
    eating_start_time = 0  # time when the snake starts eating
    eating_duration = 400  # duration of the eating animation in milliseconds

    # particles system
    particles = []

    while not game_over:
        while game_close:
            WINDOW.fill(BLACK)
            message("You Lost! Press Q/ESCAPE-Quit or Space-Play Again", RED)
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

        # check for keyboard input and other events (quit)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and direction != "RIGHT":
                    x1_change = -SNAKE_BLOCK
                    y1_change = 0
                    direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    x1_change = SNAKE_BLOCK
                    y1_change = 0
                    direction = "RIGHT"
                elif event.key == pygame.K_UP and direction != "DOWN":
                    y1_change = -SNAKE_BLOCK
                    x1_change = 0
                    direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    y1_change = SNAKE_BLOCK
                    x1_change = 0
                    direction = "DOWN"

        # check if snake hits the wall
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        # update snake position
        x1 += x1_change
        y1 += y1_change
        WINDOW.fill(BLUE)

        # draw food
        WINDOW.blit(APPLE_IMG, (food_x, food_y))
        # pygame.draw.circle(WINDOW, RED, (int(food_x + SNAKE_BLOCK // 2), int(food_y + SNAKE_BLOCK // 2)),
        #                    SNAKE_BLOCK // 2)

        # add snake head to the snake list
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]  # remove the tail of the snake

        # check if snake hits itself
        for block in snake_list[:-1]:
            if block == snake_head:
                game_close = True

        # update eye animation
        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time > blink_interval:
            eye_state = not eye_state  # toggle eye state
            last_blink_time = current_time

        # check if snake eats the food
        if x1 == food_x and y1 == food_y:
            food_x = round(random.randrange(0, WIDTH - 20) / 20.0) * 20.0
            food_y = round(random.randrange(0, HEIGHT - 20) / 20.0) * 20.0
            snake_length += 1
            eating = True  # start eating animation
            eating_start_time = pygame.time.get_ticks()

            # create particles
            for _ in range(20):  # create 20 particles
                particles.append(Particle(food_x + SNAKE_BLOCK // 2, food_y + SNAKE_BLOCK // 2, RED))

        # update eating animation
        if eating and current_time - eating_start_time > eating_duration:
            eating = False  # stop eating animation

        # Update and draw particles
        for particle in particles[:]:
            particle.update()
            particle.draw()
            if particle.lifespan <= 0:
                particles.remove(particle)

        # draw the snake
        draw_snake(SNAKE_BLOCK, snake_list, eye_state, direction, eating)
        # display current score
        display_score(snake_length - 1)
        pygame.display.update()

        CLOCK.tick(fps)

    pygame.quit()
    quit()


# start the game with the main menu
main_menu()
