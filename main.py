import pygame
from screens import fade_screen, show_menu, fade_out, show_pause_menu
from tilemap import load_map, draw_tiled_map, get_player_spawn, get_collision_rects, get_enemy_spawns
from player import Player
from camera import Camera
from intro import show_intro_scenes
from enemies import Enemy


# Configuración de assets
BACKGROUND_IMAGE = "assets/screen/background.png"
BACKGROUND_MUSIC = "assets/audio/menu/EscapeThatFeeling.mp3"
INTRO_MUSIC = "assets/audio/menu/EscapeThatFeeling.mp3"
GAME_MUSIC = "assets/audio/menu/EscapeThatFeeling.mp3"
TMX_MAP_PATH = "assets/tilemaps/level1_1.tmx"

LOGO_1 = "assets/logo/logoUTCJ.png"
LOGO_2 = "assets/logo/logo.png"



def fade_music(new_music, fade_time=2000):
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

def show_logo(screen, logo_path, fade_in_time=2000, display_time=4000, fade_out_time=2000):
    logo = pygame.image.load(logo_path).convert_alpha()
    original_width, original_height = logo.get_size()
    max_width = screen.get_width() * 0.6
    max_height = screen.get_height() * 0.6

    aspect_ratio = original_width / original_height
    if original_width > max_width or original_height > max_height:
        if original_width > original_height:
            new_width = int(max_width)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = int(max_height)
            new_width = int(new_height * aspect_ratio)
    else:
        new_width, new_height = original_width, original_height

    logo = pygame.transform.scale(logo, (new_width, new_height))
    rect = logo.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    for alpha in range(0, 256, 5):
        screen.fill((0, 0, 0))
        logo.set_alpha(alpha)
        screen.blit(logo, rect)
        pygame.display.update()
        pygame.time.delay(fade_in_time // 50)

    pygame.time.delay(display_time)

    for alpha in range(255, -1, -5):
        screen.fill((0, 0, 0))
        logo.set_alpha(alpha)
        screen.blit(logo, rect)
        pygame.display.update()
        pygame.time.delay(fade_out_time // 50)

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Unmei Gisei - 640x480")
    pygame.mixer.init()
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    show_logo(screen, LOGO_1)
    show_logo(screen, LOGO_2)

    background = pygame.transform.scale(pygame.image.load(BACKGROUND_IMAGE).convert(), (640, 480))
    if not show_menu(screen, background):
        pygame.quit()
        return

    fade_out(screen, 2000)
    fade_music(INTRO_MUSIC, 2000)

    if not show_intro_scenes(screen):
        pygame.quit()
        return

    fade_music(GAME_MUSIC, 2000)

    tmx_data = load_map(TMX_MAP_PATH)
    camera = Camera(tmx_data.width * tmx_data.tilewidth, tmx_data.height * tmx_data.tileheight, 640, 480)

    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight

    collision_rects = get_collision_rects(tmx_data)
    player = Player(*get_player_spawn(tmx_data))
    player_group = pygame.sprite.GroupSingle(player)

    enemies = pygame.sprite.Group()
    for enemy_data in get_enemy_spawns(tmx_data):
        enemies.add(Enemy(x=enemy_data["x"], y=enemy_data["y"], enemy_type=enemy_data["type"], speed=enemy_data["speed"], health=enemy_data["health"]))

    clock = pygame.time.Clock()
    running = True
    game_paused = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_paused = not game_paused
                    if game_paused:
                        action = show_pause_menu(screen)
                        if action == "resume":
                            game_paused = False
                        elif action == "quit":
                            running = False

        if not game_paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e]:
                player.attack()

            player.update(collision_rects, enemies, map_width, map_height, screen)
            camera.update(player.rect)
            enemies.update(collision_rects)

            screen.fill((0, 0, 0))
            draw_tiled_map(screen, tmx_data, camera.x, camera.y)
            screen.blit(player.image, camera.apply(player.rect))
            player.draw_health_bar(screen, camera)
            for enemy in enemies:
                screen.blit(enemy.image, camera.apply(enemy.rect))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()