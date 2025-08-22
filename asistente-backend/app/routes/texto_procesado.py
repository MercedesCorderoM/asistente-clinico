#ESTA CLASE PERMITE PROCESAR DE NLP A FORMATO SOAP

from fastapi import APIRouter
from pydantic import BaseModel # BaseModel p
from app.services.nlp_pipeline import estructurar_texto # Importo la función de procesamiento de texto

router = APIRouter()

#Modelo de entrada -> lo que recibimos del frontend
class TextoEntrada(BaseModel):
    texto: str
    
@router.post("/procesar")
async def procesar_texto(payload: TextoEntrada):
    #Endpoint que recibe un texto clínico, lo pasa por el pipeline NLP y devuelve un informe estructurado en formato SOAP"
    resultado = estructurar_texto(payload.texto)  # Procesamos el texto usando la función definida
    return resultado  # Devuelve el resultado del procesamiento