import pygame

class EnergyProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, damage=20):
        super().__init__()
        self.image = pygame.image.load("assets/projectiles/energy_ball.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (24, 24))  # Ajusta el tamaño si es necesario
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction  # -1 (izquierda) o 1 (derecha)
        self.speed = 8
        self.damage = damage

        # Variables para la física (gravedad y rebote)
        self.vel_y = 0            # Velocidad vertical inicial
        self.gravity = 0.5        # Aceleración gravitatoria (ajusta según necesites)
        self.bounce_factor = 0.7  # Factor de rebote (pérdida de energía al rebotar)
        self.on_ground = False    # Para verificar si toca el suelo

    def update(self, map_width, map_height, collision_rects):
        # Movimiento horizontal
        self.rect.x += self.speed * self.direction
        
        # Aplicar gravedad si no está en el suelo
        if not self.on_ground:
            self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Verificar colisiones con el suelo (o plataformas)
        self.handle_collisions(collision_rects)

        # Si la bola de energía ha tocado el suelo (o alguna plataforma), rebota
        if self.rect.bottom >= map_height:  # Suelo
            self.rect.bottom = map_height  # Asegura que la bola no se hunda en el suelo
            self.vel_y = -self.vel_y * self.bounce_factor  # Rebote: invierte y amortigua la velocidad
            # Si la velocidad del rebote es muy baja, eliminamos el proyectil
            if abs(self.vel_y) < 1:
                self.kill()

        # Si la bola cae en el vacío (más allá de un límite inferior), se elimina
        fall_limit = map_height + 200  # Límite inferior para considerar que cayó al vacío
        if self.rect.top > fall_limit:
            self.kill()

        # Elimina el proyectil si sale de los límites horizontales del mapa
        if self.rect.right < 0 or self.rect.left > map_width:
            self.kill()

    def handle_collisions(self, collision_rects):
        """Maneja colisiones con el entorno (como el suelo o plataformas)."""
        self.on_ground = False  # Reseteamos la variable cada vez que comprobamos colisiones
        for rect in collision_rects:
            if self.rect.colliderect(rect):  # Si colide con un rectángulo de colisión
                if self.vel_y > 0:  # Si se está moviendo hacia abajo (caída)
                    self.rect.bottom = rect.top  # Ajustamos la posición de la bola en el suelo
                    self.vel_y = 0  # Detener la velocidad vertical
                    self.on_ground = True  # Marcamos que tocó el suelo
