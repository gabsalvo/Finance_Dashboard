import xml.etree.ElementTree as ET
from utils.ollama_utils import deduci_importo_ai
import os

def check_importo(xml_file: str):
    """Controlla se nel file XML compaiono 'MP09' o 'MP19' e prepara payload per frontend"""
    if not os.path.exists(xml_file):
        return {
            "status": "error",
            "message": f"File {xml_file} non trovato",
            "file": xml_file,
            "importo": None
        }

    tree = ET.parse(xml_file)
    root = tree.getroot()


    
    importo = 10


    # Payload pensato per il frontend
    return {
        "status": "ok",
        "file": os.path.basename(xml_file),
        "importo": importo
    }
    
