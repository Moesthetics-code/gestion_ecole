# Utiliser une image de base Python avec les outils nécessaires
FROM python:3.9-slim

# Définir un répertoire de travail pour le projet
WORKDIR /app

# Copier les fichiers de l'application (code et tests) dans l'image Docker
COPY . /app

# Installer les dépendances nécessaires, y compris pytest
RUN pip install --no-cache-dir -r requirements.txt

# Installer les outils nécessaires (par exemple, PostgreSQL si besoin)
RUN apt-get update && apt-get install -y postgresql-client

# Définir une commande par défaut pour exécuter les tests via pytest
CMD ["pytest"]
