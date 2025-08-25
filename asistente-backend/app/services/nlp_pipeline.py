import re
from typing import Dict, List, Literal, Optional, Tuple

try:
    import spacy
except Exception:
    spacy = None

# -------------------------------
# CARGA PEREZOSA DE spaCy (ES)
# -------------------------------
_nlp = None
def get_nlp():
    global _nlp
    if _nlp is None:
        if spacy is None:
            raise RuntimeError("spaCy no está instalado.")
        try:
            _nlp = spacy.load("es_core_news_md")
        except OSError:
            raise RuntimeError(
                "Modelo 'es_core_news_md' no encontrado. Ejecuta:\n"
                "python -m spacy download es_core_news_md"
            )
    return _nlp


# -------------------------------
# PATRONES / REGLAS
# -------------------------------
# Patrones por sección (palabras completas donde aplica)
PATS_SUBJ = [
    r"\bme duele\b", r"\bdolor\b", r"\bsíntoma", r"\bmolestia",
    r"\brefiere\b", r"\bnota\b", r"\bviene por\b", r"\bdesde hace\b",
    r"\btos\b", r"\bfiebre\b", r"\bcansancio\b", r"\bnáusea", r"\bvómit", r"\bdiarrea",
]
PATS_OBJ = [
    r"\bpresión\b", r"\btensión\b", r"\bauscultación\b",
    r"\bexploración\b", r"\btemperatura\b", r"\banalítica\b",
    r"\bfrecuencia\b", r"\bsaturación\b", r"\bpulso\b",
    r"\bECG\b", r"\bradiografía\b", r"\becografía\b", r"\bRX\b",
    r"\bconstantes\b", r"\bPA\b\b", r"\bSpO2\b",
]
PATS_EVAL = [
    r"\bposible\b", r"\bprobable\b", r"\bsospecha\b", r"\bevaluación\b",
    r"\bdiagnóstico\b", r"\bimpresión\b", r"\bdx\b",
]
PATS_PLAN = [
    r"\bplan\b", r"\btratamiento\b", r"\bseguimiento\b", r"\bcontrol\b",
    r"\bprueba\b", r"\brealizar\b", r"\bindicar\b", r"\brecomendar\b",
    r"\bderivar\b", r"\biniciar\b", r"\bsuspender\b", r"\badministrar\b",
    r"\brevisar\b", r"\bsolicitar\b", r"\bprescribir\b", r"\brecetar\b",
]

Speaker = Literal["medico", "paciente", "desconocido"]

# Prefijos típicos que pueden venir en la transcripción manual o semiautomática
SPEAKER_PREFIXES = {
    "medico": [r"^m[eé]dico:", r"^doctor:", r"^dra?:", r"^dr\.:", r"^facultativo:", r"^profesional:"],
    "paciente": [r"^paciente:", r"^p:", r"^pt[eé]:", r"^enfermo:"],
}

def _detect_speaker(linea: str) -> Tuple[Speaker, str]:
    """
    Detecta hablante por prefijo. Devuelve (speaker, texto_sin_prefijo).
    Si no hay prefijo, devuelve ('desconocido', linea_original).
    """
    original = linea.strip()
    l = original.lower()
    for spk, pats in SPEAKER_PREFIXES.items():
        for pat in pats:
            if re.match(pat, l):
                # quitamos el prefijo detectado
                texto = re.sub(pat, "", l, count=1, flags=re.IGNORECASE).strip()
                # devolvemos el texto original sin prefijo (manteniendo mayúsculas si las había)
                limpio = re.sub(pat, "", original, count=1, flags=re.IGNORECASE).strip()
                return spk, limpio
    return "desconocido", original

def _match_any(patterns: List[str], text: str) -> bool:
    return any(re.search(p, text) for p in patterns)

