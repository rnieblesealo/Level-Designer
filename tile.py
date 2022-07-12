import statics
import pygame
import numpy

from random import randint
from pygame.math import Vector2
from pygame import Rect

class TileInfo:
    texture = None
    tag = 0

    def __init__(self, tag = randint(0, statics.SWATCH_LIMIT), texture = None) -> None:
        self.tag = tag
        self.texture = statics.get_texture(texture)

        # Cache texture
        if tag not in texture_cache:
            texture_cache[tag] = pygame.image.load(self.texture).convert_alpha()

    # Retrieve texture from cache
    def get_texture(self):
        return texture_cache[self.tag]

class Tile:
    info = None
    texture = None
    position = None
    rect = None
    selected = False
    
    __level_position = None # Position in level coordinates
    __cached_texture = None # Cached texture for scaling operations

    def __init__(self, info: TileInfo, position = Vector2(0, 0)) -> None:                
        self.info = info
        self.texture = info.get_texture()
        self.position = position.copy()

        self.reposition()
                
        # Auto add to tile registry
        statics.tiles[int(position.y / statics.TILE_SIZE)][int(position.x / statics.TILE_SIZE)] = self

    def reposition(self):
        # Reposition; update position and rectangle based on real position
        self.__level_position = Vector2(
            self.position.x * statics.zoom + statics.offset.x,
            self.position.y * statics.zoom + statics.offset.y,
        )

        self.rect = Rect(
            self.__level_position.x,
            self.__level_position.y,
            statics.real_tile_size,
            statics.real_tile_size
        )

        # Scale texture accordingly
        self.__cached_texture = pygame.transform.scale(self.texture, (statics.real_tile_size, statics.real_tile_size))

    def update(self, display):
        self.reposition()

        # Draw texture
        display.blit(self.__cached_texture, self.rect)

        # If selected, highlight this tile
        if self.selected:
            display.blit(select_tile, self.__level_position)

def fill(fill_tile: TileInfo):
    statics.tiles = numpy.empty((statics.CANVAS_SIZE[1], statics.CANVAS_SIZE[0]), dtype=Tile)
    for x in range(statics.CANVAS_SIZE[0]):
        for y in range(statics.CANVAS_SIZE[1]):
            Tile(fill_tile, Vector2(x * statics.TILE_SIZE, y * statics.TILE_SIZE)) #make placeholder tile, should be customizable

def highlight_hovered_tile():
    statics.VIEWPORT.blit(highlight_tile, (
            statics.n_round(statics.real_mouse_position.x, statics.TILE_SIZE) * statics.zoom + statics.offset.x,
            statics.n_round(statics.real_mouse_position.y, statics.TILE_SIZE) * statics.zoom + statics.offset.y
        )
    )

def set_swatch(new_swatch: TileInfo):
    global swatch
    swatch = new_swatch

# Initialize texture cache
texture_cache = {}

# Initialize surfaces of GUI tiles
highlight_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
highlight_tile.fill(statics.HIGHLIGHT_COLOR)

select_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
select_tile.fill(statics.SELECTED_COLOR)

MISSING = None # Fallback tile for errors

sky = None
grass = None
water = None
stone = None
dirt = None

swatches = [
    sky,
    grass,
    water,
    stone,
    dirt
]

swatch = swatches[1]
erased = sky