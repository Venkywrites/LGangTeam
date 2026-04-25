# LGangTeam 
1st Project - Docker demo 

# Docker End-to-End Project Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Steps We Followed](#steps-we-followed)
4. [Functional Workflow](#functional-workflow)
5. [Key Docker Concepts Used](#key-docker-concepts-used)
6. [Interview Summary](#interview-summary)

---

## Project Overview

We built a **Task Manager web application** deployed entirely using Docker. The app lets users create, complete, and delete tasks — with a Python backend, a database for persistence, a cache layer for performance, and a web server as the entry point.

**Stack:**
| Service | Technology | Purpose |
|---------|-----------|---------|
| Web Server | Nginx 1.27 | Reverse proxy + serve frontend files |
| Backend API | Flask (Python) + Gunicorn | REST API handling all business logic |
| Database | PostgreSQL 16 | Store tasks permanently |
| Cache | Redis 7 | Cache API responses for 60 seconds |

---

## Architecture

```
                        ┌─────────────────────────────────────┐
                        │           EC2 Instance               │
                        │                                     │
Browser ──── port 8080 ──►  ┌──────────┐                     │
                        │  │  Nginx   │  (frontend_net)       │
                        │  └────┬─────┘                       │
                        │       │ /api/* proxied               │
                        │  ┌────▼──────┐                      │
                        │  │  Flask   │  (backend_net         │
                        │  │ +Gunicorn│   + frontend_net)     │
                        │  └────┬──────┘                      │
                        │       │                             │
                        │  ┌────▼──────┐  ┌──────────┐       │
                        │  │ PostgreSQL│  │  Redis   │       │
                        │  └───────────┘  └──────────┘       │
                        └─────────────────────────────────────┘
```

**Two isolated Docker networks:**
- `frontend_net` — Nginx ↔ Flask only
- `backend_net` — Flask ↔ PostgreSQL ↔ Redis only

This means the database is never directly reachable from the web.

---

## Steps We Followed

### Step 1 — Project Structure
Created the following folder layout:
```
LGangTeam/
├── backend/          # Flask API
│   ├── app.py
│   ├── requirements.txt
│   ├── entrypoint.sh
│   └── Dockerfile
├── frontend/         # Static HTML/CSS/JS
│   ├── index.html
│   ├── style.css
│   └── app.js
├── nginx/            # Reverse proxy config
│   ├── nginx.conf
│   └── Dockerfile
├── postgres/
│   └── init.sql      # DB schema + seed data
├── docker-compose.yml
├── .env.example
└── Jenkinsfile
```

### Step 2 — Flask Backend (`backend/app.py`)
- Built a REST API with 5 endpoints: GET/POST tasks, PUT (update), DELETE, and /stats
- Connected to PostgreSQL using SQLAlchemy ORM
- Connected to Redis for response caching
- Wrapped in Gunicorn (production WSGI server, not Flask dev server)

### Step 3 — Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get install postgresql-client   # needed for pg_isready in entrypoint
COPY requirements.txt . && pip install  # install dependencies first (layer caching)
COPY . .                                # then copy source code
HEALTHCHECK ...                         # Docker monitors container health
ENTRYPOINT ["./entrypoint.sh"]
```

### Step 4 — Entrypoint Script (`backend/entrypoint.sh`)
Solves the **startup ordering problem**:
```
1. Loop: wait until PostgreSQL is ready (pg_isready)
2. Run: create database tables (db.create_all)
3. Start: gunicorn
```
Without this, Flask would crash on startup because PostgreSQL isn't ready yet.

### Step 5 — Nginx Config (`nginx/nginx.conf`)
```
/           → serve static files from /usr/share/nginx/html
/api/*      → proxy_pass to Flask backend:5000
/health     → proxy_pass to Flask /health
```
Nginx acts as the single entry point — users never talk directly to Flask.

### Step 6 — Nginx Dockerfile (`nginx/Dockerfile`)
Build context is the **project root** (set in docker-compose.yml), so paths are:
```dockerfile
COPY nginx/nginx.conf /etc/nginx/conf.d/app.conf
COPY frontend /usr/share/nginx/html      # bundle static files into the image
```

### Step 7 — PostgreSQL Init Script (`postgres/init.sql`)
- Automatically runs on **first container start** (mounted to `/docker-entrypoint-initdb.d/`)
- Creates the `tasks` table
- Seeds 2 demo rows

### Step 8 — Docker Compose (`docker-compose.yml`)
Ties everything together:
- **Health checks** on postgres and redis with `pg_isready` and `redis-cli ping`
- **`depends_on: condition: service_healthy`** — backend only starts after DB and Redis are confirmed healthy
- **Named volumes** (`postgres_data`, `redis_data`) — data survives container restarts
- **Two networks** — security isolation between tiers
- **Environment variables** from `.env` file

### Step 9 — Frontend (`frontend/`)
- Pure HTML/CSS/JS — no framework needed
- `app.js` uses `fetch()` to call `/api/tasks`, `/api/stats`
- Shows a "cached" badge when Redis serves the response
- Handles create, toggle complete, and delete

### Step 10 — Jenkinsfile (CI/CD Pipeline)
Defines 5 stages:
```
Checkout → Lint (Hadolint) → Build Images → Start Services → Health Check + Smoke Test
```
Post step always runs `docker-compose down -v` to clean up.

### Step 11 — EC2 Deployment
1. Launched EC2 instance (Amazon Linux)
2. Installed Docker + Docker Compose
3. Cloned the repository
4. Opened port 8080 in the EC2 Security Group (inbound rule)
5. Fixed `docker-buildx` format error with `DOCKER_BUILDKIT=0`
6. Ran `docker-compose up --build -d`

---

## Functional Workflow

### What happens when a user opens the app:

```
1. Browser hits http://<ec2-ip>:8080
2. Nginx receives the request
3. For / → Nginx serves index.html, style.css, app.js directly from its image
4. Browser runs app.js which calls GET /api/tasks and GET /api/stats
5. Nginx proxies /api/* to Flask on port 5000
6. Flask checks Redis for cached tasks
   ├── Cache HIT  → return tasks immediately (fast), set "cached: true"
   └── Cache MISS → query PostgreSQL, store result in Redis for 60s, return tasks
7. Browser renders the task list
```

### What happens when a user adds a task:

```
1. User types title + description, clicks "Add Task"
2. app.js sends POST /api/tasks with JSON body
3. Nginx proxies to Flask
4. Flask validates input, inserts row into PostgreSQL
5. Flask deletes the Redis cache key (cache invalidation)
6. Flask returns the new task as JSON (HTTP 201)
7. app.js calls refresh() → fetches updated task list and stats
```

### What happens when a user completes a task:

```
1. User clicks the circle checkbox
2. app.js sends PUT /api/tasks/:id with { "completed": true }
3. Flask updates the row in PostgreSQL
4. Flask invalidates Redis cache
5. UI refreshes
```

### How Redis caching works:

```
First GET /api/tasks:
  Redis → miss → query Postgres → store in Redis with 60s TTL → return

Next GET /api/tasks (within 60s):
  Redis → HIT → return immediately (no Postgres query)
  UI shows "cached" badge

After any write (POST/PUT/DELETE):
  Redis key is deleted immediately
  Next GET will query Postgres fresh again
```

---

## Key Docker Concepts Used

| Concept | Where | Why |
|---------|-------|-----|
| **Multi-service Compose** | docker-compose.yml | Run 4 services with one command |
| **Named volumes** | postgres_data, redis_data | Data persists across restarts |
| **Custom networks** | backend_net, frontend_net | Isolate DB from public-facing services |
| **Health checks** | All 4 services | Ensure services are truly ready, not just started |
| **depends_on (condition)** | backend → postgres, redis | Start order based on health, not just container start |
| **Build context** | nginx build context = `.` | Bundle frontend into nginx image at build time |
| **Entrypoint script** | backend/entrypoint.sh | Handle startup dependencies inside the container |
| **Init scripts** | postgres/init.sql | Auto-create schema on first run |
| **Environment variables** | .env → Compose → containers | Keep secrets out of code |
| **HEALTHCHECK instruction** | Both Dockerfiles | Docker marks containers healthy/unhealthy |
| **Layer caching** | COPY requirements.txt before COPY . | pip install only re-runs when requirements change |

---

## Interview Summary

### One-liner:
> "I built and deployed a containerized full-stack Task Manager application using Docker Compose, with a Flask REST API, PostgreSQL database, Redis cache, and Nginx reverse proxy — all running on an AWS EC2 instance."

### How to explain it (2-3 minutes):

**What I built:**
"The project is a Task Manager web app where you can create, complete, and delete tasks. But the real focus was the infrastructure — everything runs in Docker containers orchestrated by Docker Compose."

**The four services:**
"There are four containers. Nginx is the entry point — it serves the static frontend and proxies API calls to Flask. Flask is the Python backend that handles all the business logic and talks to PostgreSQL for persistence and Redis for caching. PostgreSQL stores the tasks permanently in a named Docker volume. Redis caches the task list for 60 seconds to reduce database load."

**Why Docker Compose:**
"Docker Compose lets me define all four services, their networks, volumes, environment variables, and startup dependencies in a single YAML file. I can bring the entire stack up with one command: `docker-compose up --build`. It also handles health checks — the backend won't start until PostgreSQL and Redis are confirmed healthy."

**Networking and security:**
"I used two isolated networks — a backend network connecting Flask, PostgreSQL, and Redis, and a frontend network connecting only Nginx and Flask. This means the database is never directly accessible from outside. Nginx is the only container exposed to the internet on port 8080."

**The startup problem I solved:**
"One challenge was startup ordering. Even with `depends_on`, Docker starts containers in order but doesn't wait for the app inside to be ready. I wrote an entrypoint shell script that uses `pg_isready` to poll PostgreSQL until it accepts connections, then runs database migrations, then starts Gunicorn. This prevents Flask from crashing on startup."

**EC2 deployment:**
"I deployed it on AWS EC2 — cloned the repo, opened port 8080 in the Security Group, and ran docker-compose. I hit a buildx architecture issue and fixed it by disabling BuildKit."

**What I'd add next:**
"For production I'd add HTTPS with an SSL certificate via Certbot, push the images to ECR, use environment-specific `.env` files, and set up the Jenkins pipeline to automate builds and deployments on every git push."
