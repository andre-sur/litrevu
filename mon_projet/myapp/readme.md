## ⚙️ Dépendances

Ce projet nécessite Python 3.9+ et les bibliothèques suivantes :

- Django 5.1.7
- Pillow (pour la gestion des images)

Installez toutes les dépendances avec :

```bash
pip install -r requirements.txt

Dans l'ordre

# Étape 1 : Créer un environnement virtuel
python -m venv env

# Étape 2 : Activer l'environnement virtuel

# Sous Windows (PowerShell)
.\env\Scripts\Activate.ps1

# Sous Windows (cmd)
.\env\Scripts\activate

# Sous macOS/Linux
source env/bin/activate

# Étape 3 : Installer les dépendances via requirements.txt
pip install -r requirements.txt

# Étape 4 : Lancez l'application
dans le Terminal : python manage.py runserver

# Étape 5 : Ouvrez dans un navigateur la page (et entrez login et mot de passe)
http://localhost:8000/accounts/login/

Autre information pour les développeurs:
Voir les docstrings pour les fonctions
Accès direct à la base de données
http://localhost:8000/admin