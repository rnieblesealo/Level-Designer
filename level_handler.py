import numpy
import pickle

import statics
import tile
import ui

from tkinter import filedialog

LEVEL_DATA_EXT = 'lvl'
SWATCH_DATA_EXT = 'swt'
PROJECT_DATA_EXT = 'lproj'

class SerializedData:
    name = None
    
    def save(self, file_ext):
        # Get path we'd like to store file in (name is defined in this window)
        path = filedialog.asksaveasfilename(defaultextension='.{E}'.format(E=file_ext))
        
        if path: # * If the path was successfully obtained (user didn't X out of window)
            # Save this class as the specified file format
            with open(path, 'wb') as f:
                pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)

            print('Successfully saved .{T} data! Path: {P}'.format(T=file_ext, P=path))
        else:
            print('Canceled data save!')

    def load(file_path):
        # Load file using specified path
        with open(file_path, 'rb') as f:
            file = pickle.load(f)
            if file != None:
                print('Successfully loaded data! Path: {N}'.format(N=file_path))
                return file

class LevelData(SerializedData):
    level = None
    swatches = None

    def __init__(self, tile_array) -> None:
        self.level = numpy.full(tile_array.shape, -1, dtype=int) # Fill level with fallback tile ID by default
        self.swatches = {}
        
        # Make level and swatches
        for y in range(tile_array.shape[0]):
            for x in range(tile_array.shape[1]):
                self.level[y][x] = tile_array[y][x].info._id # Construct level as 2D int array, where ints represent tile's ID
                
                if tile_array[y][x].info._id not in self.swatches:
                    self.swatches[tile_array[y][x].info._id] = tile_array[y][x].info # Save TileInfo of tiles included in level

    def show(self):
        print('\n--Level Array--\n\n', self.level, '\n')
        print('\n--Level Tiles--\n\n')
        for tile in self.swatches.values():
            print('ID: {ID}, Texture Filename: {T}'.format(ID=tile._id, T=tile.texture_ref))
        print('\n')

class SwatchData(SerializedData):
    swatches = None

    def __init__(self, swatch_palette, file_name = 'my_swatches') -> None:
        # Store TileInfo in swatch palette, with each referenced by their ID in a dict
        self.swatches = {}
        for i in range(len(swatch_palette)):
            self.swatches[swatch_palette[i]._id] = swatch_palette[i]
    
    def show(self):
        print('\n --Swatch Data--\n')
        for swatch in self.swatches.values():
            status = '(FOUND)' if swatch.texture_ref == swatch.r_texture_ref else '(MISSING)'
            print('ID: {ID}, Texture Filename: {T} {S}'.format(ID=swatch._id, T=swatch.texture_ref, S=status))
        print('\n')

class ProjectData(SerializedData):
    level_data = None
    swatch_data = None

    def __init__(self, tile_array, swatch_palette) -> None:
        self.level_data = LevelData(tile_array)
        self.swatch_data = SwatchData(swatch_palette)

    def show(self):
        print("========================= SAVED LEVEL DATA:\n")
        self.level_data.show()
        print("======================== SAVED SWATCH DATA:\n")
        self.swatch_data.show()

def save_project():
    proj_data = ProjectData(statics.tiles, tile.swatches)
    proj_data.save(PROJECT_DATA_EXT)
    
    return proj_data

def load_project():
    path = filedialog.askopenfilename(filetypes=[('Level Project file', '.{E}'.format(E=PROJECT_DATA_EXT))])
    proj_data = SerializedData.load(path)
    
    # We must clear these to avoid ID conflicts
    tile.swatches.clear()
    tile.texture_cache.clear()

    tile.load_swatches_from_level(proj_data.level_data)
    tile.load_swatches_from_data(proj_data.swatch_data)
    tile.load_level(proj_data.level_data)

    # Show final import project data to console
    proj_data.show()

    # ! Load UI; must be re-done AFTER level loading, as swatches must be loaded first to make swatch palette.
    ui.load()