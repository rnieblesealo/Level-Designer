import pygame
import numpy
import sys
import data

from pygame.math import Vector2
from tile import *

#TODO Erasing
#TODO Undoing
#TODO Overlap placement protection

pygame.init()
pygame.display.set_caption("Tile Drawing Test")

DISPLAY_SIZE = (800, 600)
DELTA_TIME = 0

DISPLAY = pygame.display.set_mode(DISPLAY_SIZE)
CLOCK = pygame.time.Clock()

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

data.tiles = numpy.empty((data.CANVAS_SIZE[1], data.CANVAS_SIZE[0]), dtype=Tile)
for x in range(data.CANVAS_SIZE[0]):
    for y in range(data.CANVAS_SIZE[1]):
        Tile(Vector2(x * data.TILE_SIZE, y * data.TILE_SIZE)) #placeholder, this should be modifiable

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        #TODO figure out visual gridding bug (zoom is disabled)
        # elif event.type == pygame.MOUSEWHEEL:
        #     # data.zoom += event.y * 0.05 #zoom in according to mouse wheel

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        sys.exit()

    DISPLAY.fill((25, 25, 25))

    real_position = (Vector2(pygame.mouse.get_pos()) / data.zoom) - data.offset

    #panning
    if pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LSHIFT]:
        if not is_panning:
            initial_mouse_pos = pygame.mouse.get_pos()
            is_panning = True
        data.offset = last_offset + (Vector2(pygame.mouse.get_pos()) - initial_mouse_pos)
    elif is_panning:
        last_offset = data.offset.copy()
        is_panning = False

    #placing
    else:
        if pygame.mouse.get_pressed()[0] and in_bounds(real_position) and not is_placing:            
            nearest_pos = Vector2(
                nearest_n(real_position.x, data.TILE_SIZE),
                nearest_n(real_position.y, data.TILE_SIZE)
            )

            nearest_tile = data.tiles[int(nearest_pos.y / data.TILE_SIZE)][int(nearest_pos.x / data.TILE_SIZE)]
            nearest_tile = Tile(nearest_pos, (0, 255, 0))

            is_placing = True
        else:
            is_placing = False

    #update tiles
    for y in range(data.CANVAS_SIZE[1]):
        for x in range(data.CANVAS_SIZE[0]):
            data.tiles[y][x].update(DISPLAY)

    print(real_position)

    pygame.display.update()