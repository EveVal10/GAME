import pygame
import sys
import time

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
JOYSTICK_BUTTON_A = 3  # Botón A (confirmar/seleccionar)
JOYSTICK_BUTTON_B = 1  # Botón B (retroceder/cancelar)

# Variables para controlar el movimiento del joystick
joystick_delay = 0.2  # Retardo en segundos para evitar movimientos rápidos

def show_screen(screen, text, duration=3000, font_size=50):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.delay(duration)

def fade_screen(screen, text, fade_time=1500, duration=3500, font_size=50):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, font_size)
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

def show_config_screen(screen):
    last_joystick_time = time.time()  # Inicializar con el tiempo actual

    game_screen = screen.copy()
    blurred_background = blur_surface(game_screen, factor=0.1)
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))

    font = pygame.font.Font(None, 40)
    options = ["Volumen", "Silenciar/Activar Sonido", "Pantalla Completa", "Volver"]
    selected_index = 0
    volume = pygame.mixer.music.get_volume()
    clock = pygame.time.Clock()

    slider_x = screen.get_width() // 2 - 100
    slider_y = screen.get_height() // 2 - 120
    slider_width = 200
    slider_height = 20

    while True:
        screen.blit(blurred_background, (0, 0))
        screen.blit(overlay, (0, 0))

        draw_slider(screen, slider_x, slider_y, slider_width, slider_height, volume)
        volume_text = font.render(f"Volumen: {int(volume * 100)}%", True, (255, 255, 255))
        screen.blit(volume_text, (slider_x, slider_y - 30))

        option_rects = []
        for i, option in enumerate(options):
            display_text = option
            if option == "Silenciar/Activar Sonido":
                display_text = "Silenciar" if pygame.mixer.music.get_volume() > 0 else "Activar Sonido"
            text_color = (255, 255, 0) if i == selected_index else (255, 255, 255)
            text_surface = font.render(display_text, True, text_color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2,
                                                      screen.get_height() // 2 + i * 40))
            screen.blit(text_surface, text_rect)
            option_rects.append(text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Manejo de eventos de teclado y joystick
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected_index] == "Volumen":
                        pass
                    elif options[selected_index] == "Silenciar/Activar Sonido":
                        if pygame.mixer.music.get_volume() > 0:
                            pygame.mixer.music.set_volume(0)
                        else:
                            pygame.mixer.music.set_volume(volume)
                    elif options[selected_index] == "Pantalla Completa":
                        pygame.display.toggle_fullscreen()
                    elif options[selected_index] == "Volver":
                        return
                elif event.key == pygame.K_LEFT:
                    if options[selected_index] == "Volumen":
                        volume = max(0, volume - 0.05)
                        pygame.mixer.music.set_volume(volume)
                elif event.key == pygame.K_RIGHT:
                    if options[selected_index] == "Volumen":
                        volume = min(1, volume + 0.05)
                        pygame.mixer.music.set_volume(volume)

            # Manejo de eventos del joystick
            if joystick:
                if event.type == pygame.JOYAXISMOTION:
                    # Eje vertical (eje 1 en muchos joysticks)
                    if event.axis == 1:
                        if event.value < -0.5:  # Movimiento hacia arriba
                            current_time = time.time()
                            if current_time - last_joystick_time > joystick_delay:
                                selected_index = (selected_index - 1) % len(options)
                                last_joystick_time = current_time
                        elif event.value > 0.5:  # Movimiento hacia abajo
                            current_time = time.time()
                            if current_time - last_joystick_time > joystick_delay:
                                selected_index = (selected_index + 1) % len(options)
                                last_joystick_time = current_time

                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == JOYSTICK_BUTTON_A:  # Botón A (confirmar)
                        if options[selected_index] == "Volumen":
                            pass
                        elif options[selected_index] == "Silenciar/Activar Sonido":
                            if pygame.mixer.music.get_volume() > 0:
                                pygame.mixer.music.set_volume(0)
                            else:
                                pygame.mixer.music.set_volume(volume)
                        elif options[selected_index] == "Pantalla Completa":
                            pygame.display.toggle_fullscreen()
                        elif options[selected_index] == "Volver":
                            return
                    elif event.button == JOYSTICK_BUTTON_B:  # Botón B (retroceder)
                        return

                if event.type == pygame.JOYHATMOTION:
                    if event.value == (0, 1):  # D-Pad arriba
                        selected_index = (selected_index - 1) % len(options)
                    elif event.value == (0, -1):  # D-Pad abajo
                        selected_index = (selected_index + 1) % len(options)

        clock.tick(30)

def show_menu(screen, background):
    last_joystick_time = time.time()  # Inicializar con el tiempo actual

    font = pygame.font.Font(None, 40)
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

            # Manejo de eventos de teclado y joystick
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
                        show_config_screen(screen)

            if joystick:
                if event.type == pygame.JOYAXISMOTION:
                    # Eje vertical (eje 1 en muchos joysticks)
                    if event.axis == 1:
                        if event.value < -0.5:  # Movimiento hacia arriba
                            current_time = time.time()
                            if current_time - last_joystick_time > joystick_delay:
                                selected_index = (selected_index - 1) % len(options)
                                last_joystick_time = current_time
                        elif event.value > 0.5:  # Movimiento hacia abajo
                            current_time = time.time()
                            if current_time - last_joystick_time > joystick_delay:
                                selected_index = (selected_index + 1) % len(options)
                                last_joystick_time = current_time

                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == JOYSTICK_BUTTON_A:  # Botón A (confirmar)
                        if options[selected_index] == "Jugar":
                            return True
                        elif options[selected_index] == "Salir":
                            return False
                        elif options[selected_index] == "Configuración":
                            show_config_screen(screen)
                    elif event.button == JOYSTICK_BUTTON_B:  # Botón B (retroceder)
                        return False

                if event.type == pygame.JOYHATMOTION:
                    if event.value == (0, 1):  # D-Pad arriba
                        selected_index = (selected_index - 1) % len(options)
                    elif event.value == (0, -1):  # D-Pad abajo
                        selected_index = (selected_index + 1) % len(options)

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
    last_joystick_time = time.time()  # Inicializar con el tiempo actual

    font = pygame.font.Font(None, 40)
    options = ["Reanudar", "Configuración", "Salir"]
    selected_index = 0
    clock = pygame.time.Clock()

    while True:
        screen.blit(background, (0, 0))
        title_font = pygame.font.Font(None, 60)
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

            # Manejo de eventos de teclado y joystick
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

            if joystick:
                if event.type == pygame.JOYAXISMOTION:
                    # Eje vertical (eje 1 en muchos joysticks)
                    if event.axis == 1:
                        if event.value < -0.5:  # Movimiento hacia arriba
                            current_time = time.time()
                            if current_time - last_joystick_time > joystick_delay:
                                selected_index = (selected_index - 1) % len(options)
                                last_joystick_time = current_time
                        elif event.value > 0.5:  # Movimiento hacia abajo
                            current_time = time.time()
                            if current_time - last_joystick_time > joystick_delay:
                                selected_index = (selected_index + 1) % len(options)
                                last_joystick_time = current_time

                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == JOYSTICK_BUTTON_A:  # Botón A (confirmar)
                        chosen = options[selected_index]
                        if chosen == "Reanudar":
                            return "resume"
                        elif chosen == "Configuración":
                            return "config"
                        elif chosen == "Salir":
                            return "exit"
                    elif event.button == JOYSTICK_BUTTON_B:  # Botón B (retroceder)
                        return "resume"

                if event.type == pygame.JOYHATMOTION:
                    if event.value == (0, 1):  # D-Pad arriba
                        selected_index = (selected_index - 1) % len(options)
                    elif event.value == (0, -1):  # D-Pad abajo
                        selected_index = (selected_index + 1) % len(options)

        clock.tick(30)

def main():
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Unmei Gisei - 640x480")

    # Cargar fondo
    background = pygame.image.load("assets/screen/background.png").convert()
    background = pygame.transform.scale(background, (640, 480))

    # Mostrar menú
    if not show_menu(screen, background):
        pygame.quit()
        return

    pygame.quit()

if __name__ == "__main__":
    main()