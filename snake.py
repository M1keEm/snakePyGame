import math
import random
import pygame
from collections import deque
import os
import sys

# Constants
SNAKE_BLOCK = 20
CELL_NUMBER = 40
WIDTH, HEIGHT = SNAKE_BLOCK * CELL_NUMBER, SNAKE_BLOCK * CELL_NUMBER
FPS_BASE = 10
SPEED_INCREMENT = 1
PARTICLE_COUNT = 20
FRUIT_MIN_SPAWN = 4
FRUIT_MAX_SPAWN = 10
SPEED_BOOST_DURATION = 5000
EATING_DURATION = 700
BLINK_MIN_INTERVAL = 700
BLINK_MAX_INTERVAL = 2000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 102)
BLUE = (50, 153, 213)
SHADOW_COLOR = (50, 50, 50)


def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


pygame.init()

# Display settings
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock - game speed
CLOCK = pygame.time.Clock()
current_fps = FPS_BASE

# Game music state global variable
muted = False

# Load resources
FONT_STYLE = pygame.font.Font(resource_path("dist/resources/Snake Chan/Snake Chan.ttf"), 40)
SCORE_FONT = pygame.font.Font(resource_path("dist/resources/Snake Chan/Snake Chan.ttf"), 35)
MENU_FONT = pygame.font.Font(resource_path("dist/resources/Snake Chan/Snake Chan.ttf"), 40)

# Backgrounds
MENU_BACKGROUND = pygame.transform.scale(
    pygame.image.load(resource_path("dist/resources/menu_background.jpg")), (WIDTH, HEIGHT))
GAME_BACKGROUND = pygame.image.load(resource_path("dist/resources/background_snake.png"))
ENDGAME_BACKGROUND = pygame.transform.scale(
    pygame.image.load(resource_path("dist/resources/endgame_background.png")), (WIDTH, HEIGHT))

# Fruit images
APPLE_IMG = pygame.image.load(resource_path("dist/resources/apple.png"))
APPLE_IMG_SCALED = pygame.transform.scale(APPLE_IMG, (SNAKE_BLOCK, SNAKE_BLOCK))
WATERMELON_IMG = pygame.transform.scale(
    pygame.image.load(resource_path("dist/resources/watermelon.png")), (SNAKE_BLOCK, SNAKE_BLOCK))

# Snake sprite sheet
SPRITE_SHEET = pygame.image.load(resource_path("dist/resources/sprite_sheet.png"))

# Sounds
eat_sound = pygame.mixer.Sound(resource_path("dist/resources/eat_sound.wav"))
pygame.mixer.music.load(resource_path("dist/resources/background_music.mp3"))


def get_sprite(sheet, x, y, width, height):
    """Extract a sprite from a sprite sheet"""
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
            self.speed_boost = 4

        self.reset_position()

    def is_position_valid(self, snake_list, other_fruits):
        """Check if the fruit's position is valid (not overlapping with snake/other fruits)."""
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


def spawn_particles(x, y, color, particles, count=PARTICLE_COUNT):
    """Create particles at the specified position with given color"""
    center_x = x + SNAKE_BLOCK // 2
    center_y = y + SNAKE_BLOCK // 2
    for _ in range(count):
        particles.append(Particle(center_x, center_y, color))


def load_high_score():
    """Load high score from file, return 0 if file doesn't exist."""
    try:
        with open("highscore.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0


def save_high_score(score):
    """Save the high score to a file."""
    with open("highscore.txt", "w") as file:
        file.write(str(score))


def draw_snake(snake_block, snake_list, nose_state, direction, eating):
    """Draw the snake with all its segments"""
    for i, block in enumerate(snake_list):
        segment_image = None

        # Determine segment type (head, tail, or body)
        if i == len(snake_list) - 1:  # Head
            # Select head image based on eating animation
            if eating:
                current_time = pygame.time.get_ticks()
                if current_time % 400 < 100:
                    segment_image = HEAD_DOWN_TONGUE_HIDDEN
                elif current_time % 400 < 200:
                    segment_image = HEAD_DOWN_TONGUE_MID
                else:
                    segment_image = HEAD_DOWN_TONGUE_OUT
            else:
                segment_image = HEAD_DOWN_TONGUE_HIDDEN

            # Rotate head based on direction
            if direction == "RIGHT":
                segment_image = pygame.transform.rotate(segment_image, 0)
            elif direction == "LEFT":
                segment_image = pygame.transform.rotate(segment_image, 180)
            elif direction == "UP":
                segment_image = pygame.transform.rotate(segment_image, 90)
            elif direction == "DOWN":
                segment_image = pygame.transform.rotate(segment_image, 270)

        elif i == 0:  # Tail
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

        else:  # Body segments
            prev_block = snake_list[i - 1]
            next_block = snake_list[i + 1]

            prev_dx = block[0] - prev_block[0]
            prev_dy = block[1] - prev_block[1]
            next_dx = next_block[0] - block[0]
            next_dy = next_block[1] - block[1]

            if prev_dx == next_dx and prev_dy == next_dy:  # Straight segment
                segment_image = BODY_VERTICAL if prev_dx == 0 else BODY_HORIZONTAL
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

        # Draw segment
        if segment_image:
            WINDOW.blit(segment_image, (block[0], block[1]))

        # Draw eyes/nose for head
        if i == len(snake_list) - 1:
            head_x, head_y = block[0], block[1]
            nose_radius = 1
            nose_offset = 8

            # Calculate nose positions based on direction
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

            # Draw nose with appropriate size based on nose_state
            radius = nose_radius if nose_state else nose_radius // 1.5
            pygame.draw.circle(WINDOW, BLACK, nose1_pos, radius)
            pygame.draw.circle(WINDOW, BLACK, nose2_pos, radius)


def lerp_color(color1, color2, t):
    """Linearly interpolate between two colors."""
    return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))


