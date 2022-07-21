import pygame
import numpy
import utils
import statics
import tools
import tile
import ui
import assets
import level_handler

from typing import Any, Callable
from tkinter import filedialog
from pygame import Surface, Rect, draw
from pygame.math import Vector2

class UIElement:
    position: Vector2
    dimensions: tuple
    rect: Rect
    updates = False # Does this UI element implement an update() function?

    def __init__(self, rect: Rect) -> None:
        self.position = rect.topleft
        self.dimensions = (rect.w, rect.h)
        self.rect = rect.copy()
    
    def __init__(self, position: Vector2, dimensions: Vector2) -> None:
        self.position = position.copy()
        self.dimensions = dimensions
        self.rect = Rect(
            self.position.x,
            self.position.y,
            self.dimensions[0],
            self.dimensions[1]
        )

    # ! Must call in ALL child objects on init!
    def check_if_updates(self):
        self.updates = True if getattr(self, 'update', None) != None else False

    # ! Use these setters at all times
    def set_position(self, x, y):
        self.position.x = x
        self.position.y = y
        self.rect.topleft = (x, y)

    def set_dimensions(self, w, h):
        self.rect.w = w
        self.rect.h = h

class Button(UIElement):
    color = tuple
    icon: Surface

    function = None
    argument = None
    
    __color: tuple
    __is_pressed = False

    def __init__(self, position: Vector2, dimensions: tuple, color: tuple, icon: Surface, function: Callable, argument: Any) -> None:
        super().__init__(position if position != None else Vector2(0, 0), dimensions)
        self.check_if_updates()

        self.color = color
        self.icon = icon
        self.function = function
        self.argument = argument
                
    def update(self):
        # Scan for clicks
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.__is_pressed:
                    if self.function != None:
                        if self.argument != None:
                            self.function(self.argument)
                        else:
                            self.function() 
                        self.__color = utils.lerp_rgb(self.__color, (self.color[0] * 0.25, self.color[1] * 0.25, self.color[2] * 0.25), 7.5 * statics.delta_time)
                        self.__is_pressed = True
            else:
                self.__is_pressed = False
                self.__color = utils.lerp_rgb(self.__color, (self.color[0] * 0.75, self.color[1] * 0.75, self.color[2] * 0.75), 7.5 * statics.delta_time)
        else:
            self.__color = self.color

        # Draw background
        draw.rect(statics.DISPLAY, self.__color, self.rect)
        
        # Draw icon at center
        if self.icon != None:
            statics.DISPLAY.blit(self.icon, (self.rect.center[0] - self.icon.get_width() / 2, self.rect.center[1] - self.icon.get_height() / 2))

class VerticalLayoutGroup(UIElement):
    # ! All elements within group must have the same height!

    elements: list
    spacing: int
    padding: int
    element_height: int

    def __init__(self, elements: list, position: Vector2, height: Vector2, spacing: int) -> None:
        self.elements = elements
        self.spacing = spacing
        
        super().__init__(position, (self.elements[0].dimensions[0], height))
        self.check_if_updates()
        
        # Organize elements using LG properties
        self.organize()

    # ! Call only once, NEVER every frame!
    def organize(self):
        self.element_height = self.elements[0].dimensions[1]
        self.padding = (self.dimensions[1] - (self.element_height * len(self.elements)) - (self.spacing * (len(self.elements) - 1))) / 2
        
        for y in range(len(self.elements)):
            self.elements[y].set_position(
                self.position.x,
                self.position.y + self.padding + self.element_height * y + self.spacing * y,
            )
            
            if type(self.elements[y]) == HorizontalLayoutGroup or type(self.elements[y]) == VerticalLayoutGroup:
                self.elements[y].organize() # Organize child LG elements to match new organizations

    def update(self):
        # Update children of this layout group if they define an argumentless update() function
        for element in self.elements:
            if element.updates:
                element.update()

