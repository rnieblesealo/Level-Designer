import utils
import statics

ICON_pencil = None
ICON_eraser = None
ICON_marquee = None

ICON_save = None
ICON_load = None

def initialize():
    global ICON_pencil, ICON_eraser, ICON_marquee, ICON_save, ICON_load
    
    ICON_pencil = utils.load_image(statics.get_program_asset('pencil.png'))
    ICON_eraser = utils.load_image(statics.get_program_asset('eraser.png'))
    ICON_marquee = utils.load_image(statics.get_program_asset('marquee.png'))

    ICON_save = utils.load_image(statics.get_program_asset('save.png'))
    ICON_load = utils.load_image(statics.get_program_asset('load.png'))