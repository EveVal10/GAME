import pygame
import math

class Consumable(pygame.sprite.Sprite):
    def __init__(self, x, y, consumable_type="fish", health_value=50, pickup_sound=None):
        super().__init__()
        self.consumable_type = consumable_type
        self.health_value = health_value
        self.pickup_sound = pickup_sound

        # Carga la imagen original
        fish_image = pygame.image.load("assets/consumables/fish.png").convert_alpha()
        
        # Ajusta el factor de escala o dimensiones deseadas
        scale_factor = 0.3  # Escala al 50%
        original_width, original_height = fish_image.get_size()
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        # Escala la imagen
        self.image = pygame.transform.scale(fish_image, (new_width, new_height))

        self.rect = self.image.get_rect(topleft=(x, y))

        # Para controlar la animación de "levitación"
        self.original_y = y
        self.offset_range = 5       # Qué tanto sube y baja
        self.animation_speed = 0.05 # Velocidad de desplazamiento
        self.time_elapsed = 0.0     # Conteo interno para la oscilación

    def update(self):
        # Actualiza el tiempo transcurrido
        self.time_elapsed += self.animation_speed
        
        # Calcula el desplazamiento sinusoidal
        offset = math.sin(self.time_elapsed) * self.offset_range
        
        # Ajusta la posición Y
        self.rect.y = self.original_y + offset
