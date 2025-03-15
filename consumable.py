import pygame

class Consumable(pygame.sprite.Sprite):
    def __init__(self, x, y, consumable_type="fish", health_value=50, pickup_sound=None):
        super().__init__()
        self.consumable_type = consumable_type
        self.health_value = health_value
        self.pickup_sound = pickup_sound
        # Por ahora, asigna una imagen simple (más adelante puedes cargar una imagen real)
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 255, 0))  # Verde, para distinguirlo
        self.rect = self.image.get_rect(topleft=(x, y))
