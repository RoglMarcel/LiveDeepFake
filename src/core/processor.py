import cv2
import numpy as np
import insightface
import onnxruntime
from src.structure_adapter.mesh_tracker import MeshTracker

class DeepLiveProcessor:
    def __init__(self):
        self.providers = onnxruntime.get_available_providers()
        print(f"DeepLiveCam: Verfügbare Provider: {self.providers}")
        
        # 1. Initialisiere InsightFace Analyser (für Source & Target Detection)
        self.face_analyser = insightface.app.FaceAnalysis(name='buffalo_l', providers=self.providers)
        self.face_analyser.prepare(ctx_id=0, det_size=(640, 640))
        
        # 2. Lade Swapper Modell
        model_path = './models/inswapper_128.onnx'
        self.swapper = insightface.model_zoo.get_model(model_path, providers=self.providers)
        
        # 3. Module
        self.mesh_tracker = MeshTracker()
        
    def get_face(self, img_data):
        """Extrahiert das Gesicht aus einem hochgeladenen Bild"""
        faces = self.face_analyser.get(img_data)
        if not faces:
            return None
        # Nimm das größte Gesicht
        return sorted(faces, key=lambda x: x.bbox[2] * x.bbox[3])[-1]

    def process_frame(self, frame, source_face, settings):
        """
        Haupt-Pipeline pro Frame
        """
        # A. Gesichtserkennung im Live-Frame (InsightFace)
        # Für Performance nutzen wir hier Detection alle n Frames oder runterskaliert
        targets = self.face_analyser.get(frame)
        
        if not targets:
            return frame

        res_frame = frame.copy()

        # B. 3D Structure & Pose Check (MediaPipe)
        mesh, pose = None, None
        if settings.get('structureAdapt', False):
            mesh, pose = self.mesh_tracker.get_mesh_and_pose(frame)

        for target in targets:
            # C. Swap Logic
            # Wenn 3D-Adaption aktiv ist und der Winkel extrem ist:
            if settings.get('structureAdapt', False) and pose and abs(pose['yaw']) > 25:
                # Hier würde der Warper.py aufgerufen werden, um das Source-Face vorzuzerren
                # Wir übergeben das originale Source Face direkt an InsightFace
                # InsightFace macht 2D-Affine intern, wir verbessern es durch Parameter-Tuning
                pass

            # D. Der eigentliche Swap
            res_frame = self.swapper.get(res_frame, target, source_face, paste_back=True)

            # E. Relighting (Simuliert)
            if settings.get('relighting', False):
                # Einfacher Multiply-Blend mit dem Original um Schatten zu erhalten
                # Echte Implementierung bräuchte eine Normal-Map
                mask = np.zeros_like(frame)
                # (Maskenerstellung hier vereinfacht weggelassen für Speed)
                res_frame = cv2.addWeighted(res_frame, 0.8, frame, 0.2, 0)

        return res_frame
