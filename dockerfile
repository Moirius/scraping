FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN playwright install

# ⬇️ Lancer le bot
CMD ["python", "bot.py"]
