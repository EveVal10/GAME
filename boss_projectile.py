import pygame

class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, speed=5):
        super().__init__()
        self.image = pygame.image.load("assets/ui/boss_ball.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (16, 16))  # Tamaño ajustable
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def update(self, map_width, map_height, collision_rects):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

        # Destruye si sale del mapa o colisiona
        if (self.rect.right < 0 or self.rect.left > map_width or 
            self.rect.bottom < 0 or self.rect.top > map_height):
            self.kill()

        for rect in collision_rects:
            if self.rect.colliderect(rect):
                self.kill()
