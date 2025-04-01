import pygame
import time
from screens import (
    fade_screen,
    show_menu,
    fade_out,
    show_pause_menu,
    show_config_screen
)
from tilemap import draw_tiled_map, get_player_spawn
from player import Player
from camera import Camera
from intro import show_intro_scenes, show_final_cinematic
from enemies import Enemy, MiniBoss
from consumable import Consumable
from dialog import show_dialog_with_name
from hud import HUD
from utils import get_font
from levels import load_level_data  # Nueva importación
from projectile import EnergyProjectile

# Configuración de assets
BACKGROUND_IMAGE = "assets/screen/background.png"
BACKGROUND_MUSIC = "assets/audio/menu/EscapeThatFeeling.mp3"
INTRO_MUSIC = "assets/audio/game/intro_music.mp3"
ENDING_CINEMATIC_MUSIC = "assets/audio/game/final_cinematic.mp3"
CREDITS_MUSIC = "assets/audio/menu/credits_theme.mp3"

LOGO_1 = "assets/logo/logoUTCJ.png"
LOGO_2 = "assets/logo/logo.png"

CAMP_IMAGE_PATH = "assets/intro/sleeping.png"  # Cambia la ruta según tu proyecto

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
        
def actualizar_volumen_efectos(volumen, all_sounds):
    for sonido in all_sounds:
        sonido.set_volume(volumen)
        

def show_camp_scene(screen, camp_image, duration=3000):
    """
    Muestra la imagen de 'campamento' a pantalla completa por 'duration' milisegundos,
    antes de continuar con la carga del siguiente nivel.
    """
    screen.blit(camp_image, (0, 0))
    pygame.display.flip()
    pygame.time.delay(duration) 
    
def wait_for_any_key():
    """Espera hasta que se pulse cualquier tecla o el botón de ataque (1) del joystick."""
    # Inicializar joystick si está disponible
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    
    ATTACK_BUTTON = 1 
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                return event.key
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == ATTACK_BUTTON:
                    return pygame.K_e  # Devuelve la tecla 'e' para mantener consistencia
        
        # También verificamos el estado del botón continuamente
        if joystick and joystick.get_button(ATTACK_BUTTON):
            return pygame.K_e  # Devuelve la tecla 'e' para mantener consistencia
            
        pygame.time.delay(50)
        
def show_full_conversation(npc, screen):
    """
    Muestra TODOS los bloques de diálogo del NPC, línea por línea.
    Cada vez que se pulsa cualquier tecla se avanza.
    Al terminar todos los bloques, muestra un mensaje final y espera
    una pulsación para cerrar la conversación.
    """
    # Recorre todos los bloques restantes
    while npc.current_block < len(npc.dialogue_blocks):
        npc.start_dialogue_block(npc.current_block)
        
        # Mientras haya líneas en el bloque actual, las muestra
        while npc.is_talking:
            line = npc.get_current_line()
            if line is None:
                # Si ya no hay más líneas, se llama a end_dialogue() y se sale
                break
            
            show_dialog_with_name(screen, npc.speaker, line)
            wait_for_any_key()  # Espera que el jugador pulse para pasar a la siguiente línea
            npc.advance_dialogue()
    
    # Cuando ya no hay más bloques, muestra un mensaje final (opcional)
    show_dialog_with_name(screen, npc.speaker, "Fin del diálogo. Pulsa cualquier tecla para continuar.")
    wait_for_any_key()
    npc.reset_dialogue()
        

                  

