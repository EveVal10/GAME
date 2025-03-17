import pygame

class Camera:
    def __init__(self, map_width, map_height, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.map_width = map_width
        self.map_height = map_height
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, target_rect):
        # Centra la cámara en el centro del jugador
        self.x = target_rect.centerx - self.screen_width // 2
        self.y = target_rect.centery - self.screen_height // 2

        # Evitar mostrar fuera del mapa
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0

        max_x = self.map_width - self.screen_width
        max_y = self.map_height - self.screen_height
        if self.x > max_x:
            self.x = max_x
        if self.y > max_y:
            self.y = max_y

    def apply(self, rect):
        # Devuelve un rect desplazado por la cámara
        return rect.move(-self.x, -self.y)
