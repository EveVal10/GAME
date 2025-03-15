# tilemap.py actualizado
import pygame
import pytmx

def load_map(tmx_path):
    return pytmx.load_pygame(tmx_path)

def draw_tiled_map(screen, tmx_data, camera_x=0, camera_y=0):
    for layer in tmx_data.visible_layers:
        if hasattr(layer, 'data'):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    world_x = x * tmx_data.tilewidth
                    world_y = y * tmx_data.tileheight

                    screen_x = world_x - camera_x
                    screen_y = world_y - camera_y

                    screen.blit(tile, (screen_x, screen_y))
                    
def get_player_spawn(tmx_data):
    for obj in tmx_data.objects:
        if obj.name == "PlayerSpawn":
            return int(obj.x), int(obj.y)
    return 0, 0

def get_collision_rects(tmx_data):
    collision_rects = []

    # Recorre TODAS las capas del mapa
    for layer in tmx_data.layers:
        # Verifica si esta capa es del tipo 'TiledObjectGroup'
        if isinstance(layer, pytmx.TiledObjectGroup):
            # (Opcional) Solo si el nombre de la capa es "Collisions":
            if layer.name == "Collisions":
                # Recorre cada objeto en esa capa
                for obj in layer:
                    # Crea rectángulos de pygame a partir de la posición y tamaño
                    rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    collision_rects.append(rect)

    return collision_rects

# tilemap.py (continuación)

def get_enemy_spawns(tmx_data):
    enemies = []
    for layer in tmx_data.layers:
        if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "Enemies":
            for obj in layer:
                if obj.type == "enemy":
                    enemies.append({
                        "x": obj.x,
                        "y": obj.y,
                        "type": obj.properties.get("enemy_type", "wolf"),
                        "speed": obj.properties.get("enemy_speed", 2),
                        "health": obj.properties.get("enemy_health", 100)
                    })
    return enemies

def get_consumable_spawns(tmx_data):
    consumables = []
    for layer in tmx_data.layers:
        if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "Consumables":
            for obj in layer:
                if obj.type == "consumable":
                    consumables.append({
                        "x": obj.x,
                        "y": obj.y,
                        "consumable_type": obj.properties.get("consumable_type", "fish"),
                        "health_value": obj.properties.get("health_value", 50),
                        "pickup_sound": obj.properties.get("pickup_sound", None)  # Opcional
                    })
    return consumables

def get_level_end(tmx_data):
    for layer in tmx_data.layers:
        if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "LevelEnd":
            for obj in layer:
                if obj.name == "LevelEnd":
                    return pygame.Rect(obj.x, obj.y, obj.width, obj.height)
    return None
