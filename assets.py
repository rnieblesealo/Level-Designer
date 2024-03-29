import statics
import utils

ICON_pencil = None
ICON_eraser = None
ICON_marquee = None
ICON_save = None
ICON_load = None
ICON_plus = None
ICON_minus = None
ICON_edit = None
ICON_resize = None

def initialize():
    global ICON_pencil, ICON_eraser, ICON_marquee, ICON_save, ICON_load, ICON_plus, ICON_minus, ICON_edit, ICON_resize
    
    ICON_pencil = utils.load_image(get_program_asset('pencil.png'))
    ICON_eraser = utils.load_image(get_program_asset('eraser.png'))
    ICON_marquee = utils.load_image(get_program_asset('marquee.png'))
    ICON_save = utils.load_image(get_program_asset('save.png'))
    ICON_load = utils.load_image(get_program_asset('load.png'))
    ICON_plus = utils.load_image(get_program_asset('plus.png'))
    ICON_minus = utils.load_image(get_program_asset('minus.png'))
    ICON_edit = utils.load_image(get_program_asset('edit.png'))
    ICON_resize = utils.load_image(get_program_asset('resize.png'))

def get_project_asset(file_name):
    return '{P}{N}'.format(P=statics.PROJECT_ASSETS_PATH, N=file_name)

def get_program_asset(file_name):
    return '{P}{N}'.format(P=statics.PROGRAM_ASSETS_PATH, N=file_name)