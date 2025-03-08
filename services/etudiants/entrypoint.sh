#!/bin/sh

echo "⏳ Attente de la base de données PostgreSQL..."
wait-for-it db_etudiants:5432 --timeout=30 --strict -- echo "✅ Base de données prête !"

# Vérifier si les migrations existent déjà
if [ ! -d "migrations" ]; then
    echo "📂 Initialisation de la migration..."
    flask db init
fi

echo "🔄 Exécution des migrations..."
flask db migrate -m "Automated migration" || true  # Évite les erreurs si aucun changement
flask db upgrade || true  # Évite les erreurs si la base est déjà à jour

echo "🚀 Lancement de l'application Flask..."
exec python app.py
