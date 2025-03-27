import pygame
from dialog import show_dialog_with_name
from utils import get_font
import game_state

# --- Selección del personaje ---
def show_character_selector(screen):
    font = get_font(22)
    clock = pygame.time.Clock()
    selected = 0  # 0: izquierda, 1: derecha

    arion_img = pygame.image.load("assets/characters/arion.png")
    umbrielle_img = pygame.image.load("assets/characters/umbrielle.png")

    arion_img = pygame.transform.scale(arion_img, (200, 300))
    umbrielle_img = pygame.transform.scale(umbrielle_img, (200, 300))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = 0
                elif event.key == pygame.K_RIGHT:
                    selected = 1
                elif event.key in [pygame.K_RETURN, pygame.K_z]:
                    return "arion" if selected == 0 else "umbrielle"

        screen.fill((20, 20, 20))
        screen.blit(arion_img, (screen.get_width()//4 - 100, 150))
        screen.blit(umbrielle_img, (3*screen.get_width()//4 - 100, 150))

        if selected == 0:
            pygame.draw.rect(screen, (255, 255, 255), (screen.get_width()//4 - 110, 140, 220, 320), 3)
        else:
            pygame.draw.rect(screen, (255, 255, 255), (3*screen.get_width()//4 - 110, 140, 220, 320), 3)

        text = font.render("Usa ← → para elegir. Z o Enter para confirmar.", True, (255, 255, 255))
        screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 500))

        pygame.display.flip()
        clock.tick(60)

# --- Pedir nombre al jugador ---
def ask_player_name(screen, character_key):
    font = get_font(24)
    clock = pygame.time.Clock()
    name = ""
    active = True

    prompt = "Has elegido a tu guardián. ¿Qué nombre le darás?"

    while active:
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

        screen.fill((0, 0, 0))
        prompt_surface = font.render(prompt, True, (255, 255, 255))
        name_surface = font.render(name + "_", True, (255, 255, 100))

        screen.blit(prompt_surface, (screen.get_width()//2 - prompt_surface.get_width()//2, 200))
        screen.blit(name_surface, (screen.get_width()//2 - name_surface.get_width()//2, 250))

        pygame.display.flip()
        clock.tick(60)

# --- Mostrar escenas de introducción ---
def show_intro_scenes(screen):
    scenes = [
        { "image": "assets/intro/scene1.png", "speaker": "Narrador", "dialogue": "Prólogo: El Eclipse de la Gema", "duration": None },
        { "image": "assets/intro/scene1.png", "speaker": "Narrador", "dialogue": "La noche en que el cielo se quebró, la Torre del Alba ardía con un fulgor enfermo.", "duration": None },
        { "image": "assets/intro/scene2.png", "speaker": "Narrador", "dialogue": "Felinaria, Alborfelis un reino de armonía, temblaba bajo el peso de una corrupción desconocida.", "duration": None },
        { "image": "assets/intro/scene2.png", "speaker": "Narrador", "dialogue": "Desde los cimientos de la torre, la Gema de la Unidad se fragmentaba con un crujido desgarrador...", "duration": None },
        { "image": "assets/intro/scene5.png", "speaker": "Narrador", "dialogue": "Su luz sagrada era devorada por un abismo de sombras.", "duration": None },
        { "image": "assets/intro/scene6.png", "speaker": "Narrador", "dialogue": "Los hermanos, últimos guardianes de la torre, contemplaban impotentes la caída de su hogar.", "duration": None },
        { "image": "assets/intro/scene8.png", "speaker": "Narrador", "dialogue": "La silueta de Umbra, el espíritu olvidado, emergía del núcleo de la gema...", "duration": None },
        { "image": "assets/intro/scene7.png", "speaker": "Narrador", "dialogue": "Su esencia oscura se extendía como raíces hambrientas, asfixiando la realidad.", "duration": None },
        { "image": "assets/intro/scene9.png", "speaker": "Hermana", "dialogue": "¡Debemos huir! ¡La torre está perdida!", "duration": None },
        { "image": "assets/intro/scene10.png", "speaker": "Hermano", "dialogue": "¡No! Aún podemos salvarla... ¡Todavía hay esperanza!", "duration": None },
        { "image": "assets/intro/scene11.png", "speaker": "Narrador", "dialogue": "Fue en ese instante cuando la elección quedó en manos del destino.", "duration": None },
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

        show_dialog_with_name(screen, scene["speaker"], scene["dialogue"])

    # --- Elección y nombramiento del personaje ---
    chosen = show_character_selector(screen)
    name = ask_player_name(screen, chosen)

    game_state.player_name = name
    game_state.chosen_character = chosen

    # --- Escenas tras la elección ---
    post_choice_scenes = [
        { "image": "assets/intro/scene12.png", "speaker": "Narrador", "dialogue": "El hermano elegido por el jugador se aferra a la vida.", "duration": None },
        { "image": "assets/intro/scene12.png", "speaker": "Narrador", "dialogue": "El otro... se enfrenta directamente a Umbra.", "duration": None },
        { "image": "assets/intro/scene13.png", "speaker": "Narrador", "dialogue": "Un estallido de energía elemental rompe los muros. La torre colapsa.", "duration": None },
        { "image": "assets/intro/scene14.png", "speaker": "Narrador", "dialogue": "El hermano no elegido desaparece entre el caos y las sombras.", "duration": None },
        { "image": "assets/intro/scene15.png", "speaker": "Narrador", "dialogue": "El hermano restante lucha. Pero es inútil.", "duration": None },
        { "image": "assets/intro/scene16.png", "speaker": "Narrador", "dialogue": "Un golpe brutal lo arroja contra las ruinas. Su mundo se desmorona.", "duration": None },
        { "image": "assets/intro/scene17.png", "speaker": "Narrador", "dialogue": f"{game_state.player_name} siente cómo su conciencia se apaga lentamente.", "duration": None },
        { "image": "assets/intro/scene17.png", "speaker": "Narrador", "dialogue": "El tiempo deja de existir...", "duration": None },
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
        show_dialog_with_name(screen, scene["speaker"], dialogue)

    # --- Salto temporal de 100 años ---
    post_time_skip_scenes = [
        { "image": "assets/intro/scene18.png", "speaker": "Narrador", "dialogue": "Silencio. Oscuridad. Un susurro lejano atraviesa el abismo del tiempo.", "duration": None },
        { "image": "assets/intro/scene18.png", "speaker": "Narrador", "dialogue": "Cien años pasaron desde la caída de la Torre del Alba.", "duration": None },
        { "image": "assets/intro/scene19.png", "speaker": "Narrador", "dialogue": "La historia de los guardianes se desvaneció como polvo en el viento. El mundo cambió.", "duration": None },
        { "image": "assets/intro/scene19.png", "speaker": "Narrador", "dialogue": "Los reinos cayeron. Nuevas criaturas caminaron la tierra. Pero una esperanza dormía…", "duration": None },
        { "image": "assets/intro/scene20.png", "speaker": "Narrador", "dialogue": f"...hasta que los ojos de {game_state.player_name} se abrieron nuevamente.", "duration": None },
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
        show_dialog_with_name(screen, scene["speaker"], dialogue)

    # --- Encuentro con Athelia ---
    extended_intro_scenes = [
        { "image": "assets/intro/scene21.png", "speaker": "Narrador", "dialogue": f"Al mirar hacia el cielo, {game_state.player_name} y voler a mirar a su alrededor, encuentra con una figura observadora.", "duration": None },
        { "image": "assets/intro/scene21.png", "speaker": "Narrador", "dialogue": "La figura toma forma: un ser grácil de pelaje azulado, con vetas luminosas y ojos violetas.", "duration": None },
        { "image": "assets/intro/scene22.png", "speaker": "???", "dialogue": "Te has despertado por fin. Mi nombre es Athelia.", "duration": None },
        { "image": "assets/intro/scene22.png", "speaker": f"{game_state.player_name}", "dialogue": "¿Dónde... dónde estamos?", "duration": None },
        { "image": "assets/intro/scene19.png", "speaker": "Athelia", "dialogue": "Esta región se llama Aurumwood. Alguna vez fue parte del reino exterior de Felinaria.", "duration": None },
        { "image": "assets/intro/scene19.png", "speaker": "Athelia", "dialogue": "Han pasado muchas cosas desde que... desapareciste.", "duration": None },
        { "image": "assets/intro/scene23.png", "speaker": f"{game_state.player_name}", "dialogue": "Debo encontrar a mi hermano. Y necesito descubrir qué pasó realmente.", "duration": None },
        { "image": "assets/intro/scene23.png", "speaker": "Athelia", "dialogue": "Lo sé. Por eso estoy aquí. He escuchado rumores... hay rastros de memoria en las ciudades que aún quedan en pie.", "duration": None },
        { "image": "assets/intro/scene23.png", "speaker": f"{game_state.player_name}", "dialogue": "¿Qué ciudades existen ahora? ¿Y qué pasó con las demás?", "duration": None },
        { "image": "assets/intro/scene23.png", "speaker": "Athelia", "dialogue": "Existían seis grandes ciudades. Cinco sobrevivieron. La sexta... quedó sepultada en la oscuridad.", "duration": None },
        { "image": "assets/intro/scene23.png", "speaker": f"{game_state.player_name}", "dialogue": "Debo ir a las ciudades que queden. Tal vez allí encuentre rastros de mi hermano... o de la verdad.", "duration": None },
        { "image": "assets/intro/scene24.png", "speaker": "Athelia", "dialogue": "Conozco un camino hacia Ludoria, la Ciudad de la Música y los Cristales. Pero deberás tener cuidado.", "duration": None },
        { "image": "assets/intro/scene25.png", "speaker": "Narrador", "dialogue": f"Y así, tras cien años de silencio, el viaje de {game_state.player_name} comienza de nuevo.", "duration": None },
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
        show_dialog_with_name(screen, scene["speaker"], dialogue)

    return True
