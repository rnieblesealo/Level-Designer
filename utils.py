import numpy
import pygame

from pygame import Surface, Rect, transform, image
from pygame.font import Font
from pygame.math import Vector2

# * Imports done!

def fit(dimensions = Vector2(0, 0), texture = None) -> Surface:
    """
    Scales a texture proportionally to given dimensions.
    """
        
    return transform.scale(texture, (dimensions.x, dimensions.y / (texture.get_width() / texture.get_height())))

def scale_surface(surface = None, scale = 1) -> Surface:
    """
    Scales a surface by a numeric factor.
    """

    return transform.scale(surface, (surface.get_width() * scale, surface.get_height() * scale))

def scale_rect(rect = Rect(0, 0, 0, 0), scale = 1) -> Rect:
    """
    Scales a rectangle by a numeric factor from its origin.
    """

    return Rect(
        rect.left * scale,
        rect.top * scale,
        rect.width * scale,
        rect.height * scale
    )

def load_image(filepath = 'assets/image.png') -> Surface:
    """
    Efficiently loads and image and converts it to a more suitable format.
    Using this instead of regular image.load() speeds up performance considerably.
    """
    
    return image.load(filepath).convert_alpha() #convert_alpha() FTW!

def load_image_scaled(filepath = 'assets/image.png', scale = 1) -> Surface:
    """
    Shorthand for efficiently loading a scaled texture.
    """
    
    return scale_surface(load_image(filepath), scale)

def load_backdrop(filepath = 'assets/backdrop.png') -> Surface:
    """
    Shorthand for loading a texture scaled proportionately to the display's width.
    """
    
    return fit(load_image(filepath))

def draw_text(filepath = 'assets/font.ttf', text = 'Sample Text', position = Vector2(0, 0), size = 1):
    """
    Draws text centered over a specified position.
    """

    font = Font(filepath, size)
    font_surface = font.render(text, True, (255, 255, 255))
    font_surface_rect = font_surface.get_rect()

    # Set text rect center to position (this centers the text over @position in a new rect!)
    font_surface_rect.center = position

    globals.DISPLAY.blit(font_surface, font_surface_rect)

def draw_surface(display = None, surface = None, position = Vector2(0, 0)) -> Rect:
    """
    Draws a surface centered over a specified position.
    """

    surface_rect = surface.get_rect()
    surface_rect.center = position

    return display.blit(surface, surface_rect)

def lerp(a = 0, b = 1, t = 0.5) -> float:
    """
    Simple linear interpolation.
    """

    if t > 1:
        print("lerp t exceeds 1")
        return None
    return a + t * (b - a)

def draw_circle(display = None, center = Vector2(0, 0), radius = 5) -> None:
    """
    Shorthand for drawing a circle.
    """

    pygame.draw.circle(display, (255, 0, 0), center, radius)

def draw_rect(display = None, center = Vector2(0, 0), dimensions = Vector2(10, 10), color = (255, 255, 255)) -> None:
    """
    Shorthand for drawing a rect.
    Note: As this generates a rect every call, it may be inefficient.
    """

    r = Rect(0, 0, dimensions.x, dimensions.y)
    r.center = center

    pygame.draw.rect(display, color, r)

def lerp_rgb(a = (0, 0, 0), b = (255, 255, 255), t = 0.5):
    """
    Linearly interpolates between two colors.
    """

    if t > 1:
        print("rgb lerp t exceeds 1")
        return None
    return (
        int(a[0] + t * (b[0] - a[0])),
        int(a[1] + t * (b[1] - a[1])),
        int(a[2] + t * (b[2] - a[2]))
    )

def n_round(x: float | int, n: int):
    return numpy.floor(x / n) * n

def place_at_first_empty(item, matrix, empty):
    if len(matrix.shape) > 2:
        return
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            if matrix[y][x] == empty:
                matrix[y][x] = item
                return