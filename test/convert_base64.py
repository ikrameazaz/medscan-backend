import base64
import os

# Chemin vers l'image
image_path = os.path.join(os.path.dirname(__file__), "Eczema.jpg")

# Lire et encoder l'image
with open(image_path, "rb") as f:
    image_data = f.read()
    b64_image = base64.b64encode(image_data).decode("utf-8")

# Ajouter le préfixe base64 et écrire dans le fichier
with open("image_b64.txt", "w", encoding="utf-8") as out_file:
    out_file.write("data:image/jpeg;base64," + b64_image)

print("✅ Image encodée et enregistrée dans image_b64.txt")
