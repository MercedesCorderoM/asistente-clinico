from fastapi import APIRouter, UploadFile
import tempfile
import subprocess

router = APIRouter()

@router.post("/transcribir")
async def transcribir(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Llamar a whisper para transcribir
    # Ejemplo con whisper-cli (requiere instalar openai-whisper)
    result = subprocess.run(
        ["whisper", tmp_path, "--model", "small", "--language", "es", "--output_format", "json"],
        capture_output=True,
        text=True
    )

    # Aquí deberías parsear el JSON generado por Whisper
    # y devolver la transcripción como string.
    transcripcion = "Texto transcrito aquí..."

    return {"transcripcion": transcripcion}
