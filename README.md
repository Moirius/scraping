# 🎬 Assistant de Prospection Vidéo Intelligent (en cours de développement)

## 📌 Objectif

Développer un assistant intelligent pour les vidéastes, capable de :
- Trouver des entreprises locales (ex : “restauration Rennes”)
- Diagnostiquer leur présence en ligne et leur communication vidéo
- Collecter automatiquement leurs coordonnées et réseaux sociaux
- Générer un email de prospection personnalisé
- Être utilisable facilement (ex : via Telegram)
- Rester dans un environnement gratuit ou low-cost

---

## ⚙️ Fonctionnalités en cours

### 1. 🔍 Recherche d'entreprises locales
- Recherche via Google Places API
- Entrée : `mot-clé + ville`
- Exemple : `coiffure Brest` → 5 à 20 entreprises

### 2. 🌐 Scraping web + réseaux sociaux
Pour chaque entreprise :
- Scraping du site web (emails, liens vers les réseaux sociaux)
- Scraping des profils Instagram et Facebook (followers, likes, adresse, email…)
- Capacité à détecter et re-scraper un site web trouvé sur Facebook (⚠️ boucles infinies évitées)

### 3. 📩 Stockage structuré
- Base de données SQLite (`leads.sqlite`)
- Insertion automatique des leads, infos web, avis, réseaux sociaux

### 4. 🧠 Analyse (à venir)
- Détection de présence vidéo (reels, YouTube, etc.)
- Score d’opportunité
- Suggestions automatisées

### 5. ✉️ Email de prospection (à venir)
- Template dynamique avec diagnostic
- Export ou envoi automatisé

### 6. 🤖 Interface Telegram (à venir)
- Commande type : `/entreprises coiffure Brest`
- → renvoi de leads + diagnostic + email

---

## 🧰 Stack technique

| Composant         | Technologie                       |
|------------------|-----------------------------------|
| Scraping Web      | Playwright, Requests, BeautifulSoup |
| Réseaux sociaux   | Scraping dynamique (Facebook / Instagram) |
| Stockage          | SQLite                            |
| Analyse & Email   | GPT + règles simples (à venir)    |
| Interface Bot     | python-telegram-bot (à venir)     |
| Déploiement       | Render / Docker (prévu)           |

---

## 📁 Structure du projet

```

prospection-bretagne/
├── scraping/
│   ├── search\_google.py
│   ├── extract\_socials.py
│   ├── social\_playwright.py
│   └── save\_facebook\_session.py
├── utils/
│   ├── db.py
│   ├── logger.py
│   └── helpers.py
├── data/
│   └── leads.sqlite
├── templates/
│   └── mail\_template.txt (à venir)
├── telegram\_bot/
│   └── bot.py (à venir)
├── main.py
├── requirements.txt
└── README.md

````

---

1. Installer les dépendances :

```bash

pip install -r requirements.txt
```

2. Configurer vos clés d’API (Google, OpenAI...) dans un fichier `.env` ou directement dans le code :

📌 Si vous utilisez un agent IA (ex. : via une interface comme OpenAI), les clés API sont renseignées dans les paramètres d’environnement de l’interface.

📌 Sinon, les clés sont sauvegardées localement dans un fichier `.env`, à la racine du projet, par exemple :

GOOGLE_API_KEY=xxx
OPENAI_API_KEY=xxx


---

## ▶️ Utilisation

Lancer la version CLI :

```bash
python main.py
```

---

## ✅ État actuel

* ✔️ Scraping Google Maps
* ✔️ Scraping site web + réseaux sociaux (Facebook, Instagram)
* ✔️ Stockage en base
* 🚧 Scraping événementiel
* 🚧 Diagnostic automatisé
* 🚧 Génération d’email
* 🚧 Intégration Telegram

---

## 🔮 Idées futures

* Envoi automatique des emails
* Interface web de suivi
* Tableau de bord de scoring
* Relances programmées
* Version SaaS multi-utilisateurs

---