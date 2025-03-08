# Utilisation de l'image Python
FROM python:3.9

# Installer curl et autres dépendances (si nécessaire)
RUN apt-get update && apt-get install -y curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Ajouter wait-for-it à l'image Docker
RUN curl -sS https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /usr/local/bin/wait-for-it \
    && chmod +x /usr/local/bin/wait-for-it

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers dans l'image Docker
COPY . .

# Copier les fichiers nécessaires et Installation des dépendances
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exposition du port utilisé (changer selon le service)
EXPOSE 5001  

# Commande pour démarrer le service (attend la base de données et exécute les migrations, puis lance l'application)
# Copier et rendre le script de démarrage exécutable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Définir le script d'entrée
ENTRYPOINT ["/app/entrypoint.sh"]
