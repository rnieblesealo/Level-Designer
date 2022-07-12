import numpy
import pickle

EXTENSION_NAME = 'lvl'

class LevelData:
    level = None
    tiles = None

    def save(self, tile_array, file_name = 'my_level'):
        self.level = numpy.full(tile_array.shape, -1, dtype=int) # Fill level with fallback tile ID by default
        self.tiles = {}
        
        for y in range(tile_array.shape[0]):
            for x in range(tile_array.shape[1]):
                self.level[y][x] = tile_array[y][x].info._id # Construct level as 2D int array, where ints represent tile's ID
                
                if tile_array[y][x].info._id not in self.tiles:
                    self.tiles[tile_array[y][x].info._id] = tile_array[y][x].info # Save TileInfo of tiles included in level

        # Save this class as a .lvl file
        with open('{N}.{X}'.format(N=file_name, X=EXTENSION_NAME), 'wb') as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)