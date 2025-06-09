# MedScan - Backend API

Ce projet est le backend de l'application **MedScan**, un système intelligent de détection de maladies dermatologiques à partir d'images, développé avec **Flask**, **TensorFlow** et **JWT Auth**.

---

## 📁 Structure des fichiers

| Fichier / Dossier        | Rôle                                                                 |
|--------------------------|----------------------------------------------------------------------|
| `app.py`                 | Point d'entrée principal de l'application Flask.                     |
| `models.py`              | Définit les modèles de la base de données (`User`, `Diagnostic`).    |
| `routes.py`              | Contient toutes les routes API (authentification, diagnostic, etc.). |
| `ai_model.py`            | Gère le chargement et l'exécution du modèle IA pour l'analyse d'image.|
| `config.py`              | Paramètres de configuration (JWT, base de données, etc.).            |
| `requirements.txt`       | Liste des dépendances Python.                                        |
| `test/convert_base64.py` | Script pour encoder une image en base64 (utile pour les tests).      |
| `venv/`                  | Environnement virtuel Python (à ne pas versionner sur GitHub).       |

---

## 🔐 Authentification

L'authentification est basée sur **JWT**.  
Tu dois d’abord **t’inscrire** (`/register`), puis **te connecter** (`/login`) pour obtenir un **token JWT** à inclure ensuite dans les appels aux routes protégées.

Exemple d’en-tête :
```
Authorization: Bearer <JWT_TOKEN>
```

---

## 🔗 Endpoints disponibles

### 🔸 POST `/register`
**Créer un nouvel utilisateur**

**Body JSON :**
```json
{
  "email": "exemple@mail.com",
  "password": "motdepasse"
}
```

---

### 🔸 POST `/login`
**Connexion et récupération du token JWT**

**Body JSON :**
```json
{
  "email": "exemple@mail.com",
  "password": "motdepasse"
}
```

**Réponse :**
```json
{
  "token": "...."
}
```

---

### 🔸 POST `/diagnostic`
**Analyser une image encodée en base64**

**Headers :**
```
Authorization: Bearer <JWT_TOKEN>
```

**Body JSON :**
```json
{
  "image_base64": "<image encodée en base64>"
}
```

**Réponse :**
```json
{
  "maladie": "Nom_de_la_maladie",
  "score": 0.98
}
```

---

### 🔸 GET `/diagnosticsHistory`
**Récupérer l’historique des diagnostics de l’utilisateur connecté**

**Headers :**
```
Authorization: Bearer <JWT_TOKEN>
```

**Réponse :**
```json
[
  {
    "maladie": "Acné",
    "score": 0.93,
    "date": "2025-06-09 17:10"
  },
  ...
]
```

## Étapes d'installation et de configuration 

### Prérequis

- Python 3.11 (ou compatible avec le projet)
- `git` installé
- Connexion Internet
- Un terminal (CMD, PowerShell ou VS Code Terminal)

### 1. Cloner le projet

```bash
git clone https://github.com/ikrameazaz/medscan-backend.git
cd medscan-backend
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
```

### ▶3. Activer l’environnement virtuel

#### Sous Windows :

```bash
.env\Scriptsctivate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

> ⚠️ Si TensorFlow échoue à s’installer, il faut utiliser une version compatible avec ton Python (ex : `tensorflow==2.15.0` pour Python 3.11)

### 5. Créer un fichier `.env` à la racine avec :

```env
SECRET_KEY=ton_cle_secrete
JWT_SECRET_KEY=ta_cle_jwt
DATABASE_URL=sqlite:///db.sqlite3
```

Ou configure avec PostgreSQL :

```env
DATABASE_URL=postgresql://utilisateur:motdepasse@localhost:5432/medscan_db
```

### 6. Placer le modèle IA dans le bon dossier

Créer un dossier `models/` à la racine si ce n’est pas déjà fait et y mettre :

```
models/dermato_model.h5
```

---

---

## Tester avec Postman

1. **Inscription** via `/register`
2. **Connexion** via `/login` et récupération du token
3. **Envoi d’un diagnostic** via `/diagnostic` :
   - Token valide
   - Image encodée en base64 (peut être générée avec `test/convert_base64.py`)
4. **Consultation de l’historique** via `/diagnosticsHistory`

---

## 🛠 Outils recommandés

- ✅ [Postman](https://www.postman.com/) : test des API
- ✅ Python 3.11 ou plus
- ✅ [Visual Studio Code](https://code.visualstudio.com/) + extension Python
- ✅ Git pour la gestion de version
- ✅ [TensorFlow](https://www.tensorflow.org/) pour le modèle IA

---

## 👤 Auteur

👩‍💻 **Ikrame Azaz** — Développement backend & IA  
🌐 Projet collaboratif — Backend relié à un frontend React