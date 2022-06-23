import pygame
import numpy
import sys

import statics
import tile
import ui

from pygame import Rect
from pygame.math import Vector2

pygame.init()
pygame.display.set_caption("Tile Drawing Test")

statics.DISPLAY = pygame.display.set_mode(statics.DISPLAY_SIZE, pygame.DOUBLEBUF)
statics.VIEWPORT = pygame.Surface(statics.VIEWPORT_SIZE)
statics.CLOCK = pygame.time.Clock()

pencil_icon = pygame.image.load('Assets/pencil.png').convert_alpha()
eraser_icon = pygame.image.load('Assets/eraser.png').convert_alpha()
marquee_icon = pygame.image.load('Assets/marquee.png').convert_alpha()

last_offset = Vector2(0, 0)
initial_mouse_pos = Vector2(0, 0)
is_panning = False

def round_to_n(x: float | int, n: int):
    return numpy.floor(x / n) * n

def in_level_bounds(pos: tuple):
    if (pos[0] >= 0 and pos[0] < statics.CANVAS_SIZE[0] * statics.TILE_SIZE) and (pos[1] >= 0 and pos[1] < statics.CANVAS_SIZE[1] * statics.TILE_SIZE):
        return True
    return False

def get_tile_at_mouse():
    nearest_pos = Vector2(
        round_to_n(level_mouse_position.x, statics.TILE_SIZE),
        round_to_n(level_mouse_position.y, statics.TILE_SIZE)
    )

    return statics.tiles[int(nearest_pos.y / statics.TILE_SIZE)][int(nearest_pos.x / statics.TILE_SIZE)]

# TOOLS -- TEMPORARY PLACEMENT HERE! ================================================

def pencil(_tile):
    #replace tile w/selected one
    _tile = tile.Tile(tile.SAMPLE, _tile.position)

def eraser(_tile):
    #replace operand tile w/blank tile
    _tile = tile.Tile(tile.DEFAULT, _tile.position)

def marquee(_tile):
    pass

def set_tool(new_tool):
    global use_current_tool
    use_current_tool = new_tool

use_current_tool = pencil

# ===================================================================================

#fill canvas with empty tiles
statics.tiles = numpy.empty((statics.CANVAS_SIZE[1], statics.CANVAS_SIZE[0]), dtype=tile.Tile)
for x in range(statics.CANVAS_SIZE[0]):
    for y in range(statics.CANVAS_SIZE[1]):
        tile.Tile(tile.DEFAULT, Vector2(x * statics.TILE_SIZE, y * statics.TILE_SIZE)) #make placeholder tile, should be customizable

#center level draw area over viewport
statics.offset = Vector2(
    (statics.VIEWPORT_SIZE[0] - statics.LEVEL_SIZE[0] * statics.zoom) / 2,
    (statics.VIEWPORT_SIZE[1] - statics.LEVEL_SIZE[1] * statics.zoom) / 2
)

#button
pencil_button = ui.Button(Vector2(0, 0), (45, 45), statics.FOREGROUND_COLOR, pencil_icon, set_tool, pencil)
eraser_button = ui.Button(Vector2(0, 0), (45, 45), statics.FOREGROUND_COLOR, eraser_icon, set_tool, eraser)
marquee_button = ui.Button(Vector2(0, 0), (45, 45), statics.FOREGROUND_COLOR, marquee_icon, set_tool, marquee)

#horizontal layout group, implement vertical LG to store them all, for now, we will have multiple w/manually calculated positions
handle_0 = Rect(0, 25, statics.SIDEBAR_SIZE, 45)
handle_1 = Rect(0, 25 + 25 + handle_0.height, statics.SIDEBAR_SIZE, 45)
hlg_0 = ui.HorizontalLayoutGroup([pencil_button, eraser_button], handle_0, 30)
hlg_1 = ui.HorizontalLayoutGroup([marquee_button], handle_1, 30)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        #TODO figure out visual gridding bug (zoom is disabled)
        # elif event.type == pygame.MOUSEWHEEL:
        #     # data.zoom += event.y * 0.05 #zoom in according to mouse wheel

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        sys.exit()

    statics.DISPLAY.fill(statics.FOREGROUND_COLOR)
    statics.DISPLAY.blit(statics.VIEWPORT, (statics.SIDEBAR_SIZE, 0))
    statics.VIEWPORT.fill(statics.BACKGROUND_COLOR)
    
    statics.delta_time = statics.CLOCK.tick(60) / 1000

    #mouse position within level
    #NOTE math here is mathematically simplified version of original formula; future documentation will include its derivation
    level_mouse_position = Vector2(
        (2 * pygame.mouse.get_pos()[0] - statics.DISPLAY_SIZE[0] + statics.VIEWPORT_SIZE[0] - 2 * statics.offset.x) / (2 * statics.zoom),
        (2 * pygame.mouse.get_pos()[1] - statics.DISPLAY_SIZE[1] + statics.VIEWPORT_SIZE[1] - 2 * statics.offset.y) / (2 * statics.zoom),
    )

    #panning
    if pygame.mouse.get_pressed()[0]:
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            if not is_panning:
                initial_mouse_pos = pygame.mouse.get_pos()
                is_panning = True
            statics.offset = last_offset + (Vector2(pygame.mouse.get_pos()) - initial_mouse_pos)
        #when not panning, we can only be placing
        else:
            last_offset = statics.offset.copy()
            is_panning = False
            
            if in_level_bounds(level_mouse_position):                
                use_current_tool(get_tile_at_mouse())
    #reached when we are not panning or placing; if the mouse isn't down, we couldn't possibly be doing either
    else:
        last_offset = statics.offset.copy()
        is_panning = False

    #update tiles
    for y in range(statics.CANVAS_SIZE[1]):
        for x in range(statics.CANVAS_SIZE[0]):
            statics.tiles[y][x].update(statics.VIEWPORT)

    #draw a semitransparent highlighter tile to indicate current block pointed at
    if in_level_bounds(level_mouse_position):
        h_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
        h_tile.fill(statics.HIGHLIGHT_COLOR)
        statics.VIEWPORT.blit(h_tile, (
                round_to_n(level_mouse_position.x, statics.TILE_SIZE) * statics.zoom + statics.offset.x,
                round_to_n(level_mouse_position.y, statics.TILE_SIZE) * statics.zoom + statics.offset.y,
            )
        )

    #horizontal layout group update
    for element in hlg_0.elements:
        element.update(statics.DISPLAY)
    for element in hlg_1.elements:
        element.update(statics.DISPLAY)
   
    pygame.display.update()