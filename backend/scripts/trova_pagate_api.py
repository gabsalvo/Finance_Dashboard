import xml.etree.ElementTree as ET
import os

def check_pagata(xml_file: str):
    """Controlla se nel file XML compaiono 'MP09' o 'MP19'"""
    if not os.path.exists(xml_file):
        return {"error": f"File {xml_file} non trovato"}

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

    return {
        "file": xml_file,
        "pagata": len(found) > 0,
        "dettagli": found
    }
