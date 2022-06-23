import pygame
import utils
import statics

from typing import Any, Callable
from pygame import Surface, Rect, draw
from pygame.math import Vector2

class Button:
    position: Vector2
    bounds: tuple
    color = tuple
    icon: Surface

    function = None
    argument = None
    
    __rect: Rect
    __color: tuple
    __is_pressed = False

    def __init__(self, position: Vector2, bounds: tuple, color: tuple, icon: Surface, function: Callable, argument: Any) -> None:
        self.position = position.copy()
        self.bounds = bounds
        self.color = color
        self.icon = icon
        self.function = function
        self.argument = argument
        
        self.__rect = Rect(
            self.position.x,
            self.position.y,
            self.bounds[0],
            self.bounds[1]
        )
        
    def get_rect(self):
        return self.__rect

    def update(self, display: Surface):
        #scan for clicks TODO fix this monstrosity
        if self.__rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.__is_pressed:
                    if self.function != None:
                        self.function(self.argument)
                        self.__color = utils.lerp_rgb(self.__color, (
                            self.color[0] * 0.25, 
                            self.color[1] * 0.25, 
                            self.color[2] * 0.25
                        ), 7.5 * statics.delta_time)
                    self.__is_pressed = True
            else:
                self.__is_pressed = False
                self.__color = utils.lerp_rgb(self.__color, (
                    self.color[0] * 0.75, 
                    self.color[1] * 0.75, 
                    self.color[2] * 0.75
                ), 7.5 * statics.delta_time)
        else:
            self.__color = self.color

        #draw rect
        draw.rect(display, self.__color, self.__rect)
        
        #draw icon
        if self.icon != None:
            display.blit(self.icon, (self.__rect.center[0] - self.icon.get_width() / 2, self.__rect.center[1] - self.icon.get_height() / 2))

class HorizontalLayoutGroup:
    #NOTE: All elements within group must have the same width!

    elements: list
    handle: Rect
    spacing: int

    __element_width: int
    __padding: int

    def __init__(self, elements: list, handle: Rect, spacing: int) -> None:
        self.elements = elements
        self.handle = handle
        self.spacing = spacing

        self.__element_width = self.elements[0].get_rect().width    
        self.__padding = (self.handle.width - (self.__element_width * len(self.elements)) - (self.spacing * (len(self.elements) - 1))) / 2

        #organize elements
        self.organize()

    #call only once, NEVER in update
    def organize(self):
        for x in range(len(self.elements)):
            rect = self.elements[x].get_rect()
            rect.left = self.handle.left + self.__padding + self.__element_width * x + self.spacing * x
            rect.top = self.handle.top