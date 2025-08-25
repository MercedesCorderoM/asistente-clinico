# ESTA CLASE PERMITE PROCESAR DE NLP A FORMATO SOAP

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.nlp_pipeline import estructurar_texto

router = APIRouter()

class TextoEntrada(BaseModel):
    texto: str

@router.post("/procesar")
async def procesar_texto(payload: TextoEntrada):
    resultado = estructurar_texto(payload.texto)
    return resultado
