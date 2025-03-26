import pygame
import sys
import time
from utils import get_font

# Inicialización de Pygame
pygame.init()
# Inicialización del joystick
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick conectado: {joystick.get_name()}")
else:
    joystick = None
    print("No se detectó ningún joystick.")

# Mapeo de botones del joystick
JOYSTICK_BUTTON_A = 0  # Botón A (confirmar/seleccionar) - Normalmente 0 en muchos joysticks
JOYSTICK_BUTTON_B = 1  # Botón B (retroceder/cancelar)
JOYSTICK_BUTTON_START = 7  # Botón Start/Menu

# Variables para controlar el movimiento del joystick
joystick_delay = 0.2  # Retardo en segundos para evitar movimientos rápidos
last_joystick_move_time = 0

def show_screen(screen, text, duration=3000, font_size=50):
    screen.fill((0, 0, 0))
    font = get_font(20)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.delay(duration)

def fade_screen(screen, text, fade_time=1500, duration=3500, font_size=50):
    clock = pygame.time.Clock()
    font = get_font(20)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    # Fade in
    for alpha in range(0, 256, 5):
        screen.fill((0, 0, 0))
        text_surface.set_alpha(alpha)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        clock.tick(30)

    pygame.time.delay(duration)

    # Fade out
    for alpha in range(255, -1, -5):
        screen.fill((0, 0, 0))
        text_surface.set_alpha(alpha)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        clock.tick(30)

def draw_slider(screen, x, y, width, height, value):
    pygame.draw.rect(screen, (140, 159, 161), (x, y, width, height), border_radius=5)
    pygame.draw.rect(screen, (145, 211, 217), (x, y, int(width * value), height), border_radius=5)

def blur_surface(surface, factor=0.1):
    width, height = surface.get_size()
    small_size = (max(1, int(width * factor)), max(1, int(height * factor)))
    small_surface = pygame.transform.smoothscale(surface, small_size)
    return pygame.transform.smoothscale(small_surface, (width, height))

def handle_joystick_movement(current_index, option_count):
    global last_joystick_move_time
    current_time = time.time()
    
    if current_time - last_joystick_move_time > joystick_delay:
        # Eje vertical (eje 1 en muchos joysticks)
        if abs(joystick.get_axis(1)) > 0.5:
            if joystick.get_axis(1) < -0.5:  # Movimiento hacia arriba
                new_index = (current_index - 1) % option_count
            else:  # Movimiento hacia abajo
                new_index = (current_index + 1) % option_count
            last_joystick_move_time = current_time
            return new_index
    
    return current_index

