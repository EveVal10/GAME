import pygame
import os
import random
from boss_projectile import BossProjectile
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="bandit", speed=2, health=50, damage=15,
                 effects_volume=0.5, all_sounds=None):
        super().__init__()
        self.type = enemy_type
        self.speed = speed
        self.health = health
        self.damage = damage
        self.max_health = health 
        self.knockback_resistance = 0.8
        self.last_damage_time = 0 
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
            "hurt":   self.load_frames(os.path.join(base_path, "hurt")),
        }
        
        # Control de animación
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5  # Ajusta la velocidad de cambio de fotogramas

        # Primera imagen (o Surface temporal si falta "idle")
        if self.animations["idle"]:
            self.original_image = self.animations["idle"][0].copy()
        else:
            self.image = pygame.Surface((32, 64))
            self.image.fill((255, 0, 0))
            self.original_image = pygame.Surface((32, 64))
            self.original_image.fill((255, 0, 0))

            
        self.image = self.original_image.copy()
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
            
        # Al final de __init__, después de crear la imagen y el rectángulo:
        self.dead = False
        self.death_animation_finished = False
        self.death_start_time = 0
    

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
        current_time = pygame.time.get_ticks()
    
        # Si el enemigo está muerto, procesamos la animación de muerte y salimos
        if self.dead:
            self.handle_death()
            return
    
        # Si el enemigo está en estado "hurt" y aún no se cumplió el tiempo mínimo (500 ms), 
        # evitamos actualizar la lógica (IA, colisiones, ataques) y solo animamos.
        if self.state == "hurt" and current_time - self.last_damage_time < 500:
            if self.stunned:
                if current_time - self.last_stun_time > self.stun_duration:
                    self.stunned = False
                self.velocity.x *= self.knockback_resistance
            self.animate()
            return
        else:
            # Si el tiempo de "hurt" ya pasó y el estado es "hurt", volvemos a "idle"
            if self.state == "hurt":
                self.set_state("idle")
    
        # Procesar el estado de stun
        if self.stunned:
            if current_time - self.last_stun_time > self.stun_duration:
                self.stunned = False
            self.velocity.x *= self.knockback_resistance
    
        # Si no está aturdido y no en estado de muerte, se ejecuta la lógica normal
        if not self.stunned and self.state != "death":
            self.ai_logic(player)
            self.move_and_collide(collision_rects)
            self.handle_attack(player)
    
        # Se anima siempre (esto actualizará la animación hurt o la normal según corresponda)
        self.animate()
   
    def handle_death(self):
     # Si aún no hemos mostrado todos los frames de la animación de death:
     if self.current_frame < len(self.animations["death"]) - 1:
         self.animation_timer += 1
         if self.animation_timer >= self.animation_speed * 2:  # Puedes ajustar la velocidad
             self.animation_timer = 0
             self.current_frame += 1
             self.image = self.animations["death"][self.current_frame]
     else:
         # Una vez finalizada la animación, mantenemos el último frame
         self.image = self.animations["death"][-1]
         # Y tras una demora (por ejemplo, 3000 ms), eliminamos al enemigo:
         if pygame.time.get_ticks() - self.death_start_time >= 3000:
             self.kill()
    

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
        # Selección de la animación según el estado
        if self.state == "chase":
            frames_list = self.animations.get("run", [])
        else:
            frames_list = self.animations.get(self.state, [])
        
        if not frames_list:
            frames_list = self.animations.get("idle", [])
        
        if not frames_list:
            return
    
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(frames_list)
    
        # Actualiza la imagen base del sprite según el frame actual
        self.original_image = frames_list[self.current_frame].copy()
        if self.direction == -1:
            self.original_image = pygame.transform.flip(self.original_image, True, False)
    
        # Se asigna la imagen base
        self.image = self.original_image.copy()
    
        # Si se ha recibido daño recientemente (menos de 500 ms), se usa la animación "hurt"
        if pygame.time.get_ticks() - self.last_damage_time < 500:
            hurt_frames = self.animations.get("hurt", [])
            if hurt_frames:
                # Aquí se recorre la animación de hurt; si tienes más de 1 frame, puedes ajustar el avance
                hurt_sprite = hurt_frames[self.current_frame % len(hurt_frames)].copy()
                if self.direction == -1:
                    hurt_sprite = pygame.transform.flip(hurt_sprite, True, False)
                self.image = hurt_sprite
            
    def take_damage(self, amount, knockback_direction=0):
        
        if self.dead:
            return  # No recibimos daño si estamos muertos

        
        """Reduce la salud y aplica knockback en una dirección."""
        self.health -= amount
        self.last_damage_time = pygame.time.get_ticks()
        self.state = "hurt"
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
            self.dead = True
            self.current_frame = 0
            self.animation_timer = 0
            self.death_start_time = pygame.time.get_ticks()


