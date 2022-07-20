import numpy
import pickle

import statics
import tile

LEVEL_DATA_EXT = 'lvl'
SWATCH_DATA_EXT = 'swt'

class LevelData:
    level = None
    swatches = None

    def __init__(self, tile_array, file_name = 'my_level') -> None:
        self.level = numpy.full(tile_array.shape, -1, dtype=int) # Fill level with fallback tile ID by default
        self.swatches = {}
        
        # Save level and swatches
        for y in range(tile_array.shape[0]):
            for x in range(tile_array.shape[1]):
                self.level[y][x] = tile_array[y][x].info._id # Construct level as 2D int array, where ints represent tile's ID
                
                if tile_array[y][x].info._id not in self.swatches:
                    self.swatches[tile_array[y][x].info._id] = tile_array[y][x].info # Save TileInfo of tiles included in level

        # Save this class as a level file
        with open('{N}.{X}'.format(N=file_name, X=LEVEL_DATA_EXT), 'wb') as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)

        print('Successfully created level data! Filename: {N}'.format(N=file_name))
        self.show()

    def save(tile_array, file_name = 'my_level'):
        return LevelData(tile_array, file_name)

    def load(file_path = 'my_level.{X}'.format(X=LEVEL_DATA_EXT)):
        # Load file
        with open(file_path, 'rb') as f:
            file = pickle.load(f)
            if file != None:
                print('Successfully loaded level data! Path: {N}'.format(N=file_path))
                file.show()
                return file

    def show(self):
        print('Array:\n', self.level)
        print('Tiles:')
        for tile in self.swatches.values():
            print('ID: {ID}, Texture Filename: {T}'.format(ID=tile._id, T=tile.texture_ref))

class SwatchData:
    swatches = None

    def __init__(self, swatch_palette, file_name = 'my_swatches') -> None:
        # Store TileInfo in swatch palette, with each referenced by their ID in a dict
        self.swatches = {}
        for i in range(len(swatch_palette)):
            self.swatches[swatch_palette[i]._id] = swatch_palette[i]

        # Save this class as swatch file
        with open('{N}.{X}'.format(N=file_name, X=SWATCH_DATA_EXT), 'wb') as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)

        print('Successfully created new swatch palette! Filename: {N}'.format(N=file_name))
        self.show()

    def save(swatch_palette, file_name = 'my_swatches'):
        return SwatchData(swatch_palette, file_name)
    
    def load(file_path = 'my_swatches.{X}'.format(X=SWATCH_DATA_EXT)):
        # Load file
        with open(file_path, 'rb') as f:
            file = pickle.load(f)
            if file != None:
                print('Successfully loaded swatch data! Path: {N}'.format(N=file_path))
                file.show()
                return file
        
    def show(self):
        for swatch in self.swatches.values():
            print('ID: {ID}, Texture Filename: {T}'.format(ID=swatch._id, T=swatch.texture_ref))

def save_project():
    LevelData.save(statics.tiles)
    SwatchData.save(tile.swatches)