import cv2
import numpy as np
import pickle
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from config import KNOWN_FACES_DIR, FACE_RECOGNITION_TOLERANCE, CAMERA_ID

class FaceRecognitionModule:
    def __init__(self):
        # Load Haar Cascade classifier
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        self.known_face_encodings = []
        self.known_face_names = []
        self.encodings_file = KNOWN_FACES_DIR / "face_encodings.pkl"
        self.load_known_faces()

    def _extract_face_features(self, face_region):
        if face_region.size == 0:
            return None

        # Resize to standard size
        face_region = cv2.resize(face_region, (100, 100))

        # Convert to grayscale
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)

        # Simple histogram feature (consistent size: 256)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        features = hist.flatten()

        return np.array(features, dtype=np.float32)

    def capture_face(self, name, num_samples=3):
        cap = cv2.VideoCapture(CAMERA_ID)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return False

        samples_captured = 0
        captured_encodings = []

        print(f"\nCapturing {num_samples} samples for {name}...")
        print("Position your face in front of the camera.")
        print("Press SPACE to capture, ESC to cancel")

        while samples_captured < num_samples:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            face_detected = False
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                face_detected = True

            cv2.putText(frame, f"Samples: {samples_captured}/{num_samples}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Face detected" if face_detected else "Move closer",
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if face_detected else (0, 0, 255), 2)
            cv2.imshow("Face Registration", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    face_roi = frame[y:y+h, x:x+w]
                    encoding = self._extract_face_features(face_roi)
                    if encoding is not None:
                        captured_encodings.append(encoding)
                        samples_captured += 1
                        print(f"✓ Captured sample {samples_captured}")
                    else:
                        print("❌ Could not extract features. Try again.")
                else:
                    print("❌ No face detected. Try again.")
            elif key == 27:  # ESC
                cap.release()
                cv2.destroyAllWindows()
                return False

        cap.release()
        cv2.destroyAllWindows()

        if len(captured_encodings) == num_samples:
            avg_encoding = np.mean(captured_encodings, axis=0)
            self.known_face_encodings.append(avg_encoding)
            self.known_face_names.append(name)
            self._save_encodings_to_file()
            print(f"✓ Face saved for {name}")
            return True
        return False

    def recognize_face(self, frame):
        face_locations = []
        face_names = []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_locations.append((y, x + w, y + h, x))

            face_roi = frame[y:y+h, x:x+w]
            encoding = self._extract_face_features(face_roi)

            name = "Unknown"
            if encoding is not None and len(self.known_face_encodings) > 0:
                best_match_score = -1
                best_match_index = -1

                for idx, known_enc in enumerate(self.known_face_encodings):
                    # Ensure both encodings have same shape
                    if len(encoding) == len(known_enc):
                        sim = cosine_similarity([encoding], [known_enc])[0][0]
                        if sim > best_match_score:
                            best_match_score = sim
                            best_match_index = idx

                if best_match_score > FACE_RECOGNITION_TOLERANCE and best_match_index >= 0:
                    name = self.known_face_names[best_match_index]

            face_names.append(name)

        return face_locations, face_names

    def detect_and_mark_attendance(self, callback):
        cap = cv2.VideoCapture(CAMERA_ID)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return

        print("\nStarting automatic attendance marking...")
        print("Stand in front of the camera. Attendance will be marked automatically.")
        print("Press 'Q' to quit\n")

        marked_people = {}

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            face_locations, face_names = self.recognize_face(frame)

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                if name != "Unknown":
                    color = (0, 255, 0)

                    if name not in marked_people:
                        callback(name)
                        marked_people[name] = True
                        print(f"✓ Marked attendance for {name}")
                else:
                    color = (0, 0, 255)

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            cv2.putText(frame, f"Marked: {len(marked_people)} | Press 'Q' to quit",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Automatic Attendance Marking", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if marked_people:
            print(f"\n✓ Marked attendance for {len(marked_people)} people")
        else:
            print("\n⚠ No attendance marked")

    def load_known_faces(self):
        if self.encodings_file.exists():
            with open(self.encodings_file, "rb") as f:
                data = pickle.load(f)
                self.known_face_encodings = data.get("encodings", [])
                self.known_face_names = data.get("names", [])

    def _save_encodings_to_file(self):
        data = {
            "encodings": self.known_face_encodings,
            "names": self.known_face_names
        }
        with open(self.encodings_file, "wb") as f:
            pickle.dump(data, f)

    def get_registered_faces(self):
        return list(set(self.known_face_names))
