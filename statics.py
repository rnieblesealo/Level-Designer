import pygame

DISPLAY_SIZE = (1280, 720)
VIEWPORT_SIZE = (880, 720)
SIDEBAR_SIZE = (DISPLAY_SIZE[0] - VIEWPORT_SIZE[0]) / 2

TILE_SIZE = 64
TILE_DIMENSIONS = pygame.math.Vector2(TILE_SIZE, TILE_SIZE)
CANVAS_SIZE = (20, 10) #x, y represent amount of tiles, not pixel width!
LEVEL_SIZE = (CANVAS_SIZE[0] * TILE_SIZE, CANVAS_SIZE[1] * TILE_SIZE) #actual size of entire level

BACKGROUND_COLOR = (40, 40, 40)
FOREGROUND_COLOR = (83, 83, 83)
VIEWPORT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0, 100)

DISPLAY = None
VIEWPORT = None
CLOCK = None

delta_time = 0
tiles = None
zoom = 0.5
offset = pygame.math.Vector2(0, 0)