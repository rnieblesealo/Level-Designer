import numpy
import pygame
import PIL.Image
import PIL.ImageTk
import tkinter

from pygame import Surface, Rect, draw
from pygame.math import Vector2
from tkinter import *
from tkinter import filedialog

import utils
import statics
import ui
import assets
import level_handler

from tile import TileCanvas
from tools import Toolbox

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
    # ! Modify architecture of multiple functions; it is a bit janky. Perhaps make a separate class for buttons with multiple functions?
    
    color = tuple
    icon: Surface

    functions = None
    arguments = None
    
    __color: tuple
    __is_pressed = False

    def __init__(self, position: Vector2, dimensions: tuple, color: tuple, icon: Surface, functions, arguments) -> None:
        super().__init__(position if position != None else Vector2(0, 0), dimensions)
        self.check_if_updates()

        self.color = color
        self.icon = icon
        
        if callable(functions):
            self.functions = (functions,) # * Syntax for initializing single-element tuple
            self.arguments = (arguments,)
        else:
            self.functions = functions
            self.arguments = arguments
    
    def update(self):
        # Scan for clicks
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.__is_pressed:
                    if len(self.functions) > 0 and len(self.functions) == len(self.arguments): # Execute all functions with their respective parameters in order provided
                        for i in range(len(self.functions)):
                            if self.arguments[i] != None:
                                self.functions[i](self.arguments[i])
                            else:
                                self.functions[i]() 
                        self.__color = utils.lerp_rgb(self.__color, (self.color[0] * 0.25, self.color[1] * 0.25, self.color[2] * 0.25), 7.5 * statics.delta_time)
                        self.__is_pressed = True
            else:
                self.__is_pressed = False
                self.__color = (0, 0, 0) # TODO (Fix failed interpolation) utils.lerp_rgb(self.__color, (self.color[0] * 0.75, self.color[1] * 0.75, self.color[2] * 0.75), 7.5 * statics.delta_time)
        else:
            self.__color = self.color

        # Draw background
        draw.rect(statics.DISPLAY, (self.__color), self.rect)
        
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
            button_i = ui.Button(Vector2(0, 0), button_size, statics.FOREGROUND_COLOR, pygame.transform.scale(items[i].get_texture(), (16, 16)), TileCanvas.set_swatch, items[i])
            utils.place_at_first_empty(button_i, self.palette, None) # Add button of each element to palette

class ToolPalette(ButtonPalette):
    def make_palette(self, items, shape, button_size):
        super().make_palette(items, shape, button_size)

        for i in range(len(items)):
            button_i = ui.Button(Vector2(0, 0), button_size, statics.FOREGROUND_COLOR, items[i].icon, Toolbox.set_tool, items[i])
            utils.place_at_first_empty(button_i, self.palette, None) # Add button of each element to palette