class MiniBoss(Enemy):
    def __init__(self, x, y, boss_type="noct", speed=3, health=150, damage=30,
                 effects_volume=0.5, all_sounds=None):
        super().__init__(x, y, boss_type, speed, health, damage, effects_volume, all_sounds)
        
        # Configuración mejorada para el jefe
        self.knockback_resistance = 0.95  # Mayor resistencia
        self.chase_range = 350  # Mayor rango de detección
        self.attack_range = 60  # Mayor alcance de ataque
        self.attack_cooldown = 2000  # 2 segundos entre ataques
        self.last_attack_time = 0
        self.special_attack_damage = 45  # Daño de ataque especial

        self.max_health = health * 2
        self.health = self.max_health
        self.projectiles = pygame.sprite.Group()
        self.ready_to_remove = False
        
        # Cargar sprites especiales
        self.load_special_sprites()
        
        # Sonido especial de ataque
        self.special_attack_sound = pygame.mixer.Sound("assets/audio/effects/attack.mp3")
        self.special_attack_sound.set_volume(effects_volume)
        if all_sounds is not None:
            all_sounds.append(self.special_attack_sound)
        self.velocity = pygame.math.Vector2(random.choice([-3, 3]), random.choice([-3, 3]))
        self.gravity = 0  # No gravedad, porque está volando    

    def load_special_sprites(self):
      """Solo idle con sprites escalados (64x64)"""
      base_path = f"assets/enemies/{self.type}"
      scaled_size = (112, 112)
      
      self.animations = {
          "idle": self.load_frames(os.path.join(base_path, "idle"), scaled_size)
      }

      if self.animations["idle"]:
          self.original_image = self.animations["idle"][0].copy()
          self.image = self.original_image.copy()
          self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
          self.hitbox = self.rect.copy()


    def ai_logic(self, player):
        """Comportamiento mejorado del jefe"""
        super().ai_logic(player)
        
        # 20% de probabilidad de ataque especial cuando está cerca
        if self.state == "chase" and abs(player.rect.centerx - self.rect.centerx) < self.attack_range:
            if pygame.time.get_ticks() - self.last_attack_time > self.attack_cooldown:
                if random.random() < 0.2:
                    self.special_attack(player)

    def special_attack(self, player):
      self.set_state("special_attack")
      self.special_attack_sound.play()

      cx = self.rect.centerx
      cy = self.rect.centery

      # Dispara en 4 direcciones (arriba, abajo, izquierda, derecha)
      directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

      for dx, dy in directions:
          projectile = BossProjectile(cx, cy, dx, dy)
          self.projectiles.add(projectile)

      self.last_attack_time = pygame.time.get_ticks()


    def draw_health_bar(self, surface, camera):
        """Dibuja una barra de salud mejorada"""
        bar_width = 120
        bar_height = 12
        fill = (self.health / self.max_health) * bar_width
        
        # Posición relativa a la cámara
        screen_pos = camera.apply(self.rect)
        background_rect = pygame.Rect(screen_pos.x - 10, screen_pos.y - 25, bar_width, bar_height)
        fill_rect = pygame.Rect(screen_pos.x - 10, screen_pos.y - 25, fill, bar_height)
        
        pygame.draw.rect(surface, (50, 50, 50), background_rect)
        pygame.draw.rect(surface, (200, 30, 30), fill_rect)
        pygame.draw.rect(surface, (100, 100, 100), background_rect, 2)

    def animate(self):
        """Animación mejorada con efectos visuales"""
        super().animate()
        
        # Efecto de enfado al tener poca vida
        if self.health < self.max_health * 0.3 and self.state != "death":
            if "rage" in self.animations and len(self.animations["rage"]) > 0:
                self.current_frame %= len(self.animations["rage"])
                self.image = self.animations["rage"][self.current_frame]
                if self.direction == -1:
                    self.image = pygame.transform.flip(self.image, True, False)
                    
    def move_and_collide(self, collision_rects):
       # Movimiento continuo estilo DVD Logo (sin gravedad)
       self.hitbox.x += self.velocity.x
       self.resolve_collisions(collision_rects, "horizontal")

       self.hitbox.y += self.velocity.y
       self.resolve_collisions(collision_rects, "vertical")

       self.rect.topleft = self.hitbox.topleft
       
    def resolve_collisions(self, collision_rects, direction):
        for rect in collision_rects:
            if not self.hitbox.colliderect(rect):
                continue

            if direction == "horizontal":
                if self.velocity.x > 0:
                    self.hitbox.right = rect.left
                else:
                    self.hitbox.left = rect.right
                self.velocity.x *= -1  # Invierte la dirección X al colisionar

            elif direction == "vertical":
                if self.velocity.y > 0:
                    self.hitbox.bottom = rect.top
                else:
                    self.hitbox.top = rect.bottom
                self.velocity.y *= -1  # Invierte la dirección Y al colisionar
    def ai_logic(self, player):
    # No persigue ni se mueve según jugador, movimiento libre.
        pass
    
    def animate(self):
       """Animación fija usando solo los sprites de idle."""
       frames_list = self.animations.get("idle", [])
       
       if not frames_list:
           # Si no hay sprites, usa cuadro rojo por defecto.
           self.original_image = pygame.Surface((32, 64))
           self.original_image.fill((255, 0, 0))
           self.image = self.original_image.copy()
           return

       self.animation_timer += 1
       if self.animation_timer >= self.animation_speed:
           self.animation_timer = 0
           self.current_frame = (self.current_frame + 1) % len(frames_list)

       self.original_image = frames_list[self.current_frame].copy()
       
       # Gira la imagen según la dirección horizontal (opcional, según movimiento)
       if self.velocity.x < 0:
           self.original_image = pygame.transform.flip(self.original_image, True, False)

       self.image = self.original_image.copy()
       
    def load_frames(self, folder, scale=(64, 64)):
       frames = []
       if not os.path.isdir(folder):
           return frames

       files = [f for f in os.listdir(folder) if f.endswith(".png")]

       def get_frame_number(filename):
           name_part = filename.split('.')[0]
           last_segment = name_part.split('_')[-1]
           return int(last_segment)

       files.sort(key=get_frame_number)

       for filename in files:
           path = os.path.join(folder, filename)
           image = pygame.image.load(path).convert_alpha()
           image = pygame.transform.scale(image, scale)  # <-- Escala aquí
           frames.append(image)

       return frames
    def update(self, collision_rects, player):
      super().update(collision_rects, player)
      
      if self.dead:
        return
      
      # Lanzar proyectiles cada 3 segundos
      current_time = pygame.time.get_ticks()
      if current_time - self.last_attack_time > self.attack_cooldown:
          self.special_attack(player)
     
    def handle_death(self):
     death_anim = self.animations.get("death", [])

     if not death_anim:
         self.death_animation_finished = True
         self.ready_to_remove = True  # Marca para eliminar después
         return

     if self.current_frame < len(death_anim) - 1:
         self.animation_timer += 1
         if self.animation_timer >= self.animation_speed * 2:
             self.animation_timer = 0
             self.current_frame += 1
             self.image = death_anim[self.current_frame]
     else:
         self.image = death_anim[-1]
         if pygame.time.get_ticks() - self.death_start_time >= 3000:
             self.death_animation_finished = True
             self.ready_to_remove = True  # Espera a que main lo quite

                  