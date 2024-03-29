import numpy
import os
import pickle
import pygame

from tkinter import filedialog

import statics

from tile import TileCanvas

class FileTypeInfo:
    type = None
    extension = None

    def __init__(self, type, extension) -> None:
        self.type = '{N} {T}'.format(N=statics.APP_NAME, T=type)
        self.extension = extension    

    def get_explorer_info(self):
        return [(self.type, self.extension)]

class SerializedData:
    ABORT_SAVE_ACTION_M = 'Aborting data save!'
    ABORT_LOAD_ACTION_M = 'Aborting data load!'
    CANCELLED_ERROR_M = 'User canceled operation.'
    DNE_ERROR_M = 'Path does not exist or is invalid!'
    
    FILE_TYPES = {
        'level' : FileTypeInfo('Level File', '.lyvl'),
        'swatch' : FileTypeInfo('Swatch Data', '.lysw'),
        'project' : FileTypeInfo('Project', '.lyproj')
    }

    file_type_info = None
    path = None

    def save(self):
        # Get path we'd like to store file in (name is defined in this window)
        path = filedialog.asksaveasfilename(defaultextension=self.file_type_info.extension, filetypes=self.file_type_info.get_explorer_info())
        
        if path: # * If the path was successfully obtained (user didn't X out of window)
            # Save this class as the specified file format
            self.path = path
            with open(path, 'wb') as f:
                pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            print('Successfully saved {T} data! Path: {P}'.format(T=self.file_type_info.extension, P=self.path))
        else:
            print(SerializedData.ABORT_SAVE_ACTION_M, SerializedData.CANCELLED_ERROR_M)
            return None

    def load(file_type_info):
        # Get path we'd like to store file in (name is defined in explorer window)
        path = filedialog.askopenfilename(defaultextension=file_type_info.extension, filetypes=file_type_info.get_explorer_info())    

        if path and os.path.exists(path):
            # Load file using specified path
            with open(path, 'rb') as f:
                file = pickle.load(f)
                file.path = path
                statics.OPEN_PROJECT_PATH = file.path
                
                print('Successfully loaded {T} data! Path: {P}'.format(T=file_type_info.extension, P=file.path))
                return file
        else:
            error_message = SerializedData.DNE_ERROR_M
            if not path:
                error_message = SerializedData.CANCELLED_ERROR_M
            print(SerializedData.ABORT_LOAD_ACTION_M, error_message)
            return None

class LevelData(SerializedData):
    file_type_info = SerializedData.FILE_TYPES['level']
    level = None
    swatches = None
    size = None

    def __init__(self, tile_array) -> None:
        self.level = numpy.full(tile_array.shape, -1, dtype=int) # Fill level with dummy ID by default
        self.swatches = {}
        self.size = (tile_array.shape[1], tile_array.shape[0]) # X, Y size
        
        # Make level and swatches
        for y in range(tile_array.shape[0]):
            for x in range(tile_array.shape[1]):
                self.level[y][x] = tile_array[y][x].info.id # Construct level as 2D int array, where ints are to represent tile's ID
                
                if tile_array[y][x].info.id not in self.swatches:
                    self.swatches[tile_array[y][x].info.id] = tile_array[y][x].info # Save TileInfo of tiles included in level in swatches dict

    def show(self):
        print('\n--Level Array--\n\n', self.level, '\n')
        print('\n--Level Tiles--\n\n')
        for tile in self.swatches.values():
            print('ID: {ID}, Texture Filename: {T}'.format(ID=tile.id, T=tile.texture_ref))
        print('\n')

class SwatchData(SerializedData):
    file_type_info = SerializedData.FILE_TYPES['swatch']
    swatches = None

    def __init__(self, swatch_palette) -> None:
        # Store TileInfo in swatch palette, with each referenced by their ID in a dict
        self.swatches = {}
        for i in range(len(swatch_palette)):
            self.swatches[swatch_palette[i].id] = swatch_palette[i]
    
    def show(self):
        print('\n --Swatch Data--\n')
        for swatch in self.swatches.values():
            status = '(FOUND)' if swatch.texture_ref == swatch.active_texture_ref else '(MISSING)'
            print('ID: {ID}, Texture Filename: {T} {S}'.format(ID=swatch.id, T=swatch.texture_ref, S=status))
        print('\n')

class ProjectData(SerializedData):
    file_type_info = SerializedData.FILE_TYPES['project']
    level_data = None
    swatch_data = None

    def __init__(self, tile_array, swatch_palette) -> None:
        self.level_data = LevelData(tile_array)
        self.swatch_data = SwatchData(swatch_palette)

    def show(self):
        print("========================= PROJECT LEVEL DATA:\n")
        self.level_data.show()
        print("======================== PROJECT SWATCH DATA:\n")
        self.swatch_data.show()

    def save_project():
        saved_project_data = ProjectData(statics.tiles, TileCanvas.swatches)
        saved_project_data.save()
        
        return saved_project_data

    def load_project():
        loaded_project_data = SerializedData.load(ProjectData.file_type_info)
        
        if loaded_project_data == None:
            return
        
        # Store the path of the newly opened project
        statics.OPEN_PROJECT_PATH = loaded_project_data.path
        
        # Gather global level size attributes
        statics.LEVEL_SIZE = loaded_project_data.level_data.size
        statics.LEVEL_SIZE_PX = (statics.LEVEL_SIZE[0] * statics.TILE_SIZE.x, statics.LEVEL_SIZE[1] * statics.TILE_SIZE.y)

        # We must clear these to avoid TileInfo ID conflicts
        TileCanvas.swatches.clear()
        TileCanvas.texture_cache.clear()

        # Load swatches included in the level first, then those associated to the project.
        # ! This order is necessary, as loading swatches from data automatically checks for duplicates and takes necessary steps.
        TileCanvas.load_swatches_from_level(loaded_project_data.level_data)
        TileCanvas.load_swatches_from_data(loaded_project_data.swatch_data)
        TileCanvas.load_level(loaded_project_data.level_data)

        # Change offset offset such that level draw area is centered
        statics.offset = pygame.math.Vector2(
            (statics.VIEWPORT_SIZE[0] - statics.LEVEL_SIZE_PX[0] * statics.zoom) / 2,
            (statics.VIEWPORT_SIZE[1] - statics.LEVEL_SIZE_PX[1] * statics.zoom) / 2
        )

        # Update window title to display project info
        statics.update_window_title()

        # Show final import project data to console
        loaded_project_data.show()