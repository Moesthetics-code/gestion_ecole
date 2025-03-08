class Logger {
    log(level, message) {
      const timestamp = new Date().toISOString();
      const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  
      console.log(logMessage); // Toujours afficher dans la console
  
      // Envoyer les logs au serveur Node.js
      fetch('http://localhost:4000/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level, message })
      }).catch(err => console.error('Erreur lors de l’envoi des logs', err));
    }
  
    info(message) {
      this.log('info', message);
    }
  
    error(message) {
      this.log('error', message);
    }
  }
  
  const logger = new Logger();
  export default logger;
  