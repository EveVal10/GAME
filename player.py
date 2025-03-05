import pygame
import os
import time  # Importamos time para manejar la espera

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
            "death": self.load_frames("assets/cat_m/death", scale_factor=1)
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

    def load_frames(self, folder, scale_factor=1):
        """Carga las imágenes de animación desde la carpeta dada."""
        frames = []
        for filename in sorted(os.listdir(folder)):
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

    def update(self, collision_rects, enemy_group):
        """Lógica principal del jugador."""
        if self.dead:
            self.handle_death()
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

        # Verificar colisión con enemigos
        if pygame.sprite.spritecollideany(self, enemy_group):
            self.die()

        # Aplicar movimiento horizontal
        self.rect.x += self.velocity_x
        self.handle_collisions(collision_rects, "horizontal")

        # Actualizar animación
        self.animate()

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

    def die(self):
        """Mata al jugador y activa la animación de muerte."""
        self.dead = True
        self.state = "death"
        self.current_frame = 0  # Reiniciar la animación de muerte
        self.death_start_time = None  # Reiniciar el tiempo de espera antes de reaparecer

    def handle_death(self):
        """Maneja la animación de muerte y mantiene el último frame durante 5 segundos."""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed * 2:  # Hacer la animación de muerte más lenta
            self.animation_timer = 0

            # Si la animación aún no ha terminado, avanzar de frame
            if self.current_frame < len(self.animations["death"]) - 1:
                self.current_frame += 1
            else:
                # Si la animación terminó, guardar el tiempo de inicio de espera
                if self.death_start_time is None:
                    self.death_start_time = time.time()

                # Mantener el último frame de la animación
                self.image = self.animations["death"][-1]

                # Esperar 5 segundos antes de reaparecer
                if time.time() - self.death_start_time >= 5:
                    self.respawn()  # Revivir después de 5 segundos

        # Si la animación aún no ha terminado, actualizar el frame normalmente
        else:
            self.image = self.animations["death"][self.current_frame]

    def respawn(self):
        """Reaparece al jugador en la posición inicial."""
        self.rect.topleft = self.start_pos
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.dead = False
        self.state = "idle"
        self.current_frame = 0
        self.death_start_time = None  # Reiniciar el temporizador de muerte
