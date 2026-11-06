"""Lógica de negocio que guarda en PostgreSQL (separada de las vistas y de OpenCV)."""
from datetime import datetime, time

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Asistencia, Persona, Rostro


def hora_limite() -> time:
    return datetime.strptime(settings.HORA_LIMITE_ENTRADA, "%H:%M").time()


def calcular_estado(hora: time) -> str:
    return Asistencia.Estado.PUNTUAL if hora <= hora_limite() else Asistencia.Estado.ATRASADO


def registrar_asistencia(persona_id: int, similitud: float, momento=None):
    """Registra la asistencia del día. Si ya existe, no la duplica.

    Devuelve (asistencia, creada).
    """
    momento = momento or timezone.localtime()
    hora = momento.time().replace(microsecond=0)
    return Asistencia.objects.get_or_create(
        persona_id=persona_id,
        fecha=momento.date(),
        defaults={"hora": hora, "estado": calcular_estado(hora), "similitud": round(similitud, 4)},
    )


@transaction.atomic
def registrar_persona(nombre: str, cedula: str, curso: str, vectores) -> Persona:
    """Crea la persona y guarda sus vectores faciales en una sola transacción."""
    if not vectores:
        raise ValueError("Se necesita al menos una muestra de rostro.")
    persona = Persona.objects.create(nombre=nombre, cedula=cedula, curso=curso)
    for vector in vectores:
        rostro = Rostro(persona=persona)
        rostro.set_vector(vector)
        rostro.save()
    return persona


def vectores_registrados():
    """Genera (persona_id, nombre, vector) de todas las personas activas."""
    consulta = Rostro.objects.select_related("persona").filter(persona__activo=True)
    for rostro in consulta:
        yield rostro.persona_id, rostro.persona.nombre, rostro.get_vector()
