# Anon Platform — Backend

FastAPI backend for an **anonymous posting platform**. Users publish posts and
comments with no account and no identity attached; every connected client is
pushed new posts live over a WebSocket.

Consumed by **anonfront**, deployed at `anon.devwole.space`.

---

## Stack

| Layer | Choice |
|---|---|
| Framework | FastAPI |
| Server | Uvicorn |
| ORM / models | SQLModel (SQLAlchemy + Pydantic) |
| Database | SQLite — `sqlite:///app.db` |
| Realtime | Native FastAPI WebSocket, in-process connection list |
| Object storage | S3-compatible via `boto3` (`storage.py`) |
| Also wired | Supabase async client (`database.py`) |

> **Note on persistence:** despite the Supabase client being created on startup,
> **all routes read and write the local SQLite database via SQLModel.** Supabase
> and the S3 storage helper are initialised onto `app.state` but are not used by
> the current endpoints. Earlier revisions of this README described a Supabase
> schema with deletion passwords — that is no longer how the code works.

## Architecture

```
app/
  main.py        FastAPI app: CORS, startup hooks, mounts the router, GET /
  websocks.py    APIRouter holding *all* real endpoints + the WebSocket manager
  model.py       SQLModel tables: Post, Comment, Sec
  db.py          SQLite engine + create_db_and_tables()
  database.py    Supabase async client factory (initialised, currently unused)
  storage.py     S3-compatible upload/retrieval helper (currently unused)
insert_manual.py Manual seeding helper
scratch/         Ad-hoc verification scripts
```

`main.py` is a thin shell — the substance is in `websocks.py`, which is an
`APIRouter` named `app` and included by `main.py`. Broadcasting is simple: open
sockets are held in a module-level `connections` list, and creating a post
iterates it and sends the new post as JSON to everyone.

## Data model

| Table | Fields |
|---|---|
| `Post` | `id` (UUID string, PK), `content`, `created_at`, `likes`, `views`, `comment_count` |
| `Comment` | `id` (UUID string, PK), `post_id` (indexed), `content`, `created_at`, `likes` |
| `Sec` | `id` (UUID string, PK), `device`, `messages` (JSON column) |

Timestamps use `get_adjusted_time()` — UTC **plus one hour** (WAT), stored naive.

## Getting started

```bash
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in the Supabase values
uvicorn app.main:app --reload
```

`app.db` is created automatically on startup. API on `http://127.0.0.1:8000`,
interactive docs at `/docs`.

## Configuration

| Variable | Required | Purpose |
|---|---|---|
| `SUPABASE_URL` | Yes* | Read by `database.py` on startup |
| `SUPABASE_KEY` | Yes* | Read by `database.py` on startup |

\* Required because the startup hook constructs the client unconditionally — the
app will fail to boot without them, even though no route uses the client.

The SQLite path is hardcoded in `db.py` (`sqlite:///app.db`) and is not
configurable via environment.

## API reference

| Method | Path | Version-gated | Purpose |
|---|---|---|---|
| `GET` | `/` | — | Service greeting |
| `GET` | `/version` | — | Returns the server's `CURRENT_VERSION` |
| `POST` | `/post` | **Yes** | Create a post from `{ "text": ... }`; broadcasts to all sockets |
| `GET` | `/posts` | No | List all posts |
| `POST` | `/comment/{post_id}` | No | Add a comment |
| `GET` | `/comments/{post_id}` | No | List a post's comments |
| `POST` | `/sec` | No | Store `{ device, messages }` |
| `GET` | `/sec` | No | List stored `Sec` records |
| `WS` | `/ws` | — | Receives `{ type: "post", data: {...} }` on every new post |

### Client version gating

`POST /post` calls `check_version()`, which compares the `x-app-version` request
header against `CURRENT_VERSION` (currently `1.0.8`) and is meant to reject
mismatches with **426 Upgrade Required** and `detail: "OUTDATED_CLIENT"`.

Clients must therefore send:

```
x-app-version: 1.0.8
```

The same check is present but commented out on the other routes.

## Known issues

- **`check_version()` raises `NameError`, not a 426.** `HTTPException` is never
  imported in `app/websocks.py`, so a client sending a wrong `x-app-version`
  gets a **500**, not the intended `426 OUTDATED_CLIENT`. Fix by adding
  `HTTPException` to the `fastapi` import.
- **CORS is fully open.** `main.py` builds an `origins` allow-list and then
  ignores it, passing `allow_origins=["*"]` with `allow_credentials=True`.
- **`app.db` is committed to the repository** and should be untracked and
  gitignored.
- **`@app.on_event("startup")` is deprecated** in current FastAPI; migrate to
  the `lifespan` context manager.
- **In-memory socket list** — `connections` is per-process, so broadcasting
  breaks under more than one worker.
- No test suite.
