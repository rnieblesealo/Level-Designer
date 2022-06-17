import pygame

from pygame import Surface, Rect, draw
from pygame.math import Vector2

class Button:
    position: Vector2
    bounds: tuple

    function = None
    
    __rect: Rect
    __is_pressed = False

    def __init__(self, position: Vector2, bounds: tuple, function = print) -> None:
        self.position = position.copy()
        self.bounds = bounds
        self.function = function
        
        self.__rect = Rect(
            self.position.x,
            self.position.y,
            self.bounds[0],
            self.bounds[1]
        )

    def update(self, display: Surface):
        #scan for clicks
        if pygame.mouse.get_pressed()[0] and not self.__is_pressed:
            if self.__rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                self.function("Hey!")
            self.__is_pressed = True
        else:
            self.__is_pressed = False

        #draw
        draw.rect(display, (255, 255, 255), self.__rect)