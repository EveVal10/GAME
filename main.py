import pygame
from screens import fade_screen, show_menu, fade_out
from tilemap import load_map, draw_tiled_map, get_player_spawn, get_collision_rects, get_enemy_spawns
from player import Player
from camera import Camera
from intro import show_intro_scenes
from enemies import Enemy

# Configuración de assets
BACKGROUND_IMAGE = "assets//screen//background.png"
BACKGROUND_MUSIC = "assets//audio//menu//EscapeThatFeeling.mp3"
INTRO_MUSIC = "assets//audio//menu//EscapeThatFeeling.mp3"
GAME_MUSIC = "assets//audio//menu//EscapeThatFeeling.mp3"
TMX_MAP_PATH = "assets//tilemaps//level1_1.tmx"

def fade_music(new_music, fade_time=2000):
    """Realiza un fade entre la música actual y la nueva"""
    current_music = pygame.mixer.music.get_busy()
    if current_music:
        current_volume = pygame.mixer.music.get_volume()
        for volume in range(int(current_volume * 100), 0, -5):
            pygame.mixer.music.set_volume(volume / 100)
            pygame.time.delay(fade_time // 20)

    pygame.mixer.music.load(new_music)
    pygame.mixer.music.set_volume(0)
    pygame.mixer.music.play(-1)

    for volume in range(0, 101, 5):
        pygame.mixer.music.set_volume(volume / 100)
        pygame.time.delay(fade_time // 20)

def main():
    pygame.init()
    
    # Configuración inicial
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Unmei Gisei - 640x480")
    
    # Sistema de audio
    pygame.mixer.init()
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    # Pantallas iniciales
    fade_screen(screen, "Feline Moon Studios", 2000, 4000)
    fade_screen(screen, "Unmei Gisei", 2000, 4000)

    # Menú principal
    background = pygame.transform.scale(
        pygame.image.load(BACKGROUND_IMAGE).convert(), 
        (640, 480)
    )
    if not show_menu(screen, background):
        pygame.quit()
        return

    fade_out(screen, 2000)
    fade_music(INTRO_MUSIC, 2000)

    # Introducción del juego
    if not show_intro_scenes(screen):
        pygame.quit()
        return

    fade_music(GAME_MUSIC, 2000)

    # Carga del nivel
    tmx_data = load_map(TMX_MAP_PATH)
    camera = Camera(
        tmx_data.width * tmx_data.tilewidth,
        tmx_data.height * tmx_data.tileheight,
        640,
        480
    )

    # Jugador
    collision_rects = get_collision_rects(tmx_data)
    player = Player(*get_player_spawn(tmx_data))
    player_group = pygame.sprite.GroupSingle(player)

    # Sistema de enemigos
    enemies = pygame.sprite.Group()
    for enemy_data in get_enemy_spawns(tmx_data):
        enemies.add(Enemy(
            x=enemy_data["x"],
            y=enemy_data["y"],
            enemy_type=enemy_data["type"],
            speed=enemy_data["speed"],
            health=enemy_data["health"]
        ))

    # Bucle principal del juego
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Actualización de entidades
        player.update(collision_rects, enemies)
        camera.update(player.rect)
        enemies.update(collision_rects)

        # Renderizado
        screen.fill((0, 0, 0))
        
        # Dibujar mapa
        draw_tiled_map(screen, tmx_data, camera.x, camera.y)
        
        # Dibujar jugador
        screen.blit(player.image, camera.apply(player.rect))
        
        # Dibujar enemigos
        for enemy in enemies:
            screen.blit(enemy.image, camera.apply(enemy.rect))

        # Debug de colisiones (opcional)
        for rect in collision_rects:
            pygame.draw.rect(screen, (255,0,0), camera.apply(rect), 1)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()