def show_config_screen(screen, music_volume, effects_volume, all_sounds):
    global last_joystick_move_time
    
    game_screen = screen.copy()
    blurred_background = blur_surface(game_screen, factor=0.1)
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))

    font = get_font(20)
    options = ["Volumen Música", "Volumen Efectos", "Silenciar Música", "Pantalla Completa", "Volver"]
    selected_index = 0

    clock = pygame.time.Clock()

    slider_x = screen.get_width() // 2 - 100
    slider_width = 200
    slider_height = 20

    running = True
    while running:
        screen.blit(blurred_background, (0, 0))
        screen.blit(overlay, (0, 0))

        for i, option in enumerate(options):
            text_color = (255, 255, 0) if i == selected_index else (255, 255, 255)
            text_surface = font.render(option, True, text_color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2,
                                                      screen.get_height() // 2 - 100 + i * 50))
            screen.blit(text_surface, text_rect)

            # Mostrar sliders
            if option == "Volumen Música":
                draw_slider(screen, slider_x, text_rect.y + 30, slider_width, slider_height, music_volume)
            elif option == "Volumen Efectos":
                draw_slider(screen, slider_x, text_rect.y + 30, slider_width, slider_height, effects_volume)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected_index] == "Silenciar Música":
                        music_volume = 0 if music_volume > 0 else 0.5
                        pygame.mixer.music.set_volume(music_volume)
                    elif options[selected_index] == "Pantalla Completa":
                        pygame.display.toggle_fullscreen()
                    elif options[selected_index] == "Volver":
                        running = False
                elif event.key == pygame.K_LEFT:
                    if options[selected_index] == "Volumen Música":
                        music_volume = max(0, music_volume - 0.05)
                        pygame.mixer.music.set_volume(music_volume)
                    elif options[selected_index] == "Volumen Efectos":
                        effects_volume = max(0, effects_volume - 0.05)
                        for sound in all_sounds:
                            sound.set_volume(effects_volume)
                elif event.key == pygame.K_RIGHT:
                    if options[selected_index] == "Volumen Música":
                        music_volume = min(1, music_volume + 0.05)
                        pygame.mixer.music.set_volume(music_volume)
                    elif options[selected_index] == "Volumen Efectos":
                        effects_volume = min(1, effects_volume + 0.05)
                        for sound in all_sounds:
                            sound.set_volume(effects_volume)

            # Control con joystick
            if joystick:
                # Navegación con eje vertical o D-Pad
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 1:  # Eje vertical
                        selected_index = handle_joystick_movement(selected_index, len(options))
                
                if event.type == pygame.JOYHATMOTION:
                    if event.value[1] == 1:  # D-Pad arriba
                        selected_index = (selected_index - 1) % len(options)
                    elif event.value[1] == -1:  # D-Pad abajo
                        selected_index = (selected_index + 1) % len(options)
                
                # Ajuste de volúmenes con eje horizontal
                if event.type == pygame.JOYAXISMOTION and event.axis == 0:
                    if options[selected_index] in ["Volumen Música", "Volumen Efectos"]:
                        if event.value < -0.5:  # Izquierda
                            if options[selected_index] == "Volumen Música":
                                music_volume = max(0, music_volume - 0.05)
                                pygame.mixer.music.set_volume(music_volume)
                            else:
                                effects_volume = max(0, effects_volume - 0.05)
                                for sound in all_sounds:
                                    sound.set_volume(effects_volume)
                        elif event.value > 0.5:  # Derecha
                            if options[selected_index] == "Volumen Música":
                                music_volume = min(1, music_volume + 0.05)
                                pygame.mixer.music.set_volume(music_volume)
                            else:
                                effects_volume = min(1, effects_volume + 0.05)
                                for sound in all_sounds:
                                    sound.set_volume(effects_volume)
                
                # Confirmación con botón A
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == JOYSTICK_BUTTON_A:
                        if options[selected_index] == "Silenciar Música":
                            music_volume = 0 if music_volume > 0 else 0.5
                            pygame.mixer.music.set_volume(music_volume)
                        elif options[selected_index] == "Pantalla Completa":
                            pygame.display.toggle_fullscreen()
                        elif options[selected_index] == "Volver":
                            running = False
                    
                    # Volver con botón B
                    elif event.button == JOYSTICK_BUTTON_B:
                        running = False

        # También verificamos el estado del joystick continuamente (no solo en eventos)
        if joystick:
            selected_index = handle_joystick_movement(selected_index, len(options))

        clock.tick(30)

    return music_volume, effects_volume

