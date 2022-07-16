import pygame
import sys

import statics
import assets
import tools
import tile
import ui

from pygame.math import Vector2

pygame.init()
pygame.display.set_caption("Tile Drawing Test")

# Initialize backend components
statics.DISPLAY = pygame.display.set_mode(statics.DISPLAY_SIZE, pygame.DOUBLEBUF)
statics.VIEWPORT = pygame.Surface(statics.VIEWPORT_SIZE)
statics.CLOCK = pygame.time.Clock()

# Initialize app components
assets.load()

# ! Test code; remove later; add swatches and fill level
tile.add_to_swatches(['sky.png', 'grass.png', 'dirt.png', 'stone.png', 'water.png'])
tile.fill_level(tile.DEFAULT)

# Default offset such that level draw area is centered
statics.offset = Vector2(
    (statics.VIEWPORT_SIZE[0] - statics.LEVEL_SIZE[0] * statics.zoom) / 2,
    (statics.VIEWPORT_SIZE[1] - statics.LEVEL_SIZE[1] * statics.zoom) / 2
)

# Set up tool buttons NOTE Position is (0, 0) because we will auto-set it with layout groups
BTN_pencil = ui.Button(Vector2(0, 0), (45, 45), statics.FOREGROUND_COLOR, assets.ICON_pencil, tools.set_tool, tools.t_pencil)
BTN_eraser = ui.Button(Vector2(0, 0), (45, 45), statics.FOREGROUND_COLOR, assets.ICON_eraser, tools.set_tool, tools.t_eraser)
BTN_marquee = ui.Button(Vector2(0, 0), (45, 45), statics.FOREGROUND_COLOR, assets.ICON_marquee, tools.set_tool, tools.t_marquee)

# Make button layout groups
btn_row_0 = ui.HorizontalLayoutGroup([BTN_pencil, BTN_eraser], Vector2(0, 0), statics.SIDEBAR_SIZE, 30)
btn_row_1 = ui.HorizontalLayoutGroup([BTN_marquee], Vector2(0, 0), statics.SIDEBAR_SIZE, 30)

btn_col = ui.VerticalLayoutGroup(
    [btn_row_0, btn_row_1],
    Vector2(0, 0),
    statics.DISPLAY_SIZE[1],
    30
)

# Make tile palette
tile_palette = ui.TilePalette(items = tile.swatches, shape = (4, 3), button_size = (32, 32), pos = statics.R_SIDEBAR_TOPLEFT, x_span = statics.SIDEBAR_SIZE, y_span = statics.DISPLAY_SIZE[1], spacing = 30)

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

    # Button layout group update TODO Rework this similarly to how the tile palette works
    for y in range(len(btn_col.elements)):
        for x in range(len(btn_col.elements[y].elements)):
            btn_col.elements[y].elements[x].update(statics.DISPLAY)

    # Tile palette update
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
            if tools.use_current_tool == tools.t_marquee: # We may use selection tools when our mouse is not in bounds; it has a better feel this way
                tools.clear_selection() # Clear previous selection when we initiate marquee again; this indicates we would like to start a new one
                tools.use_current_tool()
            elif statics.mouse_in_bounds():
                tools.use_current_tool(statics.get_tile_at_mouse()) # ? For now? Maybe refine tools to be a class containing metadata
            statics.is_using = True

    # Reached when we are not panning or placing; if the mouse isn't down, we couldn't possibly be doing either
    else:
        # Make a selection when selection tool is released!
        if tools.use_current_tool == tools.t_marquee and statics.is_using:
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