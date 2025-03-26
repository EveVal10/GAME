import pygame
import pytmx
import game_state  # <- Asegúrate de importar esto para acceder a player_name
from mini_boss import MiniBoss

# Importa tu clase NPC
from npc import NPC

from tilemap import (
    load_map,
    get_player_spawn,
    get_collision_rects,
    get_enemy_spawns,
    get_consumable_spawns,
    get_level_end
)
from camera import Camera
from enemies import Enemy
from consumable import Consumable

# ---------------------------
# FUNCIONES DE DIÁLOGO DINÁMICO
# ---------------------------


def parse_dialogue(dialogue_list):
    """Reemplaza 'Protagonista' por el nombre real y sustituye {player} por su nombre."""
    result = []
    for item in dialogue_list:
        speaker = item["speaker"]
        text = item["text"]

        if speaker == "Protagonista":
            speaker = game_state.player_name
        text = text.replace("{player}", game_state.player_name)

        result.append({"speaker": speaker, "text": text})
    return result

# ---------------------------
# CONFIGURACIÓN DE NIVELES
# ---------------------------


LEVEL_CONFIG = {
    "level1": {
        "map": "assets/tilemaps/level1_1.tmx",
        "music": "assets/audio/game/level1_music.mp3",
        "spawn_dialogue": [],
        "end_dialogue": [
            {"speaker": "Athelia",
                "text": "¿Te sientes bien? Esa caída... no fue precisamente suave."},
            {"speaker": "Athelia",
                "text": "Si necesitas descansar o que revise tu Marca, solo dímelo, ¿sí?"},
            {"speaker": "Athelia", "text": "No sabía que había tantos bandidos en esta zona... ¡qué desagradable sorpresa!"},
            {"speaker": "Athelia",
                "text": "Aunque… ver cómo los enfrentaste fue bastante impresionante... jijijiji."}
        ],
        "next_level": "level2"
    },
    "level2": {
        "map": "assets/tilemaps/level1_2.tmx",
        "music": "assets/audio/game/level2_music.mp3",
        "spawn_dialogue": [
            {"speaker": "Protagonista",
                "text": "Ugh... quería quedarme un poco más tirado en el suelo."},
            {"speaker": "Athelia",
                "text": "Descansar es bueno, pero quedarnos quietos no nos llevará a la verdad."},
            {"speaker": "Athelia",
                "text": "Vamos. Ya es hora de seguir el camino, ¿no crees?"}
        ],
        "end_dialogue": [
            {"speaker": "Protagonista",
                "text": "Esos gatos de huesos... me dieron escalofríos."},
            {"speaker": "Athelia",
                "text": "Son llamados Nekrath. Espíritus sin rumbo... y sin piedad."},
            {"speaker": "Protagonista", "text": "Genial. Justo lo que necesitaba."}
        ],
        "next_level": "level3"
    },
    "level3": {
        "map": "assets/tilemaps/level1_3.tmx",
        "music": "assets/audio/game/level3_music.mp3",
        "spawn_dialogue": [
            {"speaker": "Athelia", "text": "Falta poco para llegar a Ludoria."},
            {"speaker": "Athelia", "text": "Ándale, payaso dormilón... no te quedes atrás."}
        ],
        "end_dialogue": [
            {"speaker": "Athelia", "text": "Ludoria... al fin."},
            {"speaker": "Athelia",
                "text": "Aunque siendo sincera... no sé si este lugar traerá las respuestas que buscas."}
        ],
        "next_level": "level4"
    },
    "level4": {
        "map": "assets/tilemaps/level1_4.tmx",
        "music": "assets/audio/game/level3_music.mp3",
        "spawn_dialogue": [
            {"speaker": "Athelia",
                "text": "Uf... ya revisamos demasiado papeleo antiguo por hoy."},
            {"speaker": "Athelia", "text": "Tal vez hablar con la gobernadora Lysverion nos aclare un poco las cosas... o al menos nos libere de tanto polvo."}
        ],
        "end_dialogue": [
            {"speaker": "Narrador", "text": "La Ciudad de la Música y el Cristal se abre ante ellos, vibrante, viva, en perfecta armonía."},
            {"speaker": "Guardia",
             "text": "Ahí es donde reside Lysverion, la Dama de Ludoria."},
            {"speaker": "Guardia", "text": "Dicen que en ese domo habita la voz de un dios, y que la música cristalina es su ofrenda."},
            {"speaker": "Narrador", "text": "{player} siente un leve hormigueo en su Marca Elemental... recuerdos dormidos comienzan a despertar."},
            {"speaker": "Protagonista",
             "text": "¿Escuchaste eso, Athelia? Algo no está bien. ¿Y si Lysverion está en peligro?"},
            {"speaker": "Athelia",
             "text": "Lo pensé desde que el guardia dudó en sus palabras..."},
            {"speaker": "Athelia", "text": "No podemos quedarnos cruzados de patas. Si ella guarda un secreto, debemos descubrirlo."}
        ],
        "next_level": "level5"
    },
    "level5": {
        "map": "assets/tilemaps/level1_5.tmx",
        "music": "assets/audio/game/level3_music.mp3",
        "spawn_dialogue": [
            {"speaker": "Protagonista",
             "text": "Oye, Athelia, ¿cómo es que llegamos a un cementerio?"},
            {"speaker": "Athelia", "text": "No estoy segura... este lugar solía ser un campo sagrado, pero ahora parece abandonado."},
            {"speaker": "Athelia",
             "text": "Algo aquí no se siente bien. Como si la energía estuviera... distorsionada."},
            {"speaker": "Protagonista",
             "text": "Tal vez encontremos algo útil, pero mantengamos los ojos abiertos por si acaso."},
            {"speaker": "Athelia", "text": "De acuerdo, vamos con cuidado. Este lugar guarda secretos, y no todos son agradables."}
        ],
        "end_dialogue": [
            {"speaker": "Protagonista",
             "text": "Esa estatua... no se parece a nada que haya visto antes."},
            {"speaker": "Athelia",
             "text": "Es un símbolo antiguo. Algo relacionado con los Guardianes del Alba."},
            {"speaker": "Protagonista",
             "text": "Entonces, este cementerio... ¿podría ser su lugar de descanso final?"},
            {"speaker": "Athelia",
             "text": "Quizás. Pero algo me dice que no todos aquí están realmente descansando."}
        ],
        "next_level": "level6"
    },


}

