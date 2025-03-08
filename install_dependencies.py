import os
import subprocess
import sys
import platform

# Chemin du dossier contenant les micro-services
SERVICES_DIR = "services"

def install_requirements(service_path):
    """Installe les dépendances d'un micro-service."""
    requirements_file = os.path.join(service_path, "requirements.txt")
    
    if os.path.exists(requirements_file):
        print(f"\n🔹 Installation des dépendances pour {service_path}...")

        # Création de l'environnement virtuel
        venv_path = os.path.join(service_path, "venv")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)

        # Détection de l'OS et choix de la commande d'activation
        if platform.system() == "Windows":
            # Détection de l'environnement (PowerShell ou cmd)
            shell = os.getenv('SHELL', '').lower()
            if 'powershell' in shell:
                activate_script = os.path.join(venv_path, "Scripts", "Activate.ps1")
                command = f"powershell {activate_script}; pip install -r {requirements_file}"
            else:
                activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
                command = f'cmd /c "{activate_script} && pip install -r {requirements_file}"'
        else:  # Linux/macOS
            activate_script = os.path.join(venv_path, "bin", "activate")
            command = f"bash -c 'source {activate_script} && pip install -r {requirements_file}'"

        # Exécuter la commande
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"✅ Installation terminée pour {service_path}!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation dans {service_path}: {e}")
    else:
        print(f"⚠️ Aucun fichier requirements.txt trouvé dans {service_path}")

def main():
    """Parcourt tous les micro-services et installe leurs dépendances."""
    if not os.path.exists(SERVICES_DIR):
        print(f"⚠️ Le dossier '{SERVICES_DIR}' n'existe pas.")
        return

    for service in os.listdir(SERVICES_DIR):
        service_path = os.path.join(SERVICES_DIR, service)
        if os.path.isdir(service_path):
            install_requirements(service_path)

if __name__ == "__main__":
    main()
