import pygame

def show_intro_scenes(screen):
    """
    Muestra una secuencia de escenas introductorias.
    Cada escena es un diccionario con:
      - "image": ruta a la imagen.
      - "dialogue": texto que se muestra en la parte inferior.
      - "duration": tiempo en milisegundos que se muestra la escena.
         (Si duration es None, se espera a que se presione una tecla para avanzar.)
    """
    scenes = [
        {
            "image": "assets//intro//scene1.jpeg",
            "dialogue": "Hace mucho tiempo, en un mundo olvidado...",
            "duration": 4000  # milisegundos (4 segundos)
        },
        {
            "image": "assets/intro/scene2.png",
            "dialogue": "Los héroes se levantaron para enfrentar la oscuridad.",
            "duration": 4000
        },
        {
            "image": "assets/intro/scene3.png",
            "dialogue": "Pero el destino es incierto...",
            "duration": None  # Espera a que el usuario presione una tecla para avanzar
        }
    ]
    
    font = pygame.font.Font(None, 28)  # Fuente por defecto, tamaño 28
    clock = pygame.time.Clock()
    
    for scene in scenes:
        try:
            image = pygame.image.load(scene["image"]).convert()
        except Exception as e:
            print("Error al cargar la imagen:", scene["image"])
            continue
        
        # Escalar la imagen para que ocupe toda la pantalla
        image = pygame.transform.scale(image, screen.get_size())
        
        start_time = pygame.time.get_ticks()
        waiting = True
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                # Si no se especifica duración, se espera a una tecla para avanzar
                if scene["duration"] is None and event.type == pygame.KEYDOWN:
                    waiting = False
            
            # Si se especifica duración, avanzar cuando se supere el tiempo
            if scene["duration"] is not None:
                if pygame.time.get_ticks() - start_time >= scene["duration"]:
                    waiting = False

            # Dibujar la imagen de la escena
            screen.blit(image, (0, 0))
            
            # Renderizar el diálogo en la parte inferior
            dialogue_text = scene["dialogue"]
            text_surface = font.render(dialogue_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - 30)
            )
            # Dibujar un fondo semitransparente para el texto
            dialogue_bg = pygame.Surface((text_rect.width + 20, text_rect.height + 10))
            dialogue_bg.set_alpha(150)
            dialogue_bg.fill((0, 0, 0))
            dialogue_bg_rect = dialogue_bg.get_rect(center=text_rect.center)
            screen.blit(dialogue_bg, dialogue_bg_rect)
            screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            clock.tick(60)
    
    return True
