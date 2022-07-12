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
is_using = False

# TOOLS -- TEMPORARY PLACEMENT HERE! ================================================

selection = Rect(0, 0, 0, 0)
selection_anchor = (0, 0)
selection_buffer = [] #stores all selected objects

def make_selection():
    for y in range(statics.CANVAS_SIZE[1]):
        for x in range(statics.CANVAS_SIZE[0]):
            if statics.tiles[y][x].rect.colliderect(selection):
                selection_buffer.append(statics.tiles[y][x])
                statics.tiles[y][x].selected = True

def clear_selection():
    if len(selection_buffer) == 0:
        return
    for tile in selection_buffer:
        tile.selected = False
    selection_buffer.clear() 

def delete_all():
    if len(selection_buffer) == 0:
        return
    for _tile in selection_buffer:
        _tile = tile.Tile(tile.erased, _tile.position)

def pencil(_tile):
    #replace tile w/selected one
    _tile = tile.Tile(tile.swatch, _tile.position)

def eraser(_tile):
    #replace operand tile w/blank tile
    _tile = tile.Tile(tile.erased, _tile.position)

def marquee():
    global selection
    global selection_anchor
    
    if not is_using:
        selection_anchor = (
            pygame.mouse.get_pos()[0] - statics.VIEWPORT_OFFSET[0], 
            pygame.mouse.get_pos()[1] - statics.VIEWPORT_OFFSET[1]
            )
    
    dx = pygame.mouse.get_pos()[0] - statics.VIEWPORT_OFFSET[0]
    dy = pygame.mouse.get_pos()[1] - statics.VIEWPORT_OFFSET[1]
    
    # ? Why does this work?
    selection = Rect(
        selection_anchor[0],
        selection_anchor[1],
        dx - selection_anchor[0],
        dy - selection_anchor[1]
    )

    pygame.draw.rect(statics.VIEWPORT, statics.HIGHLIGHT_COLOR, selection, 1, 1)

def set_tool(new_tool):
    global current_tool, is_using
    
    clear_selection() # Clear previous selection when we switch tools!
    
    is_using = False # Clear previous tool state
    current_tool = new_tool

current_tool = pencil

# Center level draw area over viewport
statics.offset = Vector2(
    (statics.VIEWPORT_SIZE[0] - statics.LEVEL_SIZE[0] * statics.zoom) / 2,
    (statics.VIEWPORT_SIZE[1] - statics.LEVEL_SIZE[1] * statics.zoom) / 2
)

# * TEMPORARY: Add tile swatches
tile.add_to_swatches(['sky.png', 'grass.png', 'dirt.png', 'stone.png', 'water.png'])

# Fill canvas with desired tile
tile.fill_level(tile.DEFAULT)

# Set up tool buttons
pencil_button = ui.Button(Vector2(0, 0), (45, 45), statics.FOREGROUND_COLOR, pencil_icon, set_tool, pencil)
eraser_button = ui.Button(Vector2(0, 0), (45, 45), statics.FOREGROUND_COLOR, eraser_icon, set_tool, eraser)
marquee_button = ui.Button(Vector2(0, 0), (45, 45), statics.FOREGROUND_COLOR, marquee_icon, set_tool, marquee)

# Make button layout groups
btn_row_0 = ui.HorizontalLayoutGroup([pencil_button, eraser_button], Vector2(0, 0), statics.SIDEBAR_SIZE, 30)
btn_row_1 = ui.HorizontalLayoutGroup([marquee_button], Vector2(0, 0), statics.SIDEBAR_SIZE, 30)

btn_col = ui.VerticalLayoutGroup(
    [
        btn_row_0,
        btn_row_1
    ],
    Vector2(0, 0),
    statics.DISPLAY_SIZE[1],
    30
)

# Make swatch buttons
# TODO FINALIZE AND COMMENT THIS CODE
def place_at_empty(item, matrix, empty):
    # ! Only works for 2D arrays
    if len(matrix.shape) > 2:
        return
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            if matrix[y][x] == empty:
                matrix[y][x] = item
                return

