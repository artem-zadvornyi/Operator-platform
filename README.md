# Operator

**Build a business. Not just content.**

Operator is a production-grade SaaS platform for running real operations. This monorepo contains the engineering foundation: backend API, web frontend, shared contracts, and internal packages.

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS |
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2 |
| **Tooling** | Poetry, ESLint, Prettier, Ruff, pytest |

## Repository Layout

```
Operator/
├── backend/          # FastAPI API, workers, persistence
│   └── app/
│       ├── api/      # HTTP layer (routes, dependencies)
│       ├── core/     # Configuration, cross-cutting concerns
│       ├── db/       # Engine, sessions, declarative base
│       ├── models/   # SQLAlchemy ORM models
│       ├── schemas/  # Pydantic request/response models
│       ├── services/ # Business logic
│       ├── repositories/ # Data access
│       ├── workers/  # Background jobs
│       └── utils/
├── frontend/         # Next.js App Router application
│   ├── app/          # Routes and layouts
│   ├── components/   # Shared UI building blocks
│   ├── features/     # Feature-scoped modules
│   ├── hooks/        # React hooks
│   ├── lib/          # Client utilities
│   ├── services/     # API clients
│   ├── types/        # TypeScript types
│   └── styles/       # Global styles
├── shared/           # Cross-service contracts
│   ├── types/        # Shared type definitions
│   └── contracts/    # API schemas, enums, constants
├── packages/         # Internal reusable packages
├── docs/             # Architecture and product documentation
├── scripts/          # Developer and operational scripts
├── docker/           # Container definitions
└── infrastructure/   # Infrastructure-as-code
```

## Local Development

### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Node.js 20+
- PostgreSQL (for backend persistence)

### Backend

```bash
cd backend
poetry install
cp .env.example .env
poetry run operator-api
```

Migrations: `poetry run alembic upgrade head`

Quality: `poetry run ruff check . && poetry run pytest`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Quality: `npm run lint && npm run build`

### Environment

Copy `.env.example` files into each service. Never commit secrets. See `backend/.env.example` and `frontend/.env.example` for available variables.

## License

MIT — see [LICENSE](LICENSE).
