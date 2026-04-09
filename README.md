# Deep Live Cam Enhanced (DLC-E)

Eine erweiterte Version von Deep-Live-Cam mit 3D-Struktur-Anpassung und dynamischem Relighting. Dieses Projekt ermöglicht Echtzeit-Face-Swapping mit hoher Performance (>30 FPS) und verbesserter Realitätstreue durch Anpassung der Gesichtsgeometrie.

## 🚀 Features

- **Echtzeit Face-Swapping**: Basiert auf InsightFace & ONNX Runtime
- **GPU-Beschleunigung**: Automatische NVIDIA CUDA Unterstützung für maximale Performance
- **3D Structure Adapt**: Passt das Gesicht an die Kopfform und Rotation des Nutzers an (kein "flaches" Gesicht mehr)
- **Dynamic Relighting**: Simuliert Licht und Schatten passend zur Umgebung
- **Modernes UI**: React-basiertes Interface mit Live-Vorschau und FPS-Anzeige

---

## 🛠️ Installation

### Voraussetzungen
- Python 3.10 oder 3.11
- Node.js (für das Frontend)

### 1. Repository klonen & Modelle laden (Pflicht für alle)

```bash
git clone https://github.com/RoglMarcel/LiveDeepFake.git
cd LiveDeepFake
```

Lade die KI-Modelle herunter (WICHTIG!). Die Modelle (~600MB) werden in den Ordner `./models` geladen:
```bash
python download_models.py
```

### 2. UI Setup (Frontend) (Pflicht für alle)

Im UI-Ordner müssen die Abhängigkeiten via Node.js installiert werden:
```bash
cd ui
npm install
cd ..
```

### 3. Python Abhängigkeiten installieren (Wähle deine Version)

Es gibt **zwei Varianten** — je nachdem, ob du eine NVIDIA Grafikkarte nutzen möchtest oder nur die CPU.
Requirements herunterladen (für nur CPU nötig!!!):
````bash
pip install -r requirements.txt  
````

---

#### 🟢 Option A: Mit NVIDIA GPU (Stark empfohlen für flüssiges Live-Video)

Diese Methode ist wesentlich schneller, erfordert aber auf Windows die saubere, manuelle Installation der NVIDIA-Entwicklertools.

**Schritt 1: System-Voraussetzungen (NVIDIA)**
Damit Python deine GPU nutzen kann, musst du zwingend **CUDA 11.8** und **cuDNN v8.9.x** auf Systemebene installiert haben:
1. Lade dir das [NVIDIA CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive) herunter und installiere es ("Express"-Installation). Starte den PC im Anschluss am besten neu.
2. Lade dir das [cuDNN Archive v8.9.x (für CUDA 11.x)](https://developer.nvidia.com/rdp/cudnn-archive) herunter (kostenloser Nvidia-Account wird benötigt). Lade die "ZIP für Windows" herunter.
3. Entpacke die cuDNN-ZIP-Datei.
4. Kopiere die **Inhalte** der entpackten Ordner `bin`, `include` und `lib` direkt in das Installationsverzeichnis von CUDA (meist `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8`). Bei der Windows-Frage "Möchten Sie den Ordner integrieren?" wähle **Ja**, um die `.dll` Dateien zu den CUDA-Dateien hinzuzufügen. *(Das ist essenziell! Ohne diese Dateien schlägt CUDA leise fehl!)*

**Schritt 2: Die richtigen Python-Pakete**
Oft stören sich neueste Pip-Versionen (wie Numpy 2.x) untereinander. Führe diese exakten Befehle aus, um sicherzustellen, dass die CUDA-11-Abhängigkeiten harmonieren:

```bash
# Vorhandene Konflikte / fehlerhafte Caches entfernen
python -m pip uninstall onnxruntime onnxruntime-gpu mediapipe protobuf tensorflow numpy opencv-python opencv-contrib-python opencv-python-headless -y

# Passende und stabile Versionen installieren (für CUDA 11.8 und Numpy 1.x)
python -m pip install onnxruntime-gpu==1.17.1
python -m pip install "numpy<2"
python -m pip install "opencv-python<4.10" "opencv-contrib-python<4.10" "opencv-python-headless<4.10"
python -m pip install --no-cache-dir mediapipe==0.10.14
python -m pip install fastapi uvicorn python-multipart insightface
```

---

#### 🟡 Option B: Ohne NVIDIA GPU (CPU-only)

Falls du **keine NVIDIA GPU** hast (AMD, Intel oder Laptop ohne dedizierte GPU), wird die CPU zur Berechnung verwendet (erwarte ca. 5-15 FPS je nach CPU).

```bash
python -m pip uninstall onnxruntime onnxruntime-gpu numpy opencv-python mediapipe protobuf -y
python -m pip install "numpy<2" "opencv-python<4.10"
python -m pip install fastapi uvicorn python-multipart mediapipe insightface onnxruntime --user
```

*(Hinweis: Aktiviere später im UI den Schalter "Fast Mode", damit das Bild trotz schwächerer CPU nicht einfriert!)*

---

## ▶️ Starten

Du benötigst immer zwei Terminal-Fenster:

**Terminal 1: Backend (Server)**
```bash
python run.py
```

**Terminal 2: Frontend (Benutzeroberfläche)**
```bash
cd ui
npm run dev
```

Öffne dann deinen Browser auf der angezeigten Adresse (meist http://localhost:5173).

### GPU Status prüfen
Beim Start zeigt das Backend automatisch den GPU-Status an. Achte auf folgende Zeilen im Konsolen-Output:
```text
🟢 GPU Status: CUDA verfügbar ✅
...
✅ Aktiver Provider für Swapper: CUDAExecutionProvider
```
**Wichtig:** Wenn ganz weit unten im Terminal steht `Applied providers: ['CPUExecutionProvider']` ODER rote Fehlermeldungen (wie `Error 126` oder `cuDNN missing`) auftauchen, wird deine Grafikkarte **nicht** genutzt! Gehe dann nochmal die "Schritt 1: System-Voraussetzungen (NVIDIA)" genau durch, höchstwahrscheinlich fehlen die .dll Dateien von cuDNN im CUDA-Ordner.

*Tipp zur Auslastung:* Wenn dein Programm CUDA nutzt, zeigt der Windows Task-Manager oft trotzdem 0-3% bei der GPU-Auslastung an. Schalte den Graphen dort von "3D" auf "Cuda" oder "Compute_0" um, um die echte 100% Auslastung zu sehen!
