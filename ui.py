import pygame

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

    def update(self, display: Surface):
        #scan for clicks
        if pygame.mouse.get_pressed()[0] and not self.__is_pressed:
            if self.__rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) and self.function != None:
                self.function(self.argument) #execute function if exists
            self.__is_pressed = True
        else:
            self.__is_pressed = False

        #draw rect
        draw.rect(display, self.color, self.__rect)
        
        #draw icon
        if self.icon != None:
            display.blit(self.icon, (self.__rect.center[0] - self.icon.get_width() / 2, self.__rect.center[1] - self.icon.get_height() / 2))