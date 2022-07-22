import pygame
import numpy

# Program Constant Variables
APP_NAME = 'Lyle'
DISPLAY_SIZE = (1280, 720)
VIEWPORT_SIZE = (900, 720)
SIDEBAR_WIDTH = (DISPLAY_SIZE[0] - VIEWPORT_SIZE[0]) / 2
R_SIDEBAR_TOPLEFT = pygame.math.Vector2(VIEWPORT_SIZE[0] + SIDEBAR_WIDTH, 0)
VIEWPORT_OFFSET = ((DISPLAY_SIZE[0] - VIEWPORT_SIZE[0]) / 2, (DISPLAY_SIZE[1] - VIEWPORT_SIZE[1]) / 2)

TILE_SIZE = 16                                                          # Size of a tile in pixels
TILE_DIMENSIONS = pygame.math.Vector2(TILE_SIZE, TILE_SIZE)             # Shorthand Vector2 for size of a tile in pixels
CANVAS_SIZE = (20, 10)                                                  # Canvas size where (x, y) represent amount of tiles for each axis
LEVEL_SIZE = (CANVAS_SIZE[0] * TILE_SIZE, CANVAS_SIZE[1] * TILE_SIZE)   # Pixel size of entire level
SWATCH_LIMIT = 16                                                       # Limit to amount of tiles we can use to draw
PROJECT_ASSETS_PATH = 'Project Assets/'                                 # Filepath where project assets are located
PROGRAM_ASSETS_PATH = 'Program Assets/'                                 # Filepath where program assets are located
OPEN_PROJECT_PATH = None                                                # Filepath of open project

BACKGROUND_COLOR = (36, 42, 56)
FOREGROUND_COLOR = (78, 89, 111)
VIEWPORT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 255, 100)
SELECTED_COLOR = (255, 255, 0, 100)
POSITIVE_COLOR = (39, 179, 118)
NEGATIVE_COLOR = (191, 33, 47)

DISPLAY = None
VIEWPORT = None
CLOCK = None

# Global Information Variables
delta_time = 0
tiles = None
zoom = 2
offset = pygame.math.Vector2(0, 0)
real_tile_size = 0
real_mouse_pos = pygame.math.Vector2(0, 0)

# Program Interaction Variables
initial_pan_mouse_pos = pygame.math.Vector2(0, 0)
last_pan_offset = pygame.math.Vector2(0, 0)
is_panning = False
is_using_tool = False

# Shorthand &  Utility Functions
def n_round(x: float | int, n: int):
    return numpy.floor(x / n) * n

def place_at_first_empty(item, matrix, empty):
    if len(matrix.shape) > 2:
        return
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            if matrix[y][x] == empty:
                matrix[y][x] = item
                return

def in_level_bounds(pos: tuple):
    if (pos[0] >= 0 and pos[0] < CANVAS_SIZE[0] * TILE_SIZE) and (pos[1] >= 0 and pos[1] < CANVAS_SIZE[1] * TILE_SIZE):
        return True
    return False

def get_tile_at_mouse():
    nearest_pos = pygame.math.Vector2(
        n_round(real_mouse_pos.x, TILE_SIZE),
        n_round(real_mouse_pos.y, TILE_SIZE)
    )

    return tiles[int(nearest_pos.y / TILE_SIZE)][int(nearest_pos.x / TILE_SIZE)]

def mouse_in_bounds():
    return in_level_bounds(real_mouse_pos)

def get_project_asset(file_name):
    return '{P}{N}'.format(P=PROJECT_ASSETS_PATH, N=file_name)

def get_program_asset(file_name):
    return '{P}{N}'.format(P=PROGRAM_ASSETS_PATH, N=file_name)

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
        (VIEWPORT_SIZE[0] - LEVEL_SIZE[0] * zoom) / 2,
        (VIEWPORT_SIZE[1] - LEVEL_SIZE[1] * zoom) / 2
    )

def update():
    global delta_time, real_tile_size, real_mouse_pos
    
    # Update backend components
    DISPLAY.fill(FOREGROUND_COLOR)
    DISPLAY.blit(VIEWPORT, (SIDEBAR_WIDTH, 0))
    VIEWPORT.fill(BACKGROUND_COLOR)
    
    # Update dynamic app static variables
    delta_time = CLOCK.tick(60) / 1000
    real_tile_size = TILE_SIZE * zoom
    real_mouse_pos = pygame.math.Vector2(
        (2 * pygame.mouse.get_pos()[0] - DISPLAY_SIZE[0] + VIEWPORT_SIZE[0] - 2 * offset.x) / (2 * zoom),
        (2 * pygame.mouse.get_pos()[1] - DISPLAY_SIZE[1] + VIEWPORT_SIZE[1] - 2 * offset.y) / (2 * zoom), # * See notes for formula derivation
    )