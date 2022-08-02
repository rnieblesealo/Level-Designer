import numpy
import os
import pygame
import statics

from pygame import Rect
from pygame.math import Vector2
from random import randint

import assets
import utils

class TileCanvas:
    highlight_tile = pygame.Surface(statics.TILE_SIZE * statics.zoom, pygame.SRCALPHA)
    highlight_tile.fill(statics.HIGHLIGHT_COLOR)
    
    select_tile = pygame.Surface(statics.TILE_SIZE * statics.zoom, pygame.SRCALPHA)
    select_tile.fill(statics.SELECTED_COLOR)

    # Initialize swatches
    texture_cache = {}
    DEFAULT = None
    swatches = []
    swatch = None

    def initialize():
        # Add a default swatch to the palette, we do this everytime we open the app
        TileCanvas.DEFAULT = TileInfo(('t_default.png'), is_program_asset=True)
        TileCanvas.swatches.append(TileCanvas.DEFAULT)
        TileCanvas.swatch = TileCanvas.DEFAULT

        # Fill the level with the default tile
        TileCanvas.fill_level(TileCanvas.DEFAULT)

        # TODO REMOVE Add placeholder tiles for debugging
        TileCanvas.add_to_swatches(['dirt.png', 'grass.png', 'stone.png', 'water.png'])

    def update():
        # Update tiles in canvas
        for y in range(statics.LEVEL_SIZE[1]):
            for x in range(statics.LEVEL_SIZE[0]):
                statics.tiles[y][x].update(statics.VIEWPORT)

        # Scale GUI tiles
        pygame.transform.scale(TileCanvas.highlight_tile, statics.TILE_SIZE)
        pygame.transform.scale(TileCanvas.select_tile, statics.TILE_SIZE)

    def fill_level(fill_tile):
        # Init and fill entire canvas with a specific tile
        statics.tiles = numpy.empty((statics.LEVEL_SIZE[1], statics.LEVEL_SIZE[0]), dtype=Tile)
        for x in range(statics.LEVEL_SIZE[0]):
            for y in range(statics.LEVEL_SIZE[1]):
                Tile(
                    fill_tile,
                    Vector2(x, y).elementwise() * statics.TILE_SIZE
                )

    def load_level(level_data):
        # Init and fill entire canvas using level data
        statics.tiles = numpy.empty((statics.LEVEL_SIZE[1], statics.LEVEL_SIZE[0]), dtype=Tile)
        for x in range(statics.LEVEL_SIZE[0]):
            for y in range(statics.LEVEL_SIZE[1]):
                Tile(
                    level_data.swatches[level_data.level[y][x]],
                    Vector2(x, y).elementwise() * statics.TILE_SIZE
                )

    def load_swatches_from_level(level_data):
        # Load all swatches from the level into texture cache, they are for sure not going to have dupes as none exist at this stage
        # ! Load these swatches from LevelData first, and the ones from SwatchData second!
        for level_swatch in level_data.swatches.values():
            TileCanvas.swatches.append(level_swatch)
            level_swatch.check_texture_ref()
            level_swatch.cache_texture()

        # Set global swatch info to match
        TileCanvas.DEFAULT = TileCanvas.swatches[0]
        TileCanvas.swatch = TileCanvas.DEFAULT

    def load_swatches_from_data(swatch_data):
        # Load swatches that do not exist in the level but exist in swatch data; that is, the ones that aren't dupes of the one found in level data
        # ! Load swatches from level first!
        for key in swatch_data.swatches.keys():
            if key not in TileCanvas.texture_cache:
                TileCanvas.swatches.append(swatch_data.swatches[key])
                #print(os.path.exists(swatch_data.swatches[key].texture_ref))
                swatch_data.swatches[key].check_texture_ref()
                swatch_data.swatches[key].cache_texture()

    def add_to_swatches(tile_details):
        # Make tiles from info in args
        for info in tile_details:
            TileCanvas.swatches.append(TileInfo(info))

    def set_swatch(new_swatch):
        TileCanvas.swatch = new_swatch

    def highlight_hovered_tile():
        statics.VIEWPORT.blit(TileCanvas.highlight_tile, (
                utils.n_round(statics.level_mouse_pos.x, statics.TILE_SIZE.x) * statics.zoom + statics.offset.x,
                utils.n_round(statics.level_mouse_pos.y, statics.TILE_SIZE.y) * statics.zoom + statics.offset.y
            )
        )

    def generate_id():
        # Generate a random unique tile ID
        prospect = randint(0, statics.SWATCH_LIMIT)
        for swatch in TileCanvas.swatches:
            if swatch._id == prospect:
                return TileCanvas.generate_id()
        return prospect

    def in_level_bounds(pos: tuple):
        if (pos[0] >= 0 and pos[0] < statics.LEVEL_SIZE[0] * statics.TILE_SIZE.x) and (pos[1] >= 0 and pos[1] < statics.LEVEL_SIZE[1] * statics.TILE_SIZE.y):
            return True
        return False

    def mouse_in_bounds():
        return TileCanvas.in_level_bounds(statics.level_mouse_pos)

    def get_tile_at_mouse():
        nearest_pos = Vector2(
            utils.n_round(statics.level_mouse_pos.x, statics.TILE_SIZE.x),
            utils.n_round(statics.level_mouse_pos.y, statics.TILE_SIZE.y)
        )

        return statics.tiles[int(nearest_pos.y / statics.TILE_SIZE.x)][int(nearest_pos.x / statics.TILE_SIZE.y)]

