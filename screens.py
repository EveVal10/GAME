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

def show_menu(screen, background):
    font = pygame.font.Font(None, 40)
    options = ["Jugar", "Configuración", "Salir"]
    selected_index = 0

    clock = pygame.time.Clock()
    waiting = True
    while waiting:
        screen.fill((50, 50, 50))  # Limpiar pantalla
        screen.blit(background, (0, 0))

        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_index else (100, 100, 100)
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50 + i * 50))
            screen.blit(text, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if selected_index == 0:
                        return True
                    elif selected_index == 1:
                        show_config_screen(screen, background)
                    elif selected_index == 2:
                        return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    text_rect = font.render(option, True, (255, 255, 255)).get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100 + i * 50))
                    if text_rect.collidepoint(mouse_x, mouse_y):
                        if i == 0:
                            return True
                        elif i == 1:
                            show_config_screen(screen, background)
                        elif i == 2:
                            return False
        clock.tick(30)

def show_config_screen(screen, background):
    font = pygame.font.Font(None, 40)
    options = ["Silenciar", "Pantalla Completa", "Volver"]
    selected_index = 0

    slider_x = screen.get_width() // 2 - 100
    slider_y = screen.get_height() // 2 - 50
    slider_width = 200
    slider_height = 20
    volume = pygame.mixer.music.get_volume()

    clock = pygame.time.Clock()
    waiting = True
    while waiting:
        screen.fill((50, 50, 50))  # Limpiar pantalla
        screen.blit(background, (0, 0))

        draw_slider(screen, slider_x, slider_y, slider_width, slider_height, volume)
        volume_text = font.render(f"Volumen: {int(volume * 100)}%", True, (255, 255, 255))
        screen.blit(volume_text, (slider_x, slider_y - 30))

        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_index else (100, 100, 100)
            if i == 0:
                option = "Activar sonido" if pygame.mixer.music.get_volume() == 0 else "Silenciar"
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50 + (i + 1) * 50))
            screen.blit(text, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                if event.key == pygame.K_LEFT and selected_index == 0:
                    volume = max(0, volume - 0.1)
                    pygame.mixer.music.set_volume(volume)
                if event.key == pygame.K_RIGHT and selected_index == 0:
                    volume = min(1, volume + 0.1)
                    pygame.mixer.music.set_volume(volume)
                if event.key == pygame.K_RETURN:
                    if selected_index == 0:
                        if pygame.mixer.music.get_volume() > 0:
                            pygame.mixer.music.set_volume(0)
                        else:
                            pygame.mixer.music.set_volume(volume)
                    elif selected_index == 1:
                        pygame.display.toggle_fullscreen()
                    elif selected_index == 2:
                        return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if slider_x <= mouse_x <= slider_x + slider_width and slider_y <= mouse_y <= slider_y + slider_height:
                    volume = (mouse_x - slider_x) / slider_width
                    pygame.mixer.music.set_volume(volume)
        clock.tick(30)



def draw_slider(screen, x, y, width, height, value):
    pygame.draw.rect(screen, (140, 159, 161), (x, y, width, height), border_radius=5)
    pygame.draw.rect(screen, (145, 211, 217), (x, y, int(width * value), height), border_radius=5)


def show_pause_menu(screen):
    """
    Muestra el menú de pausa con opciones para reanudar, configurar o volver al menú principal.
    """
    font = pygame.font.Font(None, 50)
    options = ["Reanudar", "Configuración", "Salir"]
    selected_index = 0

    clock = pygame.time.Clock()
    paused = True

    while paused:
        window = pygame.Surface((400, 300))
        window.fill((50, 50, 50))

        for index, option in enumerate(options):
            color = (255, 255, 255) if index == selected_index else (200, 200, 200)
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(200, 100 + index * 50))
            window.blit(text, text_rect)

        screen.blit(window, (screen.get_width() // 2 - 200, screen.get_height() // 2 - 150))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if selected_index == 0:  # Reanudar
                        return "resume"
                    elif selected_index == 1:  # Configuración
                        show_config_screen(screen, screen.copy())
                    elif selected_index == 2:  # Volver al Menú Principal
                        return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for index, option in enumerate(options):
                    if 200 <= mouse_x - (screen.get_width() // 2 - 200) <= 400 and 100 + index * 50 <= mouse_y - (screen.get_height() // 2 - 150) <= 150 + index * 50:
                        if index == 0:
                            return "resume"
                        elif index == 1:
                            show_config_screen(screen, screen.copy())
                        elif index == 2:
                            return "quit"
        clock.tick(30)

def draw_slider(screen, x, y, width, height, value):
    """
    Dibuja un slider en la pantalla.
    """
    pygame.draw.rect(screen, (140, 159, 161), (x, y, width, height), border_radius=5)
    pygame.draw.rect(screen, (145, 211, 217), (x, y, int(width * value), height), border_radius=5)

def fade_screen(screen, text, fade_time=1500, duration=3500, font_size=50):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    

    for alpha in range(0, 256, 5):
        screen.fill((0, 0, 0))
        text_surface.set_alpha(alpha)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        clock.tick(30)

    pygame.time.delay(duration)

    for alpha in range(255, -1, -5):
        screen.fill((0, 0, 0))
        text_surface.set_alpha(alpha)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        clock.tick(30)

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

def game_over(screen):
    show_screen(screen, "¡Perdiste! Reiniciando...")
    main_game_loop(screen)

def main_game_loop(screen):
    player_lives = 3
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Simulación de pérdida de vida
        player_lives -= 1
        if player_lives <= 0:
            game_over(screen)
        clock.tick(30)

pygame.init()
screen = pygame.display.set_mode((800, 600))
background = pygame.Surface(screen.get_size())
background.fill((50, 50, 50)) 