# ---------------------------
# FUNCIÓN PRINCIPAL PARA CARGAR NIVELES
# ---------------------------


def load_level_data(level_name, player, effects_volume, all_sounds):
    """Carga todos los datos de un nivel incluyendo NPCs, enemigos y consumibles."""
    config = LEVEL_CONFIG[level_name]
    tmx_data = load_map(config["map"])

    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight

    npcs = load_npcs(tmx_data)

    return {
        "tmx_data": tmx_data,
        "camera": Camera(map_width, map_height, 640, 480),
        "collision_rects": get_collision_rects(tmx_data),
        "enemies": load_enemies(tmx_data, effects_volume, all_sounds),
        "consumables": load_consumables(tmx_data),
        "npcs": npcs,
        "level_end_rect": get_level_end(tmx_data),
        "spawn_dialogue": parse_dialogue(config["spawn_dialogue"]),
        "end_dialogue": parse_dialogue(config["end_dialogue"]),
        "music": config["music"],
        "next_level": config["next_level"],
        "map_width": map_width,
        "map_height": map_height,
        "player_spawn": get_player_spawn(tmx_data)
    }

# ---------------------------
# FUNCIONES DE CARGA ADICIONALES
# ---------------------------


def load_npcs(tmx_data):
    npcs = pygame.sprite.Group()

    for layer in tmx_data.layers:
        if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "NPCs":
            for obj in layer:
                if obj.type == "npc":
                    dialogue_blocks = []
                    for i in range(1, 6):
                        key = f"dialogue{i}"
                        if key in obj.properties:
                            dialogue_blocks.append(obj.properties[key])

                    if not dialogue_blocks:
                        single_dialogue = obj.properties.get("dialogue", "")
                        if single_dialogue:
                            dialogue_blocks.append(single_dialogue)

                    npc_obj = NPC(
                        x=obj.x,
                        y=obj.y,
                        width=obj.width,
                        height=obj.height,
                        npc_type=obj.properties.get("npc_type", "villager"),
                        speaker=obj.properties.get("speaker", "NPC"),
                        dialogue_blocks=dialogue_blocks
                    )
                    npcs.add(npc_obj)
    return npcs


def load_enemies(tmx_data, effects_volume, all_sounds):
    enemies = pygame.sprite.Group()
    for enemy_data in get_enemy_spawns(tmx_data):  # Obtener enemigos del mapa
        # Si el tipo de enemigo es "noct", creamos un MiniBoss
        if enemy_data["type"] == "noct":
            mini_boss = MiniBoss(
                x=enemy_data["x"],
                y=enemy_data["y"],
                boss_type=enemy_data["type"],
                speed=enemy_data["speed"],
                health=enemy_data["health"],
                damage=enemy_data["attack"],
               
               
            )
            enemies.add(mini_boss)  # Agregar el mini boss al grupo de enemigos
        else:
            # Para otros tipos de enemigos, usa la clase Enemy
            enemy = Enemy(
                x=enemy_data["x"],
                y=enemy_data["y"],
                enemy_type=enemy_data["type"],
                speed=enemy_data["speed"],
                health=enemy_data["health"],
                damage=enemy_data["attack"],
                effects_volume=effects_volume,
                all_sounds=all_sounds
            )
            enemies.add(enemy)  # Agregar el enemigo al grupo de enemigos
    return enemies



def load_consumables(tmx_data):
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
