import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Charger le modèle personnalisé (remplace le chemin par celui où ton modèle est sauvegardé)
model = load_model('models/dermato_model.h5')  # Remplace ce chemin par ton propre modèle

# Définir les classes de ton modèle (Adapte les classes selon tes besoins)
classes = ['Healthy', 'Cowpox', 'Monkeypox', 'HFMD', 'Measles', 'Chickenpox']  # Remplace ou ajoute d'autres classes si nécessaire

def predict_from_camera():
    """
    Fonction de prédiction en temps réel à partir de la caméra.
    """
    # Ouvre la caméra (généralement la première caméra est indexée à 0)
    cap = cv2.VideoCapture(0)

    # Vérifie si la caméra a été ouverte correctement
    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir la caméra.")
        exit()

    while True:
        # Capture une image à partir de la caméra
        ret, frame = cap.read()
        if not ret:
            print("Erreur: Impossible de capturer l'image.")
            break

        # Convertir l'image BGR (OpenCV) en RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        img_eq = cv2.equalizeHist(img_gray)

        # Redimensionner l'image pour qu'elle corresponde à l'entrée de ton modèle (224x224)
        img_resized = cv2.resize(img_eq, (224, 224))  # Assurez-vous que les dimensions correspondent à ce que votre modèle attend
        
        # Convertir l'image en 3 canaux (RGB) si nécessaire
        img_resized_rgb = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2RGB)  # Convertir en RGB si l'image est en niveaux de gris
        
        # Ajouter une dimension batch et normaliser les pixels
        img_array = np.expand_dims(img_resized_rgb, axis=0)  # Ajouter une dimension pour le batch (1 image)
        img_preprocessed = img_array / 255.0  # Normalisation des pixels (si nécessaire)
        
        # Faire la prédiction sur l'image capturée
        preds = model.predict(img_preprocessed)

        # Obtenir les probabilités pour chaque classe
        class_probs = preds[0]
        
        # Afficher les probabilités pour chaque classe dans la console
        print("Probabilités pour chaque classe :")
        for i, prob in enumerate(class_probs):
            print(f"{classes[i]}: {prob:.2f}")

        # Trouver la classe avec la probabilité la plus élevée
        predicted_class = np.argmax(preds)  # L'indice de la classe avec la probabilité la plus élevée
        predicted_prob = np.max(preds)  # La probabilité associée à la classe prédite

        # Gestion du seuil de confiance
        if predicted_prob > 0.7:
            label = f"{classes[predicted_class]}: {predicted_prob:.2f}"
        else:
            label = "Inconnu ou incertain"

        # Afficher la classe et la probabilité sur l'image
        cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Affiche l'image capturée dans une fenêtre nommée 'Webcam'
        cv2.imshow('Webcam', frame)

        # Attendre l'appui sur la touche 'q' pour quitter
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Relâche la caméra et ferme les fenêtres OpenCV
    cap.release()
    cv2.destroyAllWindows()
