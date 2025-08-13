import spacy # Tareas de NLP

nlp = spacy.load("es_core_news_md")  # Carga del modelo de lenguaje en español

def estructurar_texto(texto: str) -> dict: # Se espera un texto en español y devuelve un diccionario con la estructura del texto
    doc = nlp(texto)
    frases = [sent.text.stip() for sent in doc.sents]
    
    secciones = {
        "Subjetivo": [], # Lo que dice el paciente( síntomas, molestias, antecedentes relatados)
        "Objetivo": [], #Datos observables o medidos por el médico (exploración física, pruebas)
        "Evaluación": [], #Interpretación o hipótesis diagnosticada
        "Plan": [] #Lo que se va a hacer (tratamientos, pruebas, seguimiento)
        
    }
    
    for frase in frases:
        f = frase.lower() # Convertir a minúsculas para facilitar la comparación
        if any(x in f for x in ["me duele", "dolor", "síntoma", "nota", "viene por"]):
            secciones["Subjetivo"].append(frase)
        elif any(x in f for x in ["presión", "auscultación", "exploración", "freciencia"]):
            secciones["Objetivo"].append(frase)
        elif any(x in f for x in ["posible", "sospecha", "evaluación", "diagnóstico"]):
            secciones["Evaluación"].append(frase)
        elif any(x in f for x in ["plan", "tratamiento", "seguimiento", "prueba", "realizar"]):
            secciones["Plan"].append(frase)
            
    