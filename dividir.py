from PIL import Image
import os

def dividir_sprite(sheet_path, filas, columnas, ancho, alto, salida="frames"):
    # Cargar la imagen del sprite sheet
    sheet = Image.open(sheet_path)

    # Crear la carpeta de salida si no existe
    os.makedirs(salida, exist_ok=True)

    # Extraer cada frame
    for fila in range(filas):
        for col in range(columnas):
            # Calcular la posición del frame en el sprite sheet
            x = col * ancho
            y = fila * alto
            frame = sheet.crop((x, y, x + ancho, y + alto))
            
            # Guardar cada frame como imagen
            frame.save(f"{salida}/frame_{fila}_{col}.png")

    print(f"¡Frames guardados correctamente en {salida}/!")

# Ruta del archivo (Asegúrate de que esté en la misma carpeta o coloca la ruta completa)
sprite_path = "AttackCatbL.png"


# Ajustar según las dimensiones de tu sprite sheet
dividir_sprite(sprite_path, filas=1, columnas=8, ancho=32, alto=32)
