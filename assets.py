import utils

ICON_pencil = None
ICON_eraser = None
ICON_marquee = None

def load():
    global ICON_pencil
    global ICON_eraser
    global ICON_marquee
    
    ICON_pencil = utils.load_image('Assets/pencil.png')
    ICON_eraser = utils.load_image('Assets/eraser.png')
    ICON_marquee = utils.load_image('Assets/marquee.png')