import pygame
import math
import sys

from pygame import Rect, draw
from pygame.math import Vector2

pygame.init()
pygame.display.set_caption("Tile Drawing Test")

DISPLAY_SIZE = (1280, 720)
DELTA_TIME = 0

DISPLAY = pygame.display.set_mode(DISPLAY_SIZE)
CLOCK = pygame.time.Clock()

TILE_SIZE = 100

zoom = 1
offset = Vector2(0, 0)

last_offset = Vector2(0, 0)
initial_mouse_pos = Vector2(0, 0)
is_panning = False
is_placing = False

tiles = []

class Tile:
    position = None
    
    __rect = None

    def __init__(self, position = Vector2(0, 0)) -> None:
        self.position = position.copy()

        self.__rect = Rect(
            (self.position.x + offset.x) * zoom,
            (self.position.y + offset.y) * zoom,
            TILE_SIZE * zoom,
            TILE_SIZE * zoom
        )

        tiles.append(self)

    def update(self, display):
        self.__rect.x = (self.position.x + offset.x) * zoom
        self.__rect.y = (self.position.y + offset.y) * zoom
        self.__rect.width = TILE_SIZE * zoom
        self.__rect.height = TILE_SIZE * zoom

        draw.rect(display, (255, 255, 255), self.__rect)

def nearest_n(vec, n):
    return Vector2(
        math.floor(vec.x / n) * n,
        math.floor(vec.y / n) * n
    )

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEWHEEL:
            zoom += event.y * 0.1 #zoom in according to mouse wheel

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        sys.exit()

    DISPLAY.fill((25, 25, 25))

    real_position = (Vector2(pygame.mouse.get_pos()) / zoom) - offset

    #panning
    if pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LSHIFT]:
        if not is_panning:
            initial_mouse_pos = pygame.mouse.get_pos()
            is_panning = True
        offset = last_offset + (Vector2(pygame.mouse.get_pos()) - initial_mouse_pos)
    elif is_panning:
        last_offset = offset.copy()
        is_panning = False

    else:
        if pygame.mouse.get_pressed()[0] and not is_placing:
            Tile(nearest_n(real_position, TILE_SIZE))
            is_placing = True
        else:
            is_placing = False

    #update
    for tile in tiles:
        tile.update(DISPLAY)

    pygame.display.update()