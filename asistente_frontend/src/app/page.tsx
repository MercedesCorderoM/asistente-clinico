'use client';

import { useState } from 'react';
import { API_URL } from '@/lib/api';
import type { SoapSections, ProcesarRequest } from '@/lib/types';

export default function Page() {
  const [texto, setTexto] = useState('');
  const [resultado, setResultado] = useState<SoapSections | null>(null);
  const [loading, setLoading] = useState(false);
  const [errMsg, setErrMsg] = useState<string | null>(null);

  const procesarTexto = async () => {
    setLoading(true); setErrMsg(null); setResultado(null);
    try {
      const res = await fetch(`${API_URL}/procesar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto } as ProcesarRequest),
      });
      if (!res.ok) throw new Error(`Error ${res.status}: ${await res.text()}`);
      const data = (await res.json()) as SoapSections;
      setResultado(data);
    } catch (e: any) {
      setErrMsg(e?.message ?? 'Error al procesar el texto');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-3xl p-6 space-y-4">
      <h1 className="text-2xl font-bold">Asistente clínico</h1>

      <textarea
        className="w-full p-3 border rounded-md focus:outline-none focus:ring"
        rows={6}
        placeholder="Escribe o pega un texto clínico..."
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
      />

      <div className="flex items-center gap-3">
        <button
          onClick={procesarTexto}
          disabled={loading || !texto.trim()}
          className="bg-blue-600 disabled:bg-blue-300 text-white px-4 py-2 rounded-md"
        >
          {loading ? 'Procesando…' : 'Procesar informe'}
        </button>
        {errMsg && <span className="text-sm text-red-600">{errMsg}</span>}
      </div>

      {resultado && (
        <section className="mt-4 grid gap-4 sm:grid-cols-2">
          {Object.entries(resultado).map(([sec, frases]) => (
            <article key={sec} className="rounded-lg border p-4">
              <h2 className="text-lg font-semibold mb-2">{sec}</h2>
              {frases.length === 0 ? (
                <p className="text-sm text-gray-500">Sin contenido</p>
              ) : (
                <ul className="list-disc ml-5 space-y-1 text-gray-800">
                  {frases.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              )}
            </article>
          ))}
        </section>
      )}
    </main>
  );
}
