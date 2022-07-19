import pygame
import sys

import statics
import assets
import tools
import tile
import ui
import level_handler

from pygame.math import Vector2

pygame.init()
pygame.display.set_caption("Tile Drawing Test")

# Initialize backend components
statics.DISPLAY = pygame.display.set_mode(statics.DISPLAY_SIZE, pygame.DOUBLEBUF)
statics.VIEWPORT = pygame.Surface(statics.VIEWPORT_SIZE)
statics.CLOCK = pygame.time.Clock()

# Initialize app components
assets.load()
tools.load()

# # ! Test code; perform a blank start
# tile.add_to_swatches(['sky.png', 'grass.png', 'dirt.png', 'stone.png', 'water.png'])
# tile.fill_level(fill_tile=tile.DEFAULT)

# ! Test code; perform a load
level_data = level_handler.LevelData.load()
swatch_data = level_handler.SwatchData.load()

tile.load_swatches_from_level(level_data)
tile.load_swatches_from_data(swatch_data)

tile.load_level(level_data)

# Default offset such that level draw area is centered
statics.offset = Vector2(
    (statics.VIEWPORT_SIZE[0] - statics.LEVEL_SIZE[0] * statics.zoom) / 2,
    (statics.VIEWPORT_SIZE[1] - statics.LEVEL_SIZE[1] * statics.zoom) / 2
)

# Make tool palette
tool_palette = ui.ToolPalette(items = tools.toolbar, shape = (2, 2), button_size = (45, 45), position = Vector2(0, 0), dimensions = (statics.SIDEBAR_SIZE, statics.DISPLAY_SIZE[1]), spacing = 30)

# Make tile palette
tile_palette = ui.TilePalette(items = tile.swatches, shape = (4, 3), button_size = (32, 32), position = statics.R_SIDEBAR_TOPLEFT, dimensions = (statics.SIDEBAR_SIZE, statics.DISPLAY_SIZE[1]), spacing = 30)

# MAIN LOOP
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # ! Test code; perform a save
            print(statics.tiles.shape)
            level_handler.LevelData.save(statics.tiles)
            level_handler.SwatchData.save(tile.swatches)
            
            sys.exit()
        
        # TODO Figure out visual gridding bug (Zoom is disabled)
        # // elif event.type == pygame.MOUSEWHEEL:
        # //# data.zoom += event.y * 0.05 #zoom in according to mouse wheel

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        sys.exit()

    # Update backend components
    statics.DISPLAY.fill(statics.FOREGROUND_COLOR)
    statics.DISPLAY.blit(statics.VIEWPORT, (statics.SIDEBAR_SIZE, 0))
    statics.VIEWPORT.fill(statics.BACKGROUND_COLOR)
    
    # Update dynamic app static variables
    statics.delta_time = statics.CLOCK.tick(60) / 1000
    statics.real_tile_size = statics.TILE_SIZE * statics.zoom
    statics.real_mouse_pos = Vector2(
        (2 * pygame.mouse.get_pos()[0] - statics.DISPLAY_SIZE[0] + statics.VIEWPORT_SIZE[0] - 2 * statics.offset.x) / (2 * statics.zoom),
        (2 * pygame.mouse.get_pos()[1] - statics.DISPLAY_SIZE[1] + statics.VIEWPORT_SIZE[1] - 2 * statics.offset.y) / (2 * statics.zoom),
    )
    
    # Scale highlight tiles to match current tile scale
    pygame.transform.scale(tile.highlight_tile, (statics.real_tile_size, statics.real_tile_size))
    pygame.transform.scale(tile.select_tile, (statics.real_tile_size, statics.real_tile_size))

    # Update tiles
    tile.update_tiles()

    tool_palette.update()
    tile_palette.update()

    # Panning
    if pygame.mouse.get_pressed()[0]:
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            if not statics.is_panning:
                statics.initial_pan_mouse_pos = pygame.mouse.get_pos()
                statics.is_panning = True
            statics.offset = statics.last_pan_offset + (Vector2(pygame.mouse.get_pos()) - statics.initial_pan_mouse_pos)
        # When not panning but still clicking, we can only be using a tool
        else:
            statics.last_pan_offset = statics.offset.copy()
            statics.is_panning = False
            if tools.current.is_selector: # We may use selection tools when our mouse is not in bounds; it has a better feel this way
                tools.clear_selection() # Clear previous selection when we initiate marquee again; this indicates we would like to start a new one
            tools.current.use()
            statics.is_using = True

    # Reached when we are not panning or placing; if the mouse isn't down, we couldn't possibly be doing either
    else:
        # Make a selection when selection tool is released!
        if tools.current.is_selector and statics.is_using:
            tools.make_selection()

        statics.last_pan_offset = statics.offset.copy()
        statics.is_panning = False
        statics.is_using_tool = False
    
    # Check for tool shortcuts
    if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
        tools.delete_selection()

    # Draw a semitransparent highlighter tile to indicate current block pointed at
    if statics.mouse_in_bounds():
        tile.highlight_hovered_tile()

    pygame.display.update()