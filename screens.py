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
    Dibuja un slider simple y agradable en la pantalla.
    """
    # Fondo del slider
    pygame.draw.rect(screen, (140, 159, 161), (x, y, width, height), border_radius=5)
    # Barra de progreso
    pygame.draw.rect(screen, (145, 211, 217), (x, y, int(width * value), height), border_radius=5)

def show_config_screen(screen, background):
    """
    Muestra la pantalla de configuración con opciones para ajustar el sonido y la pantalla.
    """
    font = pygame.font.Font(None, 40)
    back_button = font.render("Volver", True, (255, 255, 255))
    mute_button_text = "Silenciar" if pygame.mixer.music.get_volume() > 0 else "Activar Sonido"
    mute_button = font.render(mute_button_text, True, (255, 255, 255))
    fullscreen_button = font.render("Pantalla Completa", True, (255, 255, 255))

    back_button_rect = back_button.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 100))
    mute_button_rect = mute_button.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    fullscreen_button_rect = fullscreen_button.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))

    # Slider de volumen
    slider_x = screen.get_width() // 2 - 100
    slider_y = screen.get_height() // 2 - 50
    slider_width = 200
    slider_height = 20
    volume = pygame.mixer.music.get_volume()

    clock = pygame.time.Clock()
    waiting = True
    while waiting:
        screen.blit(background, (0, 0))

        draw_slider(screen, slider_x, slider_y, slider_width, slider_height, volume)
        volume_text = font.render(f"Volumen: {int(volume * 100)}%", True, (255, 255, 255))
        screen.blit(volume_text, (slider_x, slider_y - 35))

        screen.blit(mute_button, mute_button_rect)
        screen.blit(fullscreen_button, fullscreen_button_rect)
        screen.blit(back_button, back_button_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if slider_x <= mouse_x <= slider_x + slider_width and slider_y <= mouse_y <= slider_y + slider_height:
                    volume = (mouse_x - slider_x) / slider_width
                    pygame.mixer.music.set_volume(volume)
                    mute_button_text = "Silenciar" if volume > 0 else "Activar Sonido"
                    mute_button = font.render(mute_button_text, True, (255, 255, 255))
                    mute_button_rect = mute_button.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                elif mute_button_rect.collidepoint(event.pos):
                    if pygame.mixer.music.get_volume() > 0:
                        pygame.mixer.music.set_volume(0)
                        mute_button_text = "Activar Sonido"
                    else:
                        pygame.mixer.music.set_volume(volume)
                        mute_button_text = "Silenciar"
                    mute_button = font.render(mute_button_text, True, (255, 255, 255))
                    mute_button_rect = mute_button.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                elif fullscreen_button_rect.collidepoint(event.pos):
                    pygame.display.toggle_fullscreen()
                elif back_button_rect.collidepoint(event.pos):
                    return True
        pygame.time.delay(100)

def show_menu(screen, background):
    """
    Muestra el menú y espera la selección del usuario.
    Devuelve True si se selecciona "Jugar", o False si se selecciona salir.
    """
    font = pygame.font.Font(None, 40)
    play_button = font.render("Jugar", True, (255, 255, 255))
    config_button = font.render("Configuración", True, (255, 255, 255))
    quit_button = font.render("Salir", True, (255, 255, 255))
    play_button_rect = play_button.get_rect(center=(screen.get_width() - 200, screen.get_height() // 2 - 50))
    quit_button_rect = quit_button.get_rect(center=(screen.get_width() - 200, screen.get_height() // 2 + 50))
    config_button_rect = config_button.get_rect(center=(screen.get_width() - 200, screen.get_height() // 2 ))

    clock = pygame.time.Clock()

    waiting = True
    while waiting:
        # Dibujar el fondo de pantalla
        screen.blit(background, (0, 0))

        # Dibujar los botones
        screen.blit(play_button, play_button_rect)
        screen.blit(quit_button, quit_button_rect)
        screen.blit(config_button, config_button_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    return True
                elif quit_button_rect.collidepoint(event.pos):
                    return False
                elif config_button_rect.collidepoint(event.pos):
                    show_config_screen(screen, background)  # Mostrar pantalla de configuración
        pygame.time.delay(100)

def fade_out(screen, duration):
    """
    Realiza un fade out en la pantalla, cubriéndola gradualmente con negro.
    duration: tiempo total en milisegundos para completar el fade.
    """
    fade_surface = pygame.Surface(screen.get_size()).convert()
    fade_surface.fill((0, 0, 0))
    clock = pygame.time.Clock()
    alpha = 0
    # Calcula cuántos frames se requieren (asumiendo 60 FPS)
    frames = duration / (1000 / 60)
    fade_speed = 255 / frames  # Incremento de alfa por frame

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        alpha += fade_speed
        if alpha >= 255:
            alpha = 255
            running = False
        fade_surface.set_alpha(int(alpha))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
background = pygame.Surface(screen.get_size())
background.fill((50, 50, 50))  # Fondo gris para el ejemplo



pygame.quit()