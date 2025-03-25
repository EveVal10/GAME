import pygame
from tilemap import load_map, get_player_spawn, get_collision_rects, get_enemy_spawns, get_consumable_spawns, get_level_end
from camera import Camera
from enemies import Enemy
from consumable import Consumable
import pytmx


LEVEL_CONFIG = {
    "level1": {
        "map": "assets/tilemaps/level1_1.tmx",
        "music": "assets/audio/game/level1_music.mp3",
        "spawn_dialogue": [
            {"speaker": "Athelia", "text": "¡Cuidado con las sombras!"},
            {"speaker": "Protagonista", "text": "Siento una energía oscura aquí..."}
        ],
        "end_dialogue": [
            {"speaker": "Athelia", "text": "¡El portal al siguiente nivel!"}
        ],
        "next_level": "level2"
    },
    "level2": {
        "map": "assets/tilemaps/level1_2.tmx",
        "music": "assets/audio/game/level2_music.mp3",
        "spawn_dialogue": [
            {"speaker": "Athelia", "text": "Este lugar parece más peligroso..."}
        ],
        "end_dialogue": [
            {"speaker": "Protagonista", "text": "¿Cuántos niveles más faltarán?"}
        ],
        "next_level": "level3"
    }
}

def load_level_data(level_name, player, effects_volume, all_sounds):
    """Carga todos los datos de un nivel incluyendo diálogos"""
    config = LEVEL_CONFIG[level_name]
    tmx_data = load_map(config["map"])
    
    # Añade estas líneas para calcular dimensiones del mapa
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    
    return {
        "tmx_data": tmx_data,
        "camera": Camera(
            map_width,
            map_height,
            640, 480
        ),
        "collision_rects": get_collision_rects(tmx_data),
        "enemies": load_enemies(tmx_data, effects_volume, all_sounds),
        "consumables": load_consumables(tmx_data),
        "level_end_rect": get_level_end(tmx_data),
        "spawn_dialogue": config["spawn_dialogue"],
        "end_dialogue": config["end_dialogue"],
        "npc_dialogues": get_npc_dialogues(tmx_data),
        "music": config["music"],
        "next_level": config["next_level"],
        # Añade estas dos líneas al final
        "map_width": map_width,
        "map_height": map_height,
        "player_spawn": get_player_spawn(tmx_data)
    }



def get_npc_dialogues(tmx_data):
    """Obtiene diálogos de NPCs desde el tilemap"""
    dialogues = []
    for layer in tmx_data.layers:
        if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "NPCs":
            for obj in layer:
                if obj.type == "npc":
                    dialogues.append({
                        "rect": pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                        "lines": obj.properties.get("dialogue", "").split('|'),
                        "speaker": obj.properties.get("speaker", "NPC")
                    })
    return dialogues

def load_enemies(tmx_data, effects_volume, all_sounds):
    """Carga enemigos desde el tilemap"""
    enemies = pygame.sprite.Group()
    for enemy_data in get_enemy_spawns(tmx_data):
        enemies.add(Enemy(
            x=enemy_data["x"],
            y=enemy_data["y"],
            enemy_type=enemy_data["type"],
            speed=enemy_data["speed"],
            health=enemy_data["health"],
            damage=enemy_data["attack"],
            effects_volume=effects_volume,
            all_sounds=all_sounds
        ))
    return enemies

def load_consumables(tmx_data):
    """Carga consumibles desde el tilemap"""
    consumables = pygame.sprite.Group()
    for cons_data in get_consumable_spawns(tmx_data):
        consumables.add(Consumable(
            x=cons_data["x"],
            y=cons_data["y"],
            consumable_type=cons_data["consumable_type"],
            health_value=int(cons_data["health_value"]),
            pickup_sound=cons_data.get("pickup_sound", None)
        ))
    return consumables