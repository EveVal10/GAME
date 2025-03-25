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

        self.knockback_resistance = 0.8

        

        self.stunned = False
        self.stun_duration = 300  # ms
        self.last_stun_time = 0
        
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
        # 1) Actualizar estado de stun
        if self.stunned:
            # Verificar si ha terminado el tiempo de stun
            if pygame.time.get_ticks() - self.last_stun_time > self.stun_duration:
                self.stunned = False

            # Aplicar resistencia al knockback SOLO durante el stun
            self.velocity.x *= self.knockback_resistance

        # 2) Ejecutar lógica solo si no está aturdido y está vivo
        if not self.stunned and self.state != "death":
            # Decidir estado
            self.ai_logic(player)
            # Mover + colisiones
            self.move_and_collide(collision_rects)
            # Ver ataque
            self.handle_attack(player)

        # 3) Animar siempre (incluso durante stun o muerte)
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
        """Aplica velocidad, gravedad y resuelve colisiones con stun controlado."""
        # Aplicar gravedad siempre (incluso durante stun)
        self.velocity.y += self.gravity

        # Movimiento horizontal solo si no está aturdido
        if not self.stunned:
            # Velocidad X basada en estado
            self.velocity.x = self.speed * self.direction if self.state == "chase" else 0

            # Salto automático (solo si no está aturdido)
            if self.state == "chase" and self.grounded:
                self.auto_jump(collision_rects)

        # Aplicar movimiento horizontal
        self.hitbox.x += self.velocity.x
        self.resolve_collisions(collision_rects, "horizontal")

        # Aplicar movimiento vertical
        self.hitbox.y += self.velocity.y
        self.grounded = False  # Reset antes de verificar colisiones
        self.resolve_collisions(collision_rects, "vertical")

        # Sincronizar posición del sprite
        self.rect.topleft = self.hitbox.topleft

    def auto_jump(self, collision_rects):
        """Lógica de salto automático para obstáculos."""
        sensor_x = self.hitbox.centerx + (self.direction * (self.hitbox.width//2 + 5))
        sensor_rect = pygame.Rect(sensor_x, self.hitbox.bottom-5, 5, 5)
        if any(sensor_rect.colliderect(r) for r in collision_rects):
            self.velocity.y = self.jump_force
            self.grounded = False

    def resolve_collisions(self, collision_rects, direction):
        """Maneja colisiones en una dirección específica."""
        for rect in collision_rects:
            if not self.hitbox.colliderect(rect):
                continue

            if direction == "horizontal":
                if self.velocity.x > 0:
                    self.hitbox.right = rect.left
                elif self.velocity.x < 0:
                    self.hitbox.left = rect.right
            else:  # vertical
                if self.velocity.y > 0:
                    self.hitbox.bottom = rect.top
                    self.velocity.y = 0
                    self.grounded = True
                elif self.velocity.y < 0:
                    self.hitbox.top = rect.bottom
                    self.velocity.y = 0
         
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

    def take_damage(self, amount, knockback_direction=0):
        """Reduce la salud y aplica knockback en una dirección."""
        self.health -= amount

        # Aplicar knockback solo si el enemigo sigue vivo
        if self.health > 0:
            horizontal_knockback = 15  # Empuje horizontal
            vertical_knockback = -12    # Fuerza vertical (pequeño salto)

            self.velocity.x = horizontal_knockback * knockback_direction
            self.velocity.y = vertical_knockback  # Salto hacia arriba

            self.stunned = True  # Nueva variable de estado
            self.last_stun_time = pygame.time.get_ticks()  # Registrar momento del stun

        # Muerte del enemigo
        if self.health <= 0:
            self.health = 0
            self.set_state("death")
            self.kill()
