import pygame
from dialog import show_dialog_with_name
from utils import get_font
import game_state

# Definir constantes del joystick
JOYSTICK_BUTTON_A = 0
JOYSTICK_BUTTON_B = 1
joystick = None

# Inicializar joystick si está disponible
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# --- Selección del personaje con soporte para joystick ---
def show_character_selector(screen):
    font = get_font(22)
    clock = pygame.time.Clock()
    selected = 0  # 0: izquierda, 1: derecha
    last_joystick_time = 0
    joystick_delay = 0.3  # segundos entre movimientos

    arion_img = pygame.image.load("assets/characters/arion.png")
    umbrielle_img = pygame.image.load("assets/characters/umbrielle.png")

    arion_img = pygame.transform.scale(arion_img, (200, 300))
    umbrielle_img = pygame.transform.scale(umbrielle_img, (200, 300))

    while True:
        current_time = pygame.time.get_ticks() / 1000  # Convertir a segundos
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = 0
                elif event.key == pygame.K_RIGHT:
                    selected = 1
                elif event.key in [pygame.K_RETURN, pygame.K_z, pygame.K_SPACE]:
                    return "arion" if selected == 0 else "umbrielle"
            elif joystick and event.type == pygame.JOYBUTTONDOWN:
                if event.button in [JOYSTICK_BUTTON_A, JOYSTICK_BUTTON_B]:
                    return "arion" if selected == 0 else "umbrielle"
            elif joystick and event.type == pygame.JOYHATMOTION:
                if event.value[0] == -1:  # D-Pad izquierda
                    selected = 0
                elif event.value[0] == 1:  # D-Pad derecha
                    selected = 1

        # Manejo continuo del joystick (no solo eventos)
        if joystick:
            axis_value = joystick.get_axis(0)  # Eje horizontal
            if abs(axis_value) > 0.5 and current_time - last_joystick_time > joystick_delay:
                if axis_value < -0.5:  # Izquierda
                    selected = 0
                else:  # Derecha
                    selected = 1
                last_joystick_time = current_time

        screen.fill((20, 20, 20))
        screen.blit(arion_img, (screen.get_width()//4 - 100, 150))
        screen.blit(umbrielle_img, (3*screen.get_width()//4 - 100, 150))

        if selected == 0:
            pygame.draw.rect(screen, (255, 255, 255), (screen.get_width()//4 - 110, 140, 220, 320), 3)
        else:
            pygame.draw.rect(screen, (255, 255, 255), (3*screen.get_width()//4 - 110, 140, 220, 320), 3)

        # Mostrar controles según si hay joystick conectado
   
            
        pygame.display.flip()
        clock.tick(60)

# --- Pedir nombre al jugador con soporte para joystick ---
def ask_player_name(screen, character_key):
    font = get_font(24)
    clock = pygame.time.Clock()
    name = ""
    active = True
    last_key_time = 0
    key_delay = 0.15  # segundos entre pulsaciones

    prompt = "Has elegido a tu guardián. ¿Qué nombre le darás?"

    while active:
        current_time = pygame.time.get_ticks() / 1000  # Convertir a segundos
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode
            elif joystick and event.type == pygame.JOYBUTTONDOWN:
                if event.button == JOYSTICK_BUTTON_A and name:
                    return name

        # Manejo de botones del joystick para borrar
        if joystick and joystick.get_button(JOYSTICK_BUTTON_B) and current_time - last_key_time > key_delay:
            name = name[:-1] if name else ""
            last_key_time = current_time

        screen.fill((0, 0, 0))
        prompt_surface = font.render(prompt, True, (255, 255, 255))
        name_surface = font.render(name + "_", True, (255, 255, 100))

        screen.blit(prompt_surface, (screen.get_width()//2 - prompt_surface.get_width()//2, 200))
        screen.blit(name_surface, (screen.get_width()//2 - name_surface.get_width()//2, 250))

        # Mostrar instrucciones según el control
        if joystick:
            instructions = font.render("Botón A: Confirmar | Botón B: Borrar", True, (200, 200, 200))
        else:
            instructions = font.render("Enter: Confirmar | Backspace: Borrar", True, (200, 200, 200))
        screen.blit(instructions, (screen.get_width()//2 - instructions.get_width()//2, 300))

        pygame.display.flip()
        clock.tick(60)

# --- Mostrar escenas de introducción ---
def show_intro_scenes(screen):
    scenes = [
        { "image": "assets/intro/scene1.png", "speaker": "Narrador", "dialogue": "Prólogo: El Eclipse de la Gema", "duration": None },
        # Resto de escenas comentadas...
    ]

    for scene in scenes:
        try:
            image = pygame.image.load(scene["image"]).convert()
        except Exception as e:
            print("Error al cargar la imagen:", scene["image"], "-", e)
            continue

        image = pygame.transform.scale(image, screen.get_size())
        screen.blit(image, (0, 0))
        pygame.display.flip()
        show_dialog_with_name(screen, scene["speaker"], scene["dialogue"], joystick_param=joystick)
        
    # --- Elección y nombramiento del personaje ---
    chosen = show_character_selector(screen)
    name = ask_player_name(screen, chosen)

    game_state.player_name = name
    game_state.chosen_character = chosen

    # --- Escenas tras la elección ---
    post_choice_scenes = [
        { "image": "assets/intro/scene12.png", "speaker": "Narrador", "dialogue": "El hermano elegido por el jugador se aferra a la vida.", "duration": None },
        # Resto de escenas comentadas...
    ]

    for scene in post_choice_scenes:
        try:
            image = pygame.image.load(scene["image"]).convert()
        except Exception as e:
            print("Error al cargar la imagen:", scene["image"], "-", e)
            continue

        image = pygame.transform.scale(image, screen.get_size())
        screen.blit(image, (0, 0))
        pygame.display.flip()

        dialogue = scene["dialogue"].replace("{player}", game_state.player_name)
        show_dialog_with_name(screen, scene["speaker"], dialogue, joystick_param=joystick)

    # --- Salto temporal de 100 años ---
    post_time_skip_scenes = [
        { "image": "assets/intro/scene18.png", "speaker": "Narrador", "dialogue": "Silencio. Oscuridad. Un susurro lejano atraviesa el abismo del tiempo.", "duration": None },
        # Resto de escenas comentadas...
    ]

    for scene in post_time_skip_scenes:
        try:
            image = pygame.image.load(scene["image"]).convert()
        except Exception as e:
            print("Error al cargar la imagen:", scene["image"], "-", e)
            continue

        image = pygame.transform.scale(image, screen.get_size())
        screen.blit(image, (0, 0))
        pygame.display.flip()

        dialogue = scene["dialogue"].replace("{player}", game_state.player_name)
        show_dialog_with_name(screen, scene["speaker"], dialogue, joystick_param=joystick)

    # --- Encuentro con Athelia ---
    extended_intro_scenes = [
        { "image": "assets/intro/scene21.png", "speaker": "Narrador", "dialogue": f"Al mirar hacia el cielo, {game_state.player_name} y voler a mirar a su alrededor, encuentra con una figura observadora.", "duration": None },
        # Resto de escenas comentadas...
    ]

    for scene in extended_intro_scenes:
        try:
            image = pygame.image.load(scene["image"]).convert()
        except Exception as e:
            print("Error al cargar la imagen:", scene["image"], "-", e)
            continue

        image = pygame.transform.scale(image, screen.get_size())
        screen.blit(image, (0, 0))
        pygame.display.flip()

        dialogue = scene["dialogue"].replace("{player}", game_state.player_name)
        show_dialog_with_name(screen, scene["speaker"], dialogue, joystick_param=joystick)

    return True