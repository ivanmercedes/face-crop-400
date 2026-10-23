"""Recorta todas las fotos de una carpeta a 400x400 centradas en la cara.

Uso:
    python3 crop_400.py [carpeta_origen] [carpeta_destino]

Por defecto usa la carpeta actual como origen y ./400x400 como destino.
"""
import os
import sys
import urllib.request

import cv2
import numpy as np
from PIL import Image, ImageOps

CASC_URL = "https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/haarcascade_frontalface_default.xml"
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
DST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(SRC, "400x400")
CASC = os.path.join(HERE, "haarcascade_frontalface_default.xml")
SIZE = 400

# Caras que el detector no resuelve bien: nombre de archivo -> (x, y, ancho, alto)
# en píxeles de la imagen original. Ejemplo:
#   "foto-07.png": (404, 265, 223, 223),
MANUAL = {}

if not os.path.exists(CASC):
    print("Descargando haarcascade_frontalface_default.xml...")
    urllib.request.urlretrieve(CASC_URL, CASC)

os.makedirs(DST, exist_ok=True)
det = cv2.CascadeClassifier(CASC)


def find_face(gray):
    g = cv2.equalizeHist(gray)
    for mn in (6, 4, 3):
        faces = det.detectMultiScale(g, scaleFactor=1.05, minNeighbors=mn, minSize=(40, 40))
        if len(faces):
            return max(faces, key=lambda f: f[2] * f[3])
    return None


def load_rgb(path):
    img = ImageOps.exif_transpose(Image.open(path))
    if img.mode == "RGBA" or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        return bg
    return img.convert("RGB")


def save_crop(img, face, out_path):
    w, h = img.size
    fx, fy, fw, fh = face
    side = min(max(fh * 1.9, fw * 2.2), w, h)
    cx = fx + fw / 2
    left = min(max(cx - side / 2, 0), w - side)
    top = min(max(fy - 0.3 * fh, 0), h - side)
    box = tuple(int(round(v)) for v in (left, top, left + side, top + side))
    img.crop(box).resize((SIZE, SIZE), Image.LANCZOS).save(out_path, quality=92, optimize=True)
    return box


for name in sorted(os.listdir(SRC)):
    path = os.path.join(SRC, name)
    if not os.path.isfile(path) or not name.lower().endswith((".jpg", ".jpeg", ".png")):
        continue
    img = load_rgb(path)
    w, h = img.size
    out_path = os.path.join(DST, os.path.splitext(name)[0] + ".jpg")

    if (w, h) == (SIZE, SIZE):
        img.save(out_path, quality=95)
        print(f"{name}: ya {SIZE}x{SIZE}, sin cambios")
        continue

    if name in MANUAL:
        box = save_crop(img, MANUAL[name], out_path)
        print(f"{name}: cara manual, recorte {box}")
        continue

    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    face = find_face(gray)
    if face is None:
        # sin cara detectada: recorte aproximado en la zona superior
        face = (w * 0.35, h * 0.2, w * 0.3, h * 0.35)
        note = "SIN CARA: recorte aproximado, revisar"
    else:
        note = "ok"
    box = save_crop(img, tuple(map(float, face)), out_path)
    print(f"{name}: {note}, recorte {box}")
