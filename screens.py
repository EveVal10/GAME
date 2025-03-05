import pygame

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

def show_menu(screen, background):
    """
    Muestra el menú y espera la selección del usuario.
    Devuelve True si se selecciona "Jugar", o False si se selecciona salir.
    """
    font = pygame.font.Font(None, 40)
    play_button = font.render("Jugar", True, (255, 255, 255))
    quit_button = font.render("Salir", True, (255, 255, 255))
    play_button_rect = play_button.get_rect(center=(screen.get_width() - 200, screen.get_height() // 2 - 50))
    quit_button_rect = quit_button.get_rect(center=(screen.get_width() - 200, screen.get_height() // 2 + 50))
    clock = pygame.time.Clock()

    # Mostrar botones sobre el fondo
    screen.blit(background, (0, 0))
    screen.blit(play_button, play_button_rect)
    screen.blit(quit_button, quit_button_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    return True
                elif quit_button_rect.collidepoint(event.pos):
                    return False
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
