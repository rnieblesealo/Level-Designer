import statics
import pygame
import numpy

from random import randint
from pygame import Rect
from pygame.math import Vector2

# TODO When levels are loaded, ID conflicts between TileInfos may arise; amend this.

class TileInfo:
    texture_ref = None
    _id = 0

    def __init__(self, texture = None) -> None:
        self._id = generate_id() # Generate a random ID for this new tile
        self.texture_ref = statics.get_asset_path(texture)
        self.cache_texture()

    # Cache texture
    def cache_texture(self):
        texture_cache[self._id] = pygame.image.load(self.texture_ref).convert_alpha()

    # Retrieve texture from cache
    def get_texture(self):
        return texture_cache[self._id]

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

def fill_level(fill_tile: TileInfo):
    # Init and fill entire canvas with a specific tile
    statics.tiles = numpy.empty((statics.CANVAS_SIZE[1], statics.CANVAS_SIZE[0]), dtype=Tile)
    for x in range(statics.CANVAS_SIZE[0]):
        for y in range(statics.CANVAS_SIZE[1]):
            Tile(
                fill_tile,
                Vector2(x * statics.TILE_SIZE, y * statics.TILE_SIZE)
            )

def load_level(level_data):
    # Init and fill entire canvas using level data
    statics.tiles = numpy.empty((statics.CANVAS_SIZE[1], statics.CANVAS_SIZE[0]), dtype=Tile)
    for x in range(statics.CANVAS_SIZE[0]):
        for y in range(statics.CANVAS_SIZE[1]):
            Tile(
                level_data.swatches[level_data.level[y][x]],
                Vector2(x * statics.TILE_SIZE, y * statics.TILE_SIZE)
            )

def load_swatches_from_level(level_data):
    # Load all swatches from the level into texture cache, they are for sure not going to have dupes as none exist at this stage
    # ! Load these swatches from LevelData first, and the ones from SwatchData second!
    for swatch in level_data.swatches.values():
        swatches.append(swatch)
        swatch.cache_texture()

def load_swatches_from_data(swatch_data):
    # Load swatches that do not exist in the level but exist in swatch data; that is, the ones that aren't dupes of the one found in level data
    # ! Load swatches from level first!
    for key in swatch_data.swatches.keys():
        if key not in texture_cache:
            swatches.append(swatch_data.swatches[key])
            swatch_data.swatches[key].cache_texture()

    try_assign_default_swatch()

def try_assign_default_swatch():
    global DEFAULT, swatch
    if len(swatches) > 0 and DEFAULT == None:
        DEFAULT = swatch = swatches[0] # * Syntactic sugar for assigning same value to multiple variables!
    if len(swatches) > 1:
        swatch = swatches[1]

def add_to_swatches(tile_details):
    # Make tiles from info in args
    for info in tile_details:
        swatches.append(TileInfo(info))
    
    # Assign required tiles if they do not exist
    try_assign_default_swatch()

    
def highlight_hovered_tile():
    statics.VIEWPORT.blit(highlight_tile, (
            statics.n_round(statics.real_mouse_pos.x, statics.TILE_SIZE) * statics.zoom + statics.offset.x,
            statics.n_round(statics.real_mouse_pos.y, statics.TILE_SIZE) * statics.zoom + statics.offset.y
        )
    )

def set_swatch(new_swatch: TileInfo):
    global swatch
    swatch = new_swatch

def update_tiles():
    for y in range(statics.CANVAS_SIZE[1]):
        for x in range(statics.CANVAS_SIZE[0]):
            statics.tiles[y][x].update(statics.VIEWPORT)

def generate_id():
    # Generate a random unique tile ID
    prospect = randint(0, statics.SWATCH_LIMIT)
    for swatch in swatches:
        if swatch._id == prospect:
            return generate_id()
    return prospect

# Initialize texture cache
texture_cache = {}

# Initialize surfaces of GUI tiles
highlight_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
highlight_tile.fill(statics.HIGHLIGHT_COLOR)

select_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
select_tile.fill(statics.SELECTED_COLOR)

# Initialize swatches
MISSING = None # Fallback tile for errors
DEFAULT = None # What the eraser draws

swatches = []
swatch = None