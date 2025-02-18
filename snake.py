import random
import pygame
from collections import deque

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 102)
BLUE = (50, 153, 213)

SNAKE_BLOCK = 20  # snake moves 20 pixels at a time
CELL_NUMBER = 40

# display settings
WIDTH, HEIGHT = SNAKE_BLOCK * CELL_NUMBER, SNAKE_BLOCK * CELL_NUMBER
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# clock - game speed
CLOCK = pygame.time.Clock()
current_fps = 2
speed_increment = 1

# font style
FONT_STYLE = pygame.font.SysFont("bahnschrift", 40)
SCORE_FONT = pygame.font.SysFont("comicsans", 35)
MENU_FONT = pygame.font.SysFont("comicsansms", 50)

MENU_BACKGROUND = pygame.image.load("dist/resources/menu_background.png")
MENU_BACKGROUND = pygame.transform.scale(MENU_BACKGROUND, (WIDTH, HEIGHT))

APPLE_IMG = pygame.image.load("dist/resources/apple.png")
APPLE_IMG = pygame.transform.scale(APPLE_IMG, (20, 20))

# Load snake skin images
BODY_RIGHT_BOTTOM = pygame.image.load("dist/resources/body_right_top.png")
BODY_RIGHT_TOP =  pygame.transform.rotate(BODY_RIGHT_BOTTOM, 90)
BODY_LEFT_BOTTOM = pygame.transform.rotate(BODY_RIGHT_BOTTOM, 270)
BODY_LEFT_TOP = pygame.transform.rotate(BODY_RIGHT_BOTTOM, 180)

HEAD_DOWN_TONGUE_HIDDEN = pygame.transform.rotate(pygame.image.load("dist/resources/head_down_tongue_hidden.png"), 90)
HEAD_DOWN_TONGUE_MID = pygame.transform.rotate(pygame.image.load("dist/resources/head_down_tongue_mid.png"), 90)
HEAD_DOWN_TONGUE_OUT = pygame.transform.rotate(pygame.image.load("dist/resources/head_down_tongue_out.png"), 90)

TAIL_UP = pygame.transform.rotate(pygame.image.load("dist/resources/tail_up.png"), 90)
BODY_VERTICAL = pygame.image.load("dist/resources/body_vertical.png")
BODY_HORIZONTAL = pygame.transform.rotate(BODY_VERTICAL, 90)


