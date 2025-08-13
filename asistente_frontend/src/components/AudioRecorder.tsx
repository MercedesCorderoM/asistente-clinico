'use client'
import { useState } from 'react' // 'use client' permite guardar el estado en el cliente
import { API_URL } from '@/lib/api' // Importa la URL base de la API

export default function AudioRecorder({ onTranscription }: { onTranscription: (text: string) => void }) {
  const [isRecording, setIsRecording] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        audioChunksRef.current = []

        const formData = new FormData()
        formData.append('file', audioBlob, 'recording.webm')

        const res = await fetch(`${API_URL}/transcribir`, {
          method: 'POST',
          body: formData
        })

        const data = await res.json()
        if (data?.transcripcion) {
          onTranscription(data.transcripcion)
        }
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
    } catch (err) {
      console.error("No se pudo acceder al micrófono", err)
    }
  }

  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
    setIsRecording(false)
  }

  const handleRecordClick = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  return (
    <div className="flex flex-col items-center">
      <button
        onClick={handleRecordClick}
        className={`px-4 py-2 rounded-full text-white ${isRecording ? 'bg-red-500' : 'bg-blue-500'}`}
      >
        {isRecording ? 'Detener Grabación' : 'Iniciar Grabación'}
      </button>
    </div>
  )
}