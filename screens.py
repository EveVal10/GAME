import pygame
import sys

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
    """
    Dibuja un slider simple en la pantalla para ajustar un valor (0 a 1).
    """
    # Fondo del slider
    pygame.draw.rect(screen, (140, 159, 161), (x, y, width, height), border_radius=5)
    # Barra de progreso
    pygame.draw.rect(screen, (145, 211, 217), (x, y, int(width * value), height), border_radius=5)

def blur_surface(surface, factor=0.1):
    """
    Aplica un efecto de blur a una surface.
    factor: valor entre 0 y 1; cuanto menor, mayor el blur.
    """
    width, height = surface.get_size()
    # Reducir el tamaño para suavizar detalles
    small_size = (max(1, int(width * factor)), max(1, int(height * factor)))
    small_surface = pygame.transform.smoothscale(surface, small_size)
    # Volver a escalar a tamaño original
    return pygame.transform.smoothscale(small_surface, (width, height))

def show_config_screen(screen):
    """
    Muestra el menú de configuración usando como fondo una captura actual del juego
    con efecto blur y un overlay semitransparente.
    """
    # Capturar la pantalla actual del juego
    game_screen = screen.copy()
    blurred_background = blur_surface(game_screen, factor=0.1)
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))  # Negro con transparencia (alpha 120)

    font = pygame.font.Font(None, 40)
    options = ["Volumen", "Silenciar/Activar Sonido", "Pantalla Completa", "Volver"]
    selected_index = 0
    volume = pygame.mixer.music.get_volume()
    clock = pygame.time.Clock()

    # Posición para el slider de volumen
    slider_x = screen.get_width() // 2 - 100
    slider_y = screen.get_height() // 2 - 120
    slider_width = 200
    slider_height = 20

    while True:
        # Dibujar el fondo desenfocado con overlay
        screen.blit(blurred_background, (0, 0))
        screen.blit(overlay, (0, 0))

        # Dibujar el slider de volumen
        draw_slider(screen, slider_x, slider_y, slider_width, slider_height, volume)
        volume_text = font.render(f"Volumen: {int(volume * 100)}%", True, (255, 255, 255))
        screen.blit(volume_text, (slider_x, slider_y - 30))

        # Dibujar las opciones del menú de configuración
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

            # Manejo de eventos de teclado
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected_index] == "Volumen":
                        pass  # No se realiza acción especial
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

            # Manejo de eventos de ratón
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Ajustar el volumen al hacer clic sobre el slider
                if (slider_x <= mouse_pos[0] <= slider_x + slider_width and
                        slider_y <= mouse_pos[1] <= slider_y + slider_height):
                    volume = (mouse_pos[0] - slider_x) / slider_width
                    pygame.mixer.music.set_volume(volume)
                # Revisar si se hace clic sobre alguna opción
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(mouse_pos):
                        selected_index = i
                        if options[i] == "Volumen":
                            pass
                        elif options[i] == "Silenciar/Activar Sonido":
                            if pygame.mixer.music.get_volume() > 0:
                                pygame.mixer.music.set_volume(0)
                            else:
                                pygame.mixer.music.set_volume(volume)
                        elif options[i] == "Pantalla Completa":
                            pygame.display.toggle_fullscreen()
                        elif options[i] == "Volver":
                            return

        clock.tick(30)

def show_menu(screen, background):
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(buttons_rects):
                    if rect.collidepoint(mouse_pos):
                        if options[i] == "Jugar":
                            return True
                        elif options[i] == "Salir":
                            return False
                        elif options[i] == "Configuración":
                            show_config_screen(screen)

        clock.tick(30)

def fade_out(screen, duration):
    fade_surface = pygame.Surface(screen.get_size()).convert()
    fade_surface.fill((0, 0, 0))
    clock = pygame.time.Clock()
    alpha = 0
    # Calcular la cantidad de frames que durará el fade, asumiendo ~60 fps
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
    font = pygame.font.Font(None, 40)
    options = ["Reanudar", "Configuración", "Salir"]
    selected_index = 0
    clock = pygame.time.Clock()

    while True:
        screen.blit(background, (0, 0))
        # Título de "Pausa"
        title_font = pygame.font.Font(None, 60)
        title_surface = title_font.render("PAUSA", True, (255, 255, 0))
        title_rect = title_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
        screen.blit(title_surface, title_rect)

        # Dibujar las opciones
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

            elif event.type == pygame.KEYDOWN:
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

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(buttons_rects):
                    if rect.collidepoint(mouse_pos):
                        chosen = options[i]
                        if chosen == "Reanudar":
                            return "resume"
                        elif chosen == "Configuración":
                            return "config"
                        elif chosen == "Salir":
                            return "exit"
        clock.tick(30)
