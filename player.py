import pygame
import os
import game_state

# Definir constantes para los botones del joystick
JOYSTICK_BUTTON_A = 0
JOYSTICK_BUTTON_B = 1

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, effects_volume=0.5, all_sounds=None):
        super().__init__()
        self.start_pos = (x, y)
        self.all_sounds = all_sounds if all_sounds is not None else []

        # Cargar animaciones según el personaje seleccionado
        base_path = "assets/cat_f" if game_state.chosen_character == "umbrielle" else "assets/cat_m"
        
        self.animations = {
            "idle": self.load_frames(os.path.join(base_path, "idle")),
            "left": self.load_frames(os.path.join(base_path, "l")),
            "right": self.load_frames(os.path.join(base_path, "r")),
            "jump_left": self.load_frames(os.path.join(base_path, "jump_left")),
            "jump_right": self.load_frames(os.path.join(base_path, "jump_right")),
            "death": self.load_frames(os.path.join(base_path, "death")),
            "attack_left": self.load_frames(os.path.join(base_path, "attack/left")),
            "attack_right": self.load_frames(os.path.join(base_path, "attack/right"))
        }

        # Estado inicial
        self.state = "idle"
        self.last_direction = "right"
        self.current_frame = 0
        self.image = self.animations[self.state][self.current_frame]
        self.rect = self.image.get_rect(topleft=self.start_pos)

        # Física y movimiento
        self.speed = 4
        self.jump_speed = -15
        self.gravity = 0.8
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False

        # Sistema de vida
        self.max_health = 100
        self.health = self.max_health
        self.invulnerability_duration = 1000  # 1 segundo
        self.last_damage_time = 0

        # Estado de energía
        self.has_energy = False
        self.energy_max_time = 10  # segundos
        self.energy_timer = 0

        # Control de animación
        self.animation_timer = 0
        self.animation_speed = 5  # frames por actualización

        # Ataque
        self.attacking = False
        self.attack_start_time = 0
        self.attack_duration = 500  # ms
        self.attack_has_hit = False
        self.attack_rect = None

        # Muerte
        self.dead = False
        self.death_animation_finished = False
        self.death_start_time = 0

        # Sonidos
        self.sounds = {
            "attack": self.load_sound("assets/audio/effects/attack.mp3", effects_volume),
            "jump": self.load_sound("assets/audio/effects/jump.mp3", effects_volume),
            "hurt": self.load_sound("assets/audio/effects/hurt.mp3", effects_volume),
            "walk": self.load_sound("assets/audio/effects/walk.mp3", effects_volume),
            "death": self.load_sound("assets/audio/effects/death.mp3", effects_volume)
        }

        # Inicializar joystick
        self.init_joystick()

    def extract_number(self, filename):
        """Extrae números del nombre de archivo para ordenar."""
        digits = ''.join(filter(str.isdigit, filename))
        return int(digits) if digits else 0

    def load_frames(self, folder, scale_factor=1):
        """Carga y ordena los frames de animación de forma numérica."""
        try:
            # Obtener todos los archivos PNG del directorio
            files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
            
            # Ordenar los archivos numéricamente
            files.sort(key=self.extract_number)
            
            frames = []
            for filename in files:
                try:
                    image = pygame.image.load(os.path.join(folder, filename)).convert_alpha()
                    if scale_factor != 1:
                        new_size = (int(image.get_width() * scale_factor), 
                                   int(image.get_height() * scale_factor))
                        image = pygame.transform.scale(image, new_size)
                    frames.append(image)
                except pygame.error as e:
                    print(f"Error loading image {filename}: {e}")
            
            return frames if frames else [pygame.Surface((32, 64), pygame.SRCALPHA)]
        except Exception as e:
            print(f"Error loading frames from {folder}: {e}")
            return [pygame.Surface((32, 64), pygame.SRCALPHA)]

    def load_sound(self, path, volume):
        """Carga y configura un sonido."""
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            self.all_sounds.append(sound)
            return sound
        except pygame.error as e:
            print(f"Error loading sound {path}: {e}")
            return pygame.mixer.Sound(buffer=bytearray(100))  # Sonido vacío

    def init_joystick(self):
        """Inicializa el joystick si está disponible."""
        try:
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"Joystick conectado: {self.joystick.get_name()}")
            else:
                self.joystick = None
                print("No se detectó ningún joystick.")
        except Exception as e:
            print(f"Error initializing joystick: {e}")
            self.joystick = None

    def update(self, collision_rects, enemy_group, map_width, map_height):
        """Actualiza el estado del jugador."""
        if self.dead:
            self.handle_death()
            return

        self.handle_movement()
        self.handle_jump()
        self.apply_gravity()
        self.handle_collisions(collision_rects, enemy_group)
        self.check_map_bounds(map_width, map_height)
        self.handle_attack(enemy_group)
        self.update_energy()
        self.animate()

    def handle_movement(self):
        """Maneja el movimiento horizontal del jugador."""
        self.velocity_x = 0
        moving = False

        # Teclado
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
            self.state = "left"
            self.last_direction = "left"
            moving = True
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
            self.state = "right"
            self.last_direction = "right"
            moving = True

        # Joystick - movimiento digitalizado
        if self.joystick:
            # Eje horizontal
            axis_x = self.joystick.get_axis(0)
            if axis_x < -0.5:  # Izquierda
                self.velocity_x = -self.speed
                self.state = "left"
                self.last_direction = "left"
                moving = True
            elif axis_x > 0.5:  # Derecha
                self.velocity_x = self.speed
                self.state = "right"
                self.last_direction = "right"
                moving = True

            # D-Pad horizontal
            hat = self.joystick.get_hat(0)
            if hat[0] == -1:  # Izquierda
                self.velocity_x = -self.speed
                self.state = "left"
                self.last_direction = "left"
                moving = True
            elif hat[0] == 1:  # Derecha
                self.velocity_x = self.speed
                self.state = "right"
                self.last_direction = "right"
                moving = True

        if self.velocity_x == 0 and not self.attacking:
            self.state = "idle"

        # Sonido de caminar
        if moving and self.on_ground and not self.attacking:
            if not pygame.mixer.Channel(1).get_busy():
                pygame.mixer.Channel(1).play(self.sounds["walk"])
        else:
            pygame.mixer.Channel(1).stop()

    def handle_jump(self):
        """Maneja el salto del jugador."""
        jump_pressed = (pygame.key.get_pressed()[pygame.K_SPACE] or 
                       (self.joystick and self.joystick.get_button(JOYSTICK_BUTTON_A)))
        
        if jump_pressed and self.on_ground:
            self.velocity_y = self.jump_speed
            self.on_ground = False
            self.sounds["jump"].play()

    def apply_gravity(self):
        """Aplica gravedad al jugador."""
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Animación de salto
        if not self.on_ground:
            if self.last_direction == "left":
                self.state = "jump_left"
            else:
                self.state = "jump_right"

    def handle_collisions(self, collision_rects, enemy_group):
        """Maneja colisiones con el entorno y enemigos."""
        # Colisiones verticales (gravedad/salto)
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if self.velocity_y > 0:  # Cayendo
                    self.rect.bottom = rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # Saltando
                    self.rect.top = rect.bottom
                    self.velocity_y = 0

        # Colisiones horizontales (movimiento)
        self.rect.x += self.velocity_x
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if self.velocity_x > 0:  # Derecha
                    self.rect.right = rect.left
                elif self.velocity_x < 0:  # Izquierda
                    self.rect.left = rect.right

        # Colisiones con enemigos
        hits = pygame.sprite.spritecollide(self, enemy_group, False)
        for enemy in hits:
            self.take_damage(getattr(enemy, "damage", 10))

    def check_map_bounds(self, map_width, map_height):
        """Limita al jugador dentro de los bordes del mapa."""
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(map_width, self.rect.right)
        self.rect.top = max(0, self.rect.top)

        # Caída mortal
        if self.rect.top > map_height + 200:
            self.die()

    def animate(self):
        """Actualiza la animación del jugador."""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.state])
            self.image = self.animations[self.state][self.current_frame]

    def take_damage(self, amount, play_sound=True):
        """Reduce la salud del jugador."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time < self.invulnerability_duration:
            return

        self.health = max(0, self.health - amount)
        if play_sound:
            self.sounds["hurt"].play()
        self.last_damage_time = current_time

        if self.health <= 0:
            self.die()

    def die(self):
        """Inicia la animación de muerte."""
        if not self.dead:
            self.dead = True
            self.death_animation_finished = False
            self.state = "death"
            self.current_frame = 0
            self.animation_timer = 0
            self.death_start_time = pygame.time.get_ticks()
            self.sounds["death"].play()

    def handle_death(self):
        """Maneja la animación de muerte."""
        if self.current_frame < len(self.animations["death"]) - 1:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed * 2:
                self.animation_timer = 0
                self.current_frame += 1
                self.image = self.animations["death"][self.current_frame]
        else:
            self.image = self.animations["death"][-1]
            if pygame.time.get_ticks() - self.death_start_time >= 5000:
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
        self.death_start_time = 0
        self.health = self.max_health
        self.attacking = False
        self.attack_has_hit = False

    def attack(self):
        """Inicia la animación de ataque."""
        if not self.attacking and not self.dead:
            self.attacking = True
            self.attack_has_hit = False
            self.attack_start_time = pygame.time.get_ticks()
            if self.last_direction == "left":
                self.state = "attack_left"
            else:
                self.state = "attack_right"
            self.current_frame = 0
            self.animation_timer = 0
            self.sounds["attack"].play()

    def handle_attack(self, enemy_group):
        """Maneja la animación y el daño del ataque."""
        if not self.attacking:
            return

        # Actualizar animación de ataque
        if self.current_frame < len(self.animations[self.state]) - 1:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame += 1
                self.image = self.animations[self.state][self.current_frame]
        elif pygame.time.get_ticks() - self.attack_start_time >= self.attack_duration:
            self.attacking = False
            self.state = "idle"
            self.current_frame = 0
            self.attack_rect = None
            return

        # Manejar daño del ataque
        if not self.attack_has_hit and self.current_frame >= 2:
            attack_range = 40
            if self.last_direction == "left":
                self.attack_rect = pygame.Rect(
                    self.rect.left - attack_range,
                    self.rect.top,
                    attack_range,
                    self.rect.height
                )
            else:
                self.attack_rect = pygame.Rect(
                    self.rect.right,
                    self.rect.top,
                    attack_range,
                    self.rect.height
                )

            # Verificar colisión con enemigos
            for enemy in enemy_group:
                if self.attack_rect.colliderect(enemy.rect):
                    knockback_dir = -1 if self.last_direction == "left" else 1
                    enemy.take_damage(20, knockback_dir)
                    self.attack_has_hit = True

    def update_energy(self):
        """Actualiza el temporizador de energía especial."""
        if self.has_energy:
            self.energy_timer -= 1 / 60  # Asume 60 FPS
            if self.energy_timer <= 0:
                self.has_energy = False
                self.energy_timer = 0

    # def jump(self):
    # """Método público para hacer saltar al jugador."""
    # if self.on_ground and not self.dead:
    #     self.velocity_y = self.jump_speed
    #     self.on_ground = False
    #     self.sounds["jump"].play()
    #     # Actualizar animación
    #     if self.last_direction == "left":
    #         self.state = "jump_left"
    #     else:
    #         self.state = "jump_right"
    #     self.current_frame = 0