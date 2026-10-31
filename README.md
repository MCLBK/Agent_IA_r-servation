# GrowUp AI — Assistant Voyage Intelligent

Plateforme SaaS de reservation de voyages propulsee par IA conversationnelle.

## Architecture

- **Backend** : Python 3.12 + FastAPI + SQLAlchemy + SQLite
- **Frontend** : Next.js 14 + React + TypeScript + Tailwind CSS
- **IA** : Mode Demo (regles) ou Ollama (Mistral, local)

## Demarrage rapide (developpement)

### Pre-requis

- Python 3.12+
- Node.js 20+
- (Optionnel) Ollama pour le mode IA

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Le backend demarre sur http://localhost:8000. Les donnees de demo sont chargees automatiquement.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend demarre sur http://localhost:3000.

### 3. Utilisation

- **Chat voyageur** : http://localhost:3000
- **Dashboard agence** : http://localhost:3000/login

Comptes de demo :
| Email | Mot de passe | Role |
|---|---|---|
| admin@demo.com | admin123 | Administrateur |
| agent@demo.com | agent123 | Agent |

## Deploiement Docker

```bash
docker-compose up --build
```

## Mode IA

Par defaut, la plateforme fonctionne en **mode Demo** (regles) sans aucune dependance IA.

Pour activer Ollama :
1. Installer Ollama : https://ollama.ai
2. Telecharger un modele : `ollama pull mistral`
3. Modifier `backend/.env` : `AI_PROVIDER=ollama`
4. Redemarrer le backend

## Structure du projet

```
agent_voyage/
  backend/
    app/
      ai/           # Agent conversationnel, prompts, providers
      api/          # Endpoints REST (auth, chat, catalog, bookings...)
      services/     # Logique metier (auth, catalog, booking)
      models.py     # Modeles SQLAlchemy
      schemas.py    # Schemas Pydantic
      config.py     # Configuration
      database.py   # Connexion BDD
      seed.py       # Donnees de demo
      main.py       # Application FastAPI
  frontend/
    src/
      app/
        page.tsx              # Chat voyageur
        login/                # Connexion
        dashboard/            # Espace professionnel
          page.tsx            # Tableau de bord
          catalog/            # Gestion du catalogue
          bookings/           # Gestion des reservations
          conversations/      # Suivi des conversations
          settings/           # Parametres
      lib/
        api.ts                # Client API
        auth.ts               # Gestion auth cote client
```

## Fonctionnalites

### Assistant voyageur
- Conversation guidee de l'inspiration a la reservation
- Recherche de destinations, vols, hotels
- Resume et confirmation de reservation
- Escalade automatique vers un conseiller humain

### Dashboard agence
- Tableau de bord avec KPI (conversations, reservations, CA, taux de conversion)
- Gestion du catalogue (destinations, vols, hotels)
- Suivi des reservations (confirmation, annulation)
- Consultation des conversations IA
- Parametres et securite

### Securite
- Authentification JWT
- Isolation multi-tenant
- Aucune donnee bancaire collectee dans le chat
- Pas de collecte de passeport (v1)
- Double verification des prix
- Protection anti prompt-injection
- Conformite RGPD

## Technologies (100% gratuites)

| Composant | Technologie |
|---|---|
| Backend | FastAPI, SQLAlchemy, SQLite |
| Frontend | Next.js 14, React, Tailwind CSS |
| IA | Ollama (local) ou mode Demo |
| Auth | JWT + bcrypt |
| Deploiement | Docker Compose |
