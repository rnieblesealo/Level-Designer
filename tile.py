import statics

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
            (self.position.x * statics.zoom + statics.offset.x),
            (self.position.y * statics.zoom + statics.offset.y),
            statics.TILE_SIZE * statics.zoom,
            statics.TILE_SIZE * statics.zoom
        )

        #auto add to tile registry
        statics.tiles[int(position.y / statics.TILE_SIZE)][int(position.x / statics.TILE_SIZE)] = self

    def update(self, display):
        self.__rect.x = (self.position.x * statics.zoom + statics.offset.x)
        self.__rect.y = (self.position.y * statics.zoom + statics.offset.y)
        self.__rect.width = statics.TILE_SIZE * statics.zoom
        self.__rect.height = statics.TILE_SIZE * statics.zoom

        draw.rect(display, self.color, self.__rect)

DEFAULT = TileInfo(-1, (25, 25, 25))
SAMPLE = TileInfo(0, (255, 0, 0))