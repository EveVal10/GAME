import pygame
import os
import time

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.start_pos = (x, y)

        # Diccionario de animaciones
        self.animations = {
            "idle": self.load_frames("assets/cat_m/idle", scale_factor=1),
            "left": self.load_frames("assets/cat_m/l", scale_factor=1),
            "right": self.load_frames("assets/cat_m/r", scale_factor=1),
            "jump_left": self.load_frames("assets/cat_m/jump_left", scale_factor=1),
            "jump_right": self.load_frames("assets/cat_m/jump_right", scale_factor=1),
            "death": self.load_frames("assets/cat_m/death", scale_factor=1),
            "attack_left": self.load_frames("assets/cat_m/attack/left", scale_factor=1),
            "attack_right": self.load_frames("assets/cat_m/attack/right", scale_factor=1)
        }

        # Estado inicial
        self.state = "idle"
        self.last_direction = "right"
        self.current_frame = 0
        self.image = self.animations[self.state][self.current_frame]
        self.rect = self.image.get_rect(topleft=self.start_pos)

        # Parámetros de movimiento
        self.speed = 4
        self.jump_speed = -15
        self.gravity = 0.8
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False

        # Bandera de muerte
        self.dead = False
        # Indica si la animación de muerte ha finalizado (tras 5s)
        self.death_animation_finished = False

        # Control de animación
        self.animation_timer = 0
        self.animation_speed = 5

        # Control de muerte
        self.death_start_time = None  # Guarda el tiempo en que comienza a "estar muerto"

        # Control de ataque
        self.attacking = False
        self.attack_start_time = None
        self.attack_duration = 0.5  # En segundos
        self.attack_has_hit = False
        self.attack_rect = None

        # --- SISTEMA DE VIDA ---
        self.max_health = 100
        self.health = self.max_health
        self.invulnerability_duration = 1.0  # 1 segundo de invulnerabilidad tras recibir daño
        self.last_damage_time = 0  # Último tiempo de daño

    def load_frames(self, folder, scale_factor=1):
        """Carga y ordena los frames de forma numérica."""
        frames = []
        files = os.listdir(folder)
        # Ordenar los archivos numéricamente (si llevan números en el nombre)
        files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))) 
                   if ''.join(filter(str.isdigit, f)) != "" else 0)
        
        for filename in files:
            if filename.endswith(".png"):
                path = os.path.join(folder, filename)
                image = pygame.image.load(path).convert_alpha()
                if scale_factor != 1:
                    width, height = image.get_size()
                    new_size = (int(width * scale_factor), int(height * scale_factor))
                    image = pygame.transform.scale(image, new_size)
                frames.append(image)

        # Si no se encuentran imágenes, crear un surface vacío para evitar errores
        return frames if frames else [pygame.Surface((32, 64))]

    def update(self, collision_rects, enemy_group, map_width, map_height):
        """
        Actualiza la lógica del jugador: movimiento, colisiones, ataque,
        daño recibido, animación y muerte.
        """
        if self.dead:
            # Si está muerto, manejamos la animación de muerte
            self.handle_death()
            return

        # Manejo de Teclado
        keys = pygame.key.get_pressed()
        self.velocity_x = 0

        # Movimiento horizontal
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.state = "left"
            self.last_direction = "left"
        elif keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.state = "right"
            self.last_direction = "right"
        else:
            # Si no se está moviendo ni atacando, quedarse en idle
            if not self.attacking:
                self.state = "idle"

        # Salto
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_speed
            self.on_ground = False

        # Gravedad y movimiento vertical
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        self.handle_collisions(collision_rects, "vertical")

        # Animación de salto
        if not self.on_ground:
            if self.last_direction == "left":
                self.state = "jump_left"
            else:
                self.state = "jump_right"

        # Verificar colisiones con enemigos (daño por contacto)
        hits = pygame.sprite.spritecollide(self, enemy_group, False)
        for enemy in hits:
            damage = getattr(enemy, "damage", 10)  # Asume que el enemigo tiene un atributo damage
            self.take_damage(damage)

        # Movimiento horizontal y colisiones
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

        # Manejo del ataque
        if self.attacking:
            self.handle_attack(enemy_group)
        else:
            self.attack_rect = None

    def handle_collisions(self, collision_rects, direction):
        """Ajusta la posición del jugador al detectar colisiones."""
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if direction == "horizontal":
                    if self.velocity_x > 0:
                        self.rect.right = rect.left
                    elif self.velocity_x < 0:
                        self.rect.left = rect.right
                else:
                    if self.velocity_y > 0:
                        self.rect.bottom = rect.top
                        self.velocity_y = 0
                        self.on_ground = True
                    elif self.velocity_y < 0:
                        self.rect.top = rect.bottom
                        self.velocity_y = 0

    def animate(self):
        """Actualiza el frame de animación."""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.state])
            self.image = self.animations[self.state][self.current_frame]

    def take_damage(self, amount):
        """
        Resta salud al jugador, considerando un periodo de invulnerabilidad
        para no recibir daño continuo cada frame.
        """
        current_time = time.time()
        if current_time - self.last_damage_time < self.invulnerability_duration:
            # Aún en periodo de invulnerabilidad
            return

        self.health -= amount
        self.last_damage_time = current_time

        # Si la salud llega a cero o menos, se muere
        if self.health <= 0:
            self.health = 0
            self.die()

    def draw_health_bar(self, surface, camera):
        """
        Dibuja la barra de salud sobre el sprite del jugador.
        'camera' es un objeto que ajusta la posición según la cámara.
        """
        applied_rect = camera.apply(self.rect)
        bar_width = self.rect.width
        bar_height = 5
        bar_x = applied_rect.x
        bar_y = applied_rect.y - 10

        # Fondo (rojo)
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Relleno (verde) según proporción de salud
        fill_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))

    def die(self):
        """Inicia la animación de muerte del jugador."""
        if not self.dead:  # Evitar llamar 'die()' múltiples veces
            self.dead = True
            self.death_animation_finished = False
            self.state = "death"
            self.current_frame = 0
            self.animation_timer = 0
            self.death_start_time = time.time()  # Registrar tiempo de muerte

    def handle_death(self):
        """
        Muestra la animación de muerte. Al pasar 5s, marcamos
        self.death_animation_finished = True, pero NO respawneamos aquí.
        """
        # Avanza la animación de muerte
        if self.current_frame < len(self.animations["death"]) - 1:
            self.animation_timer += 1
            # Hacemos la animación un poco más lenta
            if self.animation_timer >= self.animation_speed * 2:
                self.animation_timer = 0
                self.current_frame += 1
                self.image = self.animations["death"][self.current_frame]
        else:
            # Mantener el último frame de la animación
            self.image = self.animations["death"][-1]
            # Cuando pasen 5 segundos de morir,
            # marcamos la animación como finalizada
            if (time.time() - self.death_start_time) >= 5:
                self.death_animation_finished = True

    def respawn(self):
        """Reinicia la posición y los parámetros del jugador."""
        self.rect.topleft = self.start_pos
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.dead = False
        self.death_animation_finished = False
        self.state = "idle"
        self.current_frame = 0
        self.death_start_time = None
        self.health = self.max_health  # Recuperar la vida al máximo

    def attack(self):
        """Inicia la animación de ataque."""
        if not self.attacking:
            self.attacking = True
            self.attack_has_hit = False
            self.attack_start_time = time.time()
            # Usar animación de ataque correspondiente a la última dirección
            if self.last_direction == "left":
                self.state = "attack_left"
            else:
                self.state = "attack_right"
            self.current_frame = 0
            self.animation_timer = 0

    def handle_attack(self, enemy_group):
        """
        Avanza la animación de ataque y crea un rectángulo de ataque
        para dañar enemigos que colisionen con él.
        """
        if self.current_frame < len(self.animations[self.state]) - 1:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame += 1
                self.image = self.animations[self.state][self.current_frame]
        else:
            # Si ya terminó la animación de ataque, revisar si excedió la duración
            if time.time() - self.attack_start_time >= self.attack_duration:
                self.attacking = False
                self.state = "idle"
                self.current_frame = 0
                self.attack_rect = None

        # Calcular el rectángulo de ataque
        if self.attacking and self.current_frame >= 1:
            attack_range = 30
            if self.last_direction == "left":
                attack_rect = pygame.Rect(self.rect.left - attack_range,
                                          self.rect.top,
                                          attack_range,
                                          self.rect.height)
            else:
                attack_rect = pygame.Rect(self.rect.right,
                                          self.rect.top,
                                          attack_range,
                                          self.rect.height)
            self.attack_rect = attack_rect

            # Aplicar daño a enemigos sólo una vez por ataque
            if not self.attack_has_hit:
                for enemy in enemy_group:
                    if attack_rect.colliderect(enemy.rect):
                        enemy.take_damage(20)
                self.attack_has_hit = True
