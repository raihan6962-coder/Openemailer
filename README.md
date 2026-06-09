# Openmailer

Enterprise-grade email marketing, deliverability, lead outreach, email warmup, CRM, automation, and inbox management SaaS platform.

## Tech Stack

**Backend:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, Celery, Redis  
**Frontend:** Next.js 14, TypeScript, TailwindCSS, Shadcn UI, React Query, Zustand  
**Infrastructure:** Docker, Railway, Celery Workers

## Architecture

- **Multi-tenant** with row-level isolation via `workspace_id`
- **Async-first** using FastAPI async + async SQLAlchemy + aiosmtplib
- **Modular** with Repository pattern, Service layer, and clean separation
- **Event-driven** via Celery workers and APScheduler cron jobs

## Quick Start

### Docker

```bash
docker-compose -f deployment/docker-compose.yml up -d
```

### Manual

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed_data
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Project Structure

```
openmailer/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, security, database, dependencies
│   │   ├── models/        # SQLAlchemy models (50+ tables)
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── repositories/  # Data access layer
│   │   ├── services/      # Business logic layer
│   │   ├── api/v1/        # REST API routes
│   │   ├── workers/       # Celery async tasks
│   │   ├── scheduler/     # APScheduler jobs
│   │   └── tasks/         # Scheduled task implementations
│   ├── alembic/           # Database migrations
│   └── tests/             # Unit, integration, API tests
├── frontend/
│   ├── app/               # Next.js App Router pages
│   ├── components/        # React components (UI, forms, charts)
│   ├── lib/               # Utilities, API client
│   ├── store/             # Zustand state management
│   ├── hooks/             # React Query hooks
│   └── types/             # TypeScript definitions
├── deployment/            # Docker, Railway, Procfile configs
├── scripts/               # Bootstrap and migration scripts
└── docs/                  # Documentation
```

## Modules

1. **Authentication** - JWT, OAuth (Google/Outlook), MFA, RBAC, teams, workspaces
2. **Email Accounts** - SMTP/IMAP/OAuth connections, credential encryption
3. **Deliverability** - SPF/DKIM/DMARC/MX checks, DNS health, reputation scoring
4. **Email Warmup** - Auto-sending engine, human-like patterns, network exchange
5. **Spam Recovery** - Auto-detect spam, move to inbox, positive engagement signals
6. **Lead Management** - CSV/XLSX/Sheets import, auto field detection, Pandas processing
7. **Email Validation** - Syntax, MX, SMTP validation, catch-all/disposable detection
8. **Campaigns** - One-time, drip, follow-up, recurring; mailbox/domain rotation
9. **Template Builder** - Drag-drop editor, MJML, rich text, version control
10. **Inbox Management** - Unified inbox, folders, star/label/archive, reply detection
11. **CRM** - Contacts, companies, deals, pipelines, lead scoring, activity timeline
12. **Automation** - Visual workflow builder, triggers, actions, execution engine
13. **Analytics** - Event tracking, rates, charts, daily/weekly/monthly reports
14. **Billing** - Plans (Free/Starter/Growth/Agency), subscriptions, usage limits
15. **Webhooks & API** - REST API with JWT, API keys, rate limiting, OpenAPI docs

## API Documentation

With the server running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
