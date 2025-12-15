import uvicorn
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import asyncio
import os
import sys


# Fügt das aktuelle Verzeichnis zum Suchpfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Wir importieren deine Logik aus den Unterordnern
    # Dies entspricht deiner Ordnerstruktur: src -> core -> processor.py
    from src.core.processor import DeepLiveProcessor
    from src.core.thread_mgr import StreamCapture, FrameProcessorThread

    print("✅ Module erfolgreich geladen (src.core)")
except ImportError as e:
    print(f"❌ Import Fehler: {e}")
    print("Stelle sicher, dass 'processor.py' im Ordner 'src/core/' liegt.")
    # Wir beenden hier, weil ohne diese Dateien nichts geht
    sys.exit(1)

app = FastAPI()

# Erlaubt dem React-Frontend (Port 5173) den Zugriff auf diesen Server (Port 8000)
# Dies verhindert "CORS Error" im Browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globale Variablen für den Server-Status
processor = None
stream_cap = None
proc_thread = None
current_source_face = None
global_settings = {
    "structureAdapt": True,
    "relighting": True,
    "enhance": False
}


@app.on_event("startup")
def startup_event():
    global processor, stream_cap, proc_thread
    print("🚀 Starte DeepLiveCam System...")

    try:
        # KI-Modelle laden (InsightFace, ONNX)
        processor = DeepLiveProcessor()
    except Exception as e:
        print(f"❌ KRITISCHER FEHLER beim Laden der Modelle: {e}")
        print("HINWEIS: Hast du 'inswapper_128.onnx' in den 'models' Ordner gelegt und umbenannt?")
        return

    # Kamera starten (Index 0 ist meist die Standard-Webcam)
    print("📷 Öffne Webcam...")
    try:
        stream_cap = StreamCapture(source=0).start()
    except Exception as e:
        print(f"⚠️ Warnung: Konnte Webcam nicht öffnen: {e}")

    # Verarbeitungsthread starten (damit das Video flüssig läuft)
    if processor:
        proc_thread = FrameProcessorThread(processor.process_frame)
        proc_thread.start()
        print("✅ Backend ist bereit und läuft auf http://localhost:8000")
    else:
        print("⚠️ Backend läuft, aber ohne KI-Prozessor (Modell-Fehler).")


@app.post("/upload_source")
async def upload_source(file: UploadFile = File(...)):
    """Nimmt das Foto entgegen, das du im Browser hochlädst"""
    global current_source_face

    if not processor:
        return {"status": "error", "message": "KI-Modell nicht geladen"}

    # Datei lesen und in OpenCV Format wandeln
    contents = await file.read()
    nparr = np.fromstring(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Gesicht im Quellbild finden
    face = processor.get_face(img)
    if face:
        current_source_face = face
        # Sende das neue Gesicht an den laufenden Prozess
        if proc_thread:
            proc_thread.set_config(current_source_face, global_settings)
        print("👤 Neues Quell-Gesicht gesetzt!")
        return {"status": "success", "message": "Gesicht erfolgreich erkannt"}

    print("⚠️ Kein Gesicht im Bild gefunden")
    return {"status": "error", "message": "Kein Gesicht gefunden"}


@app.post("/update_settings")
async def update_settings(settings: dict):
    """Empfängt Klicks auf die Checkboxen im UI"""
    global global_settings
    global_settings.update(settings)
    if proc_thread:
        proc_thread.set_config(current_source_face, global_settings)
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Die Live-Verbindung zum Browser für das Videobild"""
    await websocket.accept()
    try:
        while True:
            # Wenn ein bearbeitetes Bild fertig ist, sende es
            if proc_thread and not proc_thread.out_queue.empty():
                frame = proc_thread.out_queue.get()

                # Komprimiere Bild zu JPG für schnellen Transfer im Netzwerk
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
                b64_frame = base64.b64encode(buffer).decode('utf-8')

                fps = int(stream_cap.fps) if stream_cap else 0

                await websocket.send_json({
                    "fps": fps,
                    "image": f"data:image/jpeg;base64,{b64_frame}"
                })
            else:
                # Falls keine KI läuft oder Queue leer ist, sende einfach das rohe Kamerabild
                if stream_cap:
                    raw_frame = stream_cap.read()
                    if raw_frame is not None and proc_thread:
                        # Schicke es in die Pipeline zurück
                        proc_thread.in_queue.put(raw_frame)

                # Kurze Pause, um CPU nicht zu überlasten
                await asyncio.sleep(0.005)

    except Exception as e:
        print(f"WebSocket Verbindung geschlossen: {e}")
    finally:
        print("Browser Tab geschlossen.")


if __name__ == "__main__":
    # Startet den Server
    uvicorn.run(app, host="0.0.0.0", port=8000)
