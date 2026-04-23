# FastAPI Item Manager - Project Summary

## Overview
A FastAPI REST API with HTTP Basic Authentication, a polished frontend web UI, Docker support, and comprehensive tests.

## Architecture

```
fastapiexample/
├── main.py              # App entry point, mounts static files, serves frontend at /
├── auth.py              # HTTP Basic Auth dependency
├── requirements.txt     # All Python dependencies
├── test_main.py         # Pytest test suite (20 tests)
├── Dockerfile           # Container definition
├── docker-compose.yml   # Docker Compose setup
├── .dockerignore        # Docker build exclusions
├── .gitignore           # Git exclusions
├── static/
│   └── index.html       # Frontend web UI (single-page app)
└── routes/
    ├── __init__.py
    └── items.py         # All /items CRUD endpoints
```

## What Was Built

### 1. Backend API (`routes/items.py`)
- `GET /items/` — List all items (requires auth)
- `GET /items/{id}` — Get single item (requires auth)
- `GET /items/search?name=...` — Search items by name (requires auth)
- `POST /items/` — Create new item (requires auth)
- `PUT /items/{id}` — Update item (requires auth)
- `DELETE /items/{id}` — Delete item (requires auth)

### 2. Authentication (`auth.py`)
- HTTP Basic Authentication
- Two default users: `admin/admin123` and `user/user123`
- All `/items/*` routes require valid credentials

### 3. Frontend (`static/index.html`)
- **Login page** — Gradient background, centered card, smooth animations, input validation
- **Dashboard** — 4 stat cards (total items, in stock, out of stock, total value)
- **Live search** — Client-side filtering with instant results
- **Item table** — Hover effects, status badges, empty state handling
- **Modal form** — Add/Edit in centered modal with backdrop blur, ESC to close
- **Toast notifications** — Auto-dismiss with icons and smooth animations
- **Responsive** — Mobile-friendly layout
- **XSS-safe** — Content escaped before rendering
- Served at `http://localhost:8000/`

### 4. Docker
- `Dockerfile` — Python 3.11-slim based image
- `docker-compose.yml` — One-command deployment (no obsolete `version` field)
- Run with: `docker-compose up --build -d`

### 5. Tests (`test_main.py`)
- 20 tests covering:
  - Auth (valid, invalid, missing credentials)
  - Get items (list, single, structure, 404)
  - Create item (with defaults, custom stock)
  - Update item (name, price, stock, 404)
  - Delete item (success, count reduction, 404)
  - Search (existing, case-insensitive, no results)
  - Root endpoint (HTML response)

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

Or with Docker:
```bash
docker-compose up --build -d
```

Run tests:
```bash
pytest test_main.py -v
```

## Dependencies
- fastapi>=0.104.0
- uvicorn>=0.24.0
- pytest>=7.4.0
- httpx>=0.25.0
