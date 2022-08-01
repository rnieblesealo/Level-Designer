import pygame
import sys

from pygame.math import Vector2

import assets
import statics

from tile import TileCanvas
from tools import Toolbox
from ui import GUI

# Initialize app components
statics.initialize()
assets.initialize()
Toolbox.initialize()
TileCanvas.initialize()
GUI.initialize() # ! Must always be done AFTER level loading, as swatches must be loaded first to make swatch palette

# MAIN LOOP
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:            
            sys.exit()
        
        # TODO Figure out visual gridding bug (Zoom is disabled)
        # // elif event.type == pygame.MOUSEWHEEL:
        # //# data.zoom += event.y * 0.05 #zoom in according to mouse wheel

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        sys.exit()

    statics.update()
    TileCanvas.update()
    GUI.update()

    # Panning
    if pygame.mouse.get_pressed()[0]:
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            if not statics.is_panning:
                statics.pan_anchor = pygame.mouse.get_pos()
                statics.is_panning = True
            statics.offset = statics.last_pan_offset + (Vector2(pygame.mouse.get_pos()) - statics.pan_anchor)
        # When not panning but still clicking, we can only be using a tool
        else:
            statics.last_pan_offset = statics.offset.copy()
            statics.is_panning = False
            if Toolbox.current.is_selector: # We may use selection tools when our mouse is not in bounds; it has a better feel this way
                Toolbox.clear_selection() # Clear previous selection when we initiate marquee again; this indicates we would like to start a new one
            Toolbox.current.use()
            statics.is_using = True

    # Reached when we are not panning or placing; if the mouse isn't down, we couldn't possibly be doing either
    else:
        # Make a selection when selection tool is released!
        if Toolbox.current.is_selector and statics.is_using:
            Toolbox.make_selection()

        statics.last_pan_offset = statics.offset.copy()
        statics.is_panning = False
        statics.is_using_tool = False
    
    # Check for tool shortcuts
    if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
        Toolbox.delete_selection()

    # Draw a semitransparent highlighter tile to indicate current block pointed at
    if TileCanvas.mouse_in_bounds():
        TileCanvas.highlight_hovered_tile()

    pygame.display.flip()