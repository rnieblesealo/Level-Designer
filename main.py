import pygame
import numpy
import sys
import data
import tile
import ui

from pygame import Surface
from pygame.math import Vector2

#TODO Erasing
#TODO Undoing
#TODO Overlap placement protection

pygame.init()
pygame.display.set_caption("Tile Drawing Test")

DISPLAY_SIZE = (1280, 720)
VIEWPORT_SIZE = (880, 720)
DELTA_TIME = 0

DISPLAY = pygame.display.set_mode(DISPLAY_SIZE)
VIEWPORT = Surface(VIEWPORT_SIZE)
CLOCK = pygame.time.Clock()

BACKGROUND_COLOR = (40, 40, 40)
FOREGROUND_COLOR = (83, 83, 83)
VIEWPORT_COLOR = (255, 255, 255)

pencil_icon = pygame.image.load('Assets/pencil.png').convert_alpha()
eraser_icon = pygame.image.load('Assets/eraser.png').convert_alpha()

last_offset = Vector2(0, 0)
initial_mouse_pos = Vector2(0, 0)
is_panning = False
is_placing = False

def nearest_n(x: float | int, n: int):
    return numpy.floor(x / n) * n

def in_bounds(pos: tuple):
    if (pos[0] >= 0 and pos[0] < data.CANVAS_SIZE[0] * data.TILE_SIZE) and (pos[1] >= 0 and pos[1] < data.CANVAS_SIZE[1] * data.TILE_SIZE):
        return True
    return False

# TOOLS -- TEMPORARY PLACEMENT HERE! ================================================

def pencil(operand):
    #replace tile w/selected one
    operand = tile.Tile(tile.SAMPLE, operand.position)

def eraser(operand):
    #replace operand tile w/blank tile
    operand = tile.Tile(tile.DEFAULT, operand.position)

def set_tool(new_tool):
    global current_tool
    current_tool = new_tool

current_tool = pencil

# ===================================================================================

#fill canvas with empty tiles
data.tiles = numpy.empty((data.CANVAS_SIZE[1], data.CANVAS_SIZE[0]), dtype=tile.Tile)
for x in range(data.CANVAS_SIZE[0]):
    for y in range(data.CANVAS_SIZE[1]):
        tile.Tile(tile.DEFAULT, Vector2(x * data.TILE_SIZE, y * data.TILE_SIZE)) #make placeholder tile, should be customizable

#center level draw area over viewport
data.offset = Vector2(
    (VIEWPORT_SIZE[0] - data.LEVEL_SIZE[0] * data.zoom) / 2,
    (VIEWPORT_SIZE[1] - data.LEVEL_SIZE[1] * data.zoom) / 2
)

#button
pencil_button = ui.Button(Vector2(40, 30), (45, 45), FOREGROUND_COLOR, pencil_icon, set_tool, pencil)
eraser_button = ui.Button(Vector2(40 + 30 + 45, 30), (45, 45), FOREGROUND_COLOR, eraser_icon, set_tool, eraser)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        #TODO figure out visual gridding bug (zoom is disabled)
        # elif event.type == pygame.MOUSEWHEEL:
        #     # data.zoom += event.y * 0.05 #zoom in according to mouse wheel

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        sys.exit()

    #testing
    if pygame.key.get_pressed()[pygame.K_e]:
        current_tool = eraser

    DISPLAY.fill(FOREGROUND_COLOR)
    DISPLAY.blit(VIEWPORT, ((DISPLAY_SIZE[0] - VIEWPORT_SIZE[0]) / 2, 0))
    VIEWPORT.fill(BACKGROUND_COLOR)

    #mouse position within level
    #NOTE math here is mathematically simplified version of original formula; future documentation will include its derivation
    real_position = Vector2(
        (2 * pygame.mouse.get_pos()[0] - DISPLAY_SIZE[0] + VIEWPORT_SIZE[0] - 2 * data.offset.x) / (2 * data.zoom),
        (2 * pygame.mouse.get_pos()[1] - DISPLAY_SIZE[1] + VIEWPORT_SIZE[1] - 2 * data.offset.y) / (2 * data.zoom),
    )

    #panning
    if pygame.mouse.get_pressed()[0]:
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            if not is_panning:
                print("Set panning!")
                initial_mouse_pos = pygame.mouse.get_pos()
                is_panning = True
            data.offset = last_offset + (Vector2(pygame.mouse.get_pos()) - initial_mouse_pos)
        #when not panning, we're placing
        else:
            last_offset = data.offset.copy()
            is_panning = False
            
            if in_bounds(real_position):
                nearest_pos = Vector2(
                    nearest_n(real_position.x, data.TILE_SIZE),
                    nearest_n(real_position.y, data.TILE_SIZE)
                )

                #get the nearest tile to our click
                nearest_tile = data.tiles[int(nearest_pos.y / data.TILE_SIZE)][int(nearest_pos.x // data.TILE_SIZE)]
                
                #use the current tool's operation with it
                current_tool(nearest_tile)
    #reached when we are not panning or placing; if the mouse isn't down, we couldn't possibly be doing either
    else:
        last_offset = data.offset.copy()
        is_placing = False
        is_panning = False

    #update tiles
    for y in range(data.CANVAS_SIZE[1]):
        for x in range(data.CANVAS_SIZE[0]):
            data.tiles[y][x].update(VIEWPORT)

    #testing
    pencil_button.update(DISPLAY)
    eraser_button.update(DISPLAY)
    print(real_position)
   
    pygame.display.update()