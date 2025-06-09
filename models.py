from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    mot_de_passe = db.Column(db.String(200))
    verifie = db.Column(db.Boolean, default=False)
    code_verification = db.Column(db.String(6), nullable=True)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)

class Diagnostic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))
    image_url = db.Column(db.String(200))
    maladie = db.Column(db.String(100))
    score = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)