def display_score(score, speed_boost_active=False):
    """Display the current score and high score with visual effects"""
    high_score = load_high_score()
    text = f"Score: {score} High Score: {high_score}"

    if muted:
        mute_text = "MUTED"
        mute_surface = SCORE_FONT.render(mute_text, True, WHITE)
        WINDOW.blit(mute_surface, (WIDTH - mute_surface.get_width() - 10, HEIGHT - mute_surface.get_height() - 10))
        # Render shadow
    shadow_text = SCORE_FONT.render(text, True, SHADOW_COLOR)
    WINDOW.blit(shadow_text, (12, 12))  # Shadow offset of 2px

    # Render outline
    outline_offset = 1
    for dx in [-outline_offset, 0, outline_offset]:
        for dy in [-outline_offset, 0, outline_offset]:
            if dx != 0 or dy != 0:
                outline_text = SCORE_FONT.render(text, True, BLACK)
                WINDOW.blit(outline_text, (10 + dx, 10 + dy))

    # Render main text
    main_text = SCORE_FONT.render(text, True, WHITE)
    WINDOW.blit(main_text, (10, 10))

    # Draw apple icon
    score_width = main_text.get_width()
    score_height = main_text.get_height()
    apple_icon_scaled = pygame.transform.scale(APPLE_IMG, (score_height, score_height))
    WINDOW.blit(apple_icon_scaled, (10 + score_width + 10, 10))

    # Show speed boost indicator
    if speed_boost_active:
        boost_text = "SPEED BOOST!"
        # Pulsate color: white -> red -> yellow -> white
        t = (math.sin(pygame.time.get_ticks() / 300) + 1) / 2  # t in [0,1]
        if t < 0.5:
            # White to Red
            color = lerp_color((255, 255, 255), (255, 0, 0), t * 2)
        else:
            # Red to Yellow
            color = lerp_color((255, 0, 0), (255, 255, 0), (t - 0.5) * 2)

        outline_size = 3
        for dx in range(-outline_size, outline_size + 1):
            for dy in range(-outline_size, outline_size + 1):
                if dx != 0 or dy != 0:
                    outline_surface = SCORE_FONT.render(boost_text, True, BLACK)
                    WINDOW.blit(outline_surface, (WIDTH - SCORE_FONT.size(boost_text)[0] - 10 + dx, 40 + dy))
        main_surface = SCORE_FONT.render(boost_text, True, color)
        WINDOW.blit(main_surface, (WIDTH - SCORE_FONT.size(boost_text)[0] - 10, 40))


def message(msg, color, y_offset=0, font=None):
    """Display text message with wrapping and visual effects"""
    if font is None:
        font = FONT_STYLE

    # Text wrapping
    words = msg.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + ' ' + word if current_line else word
        if font.size(test_line)[0] > WIDTH - 40:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    # Calculate position
    total_height = len(lines) * font.get_height()
    y_start = (HEIGHT - total_height) / 2 + y_offset
    outline_size = 2

    # Draw each line with outline effect
    for i, line in enumerate(lines):
        y_pos = y_start + i * font.get_height()

        # Draw outline
        for dx in range(-outline_size, outline_size + 1, 1):
            for dy in range(-outline_size, outline_size + 1, 1):
                if dx != 0 or dy != 0:
                    outline_surface = font.render(line, True, BLACK)
                    text_rect = outline_surface.get_rect(center=(WIDTH / 2 + dx, y_pos + dy))
                    WINDOW.blit(outline_surface, text_rect)

        # Draw main text
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH / 2, y_pos))
        WINDOW.blit(text_surface, text_rect)


def main_menu():
    """Display and handle the main menu"""
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
                    sys.exit()
                    # quit()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                # quit()


