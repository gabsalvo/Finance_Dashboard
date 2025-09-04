import sys
import xml.etree.ElementTree as ET
import subprocess
import os

def check_pagata(xml_file):
    """Controlla se nel file XML compaiono 'MP09' o 'MP19'"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    found = []

    for elem in root.iter():
        text = elem.text or ""
        if "MP09" in text or "MP19" in text:
            found.append(text)
        for val in elem.attrib.values():
            if "MP09" in val or "MP19" in val:
                found.append(str(elem.attrib))

    return len(found) > 0, found


def ask_gemma(message, model="gemma:3-4b"):
    """Invia un prompt al modello Gemma tramite Ollama"""
    prompt = f"""
Regola: se nel documento compare la dicitura MP09 o MP19, significa che la fattura è già pagata.
Analizza il contenuto e rispondi di conseguenza.

Contenuto:
{message}
"""
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode("utf-8"),
        capture_output=True
    )
    return result.stdout.decode("utf-8").strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python trova_pagate.py files/NOMEFATTURA.xml")
        sys.exit(1)

    xml_path = sys.argv[1]

    # verifica che il file esista
    if not os.path.exists(xml_path):
        print(f"Errore: file {xml_path} non trovato.")
        sys.exit(1)

    has_mp09, details = check_pagata(xml_path)

    if has_mp09:
        msg = f"Nel file {xml_path} è stata trovata la dicitura MP09 o MP19. Dettagli: {details}"
    else:
        msg = f"Nel file {xml_path} non è stata trovata alcuna dicitura MP09 o MP19."

    response = ask_gemma(msg)
    print("Risposta del modello:\n")
    print(response)
