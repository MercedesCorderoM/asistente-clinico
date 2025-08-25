'use client';

import { useState } from 'react';
import { API_URL } from '@/lib/api';
import type { SoapSections, ProcesarRequest, Speaker } from '@/lib/types';
import AudioRecorder from '@/components/AudioRecorder';

function sectionsToText(secs: SoapSections) {
  const order: Array<keyof SoapSections> = ['Subjetivo', 'Objetivo', 'Evaluación', 'Plan'];
  return order
    .map((k) => `## ${k}\n${secs[k].length ? secs[k].map((s) => `- ${s}`).join('\n') : 'Sin contenido'}`)
    .join('\n\n');
}

export default function Page() {
  const [speaker, setSpeaker] = useState<Speaker>('paciente');
  const [isRecording, setIsRecording] = useState(false);

  const [texto, setTexto] = useState('');                // conversación acumulada
  const [resultado, setResultado] = useState<SoapSections | null>(null);
  const [loading, setLoading] = useState(false);
  const [errMsg, setErrMsg] = useState<string | null>(null);

  const append = (t: string) => setTexto((prev) => (prev ? prev + '\n' + t : t));

  const procesarTexto = async () => {
    if (!texto.trim()) return;
    setLoading(true);
    setErrMsg(null);
    setResultado(null);
    try {
      const res = await fetch(`${API_URL}/procesar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto } as ProcesarRequest),
      });
      if (!res.ok) {
        const msg = await res.text().catch(() => '');
        throw new Error(`Error ${res.status}${msg ? `: ${msg}` : ''}`);
      }
      const data = (await res.json()) as SoapSections;
      setResultado(data);
    } catch (e: any) {
      setErrMsg(e?.message ?? 'Error al procesar el texto');
    } finally {
      setLoading(false);
    }
  };

  const copy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      alert('Copiado al portapapeles');
    } catch {
      alert('No se pudo copiar. Revisa permisos del navegador.');
    }
  };

  return (
    <main className="mx-auto max-w-5xl p-6 space-y-6">
      <h1 className="text-3xl font-bold">Asistente clínico</h1>

      {/* 1) Inicia consulta */}
      <section className="rounded-lg border p-4 space-y-3 bg-white">
        <h2 className="text-xl font-semibold">1) Inicia consulta</h2>
        <div className="flex items-center gap-3">
          <label className="text-sm">Hablante:</label>
          <select
            disabled={isRecording}
            value={speaker}
            onChange={(e) => setSpeaker(e.target.value as Speaker)}
            className="border rounded-md px-2 py-1"
          >
            <option value="paciente">Paciente</option>
            <option value="medico">Médico</option>
          </select>

          <AudioRecorder
            speaker={speaker}
            onPartial={append}
            onFinal={append}
            onStateChange={setIsRecording}
          />
        </div>
        <p className="text-sm text-gray-600">
          Selecciona quién habla, pulsa <b>Inicia consulta</b> para grabar una intervención y vuelve a pulsar para detener.
        </p>
      </section>

      {/* 2) Transcripción en tiempo real + Generar informe */}
      <section className="rounded-lg border p-4 space-y-3 bg-white">
        <h2 className="text-xl font-semibold">2) Transcripción</h2>
        <textarea
          className="w-full p-3 border rounded-md focus:outline-none focus:ring"
          rows={12}
          placeholder={`La conversación aparecerá aquí.\n\nEjemplo:\nPaciente: Me duele la espalda desde hace dos días.\nMédico: Exploración: dolor a la palpación lumbar.\nMédico: Sospecha lumbalgia mecánica.\nMédico: Plan: AINE, reposo relativo y revisión.`}
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
        />
        <div className="flex items-center gap-3">
          <button
            onClick={procesarTexto}
            disabled={loading || !texto.trim()}
            className="bg-blue-600 disabled:bg-blue-300 text-white px-4 py-2 rounded-md"
          >
            {loading ? 'Generando…' : 'Generar informe'}
          </button>
          {errMsg && <span className="text-sm text-red-600">{errMsg}</span>}
        </div>
      </section>

      {/* 3) Informe y acciones */}
      {resultado && (
        <section className="rounded-lg border p-4 space-y-4 bg-white">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">3) Informe (SOAP)</h2>
            <div className="flex gap-2">
              <button
                className="px-3 py-1 rounded-md border"
                onClick={() => copy(sectionsToText(resultado))}
              >
                Copiar todo
              </button>
              {/* Copiar por sección */}
              <button
                className="px-3 py-1 rounded-md border"
                onClick={() => copy(resultado.Subjetivo.join('\n'))}
              >
                Copiar Subjetivo
              </button>
              <button
                className="px-3 py-1 rounded-md border"
                onClick={() => copy(resultado.Objetivo.join('\n'))}
              >
                Copiar Objetivo
              </button>
              <button
                className="px-3 py-1 rounded-md border"
                onClick={() => copy(resultado.Evaluación.join('\n'))}
              >
                Copiar Evaluación
              </button>
              <button
                className="px-3 py-1 rounded-md border"
                onClick={() => copy(resultado.Plan.join('\n'))}
              >
                Copiar Plan
              </button>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {Object.entries(resultado).map(([sec, frases]) => (
              <article key={sec} className="rounded-lg border p-4">
                <h3 className="text-lg font-semibold mb-2">{sec}</h3>
                {frases.length === 0 ? (
                  <p className="text-sm text-gray-500">Sin contenido</p>
                ) : (
                  <ul className="list-disc ml-5 space-y-1 text-gray-800">
                    {frases.map((f: string, i: number) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                )}
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
