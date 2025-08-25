'use client';

import { useState, useRef } from 'react';
import { API_URL } from '@/lib/api';
import type { Speaker } from '@/lib/types';

function prefixLine(text: string, speaker: Speaker) {
  const label = speaker === 'medico' ? 'Médico' : 'Paciente';
  const already = new RegExp(`^\\s*(${label}):`, 'i').test(text);
  return already ? text : `${label}: ${text}`;
}
function genSessionId() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

export default function AudioRecorder({
  speaker,
  onPartial,
  onFinal,
  onStateChange,
  debug = true, // ← activa debug por defecto mientras pruebas
}: {
  speaker: Speaker;
  onPartial: (text: string) => void;
  onFinal: (text: string) => void;
  onStateChange?: (rec: boolean) => void;
  debug?: boolean;
}) {
  const [isRecording, setIsRecording] = useState(false);
  const [dbg, setDbg] = useState<string[]>([]);

  const log = (...a: any[]) => {
    if (!debug) return;
    console.log('[AudioRecorder]', ...a);
    setDbg((p) => [...p.slice(-20), a.map(String).join(' ')]);
  };

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const fullChunksRef   = useRef<Blob[]>([]);
  const bufferRef       = useRef<Blob[]>([]);
  const sendingRef      = useRef(false);
  const lastSnippetRef  = useRef('');
  const sessionIdRef    = useRef<string>(genSessionId());

  const MIN_BLOBS_FOR_SEND = 1;

  const sendBuffered = async () => {
    if (sendingRef.current) { log('skip send: already sending'); return; }
    if (bufferRef.current.length < MIN_BLOBS_FOR_SEND) { log('skip send: not enough blobs'); return; }
    sendingRef.current = true;
    try {
      const count = bufferRef.current.length;
      const part = new Blob(bufferRef.current, { type: 'audio/webm' });
      bufferRef.current = [];
      log('sending', count, 'blobs, size=', part.size);

      const fd = new FormData();
      fd.append('file', part, `live-${Date.now()}.webm`);
      fd.append('speaker', speaker);
      fd.append('session_id', sessionIdRef.current);

      const res = await fetch(`${API_URL}/transcribir`, { method: 'POST', body: fd });
      log('resp status', res.status);
      if (!res.ok) {
        const t = await res.text().catch(() => '');
        log('resp not ok:', t);
        return;
      }
      const data = await res.json();
      log('resp json keys=', Object.keys(data || {}));
      const raw = (data?.transcripcion ?? data?.texto ?? '').trim();
      log('transcripcion length=', raw.length);

      if (!raw) return;

      const lines = raw.split(/\r?\n+/).flatMap((l: string) => l.split(/(?<=[\.\?!])\s+/));
      const cleaned = lines.map((s: string) => s.trim()).filter(Boolean);
      const joined = cleaned.join(' ').trim();
      if (!joined) return;

      // para debug, desactiva el filtro de deduplicación:
      // if (joined === lastSnippetRef.current) return;
      lastSnippetRef.current = joined;

      const prefixed = cleaned.map((s: string) => prefixLine(s, speaker)).join('\n');
      onPartial(prefixed);
    } catch (e) {
      log('send error', e);
    } finally {
      sendingRef.current = false;
    }
  };

  const startRecording = async () => {
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        alert('Tu navegador no soporta getUserMedia');
        log('getUserMedia not available');
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      log('mic granted, tracks=', stream.getTracks().length);

      const prefer = 'audio/webm;codecs=opus';
      const fallback = 'audio/webm';
      const mime = (window as any).MediaRecorder?.isTypeSupported?.(prefer) ? prefer : fallback;
      if (!(window as any).MediaRecorder) {
        alert('MediaRecorder no soportado en este navegador');
        log('MediaRecorder missing');
        return;
      }
      log('mime selected=', mime);

      const mr = new MediaRecorder(stream, { mimeType: mime });
      mr.ondataavailable = (ev) => {
        log('ondataavailable size=', ev.data?.size ?? 0);
        if (!ev.data || ev.data.size === 0) return;
        fullChunksRef.current.push(ev.data);
        bufferRef.current.push(ev.data);
        if (bufferRef.current.length >= MIN_BLOBS_FOR_SEND) void sendBuffered();
      };
      mr.onerror = (ev) => log('MediaRecorder error', ev);
      mr.onstop = async () => {
        log('onstop fired');
        try {
          if (bufferRef.current.length > 0) await sendBuffered();

          const finalBlob = new Blob(fullChunksRef.current, { type: 'audio/webm' });
          log('finalBlob size=', finalBlob.size);
          fullChunksRef.current = [];
          lastSnippetRef.current = '';

          const fd = new FormData();
          fd.append('file', finalBlob, 'final.webm');
          fd.append('speaker', speaker);
          fd.append('session_id', sessionIdRef.current);

          const res = await fetch(`${API_URL}/transcribir`, { method: 'POST', body: fd });
          log('final resp status', res.status);
          if (res.ok) {
            const data = await res.json();
            const raw = (data?.transcripcion ?? data?.texto ?? '').trim();
            log('final transcripcion length=', raw.length);
            if (raw) {
              const lines = raw.split(/\r?\n+/).flatMap((l: string) => l.split(/(?<=[\.\?!])\s+/));
              const cleaned = lines.map((s: string) => s.trim()).filter(Boolean);
              const prefixed = cleaned.map((s: string) => prefixLine(s, speaker)).join('\n');
              onFinal(prefixed);
            }
          } else {
            const t = await res.text().catch(() => '');
            log('final not ok body=', t);
          }
        } finally {
          stream.getTracks().forEach((t) => t.stop());
          sessionIdRef.current = genSessionId();
        }
      };

      mediaRecorderRef.current = mr;
      bufferRef.current = [];
      fullChunksRef.current = [];
      lastSnippetRef.current = '';
      mediaRecorderRef.current.start(600);
      setIsRecording(true);
      onStateChange?.(true);
      log('recording started');
    } catch (e) {
      console.error('No se pudo acceder al micrófono', e);
      alert('No se pudo acceder al micrófono. Revisa permisos del navegador.');
      log('getUserMedia error', e);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
    onStateChange?.(false);
    log('recording stopped');
  };

  return (
    <div className="flex items-start gap-3">
      <div className="flex items-center gap-3">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          className={`px-4 py-2 rounded-full text-white ${isRecording ? 'bg-red-600' : 'bg-green-600'}`}
        >
          {isRecording ? 'Detener' : 'Inicia consulta (Grabar)'}
        </button>
        <span className="text-sm">{isRecording ? 'Grabando…' : 'Listo'}</span>
      </div>

      {debug && (
        <div className="ml-4 text-xs max-h-40 overflow-auto border rounded p-2 w-[420px] bg-gray-50">
          <div className="font-semibold mb-1">Debug AudioRecorder</div>
          <ul className="space-y-0.5">
            {dbg.map((l, i) => (<li key={i} className="font-mono">{l}</li>))}
          </ul>
        </div>
      )}
    </div>
  );
}
