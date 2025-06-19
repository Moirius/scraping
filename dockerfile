# Utilise l'image officielle Playwright avec toutes les dépendances
FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet
COPY . .

# Installer les dépendances Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Playwright est déjà installé dans l'image, mais on s'assure que les navigateurs le sont
RUN playwright install

# Lancement de ton script (change selon ton point d’entrée)
CMD ["python", "main.py"]
