import pygame
import time
from screens import (
    fade_screen,
    show_menu,
    fade_out,
    show_pause_menu,
    show_config_screen
)
from tilemap import (
    load_map,
    draw_tiled_map,
    get_player_spawn,
    get_collision_rects,
    get_enemy_spawns,
    get_consumable_spawns,
    get_level_end
)
from player import Player
from camera import Camera
from intro import show_intro_scenes
from enemies import Enemy
from consumable import Consumable
from dialog import show_dialog_with_name
from hud import HUD  # Importar la clase HUD
from utils import get_font

# Configuración de assets
BACKGROUND_IMAGE = "assets/screen/background.png"
BACKGROUND_MUSIC = "assets/audio/menu/EscapeThatFeeling.mp3"
INTRO_MUSIC = "assets/audio/game/intro_music.mp3"
GAME_MUSIC = "assets/audio/menu/EscapeThatFeeling.mp3"
TMX_MAP_PATH = "assets/tilemaps/level1_1.tmx"
NEXT_TMX_MAP_PATH = "assets/tilemaps/level1_2.tmx"

LOGO_1 = "assets/logo/logoUTCJ.png"
LOGO_2 = "assets/logo/logo.png"


GAME_MUSIC_LEVELS = {
    "level1": "assets/audio/game/level1_music.mp3",
    "level2": "assets/audio/game/level2_music.mp3",
    "level3": "assets/audio/game/level3_music.mp3"
}




