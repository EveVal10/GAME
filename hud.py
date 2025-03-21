import pygame

class HUD:
    def __init__(self, player):
        self.player = player  # Referencia al jugador para acceder a su vida
        self.hud_image = pygame.image.load("assets/hud/hud_nocoin.png").convert_alpha()
        
        # Redimensionar la imagen del HUD
        self.hud_image = pygame.transform.scale(self.hud_image, (250, 100))  # Ajusta el tamaño a lo que necesites
        
        self.bar_color = (0, 255, 0)  # Color de la barra de vida
        self.bar_width_max = 170  # Ancho máximo de la barra de vida
        self.bar_height = 14  # Altura de la barra de vida
        self.bar_x = 56  # Posición X de la barra de vida (más a la izquierda)
        self.bar_y = 14  # Posición Y de la barra de vida (más arriba)

    def draw(self, screen):
        # Dibujar el HUD base con la imagen redimensionada
        screen.blit(self.hud_image, (10, 10))

        # Calcular el ancho de la barra de vida
        bar_width = (self.player.health / self.player.max_health) * self.bar_width_max - 40

        # Dibujar la barra de vida ajustada
        pygame.draw.rect(screen, self.bar_color, (45 + self.bar_x, 10 + self.bar_y, bar_width, self.bar_height))
