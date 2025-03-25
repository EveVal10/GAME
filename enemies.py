import pygame
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="bandit", speed=2, health=50, damage=15,
                 effects_volume=0.5, all_sounds=None):
        super().__init__()
        self.type = enemy_type
        self.speed = speed
        self.health = health
        self.damage = damage
        
        # Estados posibles: "idle", "chase", "attack", "death"
        self.state = "idle"

        # Ruta base para cargar animaciones (por ejemplo: assets/enemies/bandit)
        base_path = f"assets/enemies/{enemy_type}"

        # Diccionario de animaciones: cada carpeta con sus fotogramas .png
        self.animations = {
            "idle":   self.load_frames(os.path.join(base_path, "idle")),
            "run":    self.load_frames(os.path.join(base_path, "run")),
            "attack": self.load_frames(os.path.join(base_path, "attack")),
            "death":  self.load_frames(os.path.join(base_path, "death")),
        }
        
        # Control de animación
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5  # Ajusta la velocidad de cambio de fotogramas

        # Primera imagen (o Surface temporal si falta "idle")
        if self.animations["idle"]:
            self.image = self.animations["idle"][0]
        else:
            self.image = pygame.Surface((32, 64))
            self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect(topleft=(x, y))

        # Hitbox para colisiones
        self.hitbox = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)

        # Dirección: 1 = derecha, -1 = izquierda
        self.direction = 1

        # Física
        self.velocity = pygame.math.Vector2(0, 0)
        self.gravity = 0.8
        self.jump_force = -16
        self.grounded = False

        # IA: rango de detección y ataque
        self.chase_range = 200   # distancia a la que persigue
        self.attack_range = 40   # distancia a la que ataca
        self.attack_cooldown = 1000  # milisegundos entre ataques
        self.last_attack_time = 0

        # Sonido de daño al jugador
        self.damage_sound = pygame.mixer.Sound("assets/audio/effects/hurt.mp3")
        self.damage_sound.set_volume(effects_volume)
        if all_sounds is not None:
            all_sounds.append(self.damage_sound)

    def load_frames(self, folder):
       
        frames = []
        if not os.path.isdir(folder):
            return frames  # si no existe la carpeta, retornamos vacío

        files = [f for f in os.listdir(folder) if f.endswith(".png")]

        # Para extraer el número final (ej: frame_0_12 -> 12)
        def get_frame_number(filename):
            name_part = filename.split('.')[0]
            last_segment = name_part.split('_')[-1]
            return int(last_segment)

        files.sort(key=get_frame_number)

        for filename in files:
            path = os.path.join(folder, filename)
            image = pygame.image.load(path).convert_alpha()
            frames.append(image)

        return frames

    def update(self, collision_rects, player):
       
        # 1) Decidir estado
        self.ai_logic(player)
        # 2) Mover + colisiones
        self.move_and_collide(collision_rects)
        # 3) Ver ataque
        self.handle_attack(player)
        # 4) Animar
        self.animate()

    def ai_logic(self, player):
      
        distance = abs(player.rect.centerx - self.rect.centerx)
        if distance > self.chase_range:
            self.set_state("idle")
        else:
            self.set_state("chase")
            if player.rect.centerx < self.rect.centerx:
                self.direction = -1
            else:
                self.direction = 1

    def set_state(self, new_state):
        """Cambia el estado y reinicia la animación."""
        if self.state != new_state:
            self.state = new_state
            self.current_frame = 0
            self.animation_timer = 0

    def move_and_collide(self, collision_rects):
        """Aplica velocidad horizontal, gravedad y resuelve colisiones."""
        # Velocidad X (si está en 'chase')
        self.velocity.x = 0
        if self.state == "chase":
            self.velocity.x = self.speed * self.direction

        # Mover en X
        self.hitbox.x += self.velocity.x

        # Colisiones horizontales
        for rect in collision_rects:
            if self.hitbox.colliderect(rect):
                if self.velocity.x > 0:
                    self.hitbox.right = rect.left
                elif self.velocity.x < 0:
                    self.hitbox.left = rect.right

        # Salto automático si está en "chase" + grounded + hay obstáculo
        if self.state == "chase" and self.grounded:
            sensor_x = self.hitbox.centerx + (self.direction * (self.hitbox.width // 2 + 5))
            sensor_y = self.hitbox.bottom - 5
            sensor_rect = pygame.Rect(sensor_x, sensor_y, 5, 5)
            if any(sensor_rect.colliderect(r) for r in collision_rects):
                self.velocity.y = self.jump_force
                self.grounded = False

        # Gravedad
        self.velocity.y += self.gravity
        self.hitbox.y += self.velocity.y

        # Colisiones verticales
        self.grounded = False
        for rect in collision_rects:
            if self.hitbox.colliderect(rect):
                if self.velocity.y > 0:  # Cayendo
                    self.hitbox.bottom = rect.top
                    self.velocity.y = 0
                    self.grounded = True
                elif self.velocity.y < 0:  # Saltando
                    self.hitbox.top = rect.bottom
                    self.velocity.y = 0

        # Actualiza posición real
        self.rect.topleft = self.hitbox.topleft

    def handle_attack(self, player):
       
        distance = abs(player.rect.centerx - self.rect.centerx)
        if distance <= self.attack_range and self.grounded:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.set_state("attack")
                player.take_damage(self.damage, play_sound=False)
                self.damage_sound.play()
                self.last_attack_time = current_time
        else:
            # Si no está atacando, vuelve a "idle" o "chase"
            if self.state == "attack":
                self.set_state("idle")

    def animate(self):
       
        if self.state == "chase":
            frames_list = self.animations.get("run", [])
        else:
            frames_list = self.animations.get(self.state, [])

        # Fallback a 'idle' si no hay animaciones para el estado
        if not frames_list:
            frames_list = self.animations.get("idle", [])

        if not frames_list:
            return

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(frames_list)

        self.image = frames_list[self.current_frame]

        # Flip si dirección es izquierda
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def take_damage(self, amount):
        
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.set_state("death")
            # Opción 1: matar al enemigo INMEDIATAMENTE
            self.kill()  # Se quita del grupo de sprites en cuanto muere
