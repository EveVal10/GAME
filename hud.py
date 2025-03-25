import pygame
import game_state  # Importa el estado global del juego (nombre y personaje)

class HUD:
    def __init__(self, player):
        self.player = player  # Referencia al jugador para acceder a su vida

        # Determinar el HUD según el personaje elegido
        if game_state.chosen_character == "umbrielle":
            hud_path = "assets/hud/hud_f.png"  # HUD para Umbrielle
        else:
            hud_path = "assets/hud/hud_m.png"  # HUD para Arion

        self.hud_image = pygame.image.load(hud_path).convert_alpha()

        # Redimensionar la imagen del HUD
        self.hud_image = pygame.transform.scale(self.hud_image, (250, 100))  # Ajusta según necesidad

        # Configuración de la barra de vida
        self.bar_color = (0, 255, 0)  # Verde
        self.bar_width_max = 170
        self.bar_height = 14
        self.bar_x = 56
        self.bar_y = 14

        # Fuente para mostrar el nombre del jugador
        self.font = pygame.font.Font(None, 24)  # Fuente por defecto de pygame

    def draw(self, screen):
        # Dibujar el HUD base
        screen.blit(self.hud_image, (10, 10))

        # Calcular el ancho de la barra de vida
        bar_width = (self.player.health / self.player.max_health) * self.bar_width_max - 40
        pygame.draw.rect(screen, self.bar_color, (45 + self.bar_x, 10 + self.bar_y, bar_width, self.bar_height))

        # (Opcional) Mostrar el nombre del jugador
        name_surface = self.font.render(game_state.player_name, True, (255, 255, 255))
        screen.blit(name_surface, (20, 85))  # Ajusta la posición si lo necesitas
