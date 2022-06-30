import statics
import pygame

from pygame.math import Vector2
from pygame import draw, Rect

h_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
h_tile.fill(statics.HIGHLIGHT_COLOR)

s_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
s_tile.fill(statics.SELECTED_COLOR)

def highlight_hovered_tile():
    statics.VIEWPORT.blit(h_tile, (
            statics.round_to_n(statics.real_mouse_position.x, statics.TILE_SIZE) * statics.zoom + statics.offset.x,
            statics.round_to_n(statics.real_mouse_position.y, statics.TILE_SIZE) * statics.zoom + statics.offset.y
        )
    )

class TileInfo:
    color = (0, 0, 0)
    tag = 0

    def __init__(self, tag = 0, color = (0, 0, 0)) -> None:
        self.tag = tag
        self.color = color

class Tile:
    info = None
    position = None
    rect = None
    selected = False
    
    __r_pos = None

    def __init__(self, info: TileInfo, position = Vector2(0, 0)) -> None:                
        self.info = info
        self.position = position.copy()
        self.color = info.color

        self.repos()
                
        #auto add to tile registry
        statics.tiles[int(position.y / statics.TILE_SIZE)][int(position.x / statics.TILE_SIZE)] = self

    def repos(self):
        # Reposition; update rectangle based on real position
        self.__r_pos = Vector2(
            self.position.x * statics.zoom + statics.offset.x,
            self.position.y * statics.zoom + statics.offset.y,
        )

        self.rect = Rect(
            self.__r_pos.x,
            self.__r_pos.y,
            statics.real_tile_size,
            statics.real_tile_size
        )

    def update(self, display):
        self.repos()

        draw.rect(display, self.color, self.rect)

        if self.selected:
            display.blit(s_tile, self.__r_pos)

DEFAULT = TileInfo(-1, (25, 25, 25))
SAMPLE = TileInfo(0, (255, 0, 0))