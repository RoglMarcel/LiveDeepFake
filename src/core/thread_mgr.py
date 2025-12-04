import threading
import queue
import cv2
import time

class StreamCapture:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        self.q = queue.Queue(maxsize=2) # Kleiner Puffer für geringe Latenz
        self.stopped = False
        self.fps = 0
        
    def start(self):
        t = threading.Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        last_time = time.time()
        while not self.stopped:
            if not self.q.full():
                ret, frame = self.cap.read()
                if not ret:
                    self.stop()
                    break
                self.q.put(frame)
                
                # FPS Calculation
                now = time.time()
                self.fps = 1.0 / (now - last_time)
                last_time = now
            else:
                time.sleep(0.01) # CPU schonen

    def read(self):
        return self.q.get() if not self.q.empty() else None

    def stop(self):
        self.stopped = True
        self.cap.release()

class FrameProcessorThread:
    def __init__(self, process_func):
        self.process_func = process_func
        self.in_queue = queue.Queue(maxsize=2)
        self.out_queue = queue.Queue(maxsize=2)
        self.stopped = False
        self.settings = {}
        self.source_face = None

    def start(self):
        t = threading.Thread(target=self.work, args=())
        t.daemon = True
        t.start()
        return self
    
    def set_config(self, source_face, settings):
        self.source_face = source_face
        self.settings = settings

    def work(self):
        while not self.stopped:
            try:
                frame = self.in_queue.get(timeout=1)
                
                # Rufe die komplexe KI-Logik auf
                if self.source_face is not None:
                    processed = self.process_func(frame, self.source_face, self.settings)
                else:
                    processed = frame # Pass-through wenn kein Source Face
                
                # Ergebnis in Output Queue (überschreibe alt wenn voll)
                if self.out_queue.full():
                    try: self.out_queue.get_nowait()
                    except: pass
                self.out_queue.put(processed)
                
            except queue.Empty:
                continue

    def stop(self):
        self.stopped = True
