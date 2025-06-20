import os
import sys
import asyncio
import time

# Ajoute la racine du projet au path pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import Conflict

from scraping.search_google import search_google_places
from main import run_pipeline
from utils.logger import logger

# Chargement des variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
# Render fournit la variable PORT lors de l'utilisation d'un Web Service
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", os.getenv("PORT", "8443")))

if not BOT_TOKEN:
    raise ValueError("🚨 TELEGRAM_BOT_TOKEN est manquant dans le .env")

DB_PATH = os.path.join("data", "leads.sqlite")
LOG_PATH = "scraping.log"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Message d'accueil et aide."""
    text = (
        "🤖 *Bot de prospection*\n"
        "\nCommandes disponibles :\n"
        "/run - lancer main.py\n"
        "/db - récupérer la base SQLite\n"
        "/logs - recevoir les logs\n"
        "/entreprises <mot> <ville> - recherche rapide"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def run_scraping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Exécute run_pipeline en tâche de fond et renvoie le résultat."""
    await update.message.reply_text("🚀 Lancement du scraping...")

    loop = asyncio.get_event_loop()

    def _run():
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            run_pipeline()
        return buf.getvalue()

    output = await loop.run_in_executor(None, _run)
    await update.message.reply_text("✅ Terminé")

    if output:
        snippet = output[-4000:]
        await update.message.reply_text(f"```\n{snippet}\n```", parse_mode="Markdown")


async def send_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envoie la base SQLite."""
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "rb") as f:
            await update.message.reply_document(f)
    else:
        await update.message.reply_text("❌ Base de données introuvable")


async def send_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envoie le fichier de logs."""
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "rb") as f:
            await update.message.reply_document(f)
    else:
        await update.message.reply_text("❌ Fichier de logs introuvable")


async def entreprises(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recherche rapide d'entreprises via Google Places."""
    if len(context.args) < 2:
        await update.message.reply_text("❗ Format : /entreprises <mot-clé> <ville>")
        return

    keyword = context.args[0]
    city = " ".join(context.args[1:])
    await update.message.reply_text(f"🔍 Recherche pour {keyword} à {city}")

    results = search_google_places(keyword, city, max_results=5)
    if not results:
        await update.message.reply_text("Aucune entreprise trouvée")
        return

    for r in results:
        texte = (
            f"🏢 *{r.get('nom', '')}*\n"
            f"📍 {r.get('adresse', 'N/A')}\n"
            f"📞 {r.get('téléphone', 'N/A')}\n"
            f"🌐 {r.get('site', 'N/A')}"
        )
        await update.message.reply_text(texte, parse_mode="Markdown")


def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_scraping))
    app.add_handler(CommandHandler("db", send_db))
    app.add_handler(CommandHandler("logs", send_logs))
    app.add_handler(CommandHandler("entreprises", entreprises))

    logger.info("🤖 Bot lancé")

    while True:
        try:
            if WEBHOOK_URL:
                app.run_webhook(
                    listen="0.0.0.0",
                    port=WEBHOOK_PORT,
                    webhook_url=WEBHOOK_URL,
                    drop_pending_updates=True,
                )
            else:
                app.run_polling(drop_pending_updates=True)
            break
        except Conflict:
            logger.warning("⚠️ Bot déjà actif ailleurs, nouvelle tentative dans 5s")
            time.sleep(5)
        except Exception:
            logger.error("❌ Erreur inattendue", exc_info=True)
            time.sleep(5)


if __name__ == "__main__":
    main()
