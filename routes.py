from flask import request, jsonify
from app import app, db, bcrypt
from flask_jwt_extended import create_access_token
from models import Utilisateur, Diagnostic
from PIL import Image
import base64
import io
from datetime import datetime
import random
import numpy as np
from flask import request, jsonify
from tensorflow.keras.models import load_model
from flask_jwt_extended import jwt_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_mail import Mail, Message
import os
# Configuration de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Email de l'expéditeur
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') # Mot de passe de l'expéditeur
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Email de l'expéditeur

mail = Mail(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nom = data['nom']
    email = data['email']
    

    # Vérification si l'email existe déjà dans la base de données
    existing_user = Utilisateur.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"erreur": "L'email est déjà utilisé"}), 400

    mot_de_passe = bcrypt.generate_password_hash(data['mot_de_passe']).decode('utf-8')

    # Créer un nouvel utilisateur sans le marquer comme vérifié
    user = Utilisateur(nom=nom, email=email, mot_de_passe=mot_de_passe, verifie=False)
    db.session.add(user)
    db.session.commit()

    # Générer un code de vérification aléatoire
    code = str(random.randint(100000, 999999))
    user.code_verification = code
    db.session.commit()

    # Envoi du code de vérification par email
    msg = Message("Votre code de vérification", recipients=[email])
    msg.body = f"Bonjour {nom},\n\nVotre code de vérification est : {code}"

    try:
        mail.send(msg)  # Envoi de l'email
        print(f"📨 Code de vérification envoyé à {email}: {code}")  # Affichage dans le terminal pour les tests
        return jsonify({
            "message": "Inscription réussie. Vérifiez votre email pour le code de vérification."
        }), 201
    except Exception as e:
        return jsonify({"erreur": f"Erreur lors de l'envoi de l'email : {str(e)}"}), 500

@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")
    user = Utilisateur.query.filter_by(email=email).first()

    # Vérifier si l'utilisateur existe et si le code correspond
    if user and user.code_verification == code:
        user.verifie = True  # Marquer l'utilisateur comme vérifié
        user.code_verification = None  # Supprimer le code après vérification
        db.session.commit()
        return jsonify({"message": "Utilisateur vérifié avec succès"}), 200
    else:
        return jsonify({"erreur": "Code de vérification incorrect"}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Utilisateur.query.filter_by(email=data['email']).first()
    
    if user and bcrypt.check_password_hash(user.mot_de_passe, data['mot_de_passe']):
        if not user.verifie:  # Vérification de l'email
            return jsonify({"erreur": "Votre email n'est pas vérifié"}), 400  # 400 pour erreur utilisateur
        
        # Si l'email est vérifié, générer un token
        token = create_access_token(identity=str(user.id))
        refresh = create_refresh_token(identity=str(user.id))
        return jsonify({"token": token, "refresh_token": refresh, "utilisateur_id": user.id})
    else:
        return jsonify({"erreur": "Identifiants invalides"}), 401


from itsdangerous import URLSafeTimedSerializer

# Initialisation du sérialiseur pour créer un token sécurisé
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = Utilisateur.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Si cet email est enregistré, un lien de réinitialisation a été envoyé."}), 200

    # Générer un token de réinitialisation
    token = serializer.dumps(email, salt='reset-password-salt')

    # Créer un lien de réinitialisation
    reset_link = f"http://localhost:5000/reset-password/{token}"  # Adapte l'URL à ton frontend si nécessaire

    # Envoi du lien de réinitialisation par email
    msg = Message("Réinitialisation de mot de passe", recipients=[email])
    msg.body = f"Bonjour,\n\nPour réinitialiser votre mot de passe, cliquez sur ce lien :\n{reset_link}\n\nCe lien est valable pendant 30 minutes."

    try:
        mail.send(msg)
        print(f"🔗 Lien de réinitialisation envoyé à {email}: {reset_link}")
        return jsonify({"message": "Lien de réinitialisation envoyé"}), 200
    except Exception as e:
        return jsonify({"erreur": f"Erreur lors de l'envoi de l'email : {str(e)}"}), 500
    
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    try:
        email = serializer.loads(token, salt='reset-password-salt', max_age=1800)
    except Exception:
        return "Lien invalide ou expiré", 400

    if request.method == 'GET':
        return f"""
            <form action="/reset-password/{token}" method="POST">
                <input type="password" name="nouveau_mot_de_passe" placeholder="Nouveau mot de passe" required>
                <input type="password" name="confirmation_mot_de_passe" placeholder="Confirmez le mot de passe" required>
                <button type="submit">Réinitialiser</button>
            </form>
        """

    new_password = request.form.get("nouveau_mot_de_passe")
    confirm_password = request.form.get("confirmation_mot_de_passe")

    if new_password != confirm_password:
        return "Les mots de passe ne correspondent pas", 400

    user = Utilisateur.query.filter_by(email=email).first()
    if not user:
        return "Utilisateur non trouvé", 404

    user.mot_de_passe = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return "Mot de passe mis à jour avec succès ✅"
   


@app.route('/me', methods=['GET'])
@jwt_required()
def get_user_info():
    user_id = get_jwt_identity()
    user = Utilisateur.query.get(user_id)
    if not user:
        return jsonify({"erreur": "Utilisateur non trouvé"}), 404

    return jsonify({
        "id": user.id,
        "nom": user.nom,
        "email": user.email,
        "verifie": user.verifie
    }), 200

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_token = create_access_token(identity=user_id)
    return jsonify({
        "token": new_token
    }), 200

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Déconnecté (client doit supprimer le token)"}), 200


model = load_model('models/dermato_model.h5')
classes = ['Healthy', 'Cowpox', 'Monkeypox', 'HFMD', 'Measles', 'Chickenpox']

@app.route('/diagnostic', methods=['POST'])
@jwt_required()
def diagnostic():
    data = request.get_json()
    image_base64 = data.get("image_base64")

    if not image_base64:
        return jsonify({"erreur": "Aucune image encodée reçue"}), 400

    try:
        # Décoder l'image depuis le base64
        image_bytes = base64.b64decode(image_base64)
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Prétraitement
        img = img.resize((224, 224))
        img_array = np.expand_dims(np.array(img), axis=0) / 255.0

        preds = model.predict(img_array)
        class_probs = preds[0]
        predicted_class = int(np.argmax(preds))
        predicted_prob = float(np.max(preds))

        label = classes[predicted_class] if predicted_prob > 0.7 else "Inconnu ou incertain"

        return jsonify({
            "message": "Diagnostic terminé",
            "maladie": classes[predicted_class],
            "probabilité": round(predicted_prob, 2),
            "label": label
        }), 200

    except Exception as e:
        return jsonify({"erreur": f"Erreur lors du diagnostic : {str(e)}"}), 500
@app.route('/diagnosticsHistory', methods=['GET'])
@jwt_required()
def diagnostics_history():
    user_id = get_jwt_identity()
    historiques = Diagnostic.query.filter_by(utilisateur_id=user_id).order_by(Diagnostic.date.desc()).all()
    data = [
        {
            "maladie": d.maladie,
            "score": d.score,
            "date": d.date.strftime("%Y-%m-%d %H:%M")
        } for d in historiques
    ]
    return jsonify(data)
