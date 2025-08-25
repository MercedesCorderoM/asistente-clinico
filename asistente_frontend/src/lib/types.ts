// Hablantes posibles en la conversación
export type Speaker = 'medico' | 'paciente';

// Estructura del informe clínico en formato SOAP
export interface SoapSections {
  Subjetivo: string[];
  Objetivo: string[];
  Evaluación: string[];
  Plan: string[];
}

// Payload que enviamos al backend para procesar texto
export interface ProcesarRequest {
  texto: string;
}