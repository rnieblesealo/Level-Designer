import tile
import statics
import pygame

from pygame import Rect

selection = Rect(0, 0, 0, 0)
selection_anchor = (0, 0)
selection_buffer = [] # Stores objects in current selection

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

def delete_selection():
    if len(selection_buffer) == 0:
        return
    for _tile in selection_buffer:
        _tile = tile.Tile(tile.erased, _tile.position)

def set_tool(new_tool):
    global use_current_tool, is_using
    
    clear_selection() # Clear previous selection when we switch tools!
    
    is_using = False # Clear previous tool state
    use_current_tool = new_tool

def t_pencil(_tile):
    #replace tile w/selected one
    _tile = tile.Tile(tile.swatch, _tile.position)

def t_eraser(_tile):
    #replace operand tile w/blank tile
    _tile = tile.Tile(tile.erased, _tile.position)

def t_marquee():
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

use_current_tool = t_pencil