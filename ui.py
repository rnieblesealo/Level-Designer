import pygame
import utils
import statics

from typing import Any, Callable
from pygame import Surface, Rect, draw
from pygame.math import Vector2

class Graphic:
    position: Vector2
    dimensions: tuple
    rect: Rect

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

    # ! Use these setters at all times!

    def set_position(self, x, y):
        self.position.x = x
        self.position.y = y
        self.rect.topleft = (x, y)

    def set_dimensions(self, w, h):
        self.rect.w = w
        self.rect.h = h

class Button(Graphic):
    color = tuple
    icon: Surface

    function = None
    argument = None
    
    __color: tuple
    __is_pressed = False

    def __init__(self, position: Vector2, dimensions: tuple, color: tuple, icon: Surface, function: Callable, argument: Any) -> None:
        super().__init__(position, dimensions)

        self.color = color
        self.icon = icon
        self.function = function
        self.argument = argument
                
    def update(self, display: Surface):
        # Scan for clicks
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.__is_pressed:
                    if self.function != None:
                        self.function(self.argument)
                        self.__color = utils.lerp_rgb(self.__color, (self.color[0] * 0.25, self.color[1] * 0.25, self.color[2] * 0.25), 7.5 * statics.delta_time)
                        self.__is_pressed = True
            else:
                self.__is_pressed = False
                self.__color = utils.lerp_rgb(self.__color, (self.color[0] * 0.75, self.color[1] * 0.75, self.color[2] * 0.75), 7.5 * statics.delta_time)
        else:
            self.__color = self.color

        # Draw background
        draw.rect(display, self.__color, self.rect)
        
        # Draw icon
        if self.icon != None:
            display.blit(self.icon, (self.rect.center[0] - self.icon.get_width() / 2, self.rect.center[1] - self.icon.get_height() / 2))

class VerticalLayoutGroup(Graphic):
    # ! All elements within group must have the same height!

    elements: list
    spacing: int
    padding: int
    element_height: int

    def __init__(self, elements: list, position: Vector2, height: Vector2, spacing: int) -> None:
        self.elements = elements
        self.spacing = spacing
        self.element_height = self.elements[0].dimensions[1]
        
        super().__init__(position, (self.elements[0].dimensions[0], height))
        
        self.padding = (self.dimensions[1] - (self.element_height * len(self.elements)) - (self.spacing * (len(self.elements) - 1))) / 2

        # Organize elements using LG properties
        self.organize()

    # ! Call only once, NEVER every frame!
    def organize(self):
        for y in range(len(self.elements)):
            self.elements[y].set_position(
                self.position.x,
                self.position.y + self.padding + self.element_height * y + self.spacing * y,
            )
            if type(self.elements[y]) == HorizontalLayoutGroup or type(self.elements[y]) == VerticalLayoutGroup:
                self.elements[y].organize() # Organize child LG elements to match new organizations

class HorizontalLayoutGroup(Graphic):
    # ! All elements within group must have the same width!

    elements: list
    spacing: int
    padding: int
    element_width: int

    def __init__(self, elements: list, position: Vector2, width: Vector2, spacing: int) -> None:
        self.elements = elements
        self.spacing = spacing
        self.element_width = self.elements[0].dimensions[0]
        
        super().__init__(position, (width, self.elements[0].dimensions[1]))
        
        self.padding = (self.dimensions[0] - (self.element_width * len(self.elements)) - (self.spacing * (len(self.elements) - 1))) / 2

        # Organize elements using LG properties
        self.organize()

    # ! Call only once, NEVER every frame!
    def organize(self):
        for x in range(len(self.elements)):
            self.elements[x].set_position(
                self.position.x + self.padding + self.element_width * x + self.spacing * x,
                self.position.y
            )
            if type(self.elements[x]) == HorizontalLayoutGroup or type(self.elements[x]) == VerticalLayoutGroup:
                self.elements[x].organize() # Organize child LG elements to match new organizations