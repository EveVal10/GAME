# dialog.py
import pygame

def wrap_text(text, font, max_width):
    """Divide el texto en líneas que se ajusten al ancho máximo."""
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def show_dialog_with_name(screen, speaker_name, dialog_text):
    """
    Ejemplo de función de diálogo con nombre, al estilo "caja de texto + recuadro de nombre".
    Espera a que el jugador presione una tecla para continuar.
    """
    font = pygame.font.Font(None, 28)
    name_font = pygame.font.Font(None, 24)

    margin = 20
    max_text_width = screen.get_width() - 80
    wrapped_lines = wrap_text(dialog_text, font, max_text_width)

    line_height = font.get_linesize()
    text_box_height = line_height * len(wrapped_lines) + (margin // 2)
    text_box_width = screen.get_width() - 60
    name_box_height = 28
    # Ancho según el texto del nombre, con algo de espacio
    name_box_width = name_font.size(speaker_name)[0] + 30

    # Recuadro principal (texto)
    text_box = pygame.Surface((text_box_width, text_box_height), pygame.SRCALPHA)
    text_box.fill((240, 240, 240, 200))  # gris claro semitransparente
    pygame.draw.rect(text_box, (0, 120, 200), text_box.get_rect(), 2)  # borde azul

    # Recuadro del nombre
    name_box = pygame.Surface((name_box_width, name_box_height), pygame.SRCALPHA)
    name_box.fill((60, 180, 255, 255))  # azul
    pygame.draw.rect(name_box, (255, 255, 255), name_box.get_rect(), 2)  # borde blanco

    text_box_rect = text_box.get_rect(midbottom=(screen.get_width() // 2, screen.get_height() - 20))
    name_box_rect = name_box.get_rect()
    name_box_rect.topleft = (text_box_rect.left + 20, text_box_rect.top - name_box_height + 2)

    # Renderizar nombre dentro del name_box
    name_surf = name_font.render(speaker_name, True, (255, 255, 255))
    name_surf_rect = name_surf.get_rect(center=name_box.get_rect().center)
    name_box.blit(name_surf, name_surf_rect)

    # Renderizar texto en text_box
    y_offset = 10
    for line in wrapped_lines:
        line_surf = font.render(line, True, (50, 50, 50))
        line_rect = line_surf.get_rect(topleft=(10, y_offset))
        text_box.blit(line_surf, line_rect)
        y_offset += line_height

    # Guardar estado actual de la pantalla
    background_snapshot = screen.copy()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

        # Dibujar el fondo sin el diálogo
        screen.blit(background_snapshot, (0, 0))

        # Overlay suave
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))

        # Dibujar los recuadros
        screen.blit(text_box, text_box_rect)
        screen.blit(name_box, name_box_rect)

        pygame.display.flip()

    # Limpiar el diálogo al terminar
    screen.blit(background_snapshot, (0, 0))
    pygame.display.flip()
