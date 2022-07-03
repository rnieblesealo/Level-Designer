import pygame
import numpy

DISPLAY_SIZE = (1280, 720)
VIEWPORT_SIZE = (880, 720)
SIDEBAR_SIZE = (DISPLAY_SIZE[0] - VIEWPORT_SIZE[0]) / 2
VIEWPORT_OFFSET = (
    (DISPLAY_SIZE[0] - VIEWPORT_SIZE[0]) / 2, 
    (DISPLAY_SIZE[1] - VIEWPORT_SIZE[1]) / 2
    )

TILE_SIZE = 16
TILE_DIMENSIONS = pygame.math.Vector2(TILE_SIZE, TILE_SIZE)
CANVAS_SIZE = (20, 10) #x, y represent amount of tiles, not pixel width!
LEVEL_SIZE = (CANVAS_SIZE[0] * TILE_SIZE, CANVAS_SIZE[1] * TILE_SIZE) #actual size of entire level
SWATCH_LIMIT = 16 # How many tiles can we use to draw?

BACKGROUND_COLOR = (40, 40, 40)
FOREGROUND_COLOR = (83, 83, 83)
VIEWPORT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 255, 100)
SELECTED_COLOR = (255, 255, 0, 100)

DISPLAY = None
VIEWPORT = None
CLOCK = None

delta_time = 0
tiles = None
zoom = 2
offset = pygame.math.Vector2(0, 0)
real_tile_size = 0
real_mouse_position = pygame.math.Vector2(0, 0)

def round_to_n(x: float | int, n: int):
    return numpy.floor(x / n) * n

def in_level_bounds(pos: tuple):
    if (pos[0] >= 0 and pos[0] < CANVAS_SIZE[0] * TILE_SIZE) and (pos[1] >= 0 and pos[1] < CANVAS_SIZE[1] * TILE_SIZE):
        return True
    return False

def get_tile_at_mouse():
    nearest_pos = pygame.math.Vector2(
        round_to_n(real_mouse_position.x, TILE_SIZE),
        round_to_n(real_mouse_position.y, TILE_SIZE)
    )

    return tiles[int(nearest_pos.y / TILE_SIZE)][int(nearest_pos.x / TILE_SIZE)]

def mouse_in_bounds():
    return in_level_bounds(real_mouse_position)