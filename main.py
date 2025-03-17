import pygame
import time  # Para usar time.time() si lo necesitas
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

# Importar desde dialog.py
from dialog import show_dialog_with_name

# Configuración de assets
BACKGROUND_IMAGE = "assets/screen/background.png"
BACKGROUND_MUSIC = "assets/audio/menu/EscapeThatFeeling.mp3"
INTRO_MUSIC = "assets/audio/menu/EscapeThatFeeling.mp3"
GAME_MUSIC = "assets/audio/menu/EscapeThatFeeling.mp3"
TMX_MAP_PATH = "assets/tilemaps/level1_1.tmx"
NEXT_TMX_MAP_PATH = "assets/tilemaps/level2_1.tmx"

LOGO_1 = "assets/logo/logoUTCJ.png"
LOGO_2 = "assets/logo/logo.png"


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


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Unmei Gisei - 640x480")

    # Sistema de audio
    pygame.mixer.init()
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    # Mostrar logos
    show_logo(screen, LOGO_1)
    show_logo(screen, LOGO_2)

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

    if not show_intro_scenes(screen):
        pygame.quit()
        return

    fade_music(GAME_MUSIC, 2000)

    # Cargar el primer nivel
    tmx_data = load_map(TMX_MAP_PATH)
    camera = Camera(
        tmx_data.width * tmx_data.tilewidth,
        tmx_data.height * tmx_data.tileheight,
        640, 480
    )
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight

    collision_rects = get_collision_rects(tmx_data)
    player = Player(*get_player_spawn(tmx_data))
    player_group = pygame.sprite.GroupSingle(player)

    enemies = pygame.sprite.Group()
    for enemy_data in get_enemy_spawns(tmx_data):
        enemies.add(
            Enemy(
                x=enemy_data["x"],
                y=enemy_data["y"],
                enemy_type=enemy_data["type"],
                speed=enemy_data["speed"],
                health=enemy_data["health"]
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

    # Para medir daño gradual
    health_decrease_rate = 1
    last_health_decrease = pygame.time.get_ticks()

    # Para controlar pantalla de muerte (tras animación)
    death_screen_start_time = None
    death_screen_delay = 2  # Segundos que se mostrará "Has muerto"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #
        # DETECTAR TECLA DE PAUSA
        #
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            # Hacemos una "foto" del juego en este momento
            pause_background = screen.copy()
            # Mostramos el menú de pausa
            result = show_pause_menu(screen, pause_background)
            if result == "resume":
                pass  # Reanudar sin cambios
            elif result == "config":
                # Ir a configuración usando el 'background' del menú principal
                show_config_screen(screen)
            elif result == "exit":
                # Salir del juego (o podrías volver al menú principal)
                running = False

        # Acciones de jugador (ATAQUE, etc.)
        if keys[pygame.K_e]:
            player.attack()

        # Lógica de jugador y enemigos
        player.update(collision_rects, enemies, map_width, map_height)
        camera.update(player.rect)
        enemies.update(collision_rects)

        # Disminuir salud cada segundo
        current_time = pygame.time.get_ticks()
        if current_time - last_health_decrease >= 1000:
            player.take_damage(health_decrease_rate)
            last_health_decrease = current_time

        # Consumibles
        consumable_hits = pygame.sprite.spritecollide(player, consumables, True)
        for cons in consumable_hits:
            player.health = min(player.max_health, player.health + int(cons.health_value))

        # Fin de nivel
        if level_end_rect and player.rect.colliderect(level_end_rect):
            show_dialog_with_name(screen, "Athelia", "Por fin llegamos… cada paso ha dejado huella en ti.")
            show_dialog_with_name(screen, "Protagonista", "Estoy agotado; la oscuridad y los combates me han drenado.")
            show_dialog_with_name(screen, "Protagonista", "Sin alimentarme, mi energía se desvanece. ¿Cómo podré encontrar fuerzas para atacar?")
            show_dialog_with_name(screen, "Athelia", "Ataca sin miedo, pero nunca olvides cuidar de ti. Una buena ración es tan vital como un golpe certero.")

            # Cargar siguiente nivel
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
                        health=enemy_data["health"]
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

        # ========================
        #   RENDERIZADO (DRAW)
        # ========================
        screen.fill((0, 0, 0))

        # 1) Jugador vivo
        if not player.dead:
            # Se dibuja el juego normalmente
            draw_tiled_map(screen, tmx_data, camera.x, camera.y)
            screen.blit(player.image, camera.apply(player.rect))
            player.draw_health_bar(screen, camera)

            for enemy in enemies:
                screen.blit(enemy.image, camera.apply(enemy.rect))

            for cons in consumables:
                screen.blit(cons.image, camera.apply(cons.rect))

            # Rectángulo de ataque (depuración)
            if player.attack_rect:
                attack_rect_camera = camera.apply(player.attack_rect)
                pygame.draw.rect(screen, (255, 0, 0), attack_rect_camera, 2)

            # Si el jugador vuelve a estar vivo, reseteamos el tiempo de pantalla de muerte
            death_screen_start_time = None

        # 2) Jugador muerto pero animación NO termina
        elif not player.death_animation_finished:
            # Se dibuja el juego para que se aprecie la animación de muerte
            draw_tiled_map(screen, tmx_data, camera.x, camera.y)
            screen.blit(player.image, camera.apply(player.rect))

            # Si quieres que los enemigos sigan dibujándose, lo dejas
            for enemy in enemies:
                screen.blit(enemy.image, camera.apply(enemy.rect))

        # 3) Jugador muerto y animación terminada
        else:
            # Pantalla negra y texto “¡Has muerto!”
            font = pygame.font.Font(None, 36)
            text_surface = font.render("Este es el sacrificio del destino...", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(screen.get_width()//2,
                                                      screen.get_height()//2))
            screen.blit(text_surface, text_rect)

            # Controlar cuánto tiempo se muestra este texto
            if death_screen_start_time is None:
                # Primer frame en el que entramos aquí
                death_screen_start_time = pygame.time.get_ticks()
            else:
                elapsed = (pygame.time.get_ticks() - death_screen_start_time) / 1000.0
                if elapsed >= death_screen_delay:
                    # Pasados X segundos, hacemos respawn
                    player.respawn()
                    # Reiniciamos la variable para la próxima muerte
                    death_screen_start_time = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
