from PIL import Image
import os

def dividir_sprite_centro(sheet_path, filas, columnas,
                          ancho_original, alto_original,
                          ancho_recorte, alto_recorte,
                          salida="frames"):
    # Abrimos la hoja de sprites
    sheet = Image.open(sheet_path)

    # Creamos la carpeta de salida si no existe
    os.makedirs(salida, exist_ok=True)

    for fila in range(filas):
        for col in range(columnas):
            # Coordenadas del fotograma completo en la hoja
            x = col * ancho_original
            y = fila * alto_original

            # Recorte sin necesidad de offsets ya que cada frame tiene el mismo tamaño
            recorte_left   = x
            recorte_top    = y
            recorte_right  = recorte_left + ancho_recorte
            recorte_bottom = recorte_top + alto_recorte

            # Recortamos el fotograma
            frame = sheet.crop((recorte_left, recorte_top, recorte_right, recorte_bottom))

            # Guardamos el recorte
            frame.save(f"{salida}/frame_{fila}_{col}.png")

    print(f"¡Frames guardados correctamente en '{salida}/'!")

# Usar la función:
# - filas=1 y columnas=15 si tienes una sola fila de 15 frames
# - ancho_original=224 y alto_original=240 para cada celda de la hoja
# - ancho_recorte=224 y alto_recorte=240 para recortar todo el frame

sprite_path = "Agis.png"  # Asegúrate de poner la ruta correcta de la imagen
dividir_sprite_centro(
    sheet_path=sprite_path,
    filas=1,               # Una sola fila
    columnas=15,           # 15 frames
    ancho_original=224,
    alto_original=240,
    ancho_recorte=224,
    alto_recorte=240,
    salida="frames_224x240"
)
