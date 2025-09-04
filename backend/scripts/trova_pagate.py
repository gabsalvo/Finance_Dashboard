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

def ask_gemma(message, model="gemma3:4b"):
    """Invia un prompt a Gemma tramite Ollama (funziona su Windows e Linux)"""
    prompt = f"""
Regola: se nel documento compare la dicitura MP09 o MP19,
significa che la fattura è già pagata.
Analizza il contenuto e rispondi di conseguenza.

Contenuto:
{message}
"""

    process = subprocess.Popen(
        ["ollama", "run", model],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate(input=prompt)

    if stderr:
        print("⚠️ Errore Ollama:", stderr.strip())

    return stdout.strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python trova_pagate.py files/NOMEFATTURA.xml")
        sys.exit(1)

    xml_path = sys.argv[1]

    if not os.path.exists(xml_path):
        print(f"Errore: file {xml_path} non trovato.")
        sys.exit(1)

    has_mp, details = check_pagata(xml_path)

    if has_mp:
        msg = f"Nel file {xml_path} è stata trovata la dicitura MP09/MP19. Dettagli: {details}"
    else:
        msg = f"Nel file {xml_path} non è stata trovata alcuna dicitura MP09 o MP19."

    response = ask_gemma(msg)
    print("\n📢 Risposta del modello:\n")
    print(response)
