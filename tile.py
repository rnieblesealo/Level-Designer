import data

from pygame.math import Vector2
from pygame import draw, Rect

class TileInfo:
    color = (0, 0, 0)
    tag = 0

    def __init__(self, tag = 0, color = (0, 0, 0)) -> None:
        self.tag = tag
        self.color = color

class Tile:
    info = None
    position = None
    
    __rect = None

    def __init__(self, info: TileInfo, position = Vector2(0, 0)) -> None:                
        self.info = info
        self.position = position.copy()

        self.color = info.color

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

DEFAULT = TileInfo(-1, (25, 25, 25))
SAMPLE = TileInfo(0, (255, 0, 0))