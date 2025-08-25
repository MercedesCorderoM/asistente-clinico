import os
import sys
import shutil

FFMPEG_SOURCE = "system"
try:
    # Primero verifica si FFmpeg está en el sistema
    if not shutil.which("ffmpeg"):
        import imageio_ffmpeg
        _ffexe = imageio_ffmpeg.get_ffmpeg_exe()
        os.environ["PATH"] = os.path.dirname(_ffexe) + os.pathsep + os.environ.get("PATH", "")
        FFMPEG_SOURCE = "imageio-ffmpeg"
except Exception:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from.routes import texto_procesado, transcription

app = FastAPI(
    title="Asistente Clínico API- Backend",
    version="0.1.0",
    #docs_url="/docs",
    #redoc_url="/redoc",
)

# CORS: permite el frontend local
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://127.0.0.1",
    
]

#Habilito CORS para que frontend pueda cominicarse con backend
# Esto es necesario para que el frontend pueda hacer peticiones al backend sin problemas de seguridad entre dominios.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/diag")
def diag():
    ffmpeg_path = shutil.which("ffmpeg")
    return {
        "ffmpeg_available": bool(ffmpeg_path),
        "ffmpeg_path": ffmpeg_path or "NOT FOUND",
        "ffmpeg_source": FFMPEG_SOURCE,
        "python_version": sys.version,
        "platform": sys.platform
    }
# Raíz
@app.get("/")
def root():
    return {"ok": True, "service": "asistente-backend", "version": "0.1.0"}

# Healthcheck
@app.get("/api/health")
def health():
    return {"status": "healthy"}


#Incluyo las rutas del procesamiento clínico
app.include_router(transcription.router, prefix="/api", tags=["transcripcion"])
app.include_router(texto_procesado.router, prefix="/api", tags=["procesamiento"])


# Log de inicio
if __name__ == "__main__":
    ffmpeg_check = shutil.which("ffmpeg")
    if ffmpeg_check:
        print(f"✅ FFmpeg detectado: {ffmpeg_check}")
    else:
        print("⚠️ FFmpeg no detectado en PATH")