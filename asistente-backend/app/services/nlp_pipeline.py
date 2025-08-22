import spacy # Tareas de NLP

nlp = spacy.load("es_core_news_md")  # Carga del modelo de lenguaje en español

def estructurar_texto(texto: str) -> dict: # Se espera un texto en español y devuelve un diccionario con la estructura del texto
    # Aquí se procesa un texto clínico y lo organizamos en formato SOAP:
    # - Subjetivo
    # - Objetivo
    # - Evaluación
    # - Plan
    doc = nlp(texto)
    frases = [sent.text.strip() for sent in doc.sents]
    
    # Diccionario de secciones
    secciones = {
        "Subjetivo": [], # Lo que dice el paciente( síntomas, molestias, antecedentes relatados)
        "Objetivo": [], #Datos observables o medidos por el médico (exploración física, pruebas)
        "Evaluación": [], #Interpretación o hipótesis diagnosticada
        "Plan": [] #Lo que se va a hacer (tratamientos, pruebas, seguimiento)
        
    }
    
    #Clasificamos las frases por palabras clave
    for frase in frases:
        f = frase.lower() # Convertir a minúsculas para facilitar la comparación
        
        #Subjetivo: síntomas/relato del paciente
        if any(x in f for x in ["me duele", "dolor", "síntoma", "nota",
                                "molestia", "desde hace", "viene por"]):
            secciones["Subjetivo"].append(frase)
        
        #Objetivo: datos observables/medicaciones
        elif any(x in f for x in ["presión", "auscultación", "exploración",
                                  "temperatura", "analítica", "frecuencia"]):
            secciones["Objetivo"].append(frase)
        
        #Evaluación: diagnóstico/hipótesis
        elif any(x in f for x in ["posible", "sospecha", "evaluación", "diagnóstico"]):
            secciones["Evaluación"].append(frase)
        
        #Plan: pruebas, tratamiento, seguimiento
        elif any(x in f for x in ["plan", "tratamiento", "seguimiento", "prueba", "realizar"]):
            secciones["Plan"].append(frase)
            continue
        
    return secciones  # Devuelve el diccionario con las secciones organizadas