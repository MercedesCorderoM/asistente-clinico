from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from.routes import texto_procesado, transcription

app = FastAPI(
    title="Asistente Clínico API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS: permite el frontend local
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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

#Incluyo las rutas del procesamiento clínico
app.include_router(texto_procesado.router, prefix="/api", tags=["procesamiento"])
app.include_router(transcription.router, prefix="/api", tags=["transcripcion"])

# Healthcheck
@app.get("/health")
def health():
    return {"status": "ok"}