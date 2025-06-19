# Utilise l'image Playwright avec Python et navigateurs préinstallés
FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet
COPY . .

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Télécharger les navigateurs (déjà dans l’image, mais on s’assure)
RUN playwright install

# Lancer ton script Python principal
CMD ["python", "main.py"]
