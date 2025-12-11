import os
import urllib.request
import zipfile
import shutil

# Konfiguration
MODELS_DIR = "./models"
INSIGHTFACE_DIR = os.path.join(MODELS_DIR, "buffalo_l")

# URLs der Modelle (HuggingFace Mirrors)
URL_INSWAPPER = "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx"
# Buffalo_L wird normalerweise als Zip geladen
URL_BUFFALO_ZIP = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        print(f"✅ Datei existiert bereits: {dest_path}")
        return

    print(f"⬇️ Lade herunter: {url}...")
    print(f"   Ziel: {dest_path}")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print("✅ Download abgeschlossen.")
    except Exception as e:
        print(f"❌ Fehler beim Download: {e}")

def setup_models():
    # 1. Erstelle Verzeichnisse
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
    
    # 2. Download Inswapper (Das Haupt-Swap-Modell)
    inswapper_path = os.path.join(MODELS_DIR, "inswapper_128.onnx")
    download_file(URL_INSWAPPER, inswapper_path)

    # 3. Download & Extraktion Buffalo_L (Gesichtserkennung)
    # Hinweis: InsightFace lädt dies oft automatisch nach ~/.insightface,
    # aber für Portabilität laden wir es lokal.
    buffalo_zip_path = os.path.join(MODELS_DIR, "buffalo_l.zip")
    
    if not os.path.exists(INSIGHTFACE_DIR):
        download_file(URL_BUFFALO_ZIP, buffalo_zip_path)
        
        print("📦 Entpacke buffalo_l.zip...")
        with zipfile.ZipFile(buffalo_zip_path, 'r') as zip_ref:
            zip_ref.extractall(MODELS_DIR) # Entpackt in ./models/buffalo_l
        
        # Bereinigen
        os.remove(buffalo_zip_path)
        print("✅ Buffalo_L installiert.")
    else:
        print("✅ Buffalo_L Verzeichnis existiert bereits.")

if __name__ == "__main__":
    print("--- Deep Live Cam Model Downloader ---")
    setup_models()
    print("\n🎉 Alle Modelle bereit! Du kannst jetzt 'run.py' starten.")
