"""Galería en memoria con los vectores faciales registrados.

Comparar contra una matriz en memoria es mucho más rápido que consultar
la base de datos en cada cuadro del video.
"""
import threading
from dataclasses import dataclass

import numpy as np

from .motor import normalizar


@dataclass
class Coincidencia:
    persona_id: int
    nombre: str
    similitud: float


class Galeria:
    def __init__(self, umbral: float):
        self.umbral = umbral
        self._lock = threading.Lock()
        self._matriz = np.empty((0, 128), dtype=np.float32)
        self._ids: list[int] = []
        self._nombres: list[str] = []

    def cargar(self, registros):
        """registros: iterable de (persona_id, nombre, vector)."""
        ids, nombres, vectores = [], [], []
        for persona_id, nombre, vector in registros:
            ids.append(persona_id)
            nombres.append(nombre)
            vectores.append(normalizar(np.asarray(vector, dtype=np.float32)))
        with self._lock:
            self._ids, self._nombres = ids, nombres
            self._matriz = np.vstack(vectores) if vectores else np.empty((0, 128), dtype=np.float32)

    def identificar(self, vector: np.ndarray) -> Coincidencia | None:
        """Busca el vector más parecido; devuelve None si no supera el umbral."""
        with self._lock:
            if not self._ids:
                return None
            similitudes = self._matriz @ normalizar(vector)
            mejor = int(np.argmax(similitudes))
            valor = float(similitudes[mejor])
            if valor < self.umbral:
                return None
            return Coincidencia(self._ids[mejor], self._nombres[mejor], valor)

    def __len__(self):
        return len(set(self._ids))
