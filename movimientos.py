import sys
import pygame as pg

WIDTH, HEIGTH = 720, 400
SPEED, FPS = 1, 60

pg.init()
display = pg.display.set_mode((WIDTH, HEIGTH))
background = pg.image.load("image.png").convert_alpha()
dino_image = pg.image.load("gato.png").convert_alpha()
new_size = (200, 200)
dino_image = pg.transform.scale(dino_image, new_size)

dino_rect = dino_image.get_rect()
clock = pg.time.Clock()

while 1:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        clock.tick(FPS)
    
    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT]:
        dino_rect.x -= SPEED
    if keys[pg.K_RIGHT]:
        dino_rect.x += SPEED
    if keys[pg.K_UP]:
        dino_rect.y -= SPEED
    if keys[pg.K_DOWN]:
        dino_rect.y += SPEED
    
    dino_rect.x = max(0, min(WIDTH - dino_rect.width, dino_rect.x))
    dino_rect.y = max(0, min(HEIGTH - dino_rect.height, dino_rect.y))
    
    display.blit(background, (0, 0))
    display.blit(dino_image, dino_rect)
    
    pg.display.update()
