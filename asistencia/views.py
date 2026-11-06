import csv
import time

import cv2
import numpy as np
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import servicios
from .forms import FiltroHistorialForm, PersonaForm
from .models import Asistencia, Persona
from .vision import procesador as vision


# ----------------------------------------------------------------- Panel
def panel(request):
    return render(request, "asistencia/panel.html", {"hora_limite": settings.HORA_LIMITE_ENTRADA})


def api_hoy(request):
    """Datos del día para refrescar el panel sin recargar la página."""
    hoy = timezone.localdate()
    registros = Asistencia.objects.filter(fecha=hoy).select_related("persona").order_by("-hora")
    total = Persona.objects.filter(activo=True).count()
    puntuales = registros.filter(estado=Asistencia.Estado.PUNTUAL).count()
    return JsonResponse({
        "total_personas": total,
        "presentes": registros.count(),
        "puntuales": puntuales,
        "atrasados": registros.count() - puntuales,
        "registros": [
            {
                "nombre": a.persona.nombre,
                "curso": a.persona.curso,
                "hora": a.hora.strftime("%H:%M:%S"),
                "estado": a.get_estado_display(),
                "similitud": round(a.similitud * 100),
            }
            for a in registros
        ],
    })


# ----------------------------------------------------------------- Video
def _imagen_error(mensaje: str) -> bytes:
    """Genera un JPEG con el mensaje de error para mostrarlo dentro del <img>."""
    imagen = np.full((480, 640, 3), 35, dtype=np.uint8)
    cv2.putText(imagen, "No se pudo iniciar la camara", (40, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (80, 80, 255), 2)
    texto = mensaje.encode("ascii", "ignore").decode()[:70]
    cv2.putText(imagen, texto, (40, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)
    return cv2.imencode(".jpg", imagen)[1].tobytes()


def _flujo_mjpeg(procesador):
    while True:
        jpeg = procesador.jpeg()
        if jpeg is not None:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
        time.sleep(0.04)  # ~25 cuadros por segundo


def video(request):
    try:
        procesador = vision.obtener_procesador()
    except Exception as error:
        return HttpResponse(_imagen_error(str(error)), content_type="image/jpeg")
    return StreamingHttpResponse(
        _flujo_mjpeg(procesador), content_type="multipart/x-mixed-replace; boundary=frame"
    )


# ----------------------------------------------------------------- Personas
def registrar(request):
    form = PersonaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            procesador = vision.obtener_procesador()
            vectores = procesador.capturar_muestras(settings.VISION["MUESTRAS_REGISTRO"])
        except Exception as error:
            messages.error(request, f"No se pudo usar la cámara: {error}")
            return render(request, "asistencia/registrar.html", {"form": form})

        if len(vectores) < 3:
            messages.error(request, "No se detectó bien el rostro. Colócate solo frente a la cámara, con buena luz, e intenta de nuevo.")
            return render(request, "asistencia/registrar.html", {"form": form})

        datos = form.cleaned_data
        persona = servicios.registrar_persona(datos["nombre"], datos["cedula"], datos["curso"], vectores)
        procesador.recargar_galeria()
        messages.success(request, f"{persona.nombre} registrado con {len(vectores)} muestras de rostro.")
        return redirect("personas")
    return render(request, "asistencia/registrar.html", {"form": form})


def personas(request):
    lista = Persona.objects.all().prefetch_related("rostros")
    return render(request, "asistencia/personas.html", {"personas": lista})


@require_POST
def eliminar_persona(request, pk):
    persona = get_object_or_404(Persona, pk=pk)
    persona.delete()
    if vision._instancia is not None:  # solo si la cámara ya está en uso
        vision._instancia.recargar_galeria()
    messages.success(request, f"Se eliminó a {persona.nombre}.")
    return redirect("personas")


# ----------------------------------------------------------------- Historial
def historial(request):
    form = FiltroHistorialForm(request.GET or None)
    registros = Asistencia.objects.select_related("persona")
    if form.is_valid():
        if form.cleaned_data["desde"]:
            registros = registros.filter(fecha__gte=form.cleaned_data["desde"])
        if form.cleaned_data["hasta"]:
            registros = registros.filter(fecha__lte=form.cleaned_data["hasta"])
        if form.cleaned_data["persona"]:
            registros = registros.filter(persona=form.cleaned_data["persona"])

    if request.GET.get("formato") == "csv":
        return _exportar_csv(registros)
    return render(request, "asistencia/historial.html", {"form": form, "registros": registros[:500]})


def _exportar_csv(registros):
    respuesta = HttpResponse(content_type="text/csv; charset=utf-8")
    respuesta["Content-Disposition"] = 'attachment; filename="asistencias.csv"'
    respuesta.write("﻿")  # BOM para que Excel muestre bien las tildes
    escritor = csv.writer(respuesta, delimiter=";")
    escritor.writerow(["Fecha", "Hora", "Nombre", "Cédula", "Curso", "Estado", "Similitud %"])
    for a in registros:
        escritor.writerow([
            a.fecha.strftime("%d/%m/%Y"), a.hora.strftime("%H:%M:%S"), a.persona.nombre,
            a.persona.cedula, a.persona.curso, a.get_estado_display(), round(a.similitud * 100),
        ])
    return respuesta
