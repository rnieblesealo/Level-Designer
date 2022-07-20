import utils

ICON_pencil = None
ICON_eraser = None
ICON_marquee = None

ICON_save = None
ICON_load = None

def load():
    global ICON_pencil, ICON_eraser, ICON_marquee, ICON_save, ICON_load
    
    ICON_pencil = utils.load_image('Assets/pencil.png')
    ICON_eraser = utils.load_image('Assets/eraser.png')
    ICON_marquee = utils.load_image('Assets/marquee.png')

    ICON_save = utils.load_image('Assets/save.png')
    ICON_load = utils.load_image('Assets/load.png')