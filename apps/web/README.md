# DocuFlow — Frontend

Interface de validation documentaire pour DocuFlow. Permet d'importer des factures, consulter les données extraites, les corriger et les exporter.

---

## Stack

| Outil | Rôle |
|---|---|
| Next.js 16 | Framework React (App Router) |
| TypeScript | Langage |
| Tailwind CSS v4 | Styles |
| shadcn/ui | Composants UI |
| TanStack Query | Gestion des requêtes et du cache |
| react-pdf | Visualisation des PDFs |
| lucide-react | Icônes |

---

## Structure

```
apps/web/
├── src/
│   ├── app/
│   │   ├── page.tsx                  # Liste des documents
│   │   ├── layout.tsx                # Layout global avec header
│   │   └── documents/[id]/page.tsx   # Page détail d'un document
│   ├── components/
│   │   ├── extraction-panel.tsx      # Panneau données extraites + correction
│   │   ├── import-button.tsx         # Bouton d'import de fichier
│   │   ├── pdf-viewer.tsx            # Visualiseur PDF avec zoom
│   │   ├── providers.tsx             # Provider TanStack Query
│   │   └── status-pill.tsx           # Badge de statut
│   └── lib/
│       └── api.ts                    # Client API DocuFlow
├── .env.local                        # Variables locales (non versionné)
└── next.config.ts                    # Configuration Next.js
```

---

## Prérequis

- Node.js 22+
- Backend DocuFlow en cours d'exécution sur `localhost:8000`

---

## Installation

```bash
cd apps/web
npm install
cp .env.local.example .env.local  # ou créer manuellement
```

---

## Variables d'environnement

| Variable | Description | Défaut |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | URL de base de l'API backend | `http://localhost:8000/api/v1` |

Créer un fichier `.env.local` :

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Démarrer en développement

```bash
npm run dev
```

L'interface est accessible sur `http://localhost:3000`.

---

## Build de production

```bash
npm run build
npm start
```

---

## Avec Docker Compose

Depuis la racine du dépôt :

```bash
docker compose up -d
```

Le frontend est accessible sur `http://localhost:3000`.