class TileInfo:
    texture_ref = None # ! COMPLETE path to texture, not just name!
    is_program_texture = False
    r_texture_ref = None # ! Active texture reference; may differ from main texture ref in cases where main is missing
    _id = 0

    def __init__(self, texture = None, is_program_asset = False) -> None:
        self._id = TileCanvas.generate_id() # Generate a random ID for this new tile
        self.is_program_texture = is_program_asset
    
        if self.is_program_texture:
            self.texture_ref = assets.get_program_asset(texture)
        else:
            self.texture_ref = assets.get_project_asset(texture)
            
        self.check_texture_ref()
        self.cache_texture()

    def check_texture_ref(self):
        # If texture ref is not found, try to search for one in designated assets folder
        if not os.path.exists(self.texture_ref):
            # First, get the raw name of the file by splitting at every / and grabbing the last substring, which should be the file name
            substrings = self.texture_ref.split('/')
            key = substrings[len(substrings) - 1]
            
            # Search every filename in respective assets folder for that key; if it is found, make a new texture ref with it
            directory = statics.PROGRAM_ASSETS_PATH if self.is_program_texture else statics.PROJECT_ASSETS_PATH
            found = False
            for path in os.listdir(directory):
                if path.find(key) > -1: # path.find() returns -1 on failure; this is what we should use to perform checks.
                    self.texture_ref = assets.get_project_asset(key)
                    self.r_texture_ref = assets.get_project_asset(key)
                    found = True
                    break
            
            # If nothing is found, assign a missing placeholder texture :( NOTE The original texture ref is still retained!
            if not found:
                self.r_texture_ref = assets.get_program_asset('t_missing.png')
        
        # If the texture exists, we're good to go!
        else:
            self.r_texture_ref = self.texture_ref
            return True

    # Cache texture
    def cache_texture(self):
        TileCanvas.texture_cache[self._id] = pygame.image.load(self.r_texture_ref).convert_alpha()

    # Update texture
    def update_texture(self, new_texture_ref):
        # Update and check this texture
        self.texture_ref = new_texture_ref
        self.check_texture_ref()
        self.cache_texture()

    # Retrieve texture from cache
    def get_texture(self):
        return TileCanvas.texture_cache[self._id]

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
        statics.tiles[int(position.y / statics.TILE_SIZE.y)][int(position.x / statics.TILE_SIZE.x)] = self

    def reposition(self):
        # Reposition; update position and rectangle based on real position
        self.__level_position = Vector2(
            self.position.x * statics.zoom + statics.offset.x,
            self.position.y * statics.zoom + statics.offset.y,
        )

        self.rect = Rect(
            self.__level_position.x,
            self.__level_position.y,
            statics.real_tile_size.x,
            statics.real_tile_size.y
        )

        # Scale texture accordingly
        self.__cached_texture = pygame.transform.scale(self.texture, statics.real_tile_size)

    def reload(self):
        # Recheck TileInfo; match texture to the one contained in it
        self.texture = self.info.get_texture()

    def update(self, display):
        self.reposition()

        # Draw texture
        display.blit(self.__cached_texture, self.rect)

        # If selected, highlight this tile
        if self.selected:
            display.blit(TileCanvas.select_tile, self.__level_position)