# TODO Merge these two operations, there is redundancy (it works as indended, though; this is why it has been committed as is)
swatch_palette = numpy.empty((4, 3), dtype=ui.Button)
for i in range(len(tile.swatches)):
    place_at_empty(
        ui.Button(Vector2(0, 0), (32, 32), statics.FOREGROUND_COLOR, tile.swatches[i].get_texture(), tile.set_swatch, tile.swatches[i]),
        swatch_palette,
        None
    )

elements = []
for i in range(swatch_palette.shape[0]):
    if swatch_palette[i][0] == None:
        break
    row = []
    for j in range(swatch_palette.shape[1]):
        if swatch_palette[i][j] != None:
            row.append(swatch_palette[i][j])
    elements.append(ui.HorizontalLayoutGroup(row, Vector2(0, 0), statics.SIDEBAR_SIZE, 30))
hlg = ui.VerticalLayoutGroup(elements, Vector2(statics.VIEWPORT_SIZE[0] + statics.SIDEBAR_SIZE, 0), statics.DISPLAY_SIZE[1], 30) # TODO Add static reference to top-right corner of right foreground panel's position

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        # TODO Figure out visual gridding bug (Zoom is disabled)
        # // elif event.type == pygame.MOUSEWHEEL:
        # //# data.zoom += event.y * 0.05 #zoom in according to mouse wheel

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        sys.exit()

    statics.DISPLAY.fill(statics.FOREGROUND_COLOR)
    statics.DISPLAY.blit(statics.VIEWPORT, (statics.SIDEBAR_SIZE, 0))
    statics.VIEWPORT.fill(statics.BACKGROUND_COLOR)
    
    statics.delta_time = statics.CLOCK.tick(60) / 1000
    statics.real_tile_size = statics.TILE_SIZE * statics.zoom

    statics.real_mouse_position = Vector2(
        (2 * pygame.mouse.get_pos()[0] - statics.DISPLAY_SIZE[0] + statics.VIEWPORT_SIZE[0] - 2 * statics.offset.x) / (2 * statics.zoom),
        (2 * pygame.mouse.get_pos()[1] - statics.DISPLAY_SIZE[1] + statics.VIEWPORT_SIZE[1] - 2 * statics.offset.y) / (2 * statics.zoom),
    )
    
    pygame.transform.scale(tile.highlight_tile, (statics.real_tile_size, statics.real_tile_size))
    pygame.transform.scale(tile.select_tile, (statics.real_tile_size, statics.real_tile_size))

    #update tiles
    for y in range(statics.CANVAS_SIZE[1]):
        for x in range(statics.CANVAS_SIZE[0]):
            statics.tiles[y][x].update(statics.VIEWPORT)

    # Layout group update
    for y in range(len(btn_col.elements)):
        for x in range(len(btn_col.elements[y].elements)):
            btn_col.elements[y].elements[x].update(statics.DISPLAY)

    # Layout group update
    for y in range(len(hlg.elements)):
        for x in range(len(hlg.elements[y].elements)):
            hlg.elements[y].elements[x].update(statics.DISPLAY)

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
            if current_tool == marquee: # We may use selection tools when our mouse is not in bounds; it has a better feel this way
                clear_selection() # Clear previous selection when we initiate marquee again; this indicates we would like to start a new one
                current_tool()
            elif statics.mouse_in_bounds():
                current_tool(statics.get_tile_at_mouse()) # ? For now? Maybe refine tools to be a class containing metadata
            is_using = True

    #reached when we are not panning or placing; if the mouse isn't down, we couldn't possibly be doing either
    else:
        # Make a selection when selection tool is released!
        if current_tool == marquee and is_using:
            make_selection()

        last_offset = statics.offset.copy()
        is_panning = False
        is_using = False
    
    #tool shortcuts
    if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
        delete_all()

    #draw a semitransparent highlighter tile to indicate current block pointed at
    if statics.mouse_in_bounds():
        tile.highlight_hovered_tile()

    pygame.display.update()