import xml.etree.ElementTree as ET
import os

def check_date(xml_file: str):
    """Controlla se nel file XML compaiono i tag DataScadenzaPagamento e prepara payload per frontend"""
    if not os.path.exists(xml_file):
        return {
            "status": "error",
            "message": f"File {xml_file} non trovato",
            "file": xml_file,
            "data_scadenza": None,
        }

    tree = ET.parse(xml_file)
    root = tree.getroot()

    data = None
    found = False
    for elem in root.iter():
        if elem.tag.lower().endswith("datascadenzapagamento".lower()):
            found = True
            if elem.text and elem.text.strip():
                data = elem.text.strip()
            else:
                data = "Da verificare"

    # se non abbiamo trovato nessun tag
    if not found:
        data = "Da verificare"



    # Payload pensato per il frontend
    return {
        "status": "ok",
        "file": os.path.basename(xml_file),
        "data_scadenza": data
    }
