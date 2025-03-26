import pygame
import game_state  # Importa el estado global del juego (nombre y personaje)

class HUD:
    def __init__(self, player):
        self.player = player  # Referencia al jugador para acceder a su vida

        # Determinar el HUD según el personaje elegido
        if game_state.chosen_character == "umbrielle":
            hud_path = "assets/hud/hud_f.png"
        else:
            hud_path = "assets/hud/hud_m.png"

        self.hud_image = pygame.image.load(hud_path).convert_alpha()
        self.hud_image = pygame.transform.scale(self.hud_image, (250, 100))

        # Barra de vida
        self.bar_color = (0, 255, 0)  # Verde
        self.bar_width_max = 170
        self.bar_height = 14
        self.bar_x = 56
        self.bar_y = 14

        # Barra de energía
        self.energy_color = (0, 180, 255)  # Azul claro
        self.energy_height = 10
        self.energy_y_offset = 8  # Espacio debajo de la barra de vida

        # Fuente
        self.font = pygame.font.Font(None, 24)

    def draw(self, screen):
        # HUD base
        screen.blit(self.hud_image, (10, 10))

        # Vida
        bar_width = (self.player.health / self.player.max_health) * self.bar_width_max - 40
        pygame.draw.rect(screen, self.bar_color, (45 + self.bar_x, 10 + self.bar_y, bar_width, self.bar_height))

        # Energía (solo si está activa)
        if self.player.has_energy:
            energy_ratio = self.player.energy_timer / self.player.energy_max_time
            energy_width = energy_ratio * self.bar_width_max - 40
            energy_x = 45 + self.bar_x
            energy_y = 10 + self.bar_y + self.bar_height + self.energy_y_offset
            pygame.draw.rect(screen, self.energy_color, (energy_x, energy_y, energy_width, self.energy_height))

        # Nombre del jugador
        name_surface = self.font.render(game_state.player_name, True, (255, 255, 255))
        screen.blit(name_surface, (20, 85))
