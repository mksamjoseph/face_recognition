import json
import base64
import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta
import face_recognition
from app.models import KnownPerson, UnknownPerson, PersonSighting
from django.utils.timezone import now

SIGHTING_WINDOW = timedelta(seconds=30)

encodeListKnown = []
classNames = []

@database_sync_to_async
def load_known_faces_from_db():
    global encodeListKnown, classNames
    encodeListKnown.clear()
    classNames.clear()

    known_people = KnownPerson.objects.all()
    for person in known_people:
        encoding = np.frombuffer(person.embedding, dtype=np.float64)
        encodeListKnown.append(encoding)
        classNames.append(person.name)
    print(f"[DEBUG] Loaded {len(classNames)} known faces from DB.")

@database_sync_to_async
def save_unknown_face_to_db(name, encoding, img_bytes, camera_name):
    capture_time = now()
    save_time = now()

    latency_seconds = (save_time - capture_time).total_seconds()
    if UnknownPerson.objects.filter(name=name).exists():
        print(f"[DEBUG] Unknown face '{name}' already exists in DB.")
        return
    UnknownPerson.objects.create(
        name=name,
        embedding=encoding.tobytes(),
        photo=ContentFile(img_bytes, name=f"{name}.jpg"),
        created_at=timezone.now(),
        camera_name=camera_name,
        captured_at=capture_time,
        latency=latency_seconds
    )
    print(f"[DEBUG] Saved unknown face '{name}' to DB.")

@database_sync_to_async
def create_sighting_record(known_name=None, unknown_name=None, location=None):
    now = timezone.now()
    if known_name:
        try:
            known_person = KnownPerson.objects.get(name=known_name)
        except KnownPerson.DoesNotExist:
            print(f"[DEBUG] Known person '{known_name}' not found for sighting record.")
            return
        last_sighting = PersonSighting.objects.filter(
            known_person=known_person,
            location=location
        ).order_by('-timestamp').first()
        if not last_sighting or now - last_sighting.timestamp > SIGHTING_WINDOW:
            PersonSighting.objects.create(
                known_person=known_person,
                location=location,
                timestamp=now
            )
            print(f"[DEBUG] Created sighting record for known person '{known_name}'.")
    elif unknown_name:
        try:
            unknown_person = UnknownPerson.objects.get(name=unknown_name)
        except UnknownPerson.DoesNotExist:
            print(f"[DEBUG] Unknown person '{unknown_name}' not found for sighting record.")
            return
        last_sighting = PersonSighting.objects.filter(
            unknown_person=unknown_person,
            location=location
        ).order_by('-timestamp').first()
        if not last_sighting or now - last_sighting.timestamp > SIGHTING_WINDOW:
            PersonSighting.objects.create(
                unknown_person=unknown_person,
                location=location,
                timestamp=now
            )
            print(f"[DEBUG] Created sighting record for unknown person '{unknown_name}'.")


class FaceRecognitionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Load known faces once client connects
        await load_known_faces_from_db()
        self.unknown_encodings_cache = []
        print("[DEBUG] WebSocket connected")

    async def disconnect(self, close_code):
        print(f"[DEBUG] WebSocket disconnected with code {close_code}")
        pass

    async def receive(self, text_data):
        """
        Expects JSON:
        {
          "frame": "<base64_image_string>",
          "camera_name": "camera_a"
        }
        """
        print("[DEBUG] Received data:", text_data[:100], "...")  # Log beginning of the data for brevity
        data = json.loads(text_data)
        frame_data = data.get("frame")
        camera_name = data.get("camera_name", "camera_a")
        print(f"[DEBUG] Camera name received: {camera_name}")
        
        if not frame_data:
            await self.send(text_data=json.dumps({"error": "No frame data received"}))
            print("[ERROR] No frame data received in message")
            return

        try:
            imgstr = frame_data.split("base64,")[-1]
            img_bytes = base64.b64decode(imgstr)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            print("[DEBUG] Frame decoded and converted to RGB")
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Failed to decode image: {str(e)}"}))
            print(f"[ERROR] Failed to decode image: {str(e)}")
            return

        face_locations = face_recognition.face_locations(rgb_frame)
        encodes_cur_frame = face_recognition.face_encodings(rgb_frame, face_locations)
        print(f"[DEBUG] Detected {len(face_locations)} faces")

        recognized_faces = []
        unknown_encodings_cache = self.unknown_encodings_cache

        for encode_face, face_location in zip(encodes_cur_frame, face_locations):
            matches = face_recognition.compare_faces(encodeListKnown, encode_face, tolerance=0.55)
            face_distances = face_recognition.face_distance(encodeListKnown, encode_face)
            name = "Unknown"

            if matches and any(matches):
                match_index = np.argmin(face_distances)
                if matches[match_index]:
                    name = classNames[match_index]
                    print(f"[DEBUG] Recognized known face: {name}")
            else:
                # Check if this unknown face matches any cached unknowns
                is_new_unknown = True
                for i, cached_encoding in enumerate(unknown_encodings_cache):
                    if face_recognition.compare_faces([cached_encoding], encode_face, tolerance=0.5)[0]:
                        is_new_unknown = False
                        name = f"unknown_{i + 1:03}"
                        print(f"[DEBUG] Matched cached unknown face: {name}")
                        break

                if is_new_unknown:
                    name = f"unknown_{len(unknown_encodings_cache) + 1:03}"
                    unknown_encodings_cache.append(encode_face)
                    print(f"[DEBUG] New unknown face detected and saved: {name}")

                    top, right, bottom, left = face_location
                    face_img = frame[top:bottom, left:right]
                    # Encode face image to bytes for DB saving
                    _, img_encoded = cv2.imencode('.jpg', face_img)
                    img_bytes_face = img_encoded.tobytes()

                    # Save unknown face in DB async
                    await save_unknown_face_to_db(name, encode_face, img_bytes_face, camera_name)

            # Append face bounding box + name for frontend display
            top, right, bottom, left = face_location
            recognized_faces.append({
                "x": int(left),
                "y": int(top),
                "width": int(right - left),
                "height": int(bottom - top),
                "name": name
            })
            print(name)

            # Save sighting record async
            if name.startswith("unknown"):
                await create_sighting_record(unknown_name=name, location=camera_name)
            else:
                await create_sighting_record(known_name=name, location=camera_name)

        # Send back recognized faces info
        await self.send(text_data=json.dumps({
            "status": "success",
            "faces": recognized_faces
        }))
        print(f"[DEBUG] Sent face recognition result with {len(recognized_faces)} faces")