def _clasifica_frase(frase: str, speaker: Speaker) -> str:
    """
    Clasificación con prioridad y conocimiento de hablante.
    Heurísticas:
      - Si el hablante es 'paciente', Subjetivo pesa más.
      - Si es 'medico', evaluamos Plan/Evaluación/Objetivo antes.
    """
    f = frase.lower()

    # Reglas con prioridad y ponderación por hablante
    if speaker == "medico":
        # El médico suele formular Plan / Evaluación / Objetivo
        if _match_any(PATS_PLAN, f): return "Plan"
        if _match_any(PATS_EVAL, f): return "Evaluación"
        if _match_any(PATS_OBJ, f):  return "Objetivo"
        if _match_any(PATS_SUBJ, f): return "Subjetivo"
        return "Subjetivo"  # por defecto
    elif speaker == "paciente":
        # El paciente suele aportar Subjetivo
        if _match_any(PATS_SUBJ, f): return "Subjetivo"
        # A veces el paciente menciona mediciones/constantes (“tengo 38 de fiebre”)
        if _match_any(PATS_OBJ, f):  return "Objetivo"
        if _match_any(PATS_EVAL, f): return "Evaluación"
        if _match_any(PATS_PLAN, f): return "Plan"
        return "Subjetivo"  # por defecto
    else:
        # Sin speaker: usa prioridad global (Plan > Eval > Obj > Subj)
        if _match_any(PATS_PLAN, f): return "Plan"
        if _match_any(PATS_EVAL, f): return "Evaluación"
        if _match_any(PATS_OBJ, f):  return "Objetivo"
        if _match_any(PATS_SUBJ, f): return "Subjetivo"
        return "Subjetivo"

# --------------------------------------------
# 1) Conversación con prefijos de hablante
# --------------------------------------------
def estructurar_conversacion(texto: str) -> Dict[str, List[str]]:
    """
    Acepta un texto tipo:
      "Paciente: Me duele la barriga desde hace 2 días.
       Médico: Tome asiento. Temperatura 38.2ºC. Sospecha de apendicitis.
       Médico: Plan: solicitar analítica."
    Clasifica cada línea en SOAP, considerando quién habla.
    """
    secciones: Dict[str, List[str]] = {
        "Subjetivo": [], "Objetivo": [], "Evaluación": [], "Plan": []
    }

    # 1) Separar por líneas (turnos). Si una línea es larga, luego spaCy hará sents.
    lineas = [ln for ln in texto.splitlines() if ln.strip()]

    nlp = get_nlp()

    for linea in lineas:
        speaker, contenido = _detect_speaker(linea)
        # Divide el turno en frases con spaCy (p.ej. “Temperatura 38.2ºC. Sospecha…”)
        for sent in nlp(contenido).sents:
            frase = sent.text.strip()
            if not frase:
                continue
            sec = _clasifica_frase(frase, speaker)
            secciones[sec].append(frase)

    return secciones

# --------------------------------------------
# 2) Texto libre (sin prefijos) — compat legacy
# --------------------------------------------
def estructurar_texto(texto: str) -> Dict[str, List[str]]:
    """
    Versión legacy: si NO hay prefijos de hablante en el texto,
    usa la división en oraciones y reglas generales.
    Si detecta claramente prefijos, delega a estructurar_conversacion.
    """
    # ¿Vemos prefijos típicos? Si sí, usa el modo conversación.
    hay_prefijos = any(re.search(p, texto, flags=re.IGNORECASE | re.MULTILINE)
                       for ps in SPEAKER_PREFIXES.values() for p in ps)
    if hay_prefijos:
        return estructurar_conversacion(texto)

    # Modo simple (igual a tu versión anterior pero con funciones auxiliares)
    nlp = get_nlp()
    doc = nlp(texto)
    frases = [sent.text.strip() for sent in doc.sents]

    secciones: Dict[str, List[str]] = {
        "Subjetivo": [], "Objetivo": [], "Evaluación": [], "Plan": []
    }

    for frase in frases:
        sec = _clasifica_frase(frase, speaker="desconocido")
        secciones[sec].append(frase)

    return secciones