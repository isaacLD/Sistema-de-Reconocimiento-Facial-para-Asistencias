from django.contrib import admin

from .models import Asistencia, Persona, Rostro


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cedula", "curso", "activo", "creado_en")
    search_fields = ("nombre", "cedula")


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ("persona", "fecha", "hora", "estado", "similitud")
    list_filter = ("fecha", "estado")


admin.site.register(Rostro)