def main():
    pygame.init()
    pygame.joystick.init()
    
    projectile_button_pressed = False

    ARCADE_BUTTONS = {
        'JUMP': 3,       # Botón A (típicamente)
        'ATTACK': 1,      # Botón B
        'SPECIAL': 2,     # Botón C
        'PAUSE': 6,       # Botón 7 (pausa)
        'INTERACT': 0,    # Botón D (interacción)
        'PROJECTILE': 4   # Botón para proyectiles
    }
    
    music_volume = 0.5
    effects_volume = 0.5
    all_sounds = []

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Joystick conectado: {joystick.get_name()}")
    else:
        joystick = None

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

    # Inicialización del juego
    current_level = "level1"
    level_data = load_level_data(current_level, None, effects_volume, all_sounds)
    level_data["final_cinematic_shown"] = False
    npcs = level_data["npcs"]
    player = Player(x=level_data["player_spawn"][0], y=level_data["player_spawn"][1], effects_volume=effects_volume, all_sounds=all_sounds)
    
   
    
    fade_music(level_data["music"], 2000)
    hud = HUD(player)
    
    # Mostrar diálogo inicial del nivel
    for dialogue in level_data["spawn_dialogue"]:
        show_dialog_with_name(screen, dialogue["speaker"], dialogue["text"])
        
    camp_image = pygame.image.load(CAMP_IMAGE_PATH).convert()
    camp_image = pygame.transform.scale(camp_image, (640, 480))

    clock = pygame.time.Clock()
    running = True
    health_decrease_rate = 1
    last_health_decrease = pygame.time.get_ticks()
    death_screen_start_time = None
    death_screen_delay = 2
    
    projectiles = pygame.sprite.Group() 
    
    

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_background = screen.copy()
                    result = show_pause_menu(screen, pause_background)
                    if result == "resume":
                        pass
                    elif result == "config":
                        music_volume, effects_volume = show_config_screen(screen, music_volume, effects_volume, all_sounds)
                        actualizar_volumen_efectos(effects_volume, all_sounds)
                    elif result == "exit":
                        running = False
        
                elif event.key == pygame.K_e:
                    player.attack()
                    # Verificar interacción con NPCs una sola vez
                    for npc in level_data["npcs"]:
                        if player.rect.colliderect(npc.rect):
                            show_full_conversation(npc, screen)
                            
                            break
                elif event.key == pygame.K_x and player.has_energy:
                   direction = 1 if player.last_direction == "right" else -1
                   projectile = EnergyProjectile(player.rect.centerx, player.rect.centery, direction)
                   projectiles.add(projectile)

        # Control del joystick
        if joystick:
            # Pausa con botón 7
            if joystick.get_button(ARCADE_BUTTONS['PAUSE']):
                pause_background = screen.copy()
                result = show_pause_menu(screen, pause_background)
                if result == "resume":
                    pass
                elif result == "config":
                    music_volume, effects_volume = show_config_screen(screen, music_volume, effects_volume, all_sounds)
                    actualizar_volumen_efectos(effects_volume, all_sounds)
                elif result == "exit":
                    running = False
            
            # Ataque con botón B (1)
            if joystick.get_button(ARCADE_BUTTONS['ATTACK']):
                player.attack()
                
            # Interacción con NPCs con botón D (3)
            if joystick.get_button(ARCADE_BUTTONS['INTERACT']):
                for npc in level_data["npcs"]:
                    if player.rect.colliderect(npc.rect):
                        show_full_conversation(npc, screen)
                        break
                        
            # Disparar proyectil con botón especial (4)
            # Verifica si el botón de disparo está presionado
            if joystick.get_button(ARCADE_BUTTONS['PROJECTILE']):
                if not projectile_button_pressed and player.has_energy:
                    direction = 1 if player.last_direction == "right" else -1
                    projectile = EnergyProjectile(player.rect.centerx, player.rect.centery, direction)
                    projectiles.add(projectile)
                    projectile_button_pressed = True
            else:
                projectile_button_pressed = False


        # Actualizaciones
        player.update(level_data["collision_rects"], level_data["enemies"], 
                     level_data["map_width"], level_data["map_height"])
        level_data["camera"].update(player.rect)
        
       
        
        for projectile in projectiles:
            projectile.update(level_data["map_width"], level_data["map_height"], level_data["collision_rects"])
            
        for projectile in projectiles:
           for enemy in level_data["enemies"]:
               if projectile.rect.colliderect(enemy.rect):
                   enemy.take_damage(projectile.damage, knockback_direction=projectile.direction)
                   projectile.kill()  # El proyectil desaparece al colisionar     
        
        for enemy in level_data["enemies"]:
            enemy.update(level_data["collision_rects"], player)
            
            if level_data["final_cinematic_shown"]:
                level_data["enemies"] = [e for e in level_data["enemies"] if not isinstance(e, MiniBoss) or not e.ready_to_remove]    
            

        for enemy in level_data["enemies"]:
           if isinstance(enemy, MiniBoss):
               enemy.draw_health_bar(screen, level_data["camera"])
               enemy.projectiles.update(
                   level_data["map_width"], level_data["map_height"], level_data["collision_rects"]
               )

               for bp in enemy.projectiles:
                   if bp.rect.colliderect(player.rect):
                       player.take_damage(30, play_sound=True)
                       bp.kill()


        minibosses = [enemy for enemy in level_data["enemies"] if isinstance(enemy, MiniBoss)]
        # Verifica cuántos minibosses hay

        for enemy in minibosses:
            print(f"Miniboss dead: {enemy.dead}, death animation finished: {enemy.death_animation_finished}")
        
        if minibosses and not level_data["final_cinematic_shown"]:
            all_minibosses_dead = all(
                enemy.dead and enemy.death_animation_finished
                for enemy in level_data["enemies"]
                if isinstance(enemy, MiniBoss)
            )
            print(f"All minibosses dead: {all_minibosses_dead}")
            if all_minibosses_dead:
                show_final_cinematic(screen)
                level_data["final_cinematic_shown"] = True
              
              
        level_data["consumables"].update()

        # Pérdida de salud progresiva
        current_time = pygame.time.get_ticks()
        if current_time - last_health_decrease >= 1000:
            player.take_damage(health_decrease_rate, play_sound=False)
            last_health_decrease = current_time

        # Recolectar consumibles
        consumable_hits = pygame.sprite.spritecollide(player, level_data["consumables"], True)
        for cons in consumable_hits:
          if getattr(cons, "consumable_type", "") == "energy_orb":
              player.has_energy = True
              player.energy_timer = player.energy_max_time
              # Aquí puedes poner una animación, sonido o efecto si quieres
          else:
              player.health = min(player.max_health, player.health + int(cons.health_value))

        # Cambio de nivel
        if (level_data["level_end_rect"] and 
            player.rect.colliderect(level_data["level_end_rect"])):

            # Mostrar diálogos de fin de nivel
            for dialogue in level_data["end_dialogue"]:
                show_dialog_with_name(screen, dialogue["speaker"], dialogue["text"])
             
            show_camp_scene(screen, camp_image, duration=3000)    
            
            if level_data["next_level"]:
                current_level = level_data["next_level"]
                level_data = load_level_data(current_level, player, effects_volume, all_sounds)
                level_data["final_cinematic_shown"] = False

                player.rect.topleft = level_data["player_spawn"]  # Actualizar posición
                player.health = player.max_health  # Resetear salud
                player.dead = False  # Asegurar que no está en estado muerto


                fade_music(level_data["music"], 2000)
                
                # Mostrar diálogo inicial del nuevo nivel
                for dialogue in level_data["spawn_dialogue"]:
                    show_dialog_with_name(screen, dialogue["speaker"], dialogue["text"])
            else:
                # Fin del juego
                show_dialog_with_name(screen, "Narrador", "¡Has completado todos los niveles!")
                running = False

        # Dibujado
        screen.fill((0, 0, 0))
        
        if not player.dead:
            draw_tiled_map(screen, level_data["tmx_data"], 
                         level_data["camera"].x, level_data["camera"].y)
            screen.blit(player.image, level_data["camera"].apply(player.rect))
            
            
            for npc in level_data["npcs"]:
             
                npc.update(level_data["collision_rects"])
                npc_screen_rect = level_data["camera"].apply(npc.rect)
                screen.blit(npc.image, npc_screen_rect)

                # Dibujar signo de interrogación (usa rects globales, NO ajustados)
                npc.draw_question_mark(screen, player.rect, level_data["camera"])

            
            for enemy in level_data["enemies"]:
                screen.blit(enemy.image, level_data["camera"].apply(enemy.rect))

                if isinstance(enemy, MiniBoss):
                    enemy.draw_health_bar(screen, level_data["camera"])
                    for bp in enemy.projectiles:
                        screen.blit(bp.image, level_data["camera"].apply(bp.rect))    
                  
        
                
            for cons in level_data["consumables"]:
                screen.blit(cons.image, level_data["camera"].apply(cons.rect))
            
            for p in projectiles:
                screen.blit(p.image, level_data["camera"].apply(p.rect))
    
                
            if player.attack_rect:
                attack_rect_camera = level_data["camera"].apply(player.attack_rect)
                crosshair_pos = (
                   attack_rect_camera.centerx - player.crosshair_image.get_width() // 2,
                   attack_rect_camera.centery - player.crosshair_image.get_height() // 2
                )
                screen.blit(player.crosshair_image, crosshair_pos)
                
        elif not player.death_animation_finished:
            draw_tiled_map(screen, level_data["tmx_data"], 
                         level_data["camera"].x, level_data["camera"].y)
            screen.blit(player.image, level_data["camera"].apply(player.rect))
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