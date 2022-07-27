import statics
import pygame
import numpy
import os

import utils

from random import randint
from pygame import Rect
from pygame.math import Vector2

# TODO When levels are loaded, ID conflicts between TileInfos may arise; amend this.

# Variables

# Initialize texture cache
texture_cache = {}

# Initialize surfaces of GUI tiles
highlight_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
highlight_tile.fill(statics.HIGHLIGHT_COLOR)

select_tile = pygame.Surface(statics.TILE_DIMENSIONS * statics.zoom, pygame.SRCALPHA)
select_tile.fill(statics.SELECTED_COLOR)

# Initialize swatches
DEFAULT = None

swatches = []
swatch = None

# Classes
class TileInfo:
    texture_ref = None # ! COMPLETE path to texture, not just name!
    is_program_texture = False
    r_texture_ref = None # ! Active texture reference; may differ from main texture ref in cases where main is missing
    _id = 0

    def __init__(self, texture = None, is_program_asset = False) -> None:
        self._id = generate_id() # Generate a random ID for this new tile
        self.is_program_texture = is_program_asset
    
        if self.is_program_texture:
            self.texture_ref = statics.get_program_asset(texture)
        else:
            self.texture_ref = statics.get_project_asset(texture)
            
        self.cache_texture()

    def check_texture_ref(self):
        # If texture ref is not found, try to search for one in project assets
        if not os.path.exists(self.texture_ref):
            # First, get the raw name of the file by splitting at every / and grabbing the last substring, which should be the file name
            substrings = self.texture_ref.split('/')
            key = substrings[len(substrings) - 1]
            
            print(key)

            # Search every filename in respective assets folder for that key; if it is found, make a new texture ref with it
            directory = statics.PROGRAM_ASSETS_PATH if self.is_program_texture else statics.PROJECT_ASSETS_PATH
            found = False
            for path in os.listdir(directory):
                if path.find(key):
                    self.texture_ref = statics.get_project_asset(key)
                    self.r_texture_ref = statics.get_project_asset(key)
                    found = True
            
            # If nothing is found, assign a missing placeholder texture :( NOTE The original texture ref is still retained!
            if not found:
                self.r_texture_ref = statics.get_program_asset('t_missing.png')
        
        # If the texture exists, we're good to go!
        else:
            self.r_texture_ref = self.texture_ref

    # Cache texture
    def cache_texture(self):
        self.check_texture_ref()
        texture_cache[self._id] = pygame.image.load(self.r_texture_ref).convert_alpha()

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

# Methods
def fill_level(fill_tile):
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
    global DEFAULT, swatches, swatch
    
    # Load all swatches from the level into texture cache, they are for sure not going to have dupes as none exist at this stage
    # ! Load these swatches from LevelData first, and the ones from SwatchData second!
    for level_swatch in level_data.swatches.values():
        swatches.append(level_swatch)
        level_swatch.cache_texture()

    # Set global swatch info to match
    DEFAULT = swatches[0]
    swatch = DEFAULT

def load_swatches_from_data(swatch_data):
    # Load swatches that do not exist in the level but exist in swatch data; that is, the ones that aren't dupes of the one found in level data
    # ! Load swatches from level first!
    for key in swatch_data.swatches.keys():
        if key not in texture_cache:
            swatches.append(swatch_data.swatches[key])
            swatch_data.swatches[key].cache_texture()

def add_to_swatches(tile_details):
    # Make tiles from info in args
    for info in tile_details:
        swatches.append(TileInfo(info))

def set_swatch(new_swatch):
    global swatch
    swatch = new_swatch

def highlight_hovered_tile():
    statics.VIEWPORT.blit(highlight_tile, (
            statics.n_round(statics.real_mouse_pos.x, statics.TILE_SIZE) * statics.zoom + statics.offset.x,
            statics.n_round(statics.real_mouse_pos.y, statics.TILE_SIZE) * statics.zoom + statics.offset.y
        )
    )

def generate_id():
    # Generate a random unique tile ID
    prospect = randint(0, statics.SWATCH_LIMIT)
    for swatch in swatches:
        if swatch._id == prospect:
            return generate_id()
    return prospect

# Init & Update
def initialize():
    global DEFAULT, swatches, swatch

    # Add a default swatch to the palette, we do this everytime we open the app
    DEFAULT = TileInfo(('t_default.png'), is_program_asset=True)
    swatches.append(DEFAULT)
    swatch = DEFAULT

    # Fill the level with the default tile
    fill_level(DEFAULT)

    # TODO REMOVE Add placeholder tiles for debugging
    add_to_swatches(['dirt.png', 'grass.png', 'stone.png', 'water.png'])

def update():
    # Update tiles in canvas
    for y in range(statics.CANVAS_SIZE[1]):
        for x in range(statics.CANVAS_SIZE[0]):
            statics.tiles[y][x].update(statics.VIEWPORT)

    # Scale GUI tiles
    pygame.transform.scale(highlight_tile, (statics.real_tile_size, statics.real_tile_size))
    pygame.transform.scale(select_tile, (statics.real_tile_size, statics.real_tile_size))