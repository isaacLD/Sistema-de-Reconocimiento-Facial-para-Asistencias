"""Lectura de la cámara en un hilo aparte para no bloquear al servidor."""
import platform
import threading
import time

import cv2


class Camara:
    def __init__(self, indice: int = 0):
        # En Windows, DirectShow abre la cámara mucho más rápido
        backend = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_ANY
        self.captura = cv2.VideoCapture(indice, backend)
        if not self.captura.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara {indice}")
        self.captura.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.captura.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self._frame = None
        self._lock = threading.Lock()
        self._activa = True
        threading.Thread(target=self._leer, daemon=True).start()

    def _leer(self):
        while self._activa:
            ok, frame = self.captura.read()
            if ok:
                with self._lock:
                    self._frame = cv2.flip(frame, 1)  # efecto espejo
            else:
                time.sleep(0.05)

    def leer(self):
        """Devuelve una copia del último cuadro o None si aún no hay."""
        with self._lock:
            return None if self._frame is None else self._frame.copy()

    def liberar(self):
        self._activa = False
        self.captura.release()
