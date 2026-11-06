"""Configuración del proyecto Asistencia Facial."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "cambia-esta-clave-en-el-archivo-env")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "asistencia",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Base de datos: PostgreSQL local ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "asistencia_facial"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-ec"
TIME_ZONE = "America/Guayaquil"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Configuración de visión artificial (OpenCV) ---
VISION = {
    # Carpeta con los modelos ONNX (se descargan con: python descargar_modelos.py)
    "MODELO_DETECTOR": BASE_DIR / "modelos" / "face_detection_yunet_2023mar.onnx",
    "MODELO_RECONOCEDOR": BASE_DIR / "modelos" / "face_recognition_sface_2021dec.onnx",
    # Índice de la cámara (0 = cámara integrada)
    "CAMARA_INDICE": int(os.getenv("CAMARA_INDICE", "0")),
    # Similitud coseno mínima para aceptar a una persona (valor sugerido por OpenCV: 0.363)
    "UMBRAL_SIMILITUD": float(os.getenv("UMBRAL_SIMILITUD", "0.40")),
    # Cuadros consecutivos en que debe reconocerse a alguien antes de marcar asistencia
    "CUADROS_CONFIRMACION": int(os.getenv("CUADROS_CONFIRMACION", "5")),
    # Muestras de rostro que se guardan al registrar una persona
    "MUESTRAS_REGISTRO": 5,
}

# Hora límite de entrada: después de esta hora se marca "Atrasado"
HORA_LIMITE_ENTRADA = os.getenv("HORA_LIMITE_ENTRADA", "08:15")