class HorizontalLayoutGroup(UIElement):
    # ! All elements within group must have the same width!

    elements: list
    spacing: int
    padding: int
    element_width: int

    def __init__(self, elements: list, position: Vector2, width: Vector2, spacing: int) -> None:
        self.elements = elements
        self.spacing = spacing
        
        super().__init__(position, (width, self.elements[0].dimensions[1]))
        self.check_if_updates()
        
        # Organize elements using LG properties
        self.organize()

    # ! Call only once, NEVER every frame!
    def organize(self):
        self.element_width = self.elements[0].dimensions[0]
        self.padding = (self.dimensions[0] - (self.element_width * len(self.elements)) - (self.spacing * (len(self.elements) - 1))) / 2
        
        for x in range(len(self.elements)):
            self.elements[x].set_position(
                self.position.x + self.padding + self.element_width * x + self.spacing * x,
                self.position.y
            )
            
            if type(self.elements[x]) == HorizontalLayoutGroup or type(self.elements[x]) == VerticalLayoutGroup:
                self.elements[x].organize() # Organize child LG elements to match new organizations

    def update(self):
        # Update children of this layout group if they define an argumentless update() function
        for element in self.elements:
            if element.updates:
                element.update()

class ButtonPalette(UIElement):
    palette = None
    group = None
    rows = None
    
    spacing = 0

    def __init__(self, items, shape, button_size, position, dimensions, spacing) -> None:
        super().__init__(position, dimensions)
        self.check_if_updates()

        self.spacing = spacing
        
        # Make palette and group on initialize
        self.make_palette(items, shape, button_size)
        self.make_group()
    
    # ! Add procedure to make buttons as override; by default, make_palette() only initializes palette matrix!
    def make_palette(self, items, shape, button_size):
        self.palette = numpy.empty(shape, dtype=ui.Button) # Build empty matrix with passed shape

    def make_group(self):        
        # Initialize rows manifest
        self.rows = []
        
        # Make individual row horizontal layout groups
        for i in range(self.palette.shape[0]):
            if self.palette[i][0] == None: # Terminate group construction if next row is empty
                break
            row_i = []
            for j in range(self.palette.shape[1]):
                if self.palette[i][j] != None:
                    row_i.append(self.palette[i][j])
                else:
                    break
            row_i_hlg = ui.HorizontalLayoutGroup(row_i, Vector2(0, 0), self.dimensions[0], self.spacing)
            self.rows.append(row_i_hlg)
        
        # Place all into vertical layout group NOTE At topleft of screen by dafault
        self.group = ui.VerticalLayoutGroup(self.rows, self.position, self.dimensions[1], self.spacing)

    def update(self):
        # Update all buttons
        self.group.update()

class TilePalette(ButtonPalette):    
    def make_palette(self, items, shape, button_size):
        super().make_palette(items, shape, button_size)
        
        for i in range(len(items)):
            button_i = ui.Button(Vector2(0, 0), button_size, statics.FOREGROUND_COLOR, items[i].get_texture(), tile.set_swatch, items[i])
            statics.place_at_first_empty(button_i, self.palette, None) # Add button of each element to palette

class ToolPalette(ButtonPalette):
    def make_palette(self, items, shape, button_size):
        super().make_palette(items, shape, button_size)

        for i in range(len(items)):
            button_i = ui.Button(Vector2(0, 0), button_size, statics.FOREGROUND_COLOR, items[i].icon, tools.set_tool, items[i])
            statics.place_at_first_empty(button_i, self.palette, None) # Add button of each element to palette

tool_palette = None
tile_palette = None

save_button = None
load_button = None
save_buttons = None

def load():
    global tool_palette, tile_palette, save_button, load_button, save_buttons
    
    # Initialize UI components
    tool_palette = ui.ToolPalette(items = tools.toolbar, shape = (2, 2), button_size = (45, 45), position = Vector2(0, 0), dimensions = (statics.SIDEBAR_WIDTH, statics.DISPLAY_SIZE[1]), spacing = 30)
    tile_palette = ui.TilePalette(items = tile.swatches, shape = (4, 3), button_size = (32, 32), position = statics.R_SIDEBAR_TOPLEFT, dimensions = (statics.SIDEBAR_WIDTH, statics.DISPLAY_SIZE[1]), spacing = 30)

    save_button = ui.Button(Vector2(0, 0), (statics.SIDEBAR_WIDTH / 2, 45), statics.POSITIVE_COLOR, assets.ICON_save, level_handler.save_project, None)
    load_button = ui.Button(Vector2(0, 0), (statics.SIDEBAR_WIDTH / 2, 45), statics.NEGATIVE_COLOR, assets.ICON_load, level_handler.load_project, None)
    save_buttons = ui.HorizontalLayoutGroup([save_button, load_button], Vector2(0, statics.DISPLAY_SIZE[1] - 45), statics.SIDEBAR_WIDTH, 0)

def update():
    # Update UI componentss
    tool_palette.update()
    tile_palette.update()
    save_buttons.update()