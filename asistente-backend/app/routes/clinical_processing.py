from fastapi import APIRouter
from pydantic import BaseModel
from app.services.nlp_pipeline import estructurar_texto

# Defino el router para las rutas de procesamiento clínico
router = APIRouter()

class TextoEntrada(BaseModel):
    texto: str

@router.post("/procesar_texto")
def procesar_texto(data: TextoEntrada):
    resultado = estructurar_texto(data.texto)
    return resultado