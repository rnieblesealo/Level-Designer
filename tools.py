import tile
import statics
import assets
import pygame

from pygame import Rect

# Classes
class Tool():
    icon = None
    is_selector = False

    def use(self):
        print('No function has been assigned to this tool!')

class Pencil(Tool):
    is_selector = False

    def use():
        if not statics.mouse_in_bounds():
            return
        
        # Replace selected tile w/one in argument
        operand = statics.get_tile_at_mouse()
        operand = tile.Tile(tile.swatch, operand.position)

class Eraser(Tool):
    is_selector = False

    def use():
        if not statics.mouse_in_bounds():
            return
        
        # Replace selected tile w/default one set in tile.py
        operand = statics.get_tile_at_mouse()
        operand = tile.Tile(tile.DEFAULT, operand.position)

class Marquee(Tool):
    is_selector = True

    def use():
        global selection
        global selection_anchor

        if not statics.is_using_tool:
            selection_anchor = (
                pygame.mouse.get_pos()[0] - statics.VIEWPORT_OFFSET[0], 
                pygame.mouse.get_pos()[1] - statics.VIEWPORT_OFFSET[1]
                )
        
        dx = pygame.mouse.get_pos()[0] - statics.VIEWPORT_OFFSET[0]
        dy = pygame.mouse.get_pos()[1] - statics.VIEWPORT_OFFSET[1]
        
        # ? Why does this work?
        # ! It doesn't! Fix this.
        selection = Rect(
            selection_anchor[0],
            selection_anchor[1],
            dx - selection_anchor[0],
            dy - selection_anchor[1]
        )

        pygame.draw.rect(statics.VIEWPORT, (0, 0, 0), selection, 10, 10)

# Methods
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
    global current
    
    clear_selection() # Clear previous selection when we switch tools!
        
    statics.is_using = False # Clear previous tool state
    current = new_tool

# Init
def initialize():
    # Load all tool icons
    Pencil.icon = assets.ICON_pencil
    Eraser.icon = assets.ICON_eraser
    Marquee.icon = assets.ICON_marquee

# Variables
toolbar = [Pencil, Eraser, Marquee] # We use types rather than instances, as instances are not required
current = Pencil

selection = Rect(0, 0, 0, 0)
selection_anchor = (0, 0)
selection_buffer = [] # Stores objects in current selection