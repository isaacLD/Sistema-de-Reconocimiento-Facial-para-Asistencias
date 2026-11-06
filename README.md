# Asistencia Facial – Django + OpenCV + PostgreSQL

Aplicativo web que registra la asistencia reconociendo rostros en tiempo real con la cámara.

**Asignatura:** Construcción de Software – UNEMI
**Integrantes:** _(completar)_

## Funcionalidades

- **Video en vivo** desde la cámara del computador, transmitido al navegador (MJPEG).
- **Detección de rostros** con `cv2.FaceDetectorYN` (modelo YuNet), incluyendo 5 puntos faciales.
- **Reconocimiento facial** con `cv2.FaceRecognizerSF` (modelo SFace): cada rostro se convierte en un vector de 128 valores y se compara por similitud coseno.
- **Procesamiento de imagen:** mejora de iluminación con CLAHE antes de detectar y alineación del rostro antes de reconocer.
- **Registro automático de asistencia** en PostgreSQL: una vez por persona y por día, solo después de reconocerla en varios cuadros seguidos (evita falsos positivos).
- **Puntual / Atrasado** según la hora límite configurable.
- **Panel** con indicadores (presentes, puntuales, atrasados, ausentes) que se actualiza solo.
- **Registro de personas** desde la cámara (toma 5 muestras del rostro).
- **Historial** con filtros por fecha y persona, y **exportación a CSV/Excel**.

## Tecnologías

| Componente | Herramienta |
|---|---|
| Backend | Python 3.10+ · Django 5.2 |
| Visión artificial | OpenCV (`cv2`) – YuNet + SFace |
| Base de datos | PostgreSQL 16+ (local) |

## Instalación

### 1. PostgreSQL local

1. Descarga el instalador desde <https://www.postgresql.org/download/> e instálalo (incluye pgAdmin). Anota la contraseña del usuario `postgres`.
2. Crea la base de datos (en pgAdmin → Query Tool, o con `psql -U postgres`):

   ```sql
   CREATE DATABASE asistencia_facial;
   ```

### 2. Proyecto

```bash
git clone <URL-del-repositorio>
cd asistencia_facial

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
python descargar_modelos.py    # descarga los modelos de OpenCV a /modelos
```

Copia `.env.example` como `.env` y coloca tu contraseña de PostgreSQL en `DB_PASSWORD`.

```bash
python manage.py makemigrations asistencia
python manage.py migrate
python manage.py createsuperuser   # opcional, para /admin
python manage.py runserver
```

Abre <http://127.0.0.1:8000>.

## Uso

1. **Personas → Registrar persona:** llena los datos, presiona el botón y mira a la cámara unos segundos.
2. **Panel:** cuando la persona aparece frente a la cámara, su recuadro pasa de amarillo (confirmando) a verde y la asistencia se guarda.
3. **Historial:** filtra y exporta los registros.

## Pruebas

```bash
python manage.py test
```

Incluye pruebas del reconocimiento (comparación de vectores), cálculo de puntual/atrasado, no duplicación de asistencias, validación de formularios y respuesta de las páginas.

## Estructura

```
asistencia_facial/
├── config/                 # Configuración de Django
├── asistencia/
│   ├── vision/
│   │   ├── motor.py        # Detección, reconocimiento y procesamiento (OpenCV)
│   │   ├── galeria.py      # Comparación de vectores en memoria
│   │   ├── camara.py       # Lectura de la cámara en un hilo
│   │   └── procesador.py   # Une cámara + OpenCV + BD y genera el video anotado
│   ├── servicios.py        # Lógica que guarda en PostgreSQL
│   ├── models.py           # Persona, Rostro, Asistencia
│   ├── views.py · urls.py · forms.py
│   ├── templates/ · static/
│   └── tests.py
├── modelos/                # Modelos ONNX (no se suben a Git)
├── descargar_modelos.py
├── requirements.txt
└── .env.example
```

## Configuración (`.env`)

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `CAMARA_INDICE` | Cámara a usar (0 = integrada) | `0` |
| `UMBRAL_SIMILITUD` | Similitud mínima para reconocer (más alto = más estricto) | `0.40` |
| `CUADROS_CONFIRMACION` | Cuadros seguidos antes de marcar asistencia | `5` |
| `HORA_LIMITE_ENTRADA` | Después de esta hora se marca "Atrasado" | `08:15` |

## Privacidad

Los vectores faciales son datos biométricos. Solo se guardan vectores numéricos (no fotos) y se debe contar con el consentimiento de las personas registradas.
