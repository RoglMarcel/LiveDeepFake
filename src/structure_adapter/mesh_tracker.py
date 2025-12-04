import cv2
import mediapipe as mp
import numpy as np

class MeshTracker:
    def __init__(self):
        """
        Initialisiert MediaPipe Face Mesh für Echtzeit-Tracking.
        refine_landmarks=True gibt uns auch Iris-Punkte für Blickrichtung.
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def get_mesh_and_pose(self, frame):
        """
        Extrahiert 3D-Landmarks und schätzt die Kopf-Rotation.
        Rückgabe: (landmarks_np, pose_dict) oder (None, None)
        """
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None, None

        # Wir nehmen das erste erkannte Gesicht
        face_landmarks = results.multi_face_landmarks[0]
        
        # Konvertierung in NumPy Array (x, y) für Bildverarbeitung
        landmarks_np = np.array([
            [int(lm.x * w), int(lm.y * h)] for lm in face_landmarks.landmark
        ], dtype=np.int32)

        # Einfache Pose-Schätzung (Yaw/Pitch) basierend auf Nasenspitze vs. Ohren
        # Indizes: 1 (Nase), 33 (Linkes Auge Eck), 263 (Rechtes Auge Eck)
        nose = face_landmarks.landmark[1]
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]

        # Yaw Berechnung (Links/Rechts Drehung)
        face_center_x = (left_eye.x + right_eye.x) / 2
        yaw = (nose.x - face_center_x) * 100  # Skalierter Faktor

        pose = {
            'yaw': yaw,
            'pitch': (nose.y - (left_eye.y + right_eye.y) / 2) * 100
        }

        return landmarks_np, pose
