# face-crop-400

Script de Python que recorta todas las fotos de una carpeta a **400x400** con la cara centrada. Sirve para fotos de perfil de directorios, equipos o sitios web, cuando cada foto viene con un tamaño y un encuadre distintos.

Usa el detector de caras Haar cascade de OpenCV, así que no hace falta descargar modelos pesados ni usar GPU.

## Qué hace

1. Detecta la cara en cada foto. Si hay varias, se queda con la más grande.
2. Calcula un cuadrado alrededor de la cara que incluye un poco de pelo arriba y los hombros abajo.
3. Recorta y redimensiona a 400x400, y guarda en JPEG.

Además:

- Las fotos que ya son 400x400 se copian sin cambios.
- Respeta la orientación EXIF (fotos de celular).
- Los PNG con transparencia se ponen sobre fondo blanco.
- Si el detector falla en alguna foto, puedes marcar la cara a mano en `MANUAL`.

## Instalación

```bash
pip install -r requirements.txt
```

El archivo `haarcascade_frontalface_default.xml` se descarga solo la primera vez que ejecutas el script.

## Uso

```bash
python3 crop_400.py ruta/a/las/fotos
```

Los resultados se guardan en `ruta/a/las/fotos/400x400/`. También puedes indicar la carpeta de destino:

```bash
python3 crop_400.py ruta/a/las/fotos ruta/de/salida
```

El script imprime una línea por foto. Las que dicen `SIN CARA` usaron un recorte aproximado y conviene revisarlas.

## Cuando el detector falla

El Haar cascade funciona bien con caras frontales, derechas y de buen tamaño. Puede fallar con caras de perfil, inclinadas, muy pequeñas o con sombras fuertes, y a veces confunde otra zona de la foto con una cara.

Para esas fotos, abre la imagen original, mira dónde está la cara y añádela a `MANUAL` en `crop_400.py`:

```python
MANUAL = {
    "foto-07.png": (404, 265, 223, 223),  # x, y, ancho, alto en píxeles originales
}
```

Revisa siempre los resultados: el detector no avisa cuando se equivoca.

## Ajustar el encuadre

En `save_crop()`:

- `fh * 1.9`: tamaño del recorte respecto al alto de la cara. Súbelo para encuadres más abiertos.
- `fy - 0.3 * fh`: espacio por encima de la cara.
- `SIZE`: tamaño final en píxeles.

## Licencia

MIT
