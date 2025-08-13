'use client'
import { useState } from 'react' // 'use client' permite guardar el estado en el cliente
import { API_URL } from '@/lib/api' // Importa la URL base de la API

export default function Page(){
    const [texto, setTexto] = useState('')
    const [resultado, setResultado] = useState<any>(null)

    const procesarTexto = async () => {
        const res = await fetch(`${API_URL}/procesar`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ texto }),
        })
        const data = await res.json()
        setResultado(data)
    }
return (
    <main className="p-6 space-y-4">
      <AudioRecorder onTranscription={(t) => setTexto(t)} />

      <textarea
        className="w-full p-2 border rounded"
        rows={6}
        placeholder="Introduce texto clínico o graba audio..."
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
      />

      <button
        onClick={procesarTexto}
        className="bg-green-600 text-white px-4 py-2 rounded"
      >
        Procesar informe
      </button>

      {resultado && (
        <div className="mt-4 space-y-3">
          {Object.entries(resultado).map(([key, frases]) => (
            <div key={key}>
              <h2 className="text-xl font-semibold">{key}</h2>
              <ul className="list-disc ml-5 text-gray-700">
                {(frases as string[]).map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </main>
    )
}