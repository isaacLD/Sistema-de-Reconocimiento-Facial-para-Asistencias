import numpy as np
from django.db import models


class Persona(models.Model):
    nombre = models.CharField(max_length=120)
    cedula = models.CharField(max_length=13, unique=True)
    curso = models.CharField(max_length=80, blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.cedula})"


class Rostro(models.Model):
    """Vector facial (128 valores) generado por OpenCV FaceRecognizerSF."""

    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="rostros")
    vector = models.BinaryField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def set_vector(self, vector: np.ndarray):
        self.vector = np.asarray(vector, dtype=np.float32).tobytes()

    def get_vector(self) -> np.ndarray:
        return np.frombuffer(bytes(self.vector), dtype=np.float32)


class Asistencia(models.Model):
    class Estado(models.TextChoices):
        PUNTUAL = "PUNTUAL", "Puntual"
        ATRASADO = "ATRASADO", "Atrasado"

    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="asistencias")
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=10, choices=Estado.choices)
    similitud = models.FloatField(help_text="Similitud coseno del reconocimiento (0 a 1)")

    class Meta:
        ordering = ["-fecha", "-hora"]
        constraints = [
            # Una sola asistencia por persona y por día
            models.UniqueConstraint(fields=["persona", "fecha"], name="una_asistencia_por_dia"),
        ]

    def __str__(self):
        return f"{self.persona.nombre} - {self.fecha} {self.hora:%H:%M}"
