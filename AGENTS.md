# AGENTS.md – Guide de Développement pour Codex

## 🎯 Objectif du Projet

Ce dépôt contient une application Python nommée **Assistant de Prospection Vidéo Intelligent**. Elle automatise la prospection de clients locaux en détectant leur présence en ligne, analysant leur contenu vidéo, et générant un email de contact personnalisé.

Codex est invité à contribuer à l'amélioration et au développement de cette application, en suivant les indications ci-dessous.

---

## 🧭 Structure Fonctionnelle

```

scraping/
├── main.py                  # Point d’entrée de l’application
├── requirements.txt         # Dépendances Python
├── .env                     # Variables sensibles (API keys)
│
├── scraping/                # Scraping et analyse de données externes
│   ├── search\_google.py         → recherche d'entreprises locales
│   ├── extract\_socials.py       → détection des réseaux sociaux
│   ├── social\_playwright.py     → scraping dynamique (Playwright)
│   ├── save\_facebook\_session.py
│   └── save\_instagram\_session.py
│
├── telegram\_bot/            # Interface utilisateur via Telegram
│   └── bot.py
│
├── utils/                   # Fonctions utilitaires
│   ├── db.py                    → gestion de la base SQLite
│   └── logger.py                → journalisation
│
├── templates/               # Modèle d'email de prospection
│   └── mail\_template.txt
│
├── cron/                    # Tâches automatisées
│   └── check\_events.py          → scraping d’événements locaux
│
├── data/                    # Données locales
│   └── leads.sqlite
│
├── cookies/                 # Sessions de réseaux sociaux
│   ├── fb\_auth.json
│   └── ig\_auth.json
│
├── logs/                    # Logs d’exécution
│   └── prospection.log
│
├── tests/                   # Tests unitaires
│   ├── test\_db.py
│   └── test\_extract_socials.py
│
├── README.md
└── AGENTS.md

````

---

## ✅ Tâches attendues de Codex

### 🔧 Amélioration technique
- Refactoriser les modules longs ou imbriqués
- Modulariser `bot.py` pour séparer logique et affichage
- Ajouter des types (`type hints`) dans les fonctions clés
- Centraliser les constantes (ex. endpoints, sélecteurs, regex)

### 🚀 Développement de fonctionnalités
- Ajouter la détection de TikTok, LinkedIn et YouTube
- Générer un score d’opportunité vidéo pour chaque entreprise
- Ajouter la commande `/evenements <ville>` au bot Telegram
- Proposer un résumé des événements filmables

### 🧪 Tests
- Ajouter des tests unitaires avec `pytest` dans `tests/`
- Cibler les modules : `db.py`, `extract_socials.py`, `diagnostics` (à créer)

### ✨ Interface & expérience
- Améliorer les messages Telegram pour qu'ils soient plus lisibles
- Ajouter des emojis pour clarifier le diagnostic automatique

---

## ⚙️ Instructions techniques

### Installation des dépendances

```bash
pip install -r requirements.txt
````

### Linting

```bash
black .
```

Optionnel :

```bash
pip install ruff
ruff check .
```

### Tests

```bash
pytest -q
```

---

## 🧠 Bonnes pratiques pour Codex

* Lire les fichiers `search_google.py`, `extract_socials.py`, `bot.py` en priorité
* Commiter par fonctionnalité ou correction
* Proposer une PR claire avec :

  * Titre : `[module] Brève description`
  * Exemple : `[scraping] Ajout détection TikTok`

---

## 🧩 Missions typiques que tu recevras

```text
[MISSION] Ajouter le support LinkedIn dans extract_socials.py
[MISSION] Créer une commande /evenements <ville> dans bot.py
[MISSION] Générer un score dans analyse_presence.py selon 5 critères
[MISSION] Refactorer le logging dans scraping/ et utils/
```

---

## 🔐 Variables sensibles

Les clés API (comme `OPENAI_API_KEY`) sont **déjà définies dans l’environnement Codex**.

Pas besoin de fichier `.env` dans ce dépôt.  
Assure-toi simplement que les variables suivantes sont présentes dans l’environnement Codex :

- `OPENAI_API_KEY` : pour l’accès à l’API OpenAI
- `TELEGRAM_TOKEN` : pour contrôler le bot Telegram

💡 Ces variables sont injectées automatiquement dans le runtime par Codex.
---

## 📌 Notes

* L’environnement Python utilisé est 3.10+
* Le scraping utilise **Playwright** (headless browser) → penser aux délais/erreurs
* `leads.sqlite` contient les prospects collectés → éviter de la supprimer en développement

---

Merci Codex 🙌. Tu peux commencer à travailler sur la mission suivante.

```
