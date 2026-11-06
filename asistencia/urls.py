from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel, name="panel"),
    path("video/", views.video, name="video"),
    path("api/hoy/", views.api_hoy, name="api_hoy"),
    path("personas/", views.personas, name="personas"),
    path("personas/registrar/", views.registrar, name="registrar"),
    path("personas/<int:pk>/eliminar/", views.eliminar_persona, name="eliminar_persona"),
    path("historial/", views.historial, name="historial"),
]
