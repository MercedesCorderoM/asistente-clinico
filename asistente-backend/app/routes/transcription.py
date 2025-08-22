#ESTA CLASE PERMITE TRANSCRIBIR AUDIO A TEXTO

from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
import whisper

router = APIRouter()

# Cargamos Whisper, modelo "small" para CPU adaptado a mi ordenador
model = whisper.load_model("small")

@router.post("/transcribir")
async def transcribir_audio(file: UploadFile = File(...)):
    tmp_path = None  # Inicializamos la variable para el path temporal
    try:
        # Sufijo básico; si quieres, ajusta por content_type
        suffix = ".webm"
        if file.filename and file.filename.lower().endswith(".wav"):
            suffix = ".wav"
        elif file.filename and file.filename.lower().endswith(".mp3"):
            suffix = ".mp3"
        elif file.filename and file.filename.lower().endswith(".ogg"):
            suffix = ".ogg"
    
        # Guardamos el archivo temporalmente SIN borrar al cerrar el contexto
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(await file.read()) #Leemos el archivo
            temp.flush()  # Aseguramos que el archivo se escribe en disco
            tmp_path = temp.name 

        # Transcribimos el audio usando Whisper. IMPORTANTE: usa ffmpeg, importante tenerlo instalado
        result = model.transcribe(tmp_path, language="es") #Indico que el idioma que deberá detectar es español
        texto = (result.get("text") or "").strip()  # Eliminamos espacios en blanco al inicio y al final

        return {"transcripcion": texto}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al transcribir el audio: {e}")
    
    finally:
        # Eliminamos el archivo temporal
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)  # Eliminamos el archivo temporal
            except Exception:
                pass
