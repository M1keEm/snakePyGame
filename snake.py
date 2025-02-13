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

width, height = 600, 400
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

