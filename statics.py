import numpy
import pygame
import utils

APP_NAME = 'Lyle'

DISPLAY_SIZE = (1280, 720)
DISPLAY = None

VIEWPORT_SIZE = (900, 720)
VIEWPORT_OFFSET = ((DISPLAY_SIZE[0] - VIEWPORT_SIZE[0]) / 2, (DISPLAY_SIZE[1] - VIEWPORT_SIZE[1]) / 2)
VIEWPORT = None

CLOCK = None

SIDEBAR_WIDTH = (DISPLAY_SIZE[0] - VIEWPORT_SIZE[0]) / 2
R_SIDEBAR_TOPLEFT = pygame.math.Vector2(VIEWPORT_SIZE[0] + SIDEBAR_WIDTH, 0)

TILE_SIZE = pygame.math.Vector2(16, 16)                                         # Size of a tile in pixels
LEVEL_SIZE = (20, 10)                                                           # Canvas size where (x, y) represent amount of tiles for each axis
LEVEL_SIZE_PX = (LEVEL_SIZE[0] * TILE_SIZE[0], LEVEL_SIZE[1] * TILE_SIZE[1])    # Pixel size of entire level

SWATCH_LIMIT = 16                                                               # Limit to amount of tiles we can use to draw

PROJECT_ASSETS_PATH = 'Project Assets/'                                         # Filepath where project assets are located
PROGRAM_ASSETS_PATH = 'Program Assets/'                                         # Filepath where program assets are located
OPEN_PROJECT_PATH = None                                                        # Filepath of open project

BACKGROUND_COLOR = (36, 42, 56)
FOREGROUND_COLOR = (78, 89, 111)
VIEWPORT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 255, 100)
SELECTED_COLOR = (255, 255, 0, 100)
SAVE_COLOR = (60, 174, 163)
LOAD_COLOR = (237, 85, 59)
ADD_COLOR = (255, 181, 61)

delta_time = 0
tiles = None
zoom = 2
offset = pygame.math.Vector2(0, 0)
real_tile_size = pygame.math.Vector2(0, 0)
level_mouse_pos = pygame.math.Vector2(0, 0)

# Program Interaction Variables
pan_anchor = pygame.math.Vector2(0, 0)
last_pan_offset = pygame.math.Vector2(0, 0)
is_panning = False
is_using_tool = False

def initialize():
    global DISPLAY, VIEWPORT, CLOCK, offset
    
    pygame.init()
    pygame.display.set_caption(APP_NAME)

    # Initialize backend components
    DISPLAY = pygame.display.set_mode(DISPLAY_SIZE, pygame.DOUBLEBUF)
    VIEWPORT = pygame.Surface(VIEWPORT_SIZE)
    CLOCK = pygame.time.Clock()
    
    # Default offset such that level draw area is centered
    offset = pygame.math.Vector2(
        (VIEWPORT_SIZE[0] - LEVEL_SIZE_PX[0] * zoom) / 2,
        (VIEWPORT_SIZE[1] - LEVEL_SIZE_PX[1] * zoom) / 2
    )

def update():
    global TILE_SIZE, delta_time, real_tile_size, level_mouse_pos
    
    # Update backend components
    DISPLAY.fill(FOREGROUND_COLOR)
    DISPLAY.blit(VIEWPORT, (SIDEBAR_WIDTH, 0))
    VIEWPORT.fill(BACKGROUND_COLOR)
    
    # Update dynamic app static variables
    delta_time = CLOCK.tick(60) / 1000
    real_tile_size = TILE_SIZE * zoom
    
    level_mouse_pos = pygame.math.Vector2(
        (2 * pygame.mouse.get_pos()[0] - DISPLAY_SIZE[0] + VIEWPORT_SIZE[0] - 2 * offset.x) / (2 * zoom),
        (2 * pygame.mouse.get_pos()[1] - DISPLAY_SIZE[1] + VIEWPORT_SIZE[1] - 2 * offset.y) / (2 * zoom), # * See notes for formula derivation
    )