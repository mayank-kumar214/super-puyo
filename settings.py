"""Global game constants."""

import pygame
pygame.init() 
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
FPS = 60
PLAYER_VEL = 5
BLOCK_SIZE = 96