FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

# Assure que Playwright utilise le dossier partagé pour les navigateurs
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN playwright install

# Lance le bot depuis son sous-dossier
CMD ["python", "telegram_bot/bot.py"]
