# Family Dashboard

Local-network credit-card benefit tracker for the family. Built with FastAPI + Next.js, served behind Caddy in Docker.

## Quick start

```bash
cd family-dashboard
docker-compose up -d --build
```

Then open http://localhost (or `http://<mac-mini-ip>` from another device on the LAN).

The first time, go to **+ New** and add a Cardholder (you, your partner), then add Cards (use the preset dropdown for Chase / Amex defaults).

## Common commands

| Action            | Command                                                  |
|-------------------|----------------------------------------------------------|
| Start (build)     | `docker-compose up -d --build`                            |
| Stop              | `docker-compose down`                                     |
| View logs         | `docker-compose logs -f`                                  |
| Backup SQLite     | `cp data/db.sqlite data/db.$(date +%Y%m%d).sqlite`        |
| Reset (DANGER)    | `docker-compose down && rm -f data/db.sqlite && docker-compose up -d` |

## Architecture

- **backend/** — FastAPI + SQLAlchemy + SQLite (port 8000)
- **frontend/** — Next.js 14 App Router + Tailwind (port 3000)
- **caddy/** — Reverse proxy on port 80, routes `/api/*` to backend, everything else to frontend
- **data/** — SQLite file, mounted into backend container (the only stateful directory)

## Backend tests

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Hostname (optional)

To access via `http://dashboard.local`, set up mDNS on the Mac Mini (the host
already advertises its `.local` name). Alternatively, edit `/etc/hosts` on
each device:

```
192.168.X.Y  dashboard.local
```

## Not in MVP (planned)

- Discord/webhook reminder push
- Net-benefit historical charts
- Plaid auto-import
- Auth (currently relies on LAN-only access)
