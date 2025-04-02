import pygame
from dialog import show_dialog_with_name
from utils import get_font
import game_state
from screens import show_menu  # Asegúrate de tener esto importado
import os
import sys

# Configuración de botones del joystick
JOYSTICK_BUTTONS = {
    'CONFIRM': 0,      # Botón A (confirmar)
    'BACK': 1,         # Botón B (cancelar/atrás)
    'SPECIAL': 2,      # Botón X (especial)
    'JUMP': 3          # Botón Y (saltar)
}

class VirtualKeyboard:
    def __init__(self, screen):
        self.screen = screen
        self.font = get_font(24)
        self.small_font = get_font(20)
        # Filas del teclado (letras y números)
        self.rows = [
            "ABCDEFGHIJ",
            "KLMNOPQRST",
            "UVWXYZ0123",
            "456789.,! ",
        ]
        # Botones de acción en la parte inferior
        self.action_buttons = ["BORRAR", "ACEPTAR"]
        self.selected_row = 0
        self.selected_col = 0
        self.selected_action = 0  # 0: BORRAR, 1: ACEPTAR
        self.last_joy_move = 0
        self.last_button_press = 0
        self.move_delay = 200  # ms entre movimientos
        self.button_delay = 300  # ms entre pulsaciones
        self.name = ""
        self.button_pressed = False
        self.in_actions = False  # Si estamos en la fila de acciones
        
    def draw(self):
        # Fondo semitransparente
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Dibujar teclado
        start_y = 150
        for i, row in enumerate(self.rows):
            start_x = self.screen.get_width() // 2 - (len(row) * 25)
            for j, char in enumerate(row):
                color = (255, 255, 100) if (not self.in_actions and i == self.selected_row and j == self.selected_col) else (255, 255, 255)
                text = self.font.render(char, True, color)
                self.screen.blit(text, (start_x + j * 50, start_y + i * 50))
        
        # Dibujar botones de acción en la parte inferior
        action_y = start_y + len(self.rows) * 50 + 20
        action_start_x = self.screen.get_width() // 2 - (len(self.action_buttons) * 100)
        
        for i, button in enumerate(self.action_buttons):
            color = (255, 100, 100) if (self.in_actions and i == self.selected_action) else (200, 200, 200)
            pygame.draw.rect(self.screen, color, (action_start_x + i * 200, action_y, 180, 40), 0 if (self.in_actions and i == self.selected_action) else 2)
            text = self.font.render(button, True, (0, 0, 0) if (self.in_actions and i == self.selected_action) else (255, 255, 255))
            self.screen.blit(text, (action_start_x + i * 200 + 90 - text.get_width()//2, action_y + 20 - text.get_height()//2))
        
        # Dibujar nombre actual
        name_text = self.font.render(f"Nombre: {self.name}_", True, (255, 255, 255))
        self.screen.blit(name_text, (self.screen.get_width() // 2 - name_text.get_width() // 2, 100))
        
        # Instrucciones
        instr = self.small_font.render("Mueve el joystick para navegar, Botón A para seleccionar", True, (200, 200, 200))
        self.screen.blit(instr, (self.screen.get_width() // 2 - instr.get_width() // 2, 450))
    
    def update(self, joystick):
        current_time = pygame.time.get_ticks()
        
        if not joystick:
            return None
            
        # Manejo de movimiento con joystick
        if current_time - self.last_joy_move > self.move_delay:
            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)
            
            # Movimiento horizontal
            if axis_x < -0.5:  # Izquierda
                if self.in_actions:
                    self.selected_action = max(0, self.selected_action - 1)
                else:
                    self.selected_col = max(0, self.selected_col - 1)
                self.last_joy_move = current_time
            elif axis_x > 0.5:  # Derecha
                if self.in_actions:
                    self.selected_action = min(len(self.action_buttons)-1, self.selected_action + 1)
                else:
                    self.selected_col = min(len(self.rows[self.selected_row])-1, self.selected_col + 1)
                self.last_joy_move = current_time
            
            # Movimiento vertical - SOLO cambia a acciones cuando está en la última fila y va hacia abajo
            if axis_y < -0.5:  # Arriba
                if self.in_actions:
                    self.in_actions = False
                else:
                    self.selected_row = max(0, self.selected_row - 1)
                    # Asegurar que la columna seleccionada no exceda el límite de la nueva fila
                    self.selected_col = min(self.selected_col, len(self.rows[self.selected_row])-1)
                self.last_joy_move = current_time
            elif axis_y > 0.5:  # Abajo
                if not self.in_actions and self.selected_row == len(self.rows)-1:
                    self.in_actions = True
                elif not self.in_actions:
                    self.selected_row = min(len(self.rows)-1, self.selected_row + 1)
                    # Asegurar que la columna seleccionada no exceda el límite de la nueva fila
                    self.selected_col = min(self.selected_col, len(self.rows[self.selected_row])-1)
                self.last_joy_move = current_time
        
        # Manejo del botón con delay
        if joystick.get_button(JOYSTICK_BUTTONS['CONFIRM']):
            if not self.button_pressed and current_time - self.last_button_press > self.button_delay:
                self.button_pressed = True
                self.last_button_press = current_time
                return self.handle_button_press()
        else:
            self.button_pressed = False
        
        return None
    
    def handle_button_press(self):
        if self.in_actions:
            # Manejar botones de acción
            if self.selected_action == 0:  # BORRAR
                self.name = self.name[:-1]
            elif self.selected_action == 1:  # ACEPTAR
                if self.name:
                    return self.name
        else:
            # Manejar teclas del teclado
            char = self.rows[self.selected_row][self.selected_col]
            if len(self.name) < 16:
                self.name += char
        return None

    def handle_input(self, joystick=None):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.name:
                    return self.name
                elif event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif len(self.name) < 16 and event.unicode.isprintable():
                    self.name += event.unicode
        
        # Manejo de joystick a través del método update
        result = self.update(joystick)
        return result

# --- Selección del personaje ---
def show_character_selector(screen):
    font = get_font(22)
    clock = pygame.time.Clock()
    selected = 0  # 0: izquierda, 1: derecha
    last_joy_move = 0
    move_delay = 500  # ms entre movimientos

    # Inicializar joystick si está disponible
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    arion_img = pygame.image.load("assets/characters/arion.png")
    umbrielle_img = pygame.image.load("assets/characters/umbrielle.png")

    arion_img = pygame.transform.scale(arion_img, (200, 300))
    umbrielle_img = pygame.transform.scale(umbrielle_img, (200, 300))

    while True:
        current_time = pygame.time.get_ticks()
        
        # Manejo de joystick
        if joystick and current_time - last_joy_move > move_delay:
            axis_x = joystick.get_axis(0)
            if axis_x < -0.5:  # Izquierda
                selected = 0
                last_joy_move = current_time
            elif axis_x > 0.5:  # Derecha
                selected = 1
                last_joy_move = current_time
            
            # Confirmar con botón A (0)
            if joystick.get_button(JOYSTICK_BUTTONS['CONFIRM']):
                return "arion" if selected == 0 else "umbrielle"

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

        # Mostrar instrucciones según el control usado
        if joystick:
            text = font.render("Usa el joystick para elegir. Botón A para confirmar.", True, (255, 255, 255))
        else:
            text = font.render("Usa ← → para elegir. Z o Enter para confirmar.", True, (255, 255, 255))
        
        screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 500))

        pygame.display.flip()
        clock.tick(60)

# --- Pedir nombre al jugador ---
def ask_player_name(screen, character_key):
    font = get_font(24)
    clock = pygame.time.Clock()
    
    # Inicializar joystick si está disponible
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    
    # Crear teclado virtual
    keyboard = VirtualKeyboard(screen)
    prompt = "Has elegido a tu guardián. ¿Qué nombre le darás?"

    while True:
        # Manejo de entrada
        result = keyboard.handle_input(joystick)
        if result is not None:
            return result

        # Actualizar teclado virtual con joystick
        if joystick:
            keyboard.update(joystick)

        # Dibujar
        screen.fill((0, 0, 0))
        prompt_surface = font.render(prompt, True, (255, 255, 255))
        screen.blit(prompt_surface, (screen.get_width()//2 - prompt_surface.get_width()//2, 50))
        
        keyboard.draw()
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


def fade_to_black(screen, speed=5):
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill((0, 0, 0))

    for alpha in range(0, 256, speed):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30)




def show_final_cinematic(screen):
    from screens import show_menu  # Si no está ya importado arriba
    from main import BACKGROUND_IMAGE  # Ruta para el fondo del menú principal
    
    
    fade_to_black(screen)

    # Música para la cinemática
    fade_music("assets/audio/game/final_cinematic.mp3", 2000)

    scenes = [
     { "image": "assets/intro/scene26.png", "speaker": "Protagonista", "dialogue": "Es... demasiado fuerte. Mi energía no es suficiente para derrotarlo...", "duration": None },
     { "image": "assets/intro/scene27.png", "speaker": "Athelia", "dialogue": "Lo siento... Lo siento mucho. No puedo moverme... tengo miedo. Algo en él me paraliza.", "duration": None },
     { "image": "assets/intro/scene26.png", "speaker": "Narrador", "dialogue": "De pronto, una distorsión oscura rodea al enemigo. Su figura comienza a temblar, como si algo dentro de él se quebrara.", "duration": None },
     { "image": "assets/intro/scene26.png", "speaker": "???", "dialogue": "*ʐ̨̼̜ʄ͎͕͔̼̙̰͚ᵭ̶̠̯͍̮͚̝ ͎͙͉͚͜ɯ̖͎̠̞͈̭͖̗̰ʂ̴̼͙̩͙͓...*", "duration": None },
     { "image": "assets/intro/scene28.png", "speaker": "Narrador", "dialogue": "Sin razón aparente, el enemigo detiene su ataque. La corrupción lo envuelve por completo... y desaparece en la nada.", "duration": None },
     { "image": "assets/intro/scene28.png", "speaker": "Protagonista", "dialogue": "¿Qué... fue eso?", "duration": None },
     { "image": "assets/intro/scene28.png", "speaker": "Athelia", "dialogue": "No lo sé. Algo más poderoso que nosotros lo alejó... y no creo que haya sido por compasión.", "duration": None },
     { "image": "assets/intro/scene29.png", "speaker": "???", "dialogue": "*Heheheh... sigues con vida... hermano.*", "duration": None }
    ]


    for scene in scenes:
        try:
            image = pygame.image.load(scene["image"]).convert()
        except Exception as e:
            print(f"Error al cargar escena final: {scene['image']}", e)
            continue

        image = pygame.transform.scale(image, screen.get_size())
        screen.blit(image, (0, 0))
        pygame.display.flip()
        show_dialog_with_name(screen, scene["speaker"], scene["dialogue"])

    # Música para créditos
    fade_music("assets/audio/menu/credits_theme.mp3", 2000)

    # Mostrar créditos
    show_credits(screen)
    pygame.quit()
    os.execl(sys.executable, sys.executable, *sys.argv)
    # Volver al menú principal
    background = pygame.transform.scale(pygame.image.load(BACKGROUND_IMAGE).convert(), screen.get_size())
    show_menu(screen, background, music_volume=0.5, effects_volume=0.5, all_sounds=[])

def show_credits(screen):
    font = get_font(24)
    clock = pygame.time.Clock()

    credits = [
     "UNMEI GISEI",
     "",
     "Una historia de destino y sacrificio",
     "",
     "Programación:",
     "Leonardo Ochoa Ravelo",
     "Germán Pérez Chalanda",
     "",
     "Editor de mapas:",
     "David Francisco Espinoza",
     "",
     "Diseño y arte:",
     "Germán Pérez Chalanda",
     "Karen Morales Andrade",
     "Evelin Moreno",
     "",
     "Música y efectos:",
     "Karen Morales",
     "",
     "Historia:",
     "Germán Pérez Chalanda",
     "",
     "Gracias por jugar.",
     "",
     "© 2025 Unmei Gisei Team"
    ]
    

    rendered = [font.render(line, True, (255, 255, 255)) for line in credits]
    total_height = sum(text.get_height() + 10 for text in rendered)
    y = screen.get_height()

    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))

    running = True
    while running:
        screen.blit(background, (0, 0))
        y -= 1  # velocidad del scroll

        current_y = y
        for text in rendered:
            x = screen.get_width() // 2 - text.get_width() // 2
            screen.blit(text, (x, current_y))
            current_y += text.get_height() + 10

        pygame.display.flip()
        clock.tick(60)

        if current_y < 0:
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


def fade_music(new_music, fade_time=2000):
    import pygame
    current_music = pygame.mixer.music.get_busy()
    if current_music:
        current_volume = pygame.mixer.music.get_volume()
        for volume in range(int(current_volume * 100), 0, -5):
            pygame.mixer.music.set_volume(volume / 100)
            pygame.time.delay(fade_time // 20)

    pygame.mixer.music.load(new_music)
    pygame.mixer.music.set_volume(0)
    pygame.mixer.music.play(-1)
    for volume in range(0, 101, 5):
        pygame.mixer.music.set_volume(volume / 100)
        pygame.time.delay(fade_time // 20)