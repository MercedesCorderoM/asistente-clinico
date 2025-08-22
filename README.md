# 🧠 Asistente Clínico (TFM)

Asistente digital clínico que:
- Graba la consulta médica (audio).
- Transcribe automáticamente a texto (Whisper).
- Estructura la información en formato **SOAP** (Subjetivo, Objetivo, Evaluación, Plan).
- Ofrece soporte preliminar al diagnóstico.

---

## 📂 Estructura del proyecto
ASISTENTE-CLINICO/
├─ asistente_frontend/ # Next.js (React + Tailwind + ShadCN UI)
│ ├─ src/...
│ └─ package.json
│
├─ asistente-backend/ # FastAPI (Python, Whisper, spaCy)
│ ├─ app/...
│ └─ requirements.txt
│
├─ README.md # Este archivo
└─ .gitignore


---

## ⚙️ Requisitos previos

- **Node.js** ≥ 18
- **Python** 3.10 – 3.12 (recomendado)
- **FFmpeg** instalado en el sistema  
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`  
  - macOS: `brew install ffmpeg`  
  - Windows: `choco install ffmpeg`

---

## 🚀 Instalación y ejecución

### Backend (FastAPI)

```bash
cd asistente-backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu

uvicorn app.main:app --reload --port 8000

PARA EL FRONTEND
 cd asistente_frontend
 npm install
 Crear archivo .env.local: NEXT_PUBLIC_API_URL=http://localhost:8000
 Ejecutar en desarrollo: npm run dev
 --> Frontend en: http://localhost:3000


🔄 Flujo de uso

1. Iniciar backend (FastAPI).
2 Iniciar frontend (Next.js).
3. En el navegador:
   - Pulsar Iniciar grabación para grabar audio y transcribirlo.
   - Editar/agregar texto en el área de texto.
   - Pulsar Procesar informe para estructurar en formato SOAP.

📦 Dependencias principales

Frontend: Next.js, React, Tailwind, ShadCN UI.

Backend: FastAPI, Whisper (openai-whisper), spaCy (es_core_news_md), PyTorch (CPU).

🔐 Privacidad

- Los audios se procesan localmente (no se guardan por defecto).
- Cumplimiento con RGPD: anonimizar datos y evitar persistencia salvo consentimiento expreso.