class Fruit:
    def __init__(self, snake_block, width, height):
        self.x = None
        self.y = None
        self.snake_block = snake_block
        self.width = width
        self.height = height
        self.image = pygame.image.load("dist/resources/apple.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (snake_block, snake_block))
        self.reset_position()

    def is_position_valid(self, snake_list, other_fruits):
        """Check if the fruit's position is valid (not overlapping with the snake or other fruits)."""
        if snake_list:
            for block in snake_list:
                if block[0] == self.x and block[1] == self.y:
                    return False

        if other_fruits:
            for fruit in other_fruits:
                if fruit != self and fruit.x == self.x and fruit.y == self.y:
                    return False

        return True

    def reset_position(self, snake_list=None, other_fruits=None):
        """Reset the fruit's position to a random location on the grid, ensuring it doesn't overlap with the snake or other fruits."""
        while True:
            self.x = round(random.randrange(0, self.width - self.snake_block) / self.snake_block) * self.snake_block
            self.y = round(random.randrange(0, self.height - self.snake_block) / self.snake_block) * self.snake_block

            # Check if the new position is valid
            if self.is_position_valid(snake_list, other_fruits):
                break

    def draw(self, window):
        """Draw the fruit on the window."""
        window.blit(self.image, (self.x, self.y))

    def is_eaten(self, snake_head):
        """Check if the snake's head has collided with the fruit."""
        return snake_head[0] == self.x and snake_head[1] == self.y


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


eat_sound = pygame.mixer.Sound("dist/resources/eat_sound.wav")


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


# drawing the snake
def draw_snake(snake_block, snake_list, eye_state, direction, eating):
    for i, block in enumerate(snake_list):
        segment_type = None
        segment_image = None

        # Determine the segment type
        if i == len(snake_list) - 1:  # Head
            segment_type = "HEAD"
            if eating:
                # Use different head images for eating animation
                current_time = pygame.time.get_ticks()
                if current_time % 300 < 100:
                    segment_image = HEAD_DOWN_TONGUE_HIDDEN
                elif current_time % 300 < 200:
                    segment_image = HEAD_DOWN_TONGUE_MID
                else:
                    segment_image = HEAD_DOWN_TONGUE_OUT
            else:
                segment_image = HEAD_DOWN_TONGUE_HIDDEN

            # Rotate the head image based on the direction
            if direction == "RIGHT":
                segment_image = pygame.transform.rotate(segment_image, 0)
            elif direction == "LEFT":
                segment_image = pygame.transform.rotate(segment_image, 180)
            elif direction == "UP":
                segment_image = pygame.transform.rotate(segment_image, 90)
            elif direction == "DOWN":
                segment_image = pygame.transform.rotate(segment_image, 270)

        elif i == 0:  # Tail
            segment_type = "TAIL"
            segment_image = TAIL_UP

            # Rotate the tail image based on the direction
            if direction == "RIGHT":
                segment_image = pygame.transform.rotate(segment_image, 180)
            elif direction == "LEFT":
                segment_image = pygame.transform.rotate(segment_image, 0)
            elif direction == "UP":
                segment_image = pygame.transform.rotate(segment_image, 270)
            elif direction == "DOWN":
                segment_image = pygame.transform.rotate(segment_image, 90)

        else:  # Body or turning segment
            prev_block = snake_list[i - 1]
            next_block = snake_list[i + 1]

            # Determine the direction of the current segment
            prev_dx = block[0] - prev_block[0]
            prev_dy = block[1] - prev_block[1]
            next_dx = next_block[0] - block[0]
            next_dy = next_block[1] - block[1]

            if prev_dx == next_dx and prev_dy == next_dy:  # Straight segment
                segment_type = "BODY"
                if prev_dx == 0:  # Vertical
                    segment_image = BODY_VERTICAL
                else:  # Horizontal
                    segment_image = BODY_HORIZONTAL
            else:  # Turning segment
                if (prev_dx == -snake_block and next_dy == -snake_block) or (prev_dy == -snake_block and next_dx == -snake_block):
                    segment_type = "TURN_LEFT_TOP"
                    segment_image = BODY_LEFT_TOP
                elif (prev_dx == -snake_block and next_dy == snake_block) or (prev_dy == snake_block and next_dx == -snake_block):
                    segment_type = "TURN_LEFT_BOTTOM"
                    segment_image = BODY_LEFT_BOTTOM
                elif (prev_dx == snake_block and next_dy == -snake_block) or (prev_dy == -snake_block and next_dx == snake_block):
                    segment_type = "TURN_RIGHT_TOP"
                    segment_image = BODY_RIGHT_TOP
                elif (prev_dx == snake_block and next_dy == snake_block) or (prev_dy == snake_block and next_dx == snake_block):
                    segment_type = "TURN_RIGHT_BOTTOM"
                    segment_image = BODY_RIGHT_BOTTOM

        # Draw the segment
        if segment_image:
            WINDOW.blit(segment_image, (block[0], block[1]))

        # Draw eyes on the head (if applicable)
        if segment_type == "HEAD":
            head_x, head_y = block[0], block[1]
            eye_radius = 4
            eye_offset = 5

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

            if eye_state:
                pygame.draw.circle(WINDOW, BLACK, eye1_pos, eye_radius)
                pygame.draw.circle(WINDOW, BLACK, eye2_pos, eye_radius)
            else:
                pygame.draw.circle(WINDOW, BLACK, eye1_pos, eye_radius // 1.5)
                pygame.draw.circle(WINDOW, BLACK, eye2_pos, eye_radius // 1.5)
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
    paused = False
    global current_fps

    # background music
    pygame.mixer.music.load("dist/resources/background_music.mp3")
    pygame.mixer.music.play(-1)  # loop indefinitely
    pygame.mixer.music.set_volume(0.0)

    # initial snake position
    x1, y1 = WIDTH / 2, HEIGHT / 2
    x1_change, y1_change = 0, 0

    # snake body
    snake_length = 1
    snake_list = []

    # create a Fruit object list
    fruits = [Fruit(SNAKE_BLOCK, WIDTH, HEIGHT) for _ in range(10)]

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

    # direction queue to prevent the snake from turning back on itself
    direction_queue = deque()

    while not game_over:
        while game_close:
            WINDOW.fill(BLACK)
            message("You Lost! Press Q/ESCAPE-Quit or Space-Play Again", RED)
            display_score(snake_length - 1)
            pygame.mixer.music.stop()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_SPACE:
                        current_fps = 10
                        game_loop()

        # check for keyboard input and other events (quit)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and direction != "RIGHT":
                    direction_queue.append("LEFT")
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    direction_queue.append("RIGHT")
                elif event.key == pygame.K_UP and direction != "DOWN":
                    y1_change = -SNAKE_BLOCK
                    x1_change = 0
                    direction_queue.append("UP")
                elif event.key == pygame.K_DOWN and direction != "UP":
                    y1_change = SNAKE_BLOCK
                    x1_change = 0
                    direction_queue.append("DOWN")
                elif event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

        if paused:
            continue

        # process the direction queue
        if direction_queue:
            new_direction = direction_queue.popleft()
            if new_direction == "LEFT" and direction != "RIGHT":
                x1_change = -SNAKE_BLOCK
                y1_change = 0
                direction = "LEFT"
            if new_direction == "RIGHT" and direction != "LEFT":
                x1_change = SNAKE_BLOCK
                y1_change = 0
                direction = "RIGHT"
            if new_direction == "UP" and direction != "DOWN":
                y1_change = -SNAKE_BLOCK
                x1_change = 0
                direction = "UP"
            if new_direction == "DOWN" and direction != "UP":
                y1_change = SNAKE_BLOCK
                x1_change = 0
                direction = "DOWN"

        # check if snake hits the wall
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        # update snake position
        x1 += x1_change
        y1 += y1_change
        WINDOW.fill((BLUE))

        # Draw all fruits
        for fruit in fruits:
            fruit.draw(WINDOW)

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

        # check if snake eats any fruit
        for fruit in fruits:
            if fruit.is_eaten(snake_head):
                fruit.reset_position(snake_list, fruits)
                snake_length += 1
                eating = True  # start eating animation
                eating_start_time = pygame.time.get_ticks()

                # play eat sound
                eat_sound.play()

                # create particles
                current_fps += speed_increment
                CLOCK.tick(current_fps)

                pygame.mixer.music.set_volume(
                    min(1.0, pygame.mixer.music.get_volume() + 0.05))  # Increase volume slightly
                for _ in range(20):  # create 20 particles
                    particles.append(Particle(fruit.x + SNAKE_BLOCK // 2, fruit.y + SNAKE_BLOCK // 2, RED))

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

        CLOCK.tick(current_fps)

    pygame.quit()
    quit()


# start the game with the main menu
main_menu()