class TileEditor:
    # TODO Use hex to rgb converter to process this!
    PADDING = 5
    FOREGROUND_COLOR = '#4e596f'
    BACKGROUND_COLOR = '#242a38'
    MINUS_COLOR = '#ed553b'
    PLUS_COLOR = '#3caea3'
    FONT = ('Helvetica', 10, 'bold')
    
    active_window = None
    rows = None
    
    delete_image = None
    add_image = None
    
    add_button = None

    def open():
        # Create a new active window
        TileEditor.active_window = Tk()
        TileEditor.active_window.title('Tile Editor')
        TileEditor.active_window.configure(bg=TileEditor.FOREGROUND_COLOR)
        TileEditor.active_window.protocol('WM_DELETE_WINDOW', TileEditor.on_close)
        
        # Initialize window-dependent variables
        TileEditor.delete_image = PIL.ImageTk.PhotoImage(PIL.Image.open(assets.get_program_asset('minus.png')).resize((16, 16), PIL.Image.NEAREST))
        TileEditor.add_image = PIL.ImageTk.PhotoImage(PIL.Image.open(assets.get_program_asset('plus.png')).resize((16, 16), PIL.Image.NEAREST))

        # Append tile information to window
        TileEditor.rows = []
        for i, t in enumerate(TileCanvas.swatches):
            TileEditor.rows.append(TileInfoWidget(t, i, TileEditor.active_window))
        
        # Make add tile button
        TileEditor.add_button = tkinter.Button(TileEditor.active_window, image=TileEditor.add_image, background=TileEditor.PLUS_COLOR, command=TileEditor.create_tile)
        TileEditor.add_button.image = TileEditor.add_image
        TileEditor.add_button.grid(row=len(TileEditor.rows) + 1, column=0, sticky=W, padx=TileEditor.PADDING, pady=TileEditor.PADDING)

    def on_close():
        # Reload GUI to show changes to swatches
        GUI.reload()

        # Destroy window
        TileEditor.active_window.destroy()

    def create_tile():
        if len(TileCanvas.swatches) == statics.SWATCH_LIMIT:
            print("Cannot add swatch: swatch limit reached!")
            return
        
        # Add new swatch
        TileCanvas.add_to_swatches(['sky.png'])
        TileEditor.rows.append(TileInfoWidget(TileCanvas.swatches[len(TileCanvas.swatches) - 1], len(TileEditor.rows) + 1))

        # Reposition add button
        TileEditor.add_button.grid(row=len(TileEditor.rows) + 1, column=0, sticky=W, padx=TileEditor.PADDING, pady=TileEditor.PADDING)

    def delete_tile(index):
        if len(TileCanvas.swatches) == 1:
            print("Cannot remove swatch: At least 1 swatch is required!")
            return

        # Decache swatch texture, pop texture from swatches, destroy UI element
        TileCanvas.swatches[index].uncache_texture()
        TileCanvas.swatches.pop(index)
        TileEditor.rows.pop(index).delete()

        # If the selected swatch was the deleted tile, make the last swatch in the list the new active one
        if TileCanvas.swatch.deleted:
            TileCanvas.swatch = TileCanvas.swatches[len(TileCanvas.swatches) - 1]

        # Reposition add button
        TileEditor.add_button.grid(row=len(TileEditor.rows) + 1, column=0, sticky=W, padx=TileEditor.PADDING, pady=TileEditor.PADDING)

    def update():
        if TileEditor.active_window:
            TileEditor.active_window.mainloop()

class TileInfoWidget:
    info = None
    row = None

    texture_image = None
    
    delete_button: tkinter.Button
    icon_button: tkinter.Button
    id_label: Label
    tag_label: Label
    tag_entry: Entry

    def __init__(self, info, row, window = TileEditor.active_window) -> None:
        self.info = info
        self.row = row

        self.texture_image = PIL.ImageTk.PhotoImage(PIL.Image.open(info.texture_ref).resize((16, 16), PIL.Image.NEAREST))
        
        self.delete_button = tkinter.Button(window, image=TileEditor.delete_image, background=TileEditor.MINUS_COLOR, command=lambda:TileEditor.delete_tile(row))
        self.icon_button = tkinter.Button(window, image=self.texture_image, background=TileEditor.FOREGROUND_COLOR, command=self.prompt_icon_replacement)
        self.id_label = tkinter.Label(window, text='ID: {ID}'.format(ID=info.id), background=TileEditor.BACKGROUND_COLOR, foreground='white', font=TileEditor.FONT)
        self.tag_label = Label(window, text='Tags:', background=TileEditor.FOREGROUND_COLOR, foreground='white', font=TileEditor.FONT)
        self.tag_entry = Entry(window)
        
        self.icon_button.image = self.texture_image # ! Tkinter reference handling sucks, so we must assign this to prevent the image from getting destroyed.

        self.delete_button.grid(row=self.row, column=0, sticky=W, padx=TileEditor.PADDING, pady=TileEditor.PADDING)
        self.icon_button.grid(row=self.row, column=1, sticky=W, padx=TileEditor.PADDING, pady=TileEditor.PADDING)
        self.id_label.grid(row=self.row, column=2, sticky=W, padx=TileEditor.PADDING, pady=TileEditor.PADDING)
        self.tag_label.grid(row=self.row, column=3, sticky=W, padx=TileEditor.PADDING, pady=TileEditor.PADDING)
        self.tag_entry.grid(row=self.row, column=4, sticky=W, padx=TileEditor.PADDING, pady=TileEditor.PADDING)

    def delete(self):        
        # Destroy all widgets
        self.delete_button.destroy()
        self.icon_button.destroy()
        self.id_label.destroy()
        self.tag_label.destroy()
        self.tag_entry.destroy()

    def prompt_icon_replacement(self, window = TileEditor.active_window):
        # Get new texture
        path = filedialog.askopenfilename(defaultextension='.jpg', filetypes=[('PNG Image', '.png')])
        if path:
            # Update texture
            self.info.update_texture(path)

            # Reload level textures
            for y in range(statics.LEVEL_SIZE[1]):
                for x in range(statics.LEVEL_SIZE[0]):
                    statics.tiles[y][x].reload()

            # Rebuild icon widget
            self.texture_image = PIL.ImageTk.PhotoImage(PIL.Image.open(path).resize((16, 16), PIL.Image.NEAREST))
            self.icon_button = tkinter.Button(window, image=self.texture_image, background=TileEditor.FOREGROUND_COLOR, command=self.prompt_icon_replacement)
            self.icon_button.image = self.texture_image # ! Tkinter reference handling sucks, so we must assign this to prevent the image from getting destroyed.
            self.icon_button.grid(row=self.row, column=0, sticky=W, padx=TileEditor.PADDING, pady=TileEditor.PADDING)

            # Reload UI for displayed palette to properly show
            GUI.reload()

