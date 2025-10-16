from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from scripts.check_pagata_api import check_pagata
from scripts.check_importo_api import check_importo
from scripts.check_date_api import check_date
from scripts.check_data_fornitore_api import check_date_fornitore
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import UploadFile, File


import tempfile
import os
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from zoneinfo import ZoneInfo


# --- NEW: persistence & scheduler ---
from sqlmodel import SQLModel, Field, create_engine, Session, select
from apscheduler.schedulers.asyncio import AsyncIOScheduler

FILES_DIR = Path("./files")
FILES_DIR.mkdir(exist_ok=True)

TZ = ZoneInfo("Europe/Amsterdam")

app = FastAPI(title="Finance Dashboard API")

# ---------- NEW: DB models ----------
class Invoice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    due_date: date
    supplier: Optional[str] = None
    paid: bool = False
    notified_5d: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(TZ))
    # NEW
    source: str = "invoice_xml"     # "receipt_upload" per le ricevute
    file_path: Optional[str] = None # dove salviamo il file caricato

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    kind: str  # e.g., "due_soon"
    message: str
    invoice_id: Optional[int] = None
    due_date: Optional[date] = None
    days_left: Optional[int] = None
    read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(TZ))

engine = create_engine("sqlite:///./finance.db", echo=False)

# ---------- NEW: WebSocket manager ----------
class WSManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, payload: Dict[str, Any]):
        # Send to all; drop broken sockets quietly
        dead = []
        for ws in self.connections:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

ws_manager = WSManager()

