import statics
import pygame
import numpy

from random import randint
from pygame.math import Vector2
from pygame import Rect

# * Highlighted Tile
h_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
h_tile.fill(statics.HIGHLIGHT_COLOR)

# * Selected Tile
s_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
s_tile.fill(statics.SELECTED_COLOR)

# * Testing Textures
t_empty = pygame.image.load('Assets/empty.png')
t_grass = pygame.image.load('Assets/grass.png')
t_stone = pygame.image.load('Assets/stone.png')
t_water = pygame.image.load('Assets/water.png')
t_dirt = pygame.image.load('Assets/dirt.png')
t_sky = pygame.image.load('Assets/sky.png')

# TODO Make random ID generator exclude already existing ones!
class TileInfo:
    texture = None
    tag = 0

    def __init__(self, tag = randint(0, statics.SWATCH_LIMIT), texture = t_empty) -> None:
        self.tag = tag
        self.texture = texture

class Tile:
    info = None
    position = None
    rect = None
    selected = False
    
    __r_pos = None # Position in level coordinates
    __tex_cache = None # Cached texture for scaling operations

    def __init__(self, info: TileInfo, position = Vector2(0, 0)) -> None:                
        self.info = info
        self.position = position.copy()

        self.repos()
                
        # Auto add to tile registry
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

        # Scale texture accordingly
        self.__tex_cache = pygame.transform.scale(self.info.texture, (statics.real_tile_size, statics.real_tile_size))

    def update(self, display):
        self.repos()

        # Draw texture
        display.blit(self.__tex_cache, self.rect)

        # If selected, highlight this tile
        if self.selected:
            display.blit(s_tile, self.__r_pos)

def fill(fill_tile: TileInfo):
    statics.tiles = numpy.empty((statics.CANVAS_SIZE[1], statics.CANVAS_SIZE[0]), dtype=Tile)
    for x in range(statics.CANVAS_SIZE[0]):
        for y in range(statics.CANVAS_SIZE[1]):
            Tile(fill_tile, Vector2(x * statics.TILE_SIZE, y * statics.TILE_SIZE)) #make placeholder tile, should be customizable

def highlight_hovered_tile():
    statics.VIEWPORT.blit(h_tile, (
            statics.round_to_n(statics.real_mouse_position.x, statics.TILE_SIZE) * statics.zoom + statics.offset.x,
            statics.round_to_n(statics.real_mouse_position.y, statics.TILE_SIZE) * statics.zoom + statics.offset.y
        )
    )

def set_swatch(new_swatch: TileInfo):
    global swatch
    swatch = new_swatch

MISSING = TileInfo(-1, t_empty) # * Fallback tile for errors

sky = None
grass = None
water = None
stone = None
dirt = None

swatches = []

swatch = None
erased = None