import random
import pygame
from collections import deque

import os
import sys


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


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
current_fps = 10
speed_increment = 1

# font style
FONT_STYLE = pygame.font.Font(resource_path("dist/resources/Snake Chan/Snake Chan.ttf"), 40)
SCORE_FONT = pygame.font.Font(resource_path("dist/resources/Snake Chan/Snake Chan.ttf"), 35)
MENU_FONT = pygame.font.Font(resource_path("dist/resources/Snake Chan/Snake Chan.ttf"), 40)

MENU_BACKGROUND = pygame.image.load(resource_path("dist/resources/menu_background.jpg"))
MENU_BACKGROUND = pygame.transform.scale(MENU_BACKGROUND, (WIDTH, HEIGHT))
GAME_BACKGROUND = pygame.image.load(resource_path("dist/resources/background_snake.png"))
ENDGAME_BACKGROUND = pygame.image.load(resource_path("dist/resources/endgame_background.png"))
ENDGAME_BACKGROUND = pygame.transform.scale(ENDGAME_BACKGROUND, (WIDTH, HEIGHT))

APPLE_IMG = pygame.image.load(resource_path("dist/resources/apple.png"))
APPLE_IMG_SCALED = pygame.transform.scale(APPLE_IMG, (20, 20))
WATERMELON_IMG = pygame.image.load(resource_path("dist/resources/watermelon.png"))
WATERMELON_IMG = pygame.transform.scale(WATERMELON_IMG, (20, 20))

SPRITE_SHEET = pygame.image.load(resource_path("dist/resources/sprite_sheet.png"))

eat_sound = pygame.mixer.Sound(resource_path("dist/resources/eat_sound.wav"))
pygame.mixer.music.load(resource_path("dist/resources/background_music.mp3"))


def get_sprite(sheet, x, y, width, height):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    return image


# Load snake skin images
TAIL_UP = pygame.transform.rotate(get_sprite(SPRITE_SHEET, 40, 0, 20, 20), 90)
BODY_VERTICAL = get_sprite(SPRITE_SHEET, 20, 0, 20, 20)
BODY_RIGHT_TOP = get_sprite(SPRITE_SHEET, 0, 0, 20, 20)
HEAD_DOWN_TONGUE_HIDDEN = pygame.transform.rotate(get_sprite(SPRITE_SHEET, 0, 20, 20, 20), 90)
HEAD_DOWN_TONGUE_MID = pygame.transform.rotate(get_sprite(SPRITE_SHEET, 20, 20, 20, 20), 90)
HEAD_DOWN_TONGUE_OUT = pygame.transform.rotate(get_sprite(SPRITE_SHEET, 40, 20, 20, 20), 90)

BODY_RIGHT_BOTTOM = pygame.transform.rotate(BODY_RIGHT_TOP, 270)
BODY_LEFT_BOTTOM = pygame.transform.rotate(BODY_RIGHT_BOTTOM, 270)
BODY_LEFT_TOP = pygame.transform.rotate(BODY_RIGHT_BOTTOM, 180)
BODY_HORIZONTAL = pygame.transform.rotate(BODY_VERTICAL, 90)


class Fruit:
    def __init__(self, snake_block, width, height, fruit_type="apple"):
        self.x = None
        self.y = None
        self.snake_block = snake_block
        self.width = width
        self.height = height
        self.fruit_type = fruit_type

        if fruit_type == "apple":
            self.image = APPLE_IMG_SCALED
            self.points = 1
            self.speed_boost = 0
        elif fruit_type == "watermelon":
            self.image = WATERMELON_IMG
            self.points = 2
            self.speed_boost = 4  # Temporary speed boost amount

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
        self.lifespan = 35  # Number of frames the particle will live

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifespan -= 1

    def draw(self):
        if self.lifespan > 0:
            pygame.draw.circle(WINDOW, self.color, (int(self.x), int(self.y)), 1)


