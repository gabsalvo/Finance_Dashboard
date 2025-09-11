from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from scripts.check_pagata_api import check_pagata
from scripts.check_importo_api import check_importo
import tempfile
import os

app = FastAPI(title="Finance Dashboard API")

@app.get("/health", tags=["Health"])
def health():
    return JSONResponse(content={"status": "ok"})

@app.post("/check_pagata", tags=["Fatture"])
async def check_pagata_fastapi(file: UploadFile = File(...)):
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

@app.post("/check_importo", tags=["Fatture"])
async def check_importo_fastapi(file: UploadFile = File(...)):
    """
    Carica un file XML e controlla con agente AI l'importo da pagare.
    """
    # crea file temporaneo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        result = check_importo(tmp_path)
    finally:
        # elimina il file temporaneo
        os.remove(tmp_path)

    return JSONResponse(content=result)
