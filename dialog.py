import pygame
from utils import get_font

def wrap_text(text, font, max_width):
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

def show_dialog_with_name(screen, speaker_name, dialog_text, effects_volume=0.5):
    font = get_font(20)
    name_font = get_font(20)

    # Sonido de letra
    blip_sound = pygame.mixer.Sound("assets/audio/effects/text_blip.mp3")
    blip_sound.set_volume(effects_volume)

    # Configuración visual
    margin = 20
    max_text_width = screen.get_width() - 80
    line_height = font.get_linesize()

    text_box_width = screen.get_width() - 60
    text_box_height = line_height * 3 + margin
    name_box_height = 28
    name_box_width = name_font.size(speaker_name)[0] + 30

    text_box = pygame.Surface((text_box_width, text_box_height), pygame.SRCALPHA)
    name_box = pygame.Surface((name_box_width, name_box_height), pygame.SRCALPHA)

    text_box_rect = text_box.get_rect(midbottom=(screen.get_width() // 2, screen.get_height() - 20))
    name_box_rect = name_box.get_rect()
    name_box_rect.topleft = (text_box_rect.left + 20, text_box_rect.top - name_box_height + 2)

    name_box.fill((60, 180, 255, 255))
    pygame.draw.rect(name_box, (255, 255, 255), name_box.get_rect(), 2)
    name_surf = name_font.render(speaker_name, True, (255, 255, 255))
    name_surf_rect = name_surf.get_rect(center=name_box.get_rect().center)
    name_box.blit(name_surf, name_surf_rect)

    background_snapshot = screen.copy()

    # Configuración del texto dinámico
    wrapped_lines = wrap_text(dialog_text, font, max_text_width)
    flat_text = "\n".join(wrapped_lines)
    display_text = ""
    char_index = 0

    base_speed = 15
    accelerate_speed = 999
    last_char_time = 0
    clock = pygame.time.Clock()

    done_typing = False

    # Inicializar joystick si está disponible
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    # Definir botones del joystick para diálogos
    JOYSTICK_BUTTONS = {
        'ACCEPT': 0,  # Botón A (típico para aceptar)
        'SKIP': 1     # Botón B (típico para cancelar/saltar)
    }

    while not done_typing:
        accelerate = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Verificar teclado y joystick para acelerar texto
        keys = pygame.key.get_pressed()
        joystick_pressed = False
        
        if joystick:
            # Verificar botones del joystick (A o B para acelerar)
            joystick_pressed = any(joystick.get_button(btn) for btn in JOYSTICK_BUTTONS.values())
        
        accelerate = keys[pygame.K_z] or keys[pygame.K_RETURN] or joystick_pressed
        current_speed = accelerate_speed if accelerate else base_speed

        current_time = pygame.time.get_ticks()
        if char_index < len(flat_text) and current_time - last_char_time >= 1000 // current_speed:
            current_char = flat_text[char_index]
            display_text += current_char
            if current_char not in [' ', '\n']:
                blip_sound.play()
            char_index += 1
            last_char_time = current_time
        elif char_index >= len(flat_text):
            done_typing = True
            blip_sound.stop()

        # Render
        screen.blit(background_snapshot, (0, 0))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))

        text_box.fill((240, 240, 240, 200))
        pygame.draw.rect(text_box, (0, 120, 200), text_box.get_rect(), 2)

        lines = display_text.split('\n')
        y_offset = 10
        for line in lines:
            text_surface = font.render(line, True, (50, 50, 50))
            text_box.blit(text_surface, (10, y_offset))
            y_offset += line_height

        screen.blit(text_box, text_box_rect)
        screen.blit(name_box, name_box_rect)
        pygame.display.flip()
        clock.tick(60)

    # Mostrar ícono de continuar ("▶") parpadeante
    waiting = True
    blink = True
    blink_timer = 0
    blink_interval = 500  # milisegundos

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_z, pygame.K_RETURN]:
                    waiting = False
            elif event.type == pygame.JOYBUTTONDOWN:
                # Cualquier botón del joystick para continuar
                if event.button in JOYSTICK_BUTTONS.values():
                    waiting = False

        # Verificar estado continuo de botones del joystick
        if joystick:
            if any(joystick.get_button(btn) for btn in JOYSTICK_BUTTONS.values()):
                waiting = False

        screen.blit(background_snapshot, (0, 0))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))
        screen.blit(text_box, text_box_rect)
        screen.blit(name_box, name_box_rect)

        # Mostrar el ícono de continuar
        blink_timer += clock.get_time()
        if blink_timer >= blink_interval:
            blink = not blink
            blink_timer = 0

        if blink:
            icon = font.render("▶", True, (100, 100, 100))
            icon_rect = icon.get_rect(bottomright=(text_box_rect.right - 10, text_box_rect.bottom - 10))
            screen.blit(icon, icon_rect)

        pygame.display.flip()
        clock.tick(60)

    screen.blit(background_snapshot, (0, 0))
    pygame.display.flip()