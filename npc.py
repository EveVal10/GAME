import pygame
import os

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height,
                 npc_type="villager",
                 speaker="NPC",
                 dialogue_blocks=None):
        """
        x, y: posición inicial del NPC.
        width, height: tamaño (en píxeles) que Tiled asignó al objeto.
        npc_type: subcarpeta de assets/npcs (p.ej. "villager").
        speaker: nombre del NPC que se mostrará en el diálogo.
        dialogue_blocks: lista de strings, donde cada string representa un "bloque" de diálogo.
                         Cada string puede usar '|' para separar líneas dentro de ese bloque.
                         Ejemplo:
                             ["Hola viajero|¿Cómo estás?",
                              "¿Regresaste?|Tengo nuevas noticias."]
        """
        super().__init__()
        
        self.type = npc_type
        self.speaker = speaker
        
        # Convertir cada "bloque" de diálogo en una lista de líneas
        # Por ejemplo, "Hola viajero|¿Cómo estás?" -> ["Hola viajero", "¿Cómo estás?"]
        self.dialogue_blocks = []
        if dialogue_blocks:
            for block_str in dialogue_blocks:
                lines = block_str.split("|")
                self.dialogue_blocks.append(lines)
        # Si no te pasan ninguno, será []
        
        # Índices para manejar el bloque y la línea actual
        self.current_block = 0
        self.current_line = 0
        self.is_talking = False
        
        self.vel_y = 0
        self.gravity = 0.5
        self.max_fall_speed = 10

        # Cargar animaciones (solo "idle" en este ejemplo)
        base_path = os.path.join("assets", "npcs", npc_type)
        idle_frames = self.load_frames(os.path.join(base_path, "idle"))

        # Escalar frames (opcional) al tamaño que Tiled define
        if width > 0 and height > 0 and idle_frames:
            scaled_frames = []
            for frame in idle_frames:
                scaled_frame = pygame.transform.scale(frame, (int(width), int(height)))
                scaled_frames.append(scaled_frame)
            idle_frames = scaled_frames

        self.animations = {
            "idle": idle_frames
        }

        # Control de animación
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5  # Ajusta para acelerar/ralentizar la animación

        # Imagen inicial
        if idle_frames:
            self.image = idle_frames[0]
        else:
            # Si no hay frames, usar un rectángulo de relleno
            self.image = pygame.Surface((width, height))
            self.image.fill((255, 0, 0))

        # Ajustar posición
        self.rect = self.image.get_rect(topleft=(x, y))

    def load_frames(self, folder):
        """
        Carga y ordena los fotogramas PNG dentro de 'folder',
        esperando nombres tipo 'frame_0.png', 'frame_1.png', etc.
        """
        frames = []
        if not os.path.isdir(folder):
            return frames

        # Filtra solo archivos PNG
        files = [f for f in os.listdir(folder) if f.endswith(".png")]

        # Ordenar por el número final del nombre (frame_0, frame_1, ...)
        def get_frame_number(filename):
            name_part = filename.split('.')[0]       # "frame_0"
            segments = name_part.split('_')          # ["frame", "0", "1"]
            return int(segments[-1])

        files.sort(key=get_frame_number)

        for filename in files:
            path = os.path.join(folder, filename)
            image = pygame.image.load(path).convert_alpha()
            frames.append(image)

        return frames

    def update(self, collision_rects, dt=1):
     """
     Aplica animación y gravedad.
     collision_rects: lista de rectángulos del mapa con los que puede colisionar.
     """
     # -------- ANIMACIÓN "idle" --------
     idle_frames = self.animations["idle"]
     if idle_frames:
         self.animation_timer += dt
         if self.animation_timer >= self.animation_speed:
             self.animation_timer = 0
             self.current_frame = (self.current_frame + 1) % len(idle_frames)
             self.image = idle_frames[self.current_frame]

     # -------- GRAVEDAD --------
     self.vel_y += self.gravity
     if self.vel_y > self.max_fall_speed:
         self.vel_y = self.max_fall_speed

     self.rect.y += self.vel_y

     # -------- COLISIÓN CON EL SUELO --------
     for rect in collision_rects:
         if self.rect.colliderect(rect):
             if self.vel_y > 0:  # cayendo
                 self.rect.bottom = rect.top
                 self.vel_y = 0

    def start_dialogue_block(self, block_index=0):
        """
        Empieza el diálogo en el bloque 'block_index' (0, 1, 2, ...).
        Cada bloque se definió en la lista 'dialogue_blocks'.
        """
        if block_index < len(self.dialogue_blocks):
            self.current_block = block_index
            self.current_line = 0
            self.is_talking = True
        else:
            # Si no existe ese bloque, se asegura de no hablar
            self.is_talking = False

    def get_current_line(self):
        """
        Devuelve el texto de la línea actual del diálogo,
        o None si ya no hay más líneas o si no está en diálogo.
        """
        if not self.is_talking:
            return None

        block = self.dialogue_blocks[self.current_block]
        if self.current_line < len(block):
            return block[self.current_line]
        else:
            # Se acabó este bloque
            self.end_dialogue()
            return None

    def advance_dialogue(self):
        """
        Pasa a la siguiente línea del bloque actual.
        Si se termina, end_dialogue() se llama y el NPC deja de hablar.
        """
        if self.is_talking:
            self.current_line += 1
            block = self.dialogue_blocks[self.current_block]
            if self.current_line >= len(block):
                self.end_dialogue()

    def end_dialogue(self):
        self.is_talking = False
        self.current_line = 0
        self.current_block += 1 
     
    def reset_dialogue(self):
        self.current_block = 0
        self.current_line = 0
        self.is_talking = False   # Avanza al siguiente bloque