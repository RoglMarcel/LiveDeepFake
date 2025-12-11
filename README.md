Deep Live Cam Enhanced (DLC-E)

Eine erweiterte Version von Deep-Live-Cam mit 3D-Struktur-Anpassung und dynamischem Relighting. Dieses Projekt ermöglicht Echtzeit-Face-Swapping mit hoher Performance (>30 FPS) und verbesserter Realitätstreue durch Anpassung der Gesichtsgeometrie.

🚀 Features

Echtzeit Face-Swapping: Basiert auf InsightFace & ONNX Runtime.

3D Structure Adapt: Passt das Gesicht an die Kopfform und Rotation des Nutzers an (kein "flaches" Gesicht mehr).

Dynamic Relighting: Simuliert Licht und Schatten passend zur Umgebung.

Modernes UI: React-basiertes Interface mit Live-Vorschau und FPS-Anzeige.

🛠️ Installation

Voraussetzungen

Python 3.10+

Node.js (für das Frontend)

CUDA Toolkit (empfohlen für NVIDIA GPUs) oder CoreML (macOS)

1. Repository klonen

git clone [https://github.com/RoglMarcel/Deep-Live-Cam-Enhanced.git](https://github.com/RoglMarcel/Deep-Live-Cam-Enhanced.git)
cd Deep-Live-Cam-Enhanced


2. Python Abhängigkeiten installieren

pip install -r requirements.txt


3. Modelle herunterladen (WICHTIG!)

Die KI-Modelle sind zu groß für GitHub. Bitte führe dieses Skript aus, um sie automatisch herunterzuladen (~600MB):

python download_models.py


Dies lädt inswapper_128.onnx und buffalo_l in den Ordner ./models.

4. UI Setup (Frontend)

Gehe in den UI-Ordner und installiere die Pakete:

cd ui
npm install
cd ..


▶️ Starten

Du benötigst zwei Terminal-Fenster:

Terminal 1: Backend (Server)

python run.py


Terminal 2: Frontend (Benutzeroberfläche)

cd ui
npm run dev


Öffne dann deinen Browser auf der angezeigten Adresse (meist http://localhost:5173).

⚠️ Troubleshooting

Fehler: "Model file not found"
Stelle sicher, dass du Schritt 3 (download_models.py) ausgeführt hast. Die Datei inswapper_128.onnx muss im Ordner models/ liegen.

Performance Probleme
Aktiviere im UI den "Fast Mode", wenn du keine dedizierte Grafikkarte hast.
