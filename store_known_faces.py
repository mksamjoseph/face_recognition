import os
import django
import cv2
import face_recognition
from datetime import datetime
from django.core.files import File

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pro1.settings")  # Replace with your Django project settings module
django.setup()

from app.models import KnownPerson  # Replace 'app' with your Django app name

# Path to known images folder
KNOWN_IMAGES_PATH = "/home/santosh/Videos/Hackathon/pro1/Static/images/"

def store_known_faces():
    print("[INFO] Storing known faces from:", KNOWN_IMAGES_PATH)

    for filename in os.listdir(KNOWN_IMAGES_PATH):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue  # Skip non-image files

        filepath = os.path.join(KNOWN_IMAGES_PATH, filename)
        img = cv2.imread(filepath)

        if img is None:
            print(f"[ERROR] Failed to load image {filename}")
            continue

        # Convert image from BGR to RGB (face_recognition expects RGB)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)

        if not encodings:
            print(f"[WARNING] No face found in {filename}")
            continue

        encoding = encodings[0]
        name = os.path.splitext(filename)[0]  # Use filename without extension as name

        # Avoid duplicate entries by name
        if KnownPerson.objects.filter(name=name).exists():
            print(f"[SKIP] {name} already exists in the database")
            continue

        from django.core.files.base import ContentFile

        with open(filepath, "rb") as f:
            file_content = f.read()
            django_file = ContentFile(file_content, name=filename)  # Only filename, not full path
            person = KnownPerson.objects.create(
            name=name,
            embedding=encoding.tobytes(),
            photo=django_file,
            created_at=datetime.now(),
            camera_name="camera_a"
        )

    print("[DONE] All known faces processed.")

if __name__ == "__main__":
    store_known_faces()
