from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from.routes import clinical_processing

app = FastAPI()

#Habilito CORS para que frontend pueda cominicarse con backend
# Esto es necesario para que el frontend pueda hacer peticiones al backend sin problemas de seguridad entre dominios.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Incluyo las rutas del procesamiento clínico
app.include_router(clinical_processing.router)