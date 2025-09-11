import xml.etree.ElementTree as ET
import os

def check_pagata(xml_file: str):
    """Controlla se nel file XML compaiono 'MP09' o 'MP19' e prepara payload per frontend"""
    if not os.path.exists(xml_file):
        return {
            "status": "error",
            "message": f"File {xml_file} non trovato",
            "file": xml_file,
            "pagata": False,
            "dettagli": []
        }

    tree = ET.parse(xml_file)
    root = tree.getroot()
    found = []

    for elem in root.iter():
        text = elem.text or ""
        if "MP09" in text or "MP19" in text:
            found.append(text.strip())
        for val in elem.attrib.values():
            if "MP09" in val or "MP19" in val:
                found.append(str(elem.attrib))

    pagata = len(found) > 0

    # Payload pensato per il frontend
    return {
        "status": "ok",
        "file": os.path.basename(xml_file),
        "pagata": pagata,
        "label": "Pagata" if pagata else "Non pagata",
        "color": "green" if pagata else "red",  # utile per badge frontend
        "dettagli": found
    }