def load_high_score():
    """Load the high score from a file. If the file doesn't exist, return 0."""
    try:
        with open("highscore.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0


def save_high_score(score):
    """Save the high score to a file."""
    with open("highscore.txt", "w") as file:
        file.write(str(score))


def main_menu():
    menu = True
    while menu:
        WINDOW.blit(MENU_BACKGROUND, (0, 0))
        message("Welcome to the Snake Game!", WHITE, -270, MENU_FONT)
        message("Press SPACE to play", WHITE, 30)
        message("Press Q or ESCAPE to quit", WHITE, 100)

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
def draw_snake(snake_block, snake_list, nose_state, direction, eating):
    for i, block in enumerate(snake_list):
        segment_image = None

        # Determine the segment type
        if i == len(snake_list) - 1:  # Head
            if eating:
                # Use different head images for eating animation
                current_time = pygame.time.get_ticks()
                if current_time % 400 < 100:
                    segment_image = HEAD_DOWN_TONGUE_HIDDEN
                elif current_time % 400 < 200:
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

        elif i == 0:
            next_block = snake_list[i + 1]

            dx = next_block[0] - block[0]
            dy = next_block[1] - block[1]

            if dx == snake_block:
                segment_image = pygame.transform.rotate(TAIL_UP, 180)
            elif dx == -snake_block:
                segment_image = TAIL_UP
            elif dy == snake_block:
                segment_image = pygame.transform.rotate(TAIL_UP, 90)
            elif dy == -snake_block:
                segment_image = pygame.transform.rotate(TAIL_UP, 270)

        else:  # Body or turning segment
            prev_block = snake_list[i - 1]
            next_block = snake_list[i + 1]

            # Determine the direction of the current segment
            prev_dx = block[0] - prev_block[0]
            prev_dy = block[1] - prev_block[1]
            next_dx = next_block[0] - block[0]
            next_dy = next_block[1] - block[1]

            if prev_dx == next_dx and prev_dy == next_dy:  # Straight segment
                if prev_dx == 0:  # Vertical
                    segment_image = BODY_VERTICAL
                else:  # Horizontal
                    segment_image = BODY_HORIZONTAL
            else:  # Turning segment
                if (prev_dx == snake_block and next_dy == -snake_block) or (
                        prev_dy == snake_block and next_dx == -snake_block):
                    segment_image = BODY_RIGHT_BOTTOM
                elif (prev_dx == -snake_block and next_dy == snake_block) or (
                        prev_dy == -snake_block and next_dx == snake_block):
                    segment_image = BODY_LEFT_TOP
                elif (prev_dx == -snake_block and next_dy == -snake_block) or (
                        prev_dy == snake_block and next_dx == snake_block):
                    segment_image = BODY_LEFT_BOTTOM
                elif (prev_dx == snake_block and next_dy == snake_block) or (
                        prev_dy == -snake_block and next_dx == -snake_block):
                    segment_image = BODY_RIGHT_TOP

        # Draw the segment
        if segment_image:
            WINDOW.blit(segment_image, (block[0], block[1]))

        # Draw eyes on the head (if applicable)
        if i == len(snake_list) - 1:
            head_x, head_y = block[0], block[1]
            nose_radius = 1
            nose_offset = 8

            if direction == "RIGHT":
                nose1_pos = (head_x + snake_block - nose_offset, head_y + nose_offset)
                nose2_pos = (head_x + snake_block - nose_offset, head_y + snake_block - nose_offset)
            elif direction == "LEFT":
                nose1_pos = (head_x + nose_offset, head_y + nose_offset)
                nose2_pos = (head_x + nose_offset, head_y + snake_block - nose_offset)
            elif direction == "DOWN":
                nose1_pos = (head_x + nose_offset, head_y + snake_block - nose_offset)
                nose2_pos = (head_x + snake_block - nose_offset, head_y + snake_block - nose_offset)
            elif direction == "UP":
                nose1_pos = (head_x + nose_offset, head_y + nose_offset)
                nose2_pos = (head_x + snake_block - nose_offset, head_y + nose_offset)

            if nose_state:
                pygame.draw.circle(WINDOW, BLACK, nose1_pos, nose_radius)
                pygame.draw.circle(WINDOW, BLACK, nose2_pos, nose_radius)
            else:
                pygame.draw.circle(WINDOW, BLACK, nose1_pos, nose_radius // 1.5)
                pygame.draw.circle(WINDOW, BLACK, nose2_pos, nose_radius // 1.5)


# display player's score
def display_score(score, speed_boost_active=False):
    # Load the high score
    high_score = load_high_score()
    # Render the score text with an outline and shadow
    text = f"Score: {score} High Score: {high_score}"
    text_color = WHITE  # Main text color
    outline_color = BLACK  # Outline color
    shadow_color = (50, 50, 50)  # Shadow color (dark gray)
    shadow_offset = 2  # Shadow offset in pixels

    # Render the shadow (behind the main text)
    shadow_text = SCORE_FONT.render(text, True, shadow_color)
    shadow_x = 10 + shadow_offset
    shadow_y = 10 + shadow_offset
    WINDOW.blit(shadow_text, (shadow_x, shadow_y))

    # Render the outline (around the main text)
    outline_offset = 1  # Outline thickness
    for dx in [-outline_offset, 0, outline_offset]:
        for dy in [-outline_offset, 0, outline_offset]:
            if dx != 0 or dy != 0:  # Skip the center (main text)
                outline_text = SCORE_FONT.render(text, True, outline_color)
                WINDOW.blit(outline_text, (10 + dx, 10 + dy))

    # Render the main text (on top of the outline and shadow)
    main_text = SCORE_FONT.render(text, True, text_color)
    WINDOW.blit(main_text, (10, 10))

    # Get the width and height of the main text
    score_width = main_text.get_width()
    score_height = main_text.get_height()

    # Scale the apple icon to match the height of the text
    apple_icon_scaled = pygame.transform.scale(APPLE_IMG, (score_height, score_height))

    # Draw the apple icon next to the score text
    apple_icon_x = 10 + score_width + 10  # 10 pixels padding after the score text
    apple_icon_y = 10  # Align with the score text vertically
    WINDOW.blit(apple_icon_scaled, (apple_icon_x, apple_icon_y))

    # If speed boost is active, show an indicator
    if speed_boost_active:
        boost_text = SCORE_FONT.render("SPEED BOOST!", True, RED)
        WINDOW.blit(boost_text, (WIDTH - boost_text.get_width() - 10, 10))


def message(msg, color, y_offset=0, font=None):
    if font is None:
        font = FONT_STYLE

    # text wrapping
    words = msg.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + ' ' + word if current_line else word
        test_width, _ = font.size(test_line)
        if test_width > WIDTH - 40:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    # calculate the y position of the text and center it
    total_height = len(lines) * font.get_height()
    y_start = (HEIGHT - total_height) / 2 + y_offset

    # draw the text with outline
    outline_color = BLACK  # outline color
    outline_size = 2  # thickness of outline

    # draw the text
    for i, line in enumerate(lines):
        # Draw outline by rendering the text multiple times with offsets
        for dx in range(-outline_size, outline_size + 1, 1):
            for dy in range(-outline_size, outline_size + 1, 1):
                if dx != 0 or dy != 0:  # Skip the center (main text)
                    outline_surface = font.render(line, True, outline_color)
                    text_rect = outline_surface.get_rect(center=(WIDTH / 2 + dx, y_start + i * font.get_height() + dy))
                    WINDOW.blit(outline_surface, text_rect)

        # Draw the main text on top
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, y_start + i * font.get_height()))
        WINDOW.blit(text_surface, text_rect)


# main game loop
def game_loop():
    game_over = False
    game_close = False
    paused = False
    global current_fps

    # Load high score at the start of the game
    high_score = load_high_score()

    # background music
    pygame.mixer.music.play(-1)  # loop indefinitely
    pygame.mixer.music.set_volume(0.01)

    # initial snake position
    x1, y1 = WIDTH / 2, HEIGHT / 2
    x1_change, y1_change = 0, 0

    # snake body
    snake_length = 1
    snake_list = []

    # Fruit tracking variables
    apples_eaten = 0
    next_watermelon_spawn = random.randint(4, 10)  # Spawn watermelon after eating 4-10 apples

    # create a Fruit object list - start with just apples
    fruits = [Fruit(SNAKE_BLOCK, WIDTH, HEIGHT) for _ in range(2)]

    # Speed boost tracking
    speed_boost_active = False
    speed_boost_start_time = 0
    speed_boost_duration = 5000  # 5 seconds boost
    original_fps = current_fps

    # nose animation logic
    nose_state = True  # True for open, False for closed
    last_breath_time = pygame.time.get_ticks()
    blink_interval = random.randint(700, 2000)  # Random interval between 300ms and 800ms

    # track the snake's direction
    direction = "RIGHT"  # initial direction

    # eating animation logic
    eating = False  # True if the snake is eating
    eating_start_time = 0  # time when the snake starts eating
    eating_duration = 700  # duration of the eating animation in milliseconds

    # particles system
    particles = []

    # direction queue to prevent the snake from turning back on itself
    direction_queue = deque()

    while not game_over:
        while game_close:
            # Save high score immediately when the game ends
            current_score = snake_length - 1
            if current_score > high_score:
                high_score = current_score
                save_high_score(high_score)

            WINDOW.blit(ENDGAME_BACKGROUND, (0, 0))
            message("You Lost! Press Q or ESCAPE to Quit", RED, -30)
            message("Press SPACE to Play Again", WHITE, 70)
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
                        # Reload high score when restarting the game
                        high_score = load_high_score()
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
                    direction_queue.append("UP")
                elif event.key == pygame.K_DOWN and direction != "UP":
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
        WINDOW.blit(GAME_BACKGROUND, (0, 0))

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

        # Check if speed boost has expired
        if speed_boost_active and current_time - speed_boost_start_time > speed_boost_duration:
            speed_boost_active = False
            current_fps = original_fps  # Reset speed to normal

        if current_time - last_breath_time > blink_interval:
            nose_state = not nose_state  # toggle nose state
            last_breath_time = current_time

        # check if snake eats any fruit
        for i, fruit in enumerate(fruits[:]):
            if fruit.is_eaten(snake_head):
                # Add points based on fruit type
                snake_length += fruit.points

                # Handle speed boost for watermelon
                if fruit.fruit_type == "watermelon":
                    speed_boost_active = True
                    original_fps = current_fps  # Store current speed
                    current_fps += fruit.speed_boost
                    speed_boost_start_time = pygame.time.get_ticks()
                    # Remove the watermelon
                    fruits.remove(fruit)
                else:  # It's an apple
                    apples_eaten += 1
                    # Create a new apple to replace the eaten one
                    fruit.reset_position(snake_list, fruits)

                    # Check if we should spawn a watermelon
                    if apples_eaten >= next_watermelon_spawn and not any(f.fruit_type == "watermelon" for f in fruits):
                        new_watermelon = Fruit(SNAKE_BLOCK, WIDTH, HEIGHT, "watermelon")
                        fruits.append(new_watermelon)
                        next_watermelon_spawn = apples_eaten + random.randint(1, 1)  # Set next watermelon spawn

                        # Create particles for watermelon spawn
                        for _ in range(20):
                            particles.append(Particle(new_watermelon.x + SNAKE_BLOCK // 2, new_watermelon.y + SNAKE_BLOCK // 2, BLUE))

                eating = True
                eating_start_time = pygame.time.get_ticks()
                eat_sound.play()

                current_fps += speed_increment
                CLOCK.tick(current_fps)
                pygame.mixer.music.set_volume(
                    min(1.0,
                        max(0.1, pygame.mixer.music.get_volume() + 0.03)))  # Increase volume slightly, max volume 1.0

                # Create particles
                if fruit.fruit_type == "watermelon":
                    particle_color = BLUE  # Yellow particles for speed boost
                else:
                    particle_color = RED  # Red particles for regular eating

                for _ in range(20):
                    particles.append(Particle(fruit.x + SNAKE_BLOCK // 2, fruit.y + SNAKE_BLOCK // 2, particle_color))

                break  # Exit the loop since we modified the fruits list

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
        draw_snake(SNAKE_BLOCK, snake_list, nose_state, direction, eating)
        # display current score with speed boost indicator
        display_score(snake_length - 1, speed_boost_active)
        pygame.display.update()

        CLOCK.tick(current_fps)

    pygame.quit()
    quit()


# start the game with the main menu
main_menu()