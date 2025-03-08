# Utilisation d'une image Python légère
FROM python:3.9-slim

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port 5000 (Flask par défaut)
EXPOSE 5000

# Définir la commande pour démarrer le service
CMD ["python", "app.py"]

