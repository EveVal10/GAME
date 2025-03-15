import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="wolf", speed=2, health=100):
        super().__init__()
        self.type = enemy_type
        self.speed = speed
        self.health = health
        self.direction = 1  # 1 = derecha, -1 = izquierda

        # Parámetros de física
        self.velocity = pygame.math.Vector2(0, 0)
        self.gravity = 0.8
        self.jump_force = -16
        self.grounded = False

        # Imagen y hitbox
        self.image = pygame.Surface((32, 64))
        self.image.fill(self._get_color())
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = pygame.Rect(x + 5, y + 5, 22, 54)

        # Daño que inflige al jugador (valor por defecto)
        self.damage = 10

    def _get_color(self):
        return {
            "wolf": (120, 120, 120),
            "slime": (0, 200, 50),
            "boss": (200, 0, 0)
        }.get(self.type, (255, 0, 0))

    def apply_gravity(self):
        self.velocity.y += self.gravity
        self.hitbox.y += self.velocity.y

    def move(self, collision_rects):
        self.velocity.x = self.speed * self.direction
        self.hitbox.x += self.velocity.x
        # Colisiones horizontales
        for rect in collision_rects:
            if self.hitbox.colliderect(rect):
                if self.velocity.x > 0:
                    self.hitbox.right = rect.left
                    self.direction = -1
                elif self.velocity.x < 0:
                    self.hitbox.left = rect.right
                    self.direction = 1

        # Movimiento vertical
        self.apply_gravity()
        self.grounded = False
        for rect in collision_rects:
            if self.hitbox.colliderect(rect):
                if self.velocity.y > 0:
                    self.hitbox.bottom = rect.top
                    self.velocity.y = 0
                    self.grounded = True
                elif self.velocity.y < 0:
                    self.hitbox.top = rect.bottom
                    self.velocity.y = 0

        self.rect.topleft = self.hitbox.topleft

    def update(self, collision_rects):
        self.move(collision_rects)
        if self.grounded:
            self._check_ledge(collision_rects)

    def _check_ledge(self, collision_rects):
        """Verifica si el enemigo está a punto de caerse y cambia de dirección."""
        sensor_y = self.hitbox.bottom + 5  # Justo debajo de los pies
        sensor_left = pygame.Rect(self.hitbox.left, sensor_y, 1, 5)
        sensor_right = pygame.Rect(self.hitbox.right - 1, sensor_y, 1, 5)
        collision_left = any(sensor_left.colliderect(r) for r in collision_rects)
        collision_right = any(sensor_right.colliderect(r) for r in collision_rects)
        if self.direction == 1 and not collision_right:
            self.direction = -1
        elif self.direction == -1 and not collision_left:
            self.direction = 1

    def take_damage(self, damage):
        """Resta salud al enemigo y lo elimina si la salud llega a cero."""
        self.health -= damage
        if self.health <= 0:
            self.kill()
