from flask import request, jsonify
from app import app, db, bcrypt
from flask_jwt_extended import create_access_token
from models import Utilisateur, Diagnostic
from ai_model import analyser_image_base64
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import random
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import create_access_token, create_refresh_token

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nom = data['nom']
    email = data['email']
    mot_de_passe = bcrypt.generate_password_hash(data['mot_de_passe']).decode('utf-8')

    user = Utilisateur(nom=nom, email=email, mot_de_passe=mot_de_passe)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Inscription réussie"}), 201



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Utilisateur.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.mot_de_passe, data['mot_de_passe']):
        token = create_access_token(identity=str(user.id))
        refresh = create_refresh_token(identity=str(user.id))
        return jsonify({"token": token,"refresh_token": refresh,"utilisateur_id": user.id})
    else:
        return jsonify({"erreur": "Identifiants invalides"}), 401
    
@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    email = data.get("email")
    user = Utilisateur.query.filter_by(email=email).first()
    if not user:
        return jsonify({"erreur": "Utilisateur non trouvé"}), 404

    code = str(random.randint(100000, 999999))
    user.code_verification = code
    db.session.commit()

    # cette ligne pour afficher le code dans le terminal :
    print(f"📨 Code de vérification pour {email} : {code}")

    return jsonify({"message": "Code de vérification envoyé"}), 200


@app.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")
    user = Utilisateur.query.filter_by(email=email).first()

    if user and user.code_verification == code:
        user.verifie = True
        user.code_verification = None
        db.session.commit()
        return jsonify({"message": "Utilisateur vérifié avec succès"}), 200
    else:
        return jsonify({"erreur": "Code invalide"}), 400
    
@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("nouveau_mot_de_passe")
    user = Utilisateur.query.filter_by(email=email).first()

    if user:
        user.mot_de_passe = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        return jsonify({"message": "Mot de passe mis à jour"}), 200
    else:
        return jsonify({"erreur": "Utilisateur non trouvé"}), 404
    
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
    data = request.get_json()
    image_b64 = data.get("image_base64")
    utilisateur_id = data.get("utilisateur_id")

    if not image_b64:
        return jsonify({"error": "Image manquante"}), 400

    resultat = analyser_image_base64(image_b64)

    diagnostic = Diagnostic(
        utilisateur_id=utilisateur_id,
        image_url="base64",
        maladie=resultat["maladie"],
        score=resultat["score"],
        date=datetime.utcnow()
    )
    db.session.add(diagnostic)
    db.session.commit()

    return jsonify(resultat)

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
