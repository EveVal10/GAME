import pygame
import os
import time  # Para manejar la espera al morir

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.start_pos = (x, y)  # Guardar la posición inicial

        # Diccionario de animaciones
        self.animations = {
            "idle": self.load_frames("assets/cat_m/idle", scale_factor=1),
            "left": self.load_frames("assets/cat_m/l", scale_factor=1),
            "right": self.load_frames("assets/cat_m/r", scale_factor=1),
            "jump_left": self.load_frames("assets/cat_m/jump_left", scale_factor=1),
            "jump_right": self.load_frames("assets/cat_m/jump_right", scale_factor=1),
            "death": self.load_frames("assets/cat_m/death", scale_factor=1),
            "attack_left": self.load_frames("assets/cat_m/attack/left", scale_factor=1),  # Ataque izquierda
            "attack_right": self.load_frames("assets/cat_m/attack/right", scale_factor=1)  # Ataque derecha
        }

        self.state = "idle"
        self.last_direction = "right"  # Guardar la última dirección
        self.current_frame = 0
        self.image = self.animations[self.state][self.current_frame]
        self.rect = self.image.get_rect(topleft=self.start_pos)

        # Parámetros de movimiento
        self.speed = 5
        self.jump_speed = -15
        self.gravity = 0.8
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.dead = False  # Bandera de muerte

        # Control de animación
        self.animation_timer = 0
        self.animation_speed = 5

        # Control de muerte
        self.death_start_time = None  # Guarda el tiempo en el que finaliza la animación de muerte

        # Control de ataque
        self.attacking = False  # Bandera de ataque
        self.attack_start_time = None  # Tiempo de inicio del ataque
        self.attack_duration = 0.5  # Duración del ataque en segundos

        # *** NUEVAS PROPIEDADES DE SALUD ***
        self.max_health = 100
        self.health = self.max_health
        self.invulnerability_duration = 1.0
        self.last_damage_time = 0  # Tiempo en que se recibió el último daño

    def load_frames(self, folder, scale_factor=1):
        """Carga y ordena los frames numéricamente."""
        frames = []
        files = os.listdir(folder)
        # Ordenar los archivos por número de frame de forma correcta
        files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))  # Orden numérico
        for filename in files:
            if filename.endswith(".png"):
                path = os.path.join(folder, filename)
                image = pygame.image.load(path).convert_alpha()

                # Escalar imagen si se necesita
                if scale_factor != 1:
                    width, height = image.get_size()
                    new_size = (int(width * scale_factor), int(height * scale_factor))
                    image = pygame.transform.scale(image, new_size)

                frames.append(image)
        return frames if frames else [pygame.Surface((32, 64))]  # Imagen vacía si no hay frames

    def update(self, collision_rects, enemy_group, map_width, map_height, screen):
        """Lógica principal del jugador, recibiendo el tamaño del mapa para limitar movimiento."""
        if self.dead:
            self.handle_death(screen)
            return  # No hacer nada más si está "muerto"

        keys = pygame.key.get_pressed()

        # Movimiento horizontal
        self.velocity_x = 0
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.state = "left"
            self.last_direction = "left"
        elif keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.state = "right"
            self.last_direction = "right"
        else:
            if not self.dead and not self.attacking:
                self.state = "idle"

        # Salto
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_speed
            self.on_ground = False

        # Gravedad
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        self.handle_collisions(collision_rects, "vertical")

        # Animación de salto (izquierda o derecha)
        if not self.on_ground:
            if self.last_direction == "left":
                self.state = "jump_left"
            else:
                self.state = "jump_right"

        # Manejar colisión con enemigos para recibir daño
        hits = pygame.sprite.spritecollide(self, enemy_group, False)
        for enemy in hits:
            damage = getattr(enemy, "damage", 10)
            self.take_damage(damage)

        # Aplicar movimiento horizontal
        self.rect.x += self.velocity_x
        self.handle_collisions(collision_rects, "horizontal")

        # Limitar la posición al tamaño del mapa
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > map_width:
            self.rect.right = map_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > map_height:
            self.rect.bottom = map_height

        # Actualizar animación
        self.animate()

        # Manejar ataque
        if self.attacking:
            self.handle_attack()

    def handle_collisions(self, collision_rects, direction):
        """Maneja colisiones con el entorno."""
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if direction == "horizontal":
                    if self.velocity_x > 0:  # Derecha
                        self.rect.right = rect.left
                    elif self.velocity_x < 0:  # Izquierda
                        self.rect.left = rect.right
                else:
                    if self.velocity_y > 0:  # Cayendo
                        self.rect.bottom = rect.top
                        self.velocity_y = 0
                        self.on_ground = True
                    elif self.velocity_y < 0:  # Subiendo
                        self.rect.top = rect.bottom
                        self.velocity_y = 0

    def animate(self):
        """Maneja la animación de los sprites."""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.state])
            self.image = self.animations[self.state][self.current_frame]

    def take_damage(self, amount):
        current_time = time.time()
        if current_time - self.last_damage_time < self.invulnerability_duration:
            return  # No aplicar daño si aún es invulnerable
        """Resta salud y verifica si debe morir."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.die()

    def draw_health_bar(self, surface, camera):
        """Dibuja una barra de salud encima del sprite del jugador.
           Se utiliza la posición ajustada de la cámara."""
        applied_rect = camera.apply(self.rect)
        bar_width = self.rect.width
        bar_height = 5
        bar_x = applied_rect.x
        bar_y = applied_rect.y - 10  # 10 píxeles por encima del sprite
        fill_width = int(bar_width * (self.health / self.max_health))
        # Fondo de la barra (rojo)
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Parte llena (verde)
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))

    def die(self):
        """Mata al jugador y activa la animación de muerte."""
        self.dead = True
        self.state = "death"
        self.current_frame = 0
        self.animation_timer = 0
        self.death_start_time = None

    def handle_death(self, screen):
        """Maneja la animación de muerte, muestra el mensaje y reinicia al jugador."""
        if self.current_frame < len(self.animations["death"]) - 1:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed * 2:
                self.animation_timer = 0
                self.current_frame += 1
                self.image = self.animations["death"][self.current_frame]
        else:
            self.image = self.animations["death"][-1]
            if self.death_start_time is None:
                self.death_start_time = time.time()
            if time.time() - self.death_start_time >= 5:
                # Mostrar mensaje "lo siento hermana" con un diseño más pequeño y triste
                font = pygame.font.Font("freesansbold.ttf", 50)
                text = font.render("lo lamento, hermana...", True, (100, 100, 150))
                text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                screen.fill((0, 0, 0))  # Limpiar pantalla
                screen.blit(text, text_rect)
                pygame.display.flip()
                pygame.time.delay(3000)  # Espera 3 segundos antes de reiniciar
                self.respawn()

    def respawn(self):
        """Reaparece al jugador en la posición inicial y restaura la salud."""
        self.rect.topleft = self.start_pos
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.dead = False
        self.state = "idle"
        self.current_frame = 0
        self.death_start_time = None
        self.health = self.max_health

    def attack(self):
        """Inicia la animación de ataque."""
        if not self.attacking:
            self.attacking = True
            if self.last_direction == "left":
                self.state = "attack_left"
            else:
                self.state = "attack_right"
            self.current_frame = 0
            self.animation_timer = 0
            self.attack_start_time = time.time()

    def handle_attack(self):
        """Maneja la animación de ataque."""
        if self.current_frame < len(self.animations[self.state]) - 1:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame += 1
                self.image = self.animations[self.state][self.current_frame]
        else:
            if time.time() - self.attack_start_time >= self.attack_duration:
                self.attacking = False
                self.state = "idle"
                self.current_frame = 0
