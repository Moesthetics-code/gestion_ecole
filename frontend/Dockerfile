# Étape 1 : Construire l'application React
FROM node:16 AS build

WORKDIR /app

# Copiez le package.json et package-lock.json
COPY package.json package-lock.json ./

# Installez les dépendances
RUN npm install

# Copiez tous les fichiers sources
COPY . .

# Construisez l'application
RUN npm run build

# Étape 2 : Configurer Nginx pour servir l'application
FROM nginx:alpine

# Supprimer le contenu par défaut de Nginx
RUN rm -rf /usr/share/nginx/html/*

# Copiez les fichiers générés par la construction de React dans le dossier de Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Exposez le port utilisé par Nginx
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
