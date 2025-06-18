# 🎬 Assistant de Prospection Vidéo Intelligent

## 📌 Objectif
Développer un outil automatisé de prospection pour vidéastes, permettant de :
- Trouver des entreprises locales (Bretagne) selon un mot-clé (ex. "restauration Rennes")
- Diagnostiquer leur présence en ligne et leur communication vidéo
- Générer un email de prospection personnalisé
- Être utilisable facilement via Telegram
- Rester dans un environnement gratuit ou low-cost

## ⚙️ Fonctionnalités

### 1. 🔍 Recherche d'entreprises
- Scraping via Google Maps / PagesJaunes
- Entrée : mot-clé + localisation
- Résultat : liste d’entreprises locales (5 à 20)

### 2. 📦 Scraping de données utiles
Pour chaque entreprise :
- Nom, adresse, téléphone, email, site
- Réseaux sociaux (Instagram, Facebook, LinkedIn, etc.)
- Nom du responsable (si dispo)
- Description d’activité, dernière publication, etc.

### 3. 🧠 Diagnostic
- Analyse de leur présence vidéo (YouTube, reels, etc.)
- Score d’opportunité
- Recommandations automatiques

### 4. ✉️ Génération d’email
- Template dynamique
- Ajout automatique du diagnostic
- Email personnalisable

### 5. 🤖 Interface Telegram
Commande simple :
```
/entreprises coiffure Brest
```

→ Liste enrichie + diagnostic + email prêts à l'emploi

### 6. 🎉 Scraping d’événements locaux
- Nom, date, lieu, contact
- Analyse des opportunités vidéo (captation, teaser…)

## 🧰 Stack Technique

| Composant | Technologie |
|----------|-------------|
| Scraping Web | Playwright / BeautifulSoup / Requests |
| Bot Telegram | python-telegram-bot |
| Stockage | SQLite (PostgreSQL optionnel) |
| Diagnostic | GPT (prompt + règles simples) |
| Déploiement | Render.com (free tier) |
| Export | CSV / Google Sheets (optionnel) |

## 📁 Structure du projet

```
prospection-bretagne/
├── scraping/
│   ├── search_google.py
│   ├── extract_socials.py
│   └── analyse_presence.py
├── telegram_bot/
│   └── bot.py
├── data/
│   └── leads.sqlite
├── templates/
│   └── mail_template.txt
├── utils/
│   └── format_diagnostic.py
├── cron/
│   └── check_events.py
├── main.py
├── requirements.txt
└── README.md
```

## 🚀 Installation

```bash
git clone https://github.com/votre-user/prospection-bretagne.git
cd prospection-bretagne
pip install -r requirements.txt
```

Configurer le bot Telegram via `.env` :

```
TELEGRAM_TOKEN=xxx
OPENAI_API_KEY=xxx
```

## ▶️ Utilisation

Lancer le bot :
```bash
python main.py
```

Depuis Telegram :
```bash
/entreprises restauration Rennes
```

## 🗺️ Roadmap MVP

- ✅ Définir fiche projet
- ✅ Créer bot Telegram test
- ✅ Scraper entreprises (Google Maps)
- ⏳ Scraper réseaux sociaux
- ⏳ Diagnostiquer présence vidéo
- ⏳ Générer email personnalisé
- ⏳ Scraper événements
- ⏳ Déploiement Render

## 🔮 Idées v2+

- Envoi automatique des emails
- Interface web de suivi
- IA scoring avancé
- Historique, relances automatisées

## 🤝 Contribuer

Pull requests bienvenues ! Contact : `prenom.nom@email.com`
