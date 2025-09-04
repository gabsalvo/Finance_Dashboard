from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from scripts.trova_pagate_api import check_pagata
import tempfile
import os

app = FastAPI(title="Finance Dashboard API")

@app.get("/health", tags=["Health"])
def health():
    return JSONResponse(content={"status": "ok"})

@app.get("/check-fattura", tags=["Fatture"])
def check_fattura(nome_file: str):
    """
    Controlla se una fattura XML contiene MP09 o MP19 (da percorso).
    Esempio: /check-fattura?nome_file=files/IT12878470157_GzFZ4.xml
    """
    base_path = os.path.join(os.path.dirname(__file__), "..", "scripts")
    file_path = os.path.abspath(os.path.join(base_path, nome_file))

    result = check_pagata(file_path)
    return JSONResponse(content=result)

@app.post("/upload-fattura", tags=["Fatture"])
async def upload_fattura(file: UploadFile = File(...)):
    """
    Carica un file XML e controlla se contiene MP09 o MP19.
    """
    # crea file temporaneo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        result = check_pagata(tmp_path)
    finally:
        # elimina il file temporaneo
        os.remove(tmp_path)

    return JSONResponse(content=result)
