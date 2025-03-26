import pygame
from utils import get_font

try:
    from main import joystick, JOYSTICK_BUTTON_A, JOYSTICK_BUTTON_B
except ImportError:
    joystick = None
   
    JOYSTICK_BUTTON_A = 0
    JOYSTICK_BUTTON_B = 1
    JOYSTICK_BUTTON_X = 2  # Botón X para interactuar con NPCs
    JOYSTICK_BUTTON_START = 6  # Botón Start para pausar

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

def show_dialog_with_name(screen, speaker_name, dialog_text, effects_volume=0.5, joystick_param=None):
    current_joystick = joystick_param if joystick_param is not None else joystick
    font = get_font(20)
    name_font = get_font(20)
    
    blip_sound = pygame.mixer.Sound("assets/audio/effects/text_blip.mp3")
    blip_sound.set_volume(effects_volume)

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
    name_box_rect = name_box.get_rect(topleft=(text_box_rect.left + 20, text_box_rect.top - name_box_height + 2))
    
    name_box.fill((60, 180, 255, 255))
    pygame.draw.rect(name_box, (255, 255, 255), name_box.get_rect(), 2)
    name_surf = name_font.render(speaker_name, True, (255, 255, 255))
    name_box.blit(name_surf, name_surf.get_rect(center=name_box.get_rect().center))
    
    background_snapshot = screen.copy()
    wrapped_lines = wrap_text(dialog_text, font, max_text_width)
    flat_text = "\n".join(wrapped_lines)
    display_text = ""
    char_index = 0

    base_speed = 15
    accelerate_speed = 999
    last_char_time = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    done_typing = False
    
    while not done_typing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                done_typing = True
                display_text = flat_text
            if current_joystick and event.type == pygame.JOYBUTTONDOWN and event.button == JOYSTICK_BUTTON_A:
                done_typing = True
                display_text = flat_text
                
        keys = pygame.key.get_pressed()
        accelerate = keys[pygame.K_z] or keys[pygame.K_RETURN] or keys[pygame.K_SPACE]
        if current_joystick:
            accelerate = accelerate or current_joystick.get_button(JOYSTICK_BUTTON_A)
        
        current_speed = accelerate_speed if accelerate else base_speed
        
        if char_index < len(flat_text) and pygame.time.get_ticks() - last_char_time >= 1000 // current_speed:
            current_char = flat_text[char_index]
            display_text += current_char
            if current_char not in [' ', '\n']:
                blip_sound.play()
            char_index += 1
            last_char_time = pygame.time.get_ticks()
        
        screen.blit(background_snapshot, (0, 0))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        screen.blit(overlay, (0, 0))
        
        text_box.fill((240, 240, 240, 200))
        pygame.draw.rect(text_box, (0, 120, 200), text_box.get_rect(), 2)
        
        y_offset = 10
        for line in display_text.split('\n'):
            text_surface = font.render(line, True, (50, 50, 50))
            text_box.blit(text_surface, (10, y_offset))
            y_offset += line_height
        
        screen.blit(text_box, text_box_rect)
        screen.blit(name_box, name_box_rect)
        pygame.display.flip()
        clock.tick(60)
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_z, pygame.K_RETURN, pygame.K_SPACE]:
                waiting = False
            if current_joystick and event.type == pygame.JOYBUTTONDOWN and event.button in [JOYSTICK_BUTTON_A, JOYSTICK_BUTTON_B]:
                waiting = False
        
        screen.blit(background_snapshot, (0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(text_box, text_box_rect)
        screen.blit(name_box, name_box_rect)
        pygame.display.flip()
        clock.tick(60)
    
    screen.blit(background_snapshot, (0, 0))
    pygame.display.flip()