# ---------- NEW: helpers ----------
def parse_due_date(payload: Dict[str, Any]) -> date:
    """
    Conforms to check_date(xml_file) output:
      payload = { status, file, data_scadenza }
    - Accepts ISO (YYYY-MM-DD), DD/MM/YYYY, YYYYMMDD.
    - Treats "Da verificare" (or empty) as missing.
    """
    raw = (payload or {}).get("data_scadenza")
    if not raw:
        raise ValueError("Missing 'data_scadenza'")
    s = str(raw).strip()
    if s.lower() == "da verificare":
        raise ValueError("Unparseable 'data_scadenza': Da verificare")

    # Try ISO first
    try:
        return date.fromisoformat(s)
    except Exception:
        pass

    # Try other common formats
    for fmt in ("%d/%m/%Y", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue

    raise ValueError(f"Unrecognised 'data_scadenza' format: {s}")


def parse_supplier(payload: Dict[str, Any]) -> Optional[str]:
    # Best-effort extraction; adapt to your `check_date_fornitore` if desired
    for key in ("supplier", "fornitore", "denominazioneFornitore", "vendor"):
        if key in payload and payload[key]:
            return str(payload[key])
    return None

async def create_due_soon_notification(sess: Session, inv: Invoice, days_left: int):
    msg = f"Fattura '{inv.filename}' in scadenza il {inv.due_date} (tra {days_left} giorni)."
    n = Notification(
        kind="due_soon",
        message=msg,
        invoice_id=inv.id,
        due_date=inv.due_date,
        days_left=days_left,
    )
    sess.add(n)
    inv.notified_5d = True
    sess.commit()
    sess.refresh(n)
    await ws_manager.broadcast({"type": "due_soon", "notification": {
        "id": n.id, "message": n.message, "invoice_id": inv.id,
        "due_date": str(inv.due_date), "days_left": days_left, "created_at": n.created_at.isoformat()
    }})

# ---------- NEW: scheduler ----------
scheduler = AsyncIOScheduler(timezone="Europe/Amsterdam")

async def scan_due_soon_job():
    today = datetime.now(TZ).date()
    with Session(engine) as sess:
        # 5 giorni
        target_5 = today + timedelta(days=5)
        q5 = select(Invoice).where(
            Invoice.due_date == target_5,
            Invoice.paid == False,
            Invoice.notified_5d == False
        )
        for inv in sess.exec(q5).all():
            await create_due_soon_notification(sess, inv, 5)

        # OGGI in scadenza (days_left=0) → notifica dedicata
        q_today = select(Invoice).where(
            Invoice.due_date == today,
            Invoice.paid == False
        )
        for inv in sess.exec(q_today).all():
            n = Notification(
                kind="due_today",
                message=f"Fattura '{inv.filename}' **in scadenza oggi** ({inv.due_date}).",
                invoice_id=inv.id,
                due_date=inv.due_date,
                days_left=0,
            )
            sess.add(n)
            sess.commit()
            sess.refresh(n)
            await ws_manager.broadcast({"type": "due_today", "notification": {
                "id": n.id, "message": n.message, "invoice_id": inv.id,
                "due_date": str(inv.due_date), "days_left": 0, "created_at": n.created_at.isoformat()
            }})

        # SCADUTE (days_left<0) → notifica “overdue” (solo una volta al giorno)
        q_over = select(Invoice).where(
            Invoice.due_date < today,
            Invoice.paid == False
        )
        for inv in sess.exec(q_over).all():
            n = Notification(
                kind="overdue",
                message=f"Fattura '{inv.filename}' **scaduta** il {inv.due_date}.",
                invoice_id=inv.id,
                due_date=inv.due_date,
                days_left=(inv.due_date - today).days,
            )
            sess.add(n)
            sess.commit()
            sess.refresh(n)
            await ws_manager.broadcast({"type": "overdue", "notification": {
                "id": n.id, "message": n.message, "invoice_id": inv.id,
                "due_date": str(inv.due_date), "days_left": (inv.due_date - today).days,
                "created_at": n.created_at.isoformat()
            }})

def ensure_schema():
     with engine.connect() as conn:
        cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info('invoice')").fetchall()]
        if "source" not in cols:
            conn.exec_driver_sql("ALTER TABLE invoice ADD COLUMN source VARCHAR NOT NULL DEFAULT 'invoice_xml';")
        if "file_path" not in cols:
            conn.exec_driver_sql("ALTER TABLE invoice ADD COLUMN file_path VARCHAR;")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    ensure_schema()
    SQLModel.metadata.create_all(engine)
    scheduler.add_job(scan_due_soon_job, "cron", hour=9, minute=0, id="scan_due_soon", replace_existing=True)
    scheduler.start()
    try:
        yield
    finally:
        # SHUTDOWN
        scheduler.shutdown(wait=False)

app = FastAPI(title="Finance Dashboard API", lifespan=lifespan)
# ---------- NEW: WebSocket endpoint ----------
@app.websocket("/ws/notifications")
async def ws_notifications(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            # We don't expect messages from client; keep alive by receiving
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)

# ---------- NEW: notifications REST ----------
@app.get("/notifications", tags=["Notifications"])
def list_notifications(limit: int = 50, unread_only: bool = False):
    with Session(engine) as sess:
        q = select(Notification).order_by(Notification.created_at.desc())
        notifs = sess.exec(q).all()
        if unread_only:
            notifs = [n for n in notifs if not n.read]
        out = [{
            "id": n.id,
            "kind": n.kind,
            "message": n.message,
            "invoice_id": n.invoice_id,
            "due_date": str(n.due_date) if n.due_date else None,
            "days_left": n.days_left,
            "read": n.read,
            "created_at": n.created_at.isoformat(),
        } for n in notifs[:limit]]
        return JSONResponse(content={"notifications": out})

@app.post("/notifications/{notif_id}/read", tags=["Notifications"])
def mark_notification_read(notif_id: int):
    with Session(engine) as sess:
        n = sess.get(Notification, notif_id)
        if not n:
            raise HTTPException(status_code=404, detail="Notification not found")
        n.read = True
        sess.add(n)
        sess.commit()
        return {"ok": True}

@app.post("/invoices/{invoice_id}/paid", tags=["Fatture"])
def mark_invoice_paid(invoice_id: int):
    with Session(engine) as sess:
        inv = sess.get(Invoice, invoice_id)
        if not inv:
            raise HTTPException(status_code=404, detail="Invoice not found")
        inv.paid = True
        sess.add(inv)
        sess.commit()
        return {"ok": True}

# ---------- Existing endpoints (unchanged signatures) ----------

@app.get("/health", tags=["Health"])
def health():
    return JSONResponse(content={"status": "ok"})

@app.post("/check_pagata", tags=["Fatture"])
async def check_pagata_fastapi(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
    try:
        result = check_pagata(tmp_path)
    finally:
        os.remove(tmp_path)
    return JSONResponse(content=result)

@app.post("/check_importo", tags=["Fatture"])
async def check_importo_fastapi(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
    try:
        result = check_importo(tmp_path)
    finally:
        os.remove(tmp_path)
    return JSONResponse(content=result)

@app.post("/check_data_scadenza", tags=["Fatture"])
async def check_data_fastapi(file: UploadFile = File(...)):
    """
    Pass-through for frontend (status, file, data_scadenza), PLUS backend info:
      {
        ... passthrough ...,
        "data_scadenza_iso": "YYYY-MM-DD" | null,
        "backend": {
          "stored_invoice": {id, filename, due_date, supplier, days_left} | null,
          "notification_sent": bool,
          "note": "...optional..."
        }
      }
    If 'data_scadenza' = "Da verificare" or unparseable, we do NOT store an invoice.
    """
    # 1) Run your checker and keep its payload intact for the frontend
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
    try:
        tool_result = check_date(tmp_path)  # <-- your function (unchanged)
    finally:
        os.remove(tmp_path)

    # 2) Try to normalise and persist if possible
    stored_invoice = None
    notification_sent = False
    due_iso = None
    note = None

    try:
        due = parse_due_date(tool_result)      # uses data_scadenza
        due_iso = due.isoformat()
        today = datetime.now(TZ).date()
        days_left = (due - today).days

        # Supplier unknown here; leave None (or integrate check_date_fornitore later)
        with Session(engine) as sess:
            inv = Invoice(
                filename=file.filename or tool_result.get("file") or "invoice.xml",
                due_date=due,
                supplier=None
            )
            sess.add(inv)
            sess.commit()
            sess.refresh(inv)

            # Immediate notify if 0..5 days (inclusive)
            if 0 <= days_left <= 5 and not inv.paid and not inv.notified_5d:
                await create_due_soon_notification(sess, inv, days_left)
                notification_sent = True

            stored_invoice = {
                "id": inv.id,
                "filename": inv.filename,
                "due_date": inv.due_date.isoformat(),
                "supplier": inv.supplier,
                "days_left": days_left
            }

    except Exception as e:
        # Keep front payload intact; just annotate backend info
        note = f"Due date not stored: {e}"

    # 3) Build a coherent, back-compatible response
    #    - Top-level mirrors your original payload fields for the frontend
    #    - Extras live under 'data_scadenza_iso' and 'backend'
    response = {
        "status": tool_result.get("status", "ok"),
        "file": tool_result.get("file", file.filename or "invoice.xml"),
        "data_scadenza": tool_result.get("data_scadenza"),
        "data_scadenza_iso": due_iso,
        "backend": {
            "stored_invoice": stored_invoice,
            "notification_sent": notification_sent,
            **({"note": note} if note else {})
        }
    }
    return JSONResponse(content=response)


@app.post("/check_data_emissione", tags=["Fatture"])
async def check_data_emissione_fastapi(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
    try:
        result = check_date_fornitore(tmp_path)
    finally:
        os.remove(tmp_path)
    return JSONResponse(content=result)

@app.post("/receipts/upload", tags=["Fatture"])
async def upload_receipts(files: List[UploadFile] = File(...)):
    """
    Carica una o più ricevute (XML), ne estrae la data di scadenza e le registra come 'receipt_upload'.
    Ritorna: per-file {ok/errore, invoice_id se creato, days_left, ...}
    """
    results = []
    today = datetime.now(TZ).date()

    for f in files:
        saved_path = FILES_DIR / f.filename
        # salva su disco in modo persistente
        with saved_path.open("wb") as out:
            out.write(await f.read())

        # prova a leggere la data con il tuo parser
        try:
            tool_result = check_date(str(saved_path))
            due = parse_due_date(tool_result)  # usa data_scadenza
            days_left = (due - today).days

            with Session(engine) as sess:
                inv = Invoice(
                    filename=f.filename,
                    due_date=due,
                    supplier=None,
                    source="receipt_upload",
                    file_path=str(saved_path),
                )
                sess.add(inv)
                sess.commit()
                sess.refresh(inv)

                # se entro 5 giorni, notifica subito
                notified = False
                if 0 <= days_left <= 5 and not inv.notified_5d:
                    await create_due_soon_notification(sess, inv, days_left)
                    notified = True

                results.append({
                    "file": f.filename,
                    "status": "ok",
                    "invoice_id": inv.id,
                    "due_date": due.isoformat(),
                    "days_left": days_left,
                    "notification_sent": notified,
                })

        except Exception as e:
            results.append({
                "file": f.filename,
                "status": "error",
                "message": str(e),
            })

    return {"uploaded": results}

@app.get("/receipts", tags=["Fatture"])
def list_receipts(limit: int = 100):
    with Session(engine) as sess:
        q = select(Invoice).where(Invoice.source == "receipt_upload").order_by(Invoice.created_at.desc())
        rows = sess.exec(q).all()
        return {"receipts": [{
            "id": r.id,
            "filename": r.filename,
            "due_date": r.due_date.isoformat(),
            "paid": r.paid,
            "file_path": r.file_path,
            "created_at": r.created_at.isoformat(),
        } for r in rows[:limit]]}

