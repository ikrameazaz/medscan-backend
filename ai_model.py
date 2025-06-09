import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
import cv2
import base64
import io

# Charger le modèle Keras
model = load_model("models/dermato_model.h5")
classes = ["Healthy", "Cowpox", "Monkeypox", "HFMD", "Measles", "Chickenpox"]

def preprocess_image(image_b64):
    # Décoder l’image base64 en tableau numpy
    image_data = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image = image.resize((224, 224))  # adapter à l’entrée du modèle
    image_array = np.array(image) / 255.0
    return np.expand_dims(image_array, axis=0)

def analyser_image_base64(image_b64):
    img_tensor = preprocess_image(image_b64)
    prediction = model.predict(img_tensor)[0]
    index = np.argmax(prediction)
    return {
        "maladie": classes[index],
        "score": round(float(prediction[index]), 2)
    }