def show_menu(screen, background, music_volume, effects_volume, all_sounds):
    global last_joystick_move_time
    
    font = get_font(20)
    options = ["Jugar", "Configuración", "Salir"]
    selected_index = 0
    clock = pygame.time.Clock()

    while True:
        screen.blit(background, (0, 0))
        buttons_rects = []
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected_index else (255, 255, 255)
            text_surface = font.render(option, True, color)
            text_rect = text_surface.get_rect(center=(screen.get_width() - 200,
                                                      screen.get_height() // 2 - 50 + i * 50))
            screen.blit(text_surface, text_rect)
            buttons_rects.append(text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected_index] == "Jugar":
                        return True
                    elif options[selected_index] == "Salir":
                        return False
                    elif options[selected_index] == "Configuración":
                        music_volume, effects_volume = show_config_screen(screen, music_volume, effects_volume, all_sounds)

            # Control con joystick
            if joystick:
                # Navegación con eje vertical o D-Pad
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 1:  # Eje vertical
                        selected_index = handle_joystick_movement(selected_index, len(options))
                
                if event.type == pygame.JOYHATMOTION:
                    if event.value[1] == 1:  # D-Pad arriba
                        selected_index = (selected_index - 1) % len(options)
                    elif event.value[1] == -1:  # D-Pad abajo
                        selected_index = (selected_index + 1) % len(options)
                
                # Confirmación con botón A
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == JOYSTICK_BUTTON_A:
                        if options[selected_index] == "Jugar":
                            return True
                        elif options[selected_index] == "Salir":
                            return False
                        elif options[selected_index] == "Configuración":
                            music_volume, effects_volume = show_config_screen(screen, music_volume, effects_volume, all_sounds)
                    
                    # Volver con botón B (en menú principal no hace nada o podría salir)
                    elif event.button == JOYSTICK_BUTTON_B:
                        if options[selected_index] == "Salir":
                            return False

        # También verificamos el estado del joystick continuamente (no solo en eventos)
        if joystick:
            selected_index = handle_joystick_movement(selected_index, len(options))

        clock.tick(30)

def fade_out(screen, duration):
    fade_surface = pygame.Surface(screen.get_size()).convert()
    fade_surface.fill((0, 0, 0))
    clock = pygame.time.Clock()
    alpha = 0
    frames = duration / (1000 / 60)
    fade_speed = 255 / frames

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        alpha += fade_speed
        if alpha >= 255:
            alpha = 255
            running = False

        fade_surface.set_alpha(int(alpha))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

def show_pause_menu(screen, background):
    global last_joystick_move_time
    
    font = get_font(20)
    options = ["Reanudar", "Configuración", "Salir"]
    selected_index = 0
    clock = pygame.time.Clock()

    while True:
        screen.blit(background, (0, 0))
        title_font = get_font(20)
        title_surface = title_font.render("PAUSA", True, (255, 255, 0))
        title_rect = title_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
        screen.blit(title_surface, title_rect)

        buttons_rects = []
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected_index else (255, 255, 255)
            text_surface = font.render(option, True, color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2,
                                                      screen.get_height() // 2 + i * 50))
            screen.blit(text_surface, text_rect)
            buttons_rects.append(text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Manejo de eventos de teclado
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    chosen = options[selected_index]
                    if chosen == "Reanudar":
                        return "resume"
                    elif chosen == "Configuración":
                        return "config"
                    elif chosen == "Salir":
                        return "exit"
                elif event.key == pygame.K_ESCAPE:
                    return "resume"

            # Manejo de eventos de joystick
            if joystick:
                # Navegación con eje vertical o D-Pad
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 1:  # Eje vertical
                        selected_index = handle_joystick_movement(selected_index, len(options))
                
                if event.type == pygame.JOYHATMOTION:
                    if event.value[1] == 1:  # D-Pad arriba
                        selected_index = (selected_index - 1) % len(options)
                    elif event.value[1] == -1:  # D-Pad abajo
                        selected_index = (selected_index + 1) % len(options)
                
                # Confirmación con botón A
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == JOYSTICK_BUTTON_A:
                        chosen = options[selected_index]
                        if chosen == "Reanudar":
                            return "resume"
                        elif chosen == "Configuración":
                            return "config"
                        elif chosen == "Salir":
                            return "exit"
                    
                    # Volver con botón B o Start
                    elif event.button in [JOYSTICK_BUTTON_B, JOYSTICK_BUTTON_START]:
                        return "resume"

        # También verificamos el estado del joystick continuamente (no solo en eventos)
        if joystick:
            selected_index = handle_joystick_movement(selected_index, len(options))

        clock.tick(30)

def main():
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Unmei Gisei - 640x480")

    # Cargar fondo
    background = pygame.image.load("assets/screen/background.png").convert()
    background = pygame.transform.scale(background, (640, 480))

    # Volúmenes iniciales
    music_volume = 0.5
    effects_volume = 0.5
    all_sounds = []  # Lista de efectos de sonido del juego

    # Mostrar menú
    if not show_menu(screen, background, music_volume, effects_volume, all_sounds):
        pygame.quit()
        return

    pygame.quit()

if __name__ == "__main__":
    main()