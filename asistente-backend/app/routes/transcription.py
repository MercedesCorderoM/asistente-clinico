# ESTA CLASE PERMITE TRANSCRIBIR AUDIO A TEXTO

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile
import os
import whisper
import uuid

router = APIRouter()

# Carga del modelo (puedes cambiar por env var WHISPER_MODEL)
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "small")
try:
    model = whisper.load_model(WHISPER_MODEL_NAME)
except Exception:
    model = whisper.load_model("base")

@router.post("/transcribir")
async def transcribir_audio(
    file: UploadFile = File(...),
    speaker: str | None = Form(None),
    session_id: str | None = Form(None),
):
    """
    Recibe audio (webm/opus preferente, acepta wav/mp3/ogg), guarda temporal y devuelve
    la transcripción en español. 'speaker' y 'session_id' se aceptan para mejorar UX.
    """
    tmp_path = None
    try:
        suffix = ".webm"
        if file.filename:
            lname = file.filename.lower()
            if lname.endswith(".wav"): suffix = ".wav"
            elif lname.endswith(".mp3"): suffix = ".mp3"
            elif lname.endswith(".ogg"): suffix = ".ogg"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Archivo de audio vacío.")
            temp.write(content)
            temp.flush()
            tmp_path = temp.name

        # Requiere ffmpeg instalado en el sistema
        result = model.transcribe(tmp_path, task="transcribe", language="es")
        texto = (result.get("text") or "").strip()

        _speaker = (speaker or "desconocido")[:16]
        _session = (session_id or str(uuid.uuid4()))[:36]

        return {"transcripcion": texto, "speaker": _speaker, "session_id": _session}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al transcribir el audio: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass