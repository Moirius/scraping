import os
import sys

# Ajoute la racine du projet au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from scraping.search_google import get_fake_results

# Charger les variables d'environnement depuis le .env
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("🚨 TELEGRAM_BOT_TOKEN est manquant dans le .env")

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenue sur le bot de prospection vidéo en Bretagne !\nUtilise la commande /entreprises <mot-clé> <ville>")

# Commande /entreprises
async def entreprises(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❗ Format attendu : /entreprises <mot-clé> <ville>")
        return

    keyword = context.args[0]
    city = " ".join(context.args[1:])

    await update.message.reply_text(f"🔍 Recherche en cours pour : *{keyword}* à *{city}*", parse_mode="Markdown")

    # Récupérer les entreprises fictives
    results = get_fake_results(keyword, city)

    if not results:
        await update.message.reply_text("Aucune entreprise trouvée.")
        return

    # Formatage propre des résultats
    for r in results:
        texte = f"""🏢 *{r['nom']}*
📍 {r['adresse']}
📞 {r['téléphone']}
🌐 {r['site'] or 'Site indisponible'}
✉️ {r['email'] or 'Email non trouvé'}"""
        await update.message.reply_text(texte, parse_mode="Markdown")

# Lancement du bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("entreprises", entreprises))
    print("🤖 Bot lancé. Ctrl+C pour arrêter.")
    app.run_polling()

if __name__ == "__main__":
    main()
