from flask import request, jsonify
from app import app, db, bcrypt
from flask_jwt_extended import create_access_token
from models import Utilisateur, Diagnostic
from webcam_predictor import predict_from_camera
from datetime import datetime
import random
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
    
@app.route('/reset-password/<token>', methods=['POST'])
def reset_password_token(token):
    try:
        # Vérifier et décoder le token
        email = serializer.loads(token, salt='reset-password-salt', max_age=1800)  # 30 minutes de validité
    except Exception:
        return jsonify({"erreur": "Lien invalide ou expiré"}), 400

    # Récupérer l'utilisateur à partir de l'email décodé
    data = request.get_json()
    new_password = data.get("nouveau_mot_de_passe")
    confirm_password = data.get("confirmation_mot_de_passe")  # Le champ de confirmation du mot de passe

    # Vérifier si le mot de passe et la confirmation du mot de passe sont identiques
    if new_password != confirm_password:
        return jsonify({"erreur": "Les mots de passe ne correspondent pas"}), 400

    user = Utilisateur.query.filter_by(email=email).first()

    if not user:
        return jsonify({"erreur": "Utilisateur non trouvé"}), 404

    # Mettre à jour le mot de passe
    user.mot_de_passe = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"message": "Mot de passe mis à jour avec succès"}), 200


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

@app.route('/diagnostic', methods=['POST'])
@jwt_required()
def diagnostic():
    # Démarre le thread pour exécuter la prédiction
    prediction = predict_from_camera()

    if prediction is None:
        return jsonify({
            "message": "Erreur lors de la capture de l'image ou de la prédiction."
        }), 500

    return jsonify({
        "message": "Diagnostic terminé",
        "maladie": prediction["class"],
        "probabilité": prediction["probability"],
        "label": prediction["label"]
    }), 200

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