class GUI:
    # Variabless
    tool_palette = None
    tile_palette = None

    edit_tile_button = None
    save_button = None
    load_button = None
    save_buttons = None

    def reload():        
        # Re-initialize project-dependent UI components
        GUI.tile_palette = ui.TilePalette(items = TileCanvas.swatches, shape = (numpy.ceil(statics.SWATCH_LIMIT / 3).astype(int), 3), button_size = (32, 32), position = statics.R_SIDEBAR_TOPLEFT, dimensions = (statics.SIDEBAR_WIDTH, statics.DISPLAY_SIZE[1]), spacing = 30)

    # Init & Update
    def initialize():        
        # Initialize UI components
        GUI.tool_palette = ui.ToolPalette(items = Toolbox.toolbar, shape = (2, 2), button_size = (45, 45), position = Vector2(0, 0), dimensions = (statics.SIDEBAR_WIDTH, statics.DISPLAY_SIZE[1]), spacing = 30)
        GUI.tile_palette = ui.TilePalette(items = TileCanvas.swatches, shape = (numpy.ceil(statics.SWATCH_LIMIT / 3).astype(int), 3), button_size = (32, 32), position = statics.R_SIDEBAR_TOPLEFT, dimensions = (statics.SIDEBAR_WIDTH, statics.DISPLAY_SIZE[1]), spacing = 30)

        GUI.edit_tile_button = ui.Button(Vector2(statics.R_SIDEBAR_TOPLEFT[0], statics.DISPLAY_SIZE[1] - 45), (statics.SIDEBAR_WIDTH, 45), statics.EDIT_COLOR, assets.ICON_edit, TileEditor.open, None)
        GUI.save_button = ui.Button(Vector2(0, 0), (statics.SIDEBAR_WIDTH / 2, 45), statics.SAVE_COLOR, assets.ICON_save, level_handler.ProjectData.save_project, None)
        GUI.load_button = ui.Button(Vector2(0, 0), (statics.SIDEBAR_WIDTH / 2, 45), statics.LOAD_COLOR, assets.ICON_load, (level_handler.ProjectData.load_project, GUI.reload), (None, None))
        GUI.save_buttons = ui.HorizontalLayoutGroup([GUI.save_button, GUI.load_button], Vector2(0, statics.DISPLAY_SIZE[1] - 45), statics.SIDEBAR_WIDTH, 0)

    def update():
        # Update UI componentss
        GUI.tool_palette.update()
        GUI.tile_palette.update()
        GUI.save_buttons.update()
        GUI.edit_tile_button.update()

        # Handle external active_window
        TileEditor.update()