def game_loop():
    """Main game loop handling all game mechanics"""
    global current_fps, muted
    game_over = False
    game_close = False
    paused = False

    # Load high score
    high_score = load_high_score()

    # Setup background music
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.01)

    # Initialize snake
    x1, y1 = WIDTH / 2, HEIGHT / 2
    x1_change, y1_change = 0, 0
    snake_length = 1
    snake_list = []
    direction = "RIGHT"
    direction_queue = deque()

    # Fruit tracking
    apples_eaten = 0
    next_watermelon_spawn = random.randint(FRUIT_MIN_SPAWN, FRUIT_MAX_SPAWN)
    fruits = [Fruit(SNAKE_BLOCK, WIDTH, HEIGHT) for _ in range(2)]

    # Animation and effects
    particles = []
    nose_state = True
    last_breath_time = pygame.time.get_ticks()
    blink_interval = random.randint(BLINK_MIN_INTERVAL, BLINK_MAX_INTERVAL)
    eating = False
    eating_start_time = 0

    # Speed boost tracking
    speed_boost_active = False
    speed_boost_start_time = 0
    original_fps = current_fps

    while not game_over:
        # Game Over screen
        while game_close:
            current_score = snake_length - 1
            if current_score > high_score:
                save_high_score(current_score)
                high_score = current_score

            WINDOW.blit(ENDGAME_BACKGROUND, (0, 0))
            message("You Lost! Press Q or ESCAPE to Quit", RED, -30)
            message("Press SPACE to Play Again", WHITE, 70)
            display_score(current_score)
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
                        current_fps = FPS_BASE
                        game_loop()

        # Handle input events
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
                    pygame.mixer.music.pause() if paused else pygame.mixer.music.unpause()
                elif event.key == pygame.K_m:
                    muted = not muted
                    if muted:
                        pygame.mixer.music.set_volume(0)
                    else:
                        pygame.mixer.music.set_volume(0.02)

        if paused:
            continue

        # Process direction queue
        if direction_queue:
            new_direction = direction_queue.popleft()
            if new_direction == "LEFT" and direction != "RIGHT":
                x1_change, y1_change = -SNAKE_BLOCK, 0
                direction = "LEFT"
            elif new_direction == "RIGHT" and direction != "LEFT":
                x1_change, y1_change = SNAKE_BLOCK, 0
                direction = "RIGHT"
            elif new_direction == "UP" and direction != "DOWN":
                y1_change, x1_change = -SNAKE_BLOCK, 0
                direction = "UP"
            elif new_direction == "DOWN" and direction != "UP":
                y1_change, x1_change = SNAKE_BLOCK, 0
                direction = "DOWN"

        # Check boundary collision
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        # Update snake position
        x1 += x1_change
        y1 += y1_change
        WINDOW.blit(GAME_BACKGROUND, (0, 0))

        # Draw fruits
        for fruit in fruits:
            fruit.draw(WINDOW)

        # Update snake list
        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        # Check self-collision
        for block in snake_list[:-1]:
            if block == snake_head:
                game_close = True

        # Update animations and timers
        current_time = pygame.time.get_ticks()

        # Check speed boost expiration
        if speed_boost_active and current_time - speed_boost_start_time > SPEED_BOOST_DURATION:
            speed_boost_active = False
            current_fps = original_fps

        # Update blinking animation
        if current_time - last_breath_time > blink_interval:
            nose_state = not nose_state
            last_breath_time = current_time
            blink_interval = random.randint(BLINK_MIN_INTERVAL, BLINK_MAX_INTERVAL)

        # Check fruit eating collision
        for i, fruit in enumerate(fruits[:]):
            if fruit.is_eaten(snake_head):
                snake_length += fruit.points
                eating = True
                eating_start_time = current_time
                if not muted:
                    eat_sound.play()

                # Handle fruit effects
                if fruit.fruit_type == "watermelon":
                    speed_boost_active = True
                    original_fps = current_fps
                    current_fps += fruit.speed_boost
                    speed_boost_start_time = current_time
                    fruits.remove(fruit)
                    spawn_particles(fruit.x, fruit.y, BLUE, particles)
                else:  # Apple
                    apples_eaten += 1
                    fruit.reset_position(snake_list, fruits)
                    spawn_particles(fruit.x, fruit.y, RED, particles)

                    # Check if should spawn watermelon
                    if apples_eaten >= next_watermelon_spawn and not any(f.fruit_type == "watermelon" for f in fruits):
                        new_watermelon = Fruit(SNAKE_BLOCK, WIDTH, HEIGHT, "watermelon")
                        fruits.append(new_watermelon)
                        next_watermelon_spawn = apples_eaten + random.randint(FRUIT_MIN_SPAWN, FRUIT_MAX_SPAWN)
                        spawn_particles(new_watermelon.x, new_watermelon.y, BLUE, particles)

                # Increase game speed slightly
                current_fps += SPEED_INCREMENT
                if not muted:
                    pygame.mixer.music.set_volume(min(1.0, max(0.1, pygame.mixer.music.get_volume() + 0.03)))
                break

        # Update eating animation
        if eating and current_time - eating_start_time > EATING_DURATION:
            eating = False

        # Update and draw particles
        for particle in particles[:]:
            particle.update()
            particle.draw()
            if particle.lifespan <= 0:
                particles.remove(particle)

        # Draw snake and score
        draw_snake(SNAKE_BLOCK, snake_list, nose_state, direction, eating)
        display_score(snake_length - 1, speed_boost_active)

        pygame.display.update()
        CLOCK.tick(current_fps)

    pygame.quit()
    sys.exit()
    # quit()


# Start the game
main_menu()
