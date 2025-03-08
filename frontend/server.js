const express = require('express');
const fs = require('fs');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Fonction pour écrire dans un fichier
function writeLog(level, message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}\n`;
  fs.appendFileSync('logs.txt', logMessage);
}

// ✅ Ajoute cette route pour répondre aux requêtes GET sur "/"
app.get('/', (req, res) => {
  res.send('Serveur en ligne et opérationnel ! 🚀');
});

// Route API pour recevoir les logs
app.post('/log', (req, res) => {
  const { level, message } = req.body;
  writeLog(level, message);
  res.status(200).send('Log enregistré');
});

// Démarrer le serveur
app.listen(4000, () => console.log('Serveur de logs démarré sur le port 4000'));
