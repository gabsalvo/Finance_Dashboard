import xml.etree.ElementTree as ET
import os

def check_date_fornitore(xml_file: str):
    """Controlla il fornitore e la data di emissione da un file XML di fattura"""
    if not os.path.exists(xml_file):
        return {
            "status": "error",
            "message": f"File {xml_file} non trovato",
            "file": xml_file,
            "data_emissione": None,
            "fornitore": None
        }

    tree = ET.parse(xml_file)
    root = tree.getroot()

    data = None
    fornitore = None

    # Cerca <Anagrafica>
    for anagrafica in root.iter():
        if anagrafica.tag.lower().endswith("anagrafica"):
            denominazione_trovata = False
            for child in anagrafica:
                tag_name = child.tag.lower()
                valore = (child.text or "").strip()

                if not valore:
                    continue

                if tag_name.endswith("denominazione"):
                    denominazione_trovata = True
                    if "FORTUNY" not in valore.upper():
                        fornitore = valore
                else:
                    # Se non c'è denominazione, prendiamo altri valori (se non contengono Fortuny)
                    if not denominazione_trovata and "FORTUNY" not in valore.upper():
                        # Se ci sono più valori concatenali
                        if fornitore:
                            fornitore += " " + valore
                        else:
                            fornitore = valore

    # Cerca <Data> → la prima trovata
    for elem in root.iter():
        if elem.tag.lower().endswith("data"):
            if elem.text and elem.text.strip():
                data = elem.text.strip()
                break

    # Payload pensato per il frontend
    return {
        "status": "ok",
        "file": os.path.basename(xml_file),
        "data_emissione": data,
        "fornitore": fornitore
    }