def fade_music(new_music, fade_time=2000):
    """Realiza un fade entre la música actual y la nueva."""
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
    """Muestra un logo con efecto de fade-in y fade-out manteniendo su relación de aspecto."""
    logo = pygame.image.load(logo_path).convert_alpha()
    original_width, original_height = logo.get_size()
    max_width = screen.get_width() * 0.6
    max_height = screen.get_height() * 0.6
    aspect_ratio = original_width / original_height

    # Ajuste de tamaño si sobrepasa el 60% de la pantalla
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

    # Fade in
    for alpha in range(0, 256, 5):
        screen.fill((0, 0, 0))
        logo.set_alpha(alpha)
        screen.blit(logo, rect)
        pygame.display.update()
        pygame.time.delay(fade_in_time // 50)

    # Mostrar el logo por un tiempo
    pygame.time.delay(display_time)

    # Fade out
    for alpha in range(255, -1, -5):
        screen.fill((0, 0, 0))
        logo.set_alpha(alpha)
        screen.blit(logo, rect)
        pygame.display.update()
        pygame.time.delay(fade_out_time // 50)
        
def actualizar_volumen_efectos(volumen):
    global all_sounds
    for sonido in all_sounds:
        sonido.set_volume(volumen)       


def main():
    pygame.init()
    pygame.joystick.init()
    
    music_volume = 0.5
    effects_volume = 0.5
    all_sounds = []

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Joystick conectado: {joystick.get_name()}")
    else:
        joystick = None
        print("No se encontró ningún joystick conectado.")

    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Unmei Gisei - 640x480")

    pygame.mixer.init()
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)

    show_logo(screen, LOGO_1)
    show_logo(screen, LOGO_2)

    background = pygame.transform.scale(
        pygame.image.load(BACKGROUND_IMAGE).convert(),
        (640, 480)
    )
    if not show_menu(screen, background, music_volume, effects_volume, all_sounds):
        pygame.quit()
        return

    fade_out(screen, 2000)
    fade_music(INTRO_MUSIC, 2000)

    if not show_intro_scenes(screen):
        pygame.quit()
        return

    # Cargar el primer nivel
    current_level = "level1"  # Indica el nivel actual
    fade_music(GAME_MUSIC_LEVELS[current_level], 2000)

    tmx_data = load_map(TMX_MAP_PATH)
    camera = Camera(
        tmx_data.width * tmx_data.tilewidth,
        tmx_data.height * tmx_data.tileheight,
        640, 480
    )
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight

    collision_rects = get_collision_rects(tmx_data)
    player = Player(*get_player_spawn(tmx_data), effects_volume=effects_volume, all_sounds=all_sounds)
    player_group = pygame.sprite.GroupSingle(player)

    hud = HUD(player)

    enemies = pygame.sprite.Group()
    for enemy_data in get_enemy_spawns(tmx_data):
        enemies.add(
            Enemy(
                x=enemy_data["x"],
                y=enemy_data["y"],
                enemy_type=enemy_data["type"],
                speed=enemy_data["speed"],
                health=enemy_data["health"],
                damage=enemy_data["attack"],
                effects_volume=effects_volume,
                all_sounds=all_sounds
            )
        )

    consumables = pygame.sprite.Group()
    for cons_data in get_consumable_spawns(tmx_data):
        consumables.add(
            Consumable(
                x=cons_data["x"],
                y=cons_data["y"],
                consumable_type=cons_data["consumable_type"],
                health_value=int(cons_data["health_value"]),
                pickup_sound=cons_data.get("pickup_sound", None)
            )
        )

    level_end_rect = get_level_end(tmx_data)

    clock = pygame.time.Clock()
    running = True

    health_decrease_rate = 1
    last_health_decrease = pygame.time.get_ticks()
    death_screen_start_time = None
    death_screen_delay = 2

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pause_background = screen.copy()
            result = show_pause_menu(screen, pause_background)
            if result == "resume":
                pass
            elif result == "config":
                music_volume, effects_volume = show_config_screen(screen, music_volume, effects_volume, all_sounds)
            elif result == "exit":
                running = False

        if keys[pygame.K_e]:
            player.attack()

        try:
            if joystick and joystick.get_button(4):
                player.attack()
        except Exception as e:
            print(f"Error en joystick: {e}")

        player.update(collision_rects, enemies, map_width, map_height)
        camera.update(player.rect)
        for enemy in enemies:
            enemy.update(collision_rects, player)
            
        consumables.update()

        current_time = pygame.time.get_ticks()
        if current_time - last_health_decrease >= 1000:
            player.take_damage(health_decrease_rate, play_sound=False)
            last_health_decrease = current_time

        consumable_hits = pygame.sprite.spritecollide(player, consumables, True)
        for cons in consumable_hits:
            player.health = min(player.max_health, player.health + int(cons.health_value))

        if level_end_rect and player.rect.colliderect(level_end_rect):
            show_dialog_with_name(screen, "Athelia", "Por fin llegamos… cada paso ha dejado huella en ti.", effects_volume=effects_volume)
            show_dialog_with_name(screen, "Protagonista", "Estoy agotado; la oscuridad y los combates me han drenado.", effects_volume=effects_volume)
            show_dialog_with_name(screen, "Protagonista", "Sin alimentarme, mi energía se desvanece. ¿Cómo podré encontrar fuerzas para atacar?", effects_volume=effects_volume)
            show_dialog_with_name(screen, "Athelia", "Ataca sin miedo, pero nunca olvides cuidar de ti. Una buena ración es tan vital como un golpe certero.", effects_volume=effects_volume)

            # Cambiar nivel
            current_level = "level2"
            fade_music(GAME_MUSIC_LEVELS[current_level], 2000)

            tmx_data = load_map(NEXT_TMX_MAP_PATH)
            camera = Camera(
                tmx_data.width * tmx_data.tilewidth,
                tmx_data.height * tmx_data.tileheight,
                640, 480
            )
            map_width = tmx_data.width * tmx_data.tilewidth
            map_height = tmx_data.height * tmx_data.tileheight
            collision_rects = get_collision_rects(tmx_data)
            player.rect.topleft = get_player_spawn(tmx_data)

            enemies.empty()
            for enemy_data in get_enemy_spawns(tmx_data):
                enemies.add(
                    Enemy(
                       
                        x=enemy_data["x"],
                        y=enemy_data["y"],
                        enemy_type=enemy_data["type"],
                        speed=enemy_data["speed"],
                        health=enemy_data["health"],
                        damage=enemy_data["attack"],   # <--
                        effects_volume=effects_volume,
                        all_sounds=all_sounds
                    )
                )

            consumables.empty()
            for cons_data in get_consumable_spawns(tmx_data):
                consumables.add(
                    Consumable(
                        x=cons_data["x"],
                        y=cons_data["y"],
                        consumable_type=cons_data["consumable_type"],
                        health_value=int(cons_data["health_value"]),
                        pickup_sound=cons_data.get("pickup_sound", None)
                    )
                )
            level_end_rect = get_level_end(tmx_data)

        screen.fill((0, 0, 0))

        if not player.dead:
            draw_tiled_map(screen, tmx_data, camera.x, camera.y)
            screen.blit(player.image, camera.apply(player.rect))

            for enemy in enemies:
                screen.blit(enemy.image, camera.apply(enemy.rect))
            for cons in consumables:
                screen.blit(cons.image, camera.apply(cons.rect))

            if player.attack_rect:
                attack_rect_camera = camera.apply(player.attack_rect)
                pygame.draw.rect(screen, (255, 0, 0), attack_rect_camera, 2)
            death_screen_start_time = None

        elif not player.death_animation_finished:
            draw_tiled_map(screen, tmx_data, camera.x, camera.y)
            screen.blit(player.image, camera.apply(player.rect))

            for enemy in enemies:
                screen.blit(enemy.image, camera.apply(enemy.rect))
        else:
            font = get_font(20)
            text_surface = font.render("Este es el sacrificio del destino...", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            screen.blit(text_surface, text_rect)

            if death_screen_start_time is None:
                death_screen_start_time = pygame.time.get_ticks()
            else:
                elapsed = (pygame.time.get_ticks() - death_screen_start_time) / 1000.0
                if elapsed >= death_screen_delay:
                    player.respawn()
                    death_screen_start_time = None

        hud.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()