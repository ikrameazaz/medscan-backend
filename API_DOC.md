
# 📘 API Documentation - MedScan Backend
Date de génération : 01/05/2025 22:16

## 🔐 Authentification
La majorité des routes nécessitent un token JWT dans l'en-tête `Authorization` :
```
Authorization: Bearer <VOTRE_TOKEN>
```

---

## 📝 POST /register
### ➤ Description : Inscription d’un nouvel utilisateur
- **URL** : `/register`
- **Méthode** : `POST`
- **Headers** : `Content-Type: application/json`
- **Body** :
```json
{
  "nom": "Amina",
  "email": "amina@test.com",
  "mot_de_passe": "1234"
}
```
- **Réponse** :
```json
{ "message": "Inscription réussie" }
```

---

## 🔐 POST /login
### ➤ Description : Connexion utilisateur
- **URL** : `/login`
- **Méthode** : `POST`
- **Body** :
```json
{
  "email": "amina@test.com",
  "mot_de_passe": "1234"
}
```
- **Réponse** :
```json
{
  "token": "<JWT_TOKEN>",
  "utilisateur_id": 1
}
```

---

## 📮 POST /verify
### ➤ Description : Demander un code de vérification (par email ou SMS simulé)
- **URL** : `/verify`
- **Méthode** : `POST`
- **Body** :
```json
{ "email": "amina@test.com" }
```
- **Réponse** :
```json
{ "message": "Code de vérification envoyé" }
```

---

## ✅ POST /verify-code
### ➤ Description : Vérifie le code reçu
- **URL** : `/verify-code`
- **Méthode** : `POST`
- **Body** :
```json
{
  "email": "amina@test.com",
  "code": "153110"
}
```
- **Réponse** :
```json
{ "message": "Utilisateur vérifié avec succès" }
```

---

## 🔁 POST /reset-password
### ➤ Description : Réinitialiser le mot de passe
- **URL** : `/reset-password`
- **Méthode** : `POST`
- **Body** :
```json
{
  "email": "amina@test.com",
  "nouveau_mot_de_passe": "123456"
}
```
- **Réponse** :
```json
{ "message": "Mot de passe mis à jour" }
```

---

## 👤 GET /me
### ➤ Description : Obtenir les infos du profil (JWT requis)
- **URL** : `/me`
- **Méthode** : `GET`
- **Headers** :
```
Authorization: Bearer <JWT_TOKEN>
```
- **Réponse** :
```json
{
  "id": 1,
  "nom": "Amina",
  "email": "amina@test.com",
  "verifie": true
}
```

---

## 🩺 POST /diagnostic
### ➤ Description : Envoyer une image encodée en base64 pour diagnostic
- **URL** : `/diagnostic`
- **Méthode** : `POST`
- **Body** :
```json
{
  "image_base64": "<BASE64_IMAGE>",
  "utilisateur_id": 1
}
```
- **Réponse** :
```json
{
  "maladie": "eczema",
  "score": 0.95
}
```

---

## 🔄 POST /refresh (optionnel)
### ➤ Description : Renouveler le token
- **URL** : `/refresh`
- **Méthode** : `POST`
- **Headers** :
```
Authorization: Bearer <VOTRE_TOKEN>
```
- **Réponse** :
```json
{ "token": "<NOUVEAU_TOKEN>" }
```

---

## ✅ Notes techniques
- Toutes les réponses sont en **JSON**
- L’API tourne sur `http://127.0.0.1:5000`
