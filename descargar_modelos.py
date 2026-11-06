"""Descarga los modelos ONNX oficiales de OpenCV Zoo a la carpeta modelos/.

Uso: python descargar_modelos.py
"""
import urllib.request
from pathlib import Path

CARPETA = Path(__file__).resolve().parent / "modelos"
BASE = "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models"
MODELOS = {
    "face_detection_yunet_2023mar.onnx": f"{BASE}/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx": f"{BASE}/face_recognition_sface/face_recognition_sface_2021dec.onnx",
}


def main():
    CARPETA.mkdir(exist_ok=True)
    for nombre, url in MODELOS.items():
        destino = CARPETA / nombre
        if destino.exists() and destino.stat().st_size > 100_000:
            print(f"✔ {nombre} ya existe")
            continue
        print(f"Descargando {nombre}...")
        urllib.request.urlretrieve(url, destino)
        if destino.stat().st_size < 100_000:
            destino.unlink()
            raise SystemExit(f"La descarga de {nombre} falló. Descárgalo manualmente desde:\n{url}")
        print(f"✔ {nombre} ({destino.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
