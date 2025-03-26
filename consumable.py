import pygame
import math
import os

class Consumable(pygame.sprite.Sprite):
    def __init__(self, x, y, consumable_type="fish", health_value=50, pickup_sound=None):
        super().__init__()
        self.consumable_type = consumable_type
        self.health_value = health_value
        self.pickup_sound = pickup_sound

        # Definir las imágenes dependiendo del tipo de consumible
        if self.consumable_type == "energy_orb":
            # Cargar las imágenes para la animación del "orb"
            self.frames = self.load_orb_frames()  # Cargar todas las imágenes del orb
            self.current_frame = 0  # Empezamos con el primer frame
            self.image = self.frames[self.current_frame]  # Usamos el primer frame como imagen inicial
        else:
            # Cargar la imagen para el "pez" por defecto (solo una imagen)
            fish_image = pygame.image.load("assets/consumables/fish/fish.png").convert_alpha()
            scale_factor = 0.3  # Escala al 30%
            self.image = pygame.transform.scale(fish_image, (int(fish_image.get_width() * scale_factor), 
                                                            int(fish_image.get_height() * scale_factor)))

        self.rect = self.image.get_rect(topleft=(x, y))

        # Para controlar la animación de "levitación"
        self.original_y = y
        self.offset_range = 5       # Qué tanto sube y baja
        self.animation_speed = 0.05 # Velocidad de desplazamiento
        self.time_elapsed = 0.0     # Conteo interno para la oscilación

    def load_orb_frames(self):
        """Carga las imágenes para la animación del energy_orb."""
        frames = []
        frame_index = 0
        while True:
            frame_name = f"assets/consumables/energy_orb/frame_0_{frame_index}.png"
            if os.path.exists(frame_name):  # Verifica si el archivo existe
                frame_image = pygame.image.load(frame_name).convert_alpha()
                frames.append(frame_image)
                frame_index += 1
            else:
                break  # Si no se encuentra la imagen, terminamos de cargar los frames
        return frames

    def update(self):
        if self.consumable_type == "energy_orb":
            # Actualizamos la animación del orb
            self.time_elapsed += self.animation_speed
            if self.time_elapsed >= 1:  # Cada segundo pasamos al siguiente frame
                self.time_elapsed = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

        # Actualiza el tiempo transcurrido para la animación de levitación
        self.time_elapsed += self.animation_speed
        
        # Calcula el desplazamiento sinusoidal
        offset = math.sin(self.time_elapsed) * self.offset_range
        
        # Ajusta la posición Y (levitación)
        self.rect.y = self.original_y + offset
