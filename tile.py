import data

from pygame.math import Vector2
from pygame import draw, Rect

class Tile:
    position = None
    color = None
    
    __rect = None

    def __init__(self, position = Vector2(0, 0), color = (50, 50, 50)) -> None:                
        self.position = position.copy()
        self.color = color

        self.__rect = Rect(
            (self.position.x + data.offset.x) * data.zoom,
            (self.position.y + data.offset.y) * data.zoom,
            data.TILE_SIZE * data.zoom,
            data.TILE_SIZE * data.zoom
        )

        #auto add to tile registry
        data.tiles[int(position.y / data.TILE_SIZE)][int(position.x / data.TILE_SIZE)] = self

    def update(self, display):
        self.__rect.x = (self.position.x + data.offset.x) * data.zoom
        self.__rect.y = (self.position.y + data.offset.y) * data.zoom
        self.__rect.width = data.TILE_SIZE * data.zoom
        self.__rect.height = data.TILE_SIZE * data.zoom

        draw.rect(display, self.color, self.__rect)