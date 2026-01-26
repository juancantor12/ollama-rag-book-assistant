AI Overview

Purpose
- Backend CLI/API for a local Ollama RAG book assistant. Provides FastAPI HTTP API, JWT auth, RBAC, and book ingestion/embedding via Chroma.

Runtime entry points
- API: `src/api/main.py` (FastAPI app, routes, CORS, startup recovery code)
- CLI: `src/app/cli.py` (interactive ask loop)
- Scripts: `run.ps1`, `run.sh` (bootstrap + run actions)

Core flow
- Upload PDF -> store in `data/`
- Generate embeddings -> stored per-book in `output/<BookName>/chroma.sqlite3`
- Ask queries -> retrieve embeddings via Chroma, call Ollama for answers

Auth + RBAC
- Login: `src/api/controllers/auth.py` (bcrypt verify, JWT in cookie)
- Permissions: `src/api/controllers/rbac.py`, `src/api/models/role.py`, `src/api/models/permission.py`
- Users CRUD: `src/api/controllers/user.py`, routes in `src/api/routes/admin.py`
- Recovery: `src/api/controllers/recovery.py` (prints recovery code on startup, table auto-created)

Chroma client
- Helper: `src/app/utils.py` -> `get_chroma_client()` sets SegmentAPI and ensures tenant/db
- Used by embeddings + checks: `src/app/generate_embeddings.py`, `src/app/db.py`, `src/app/utils.py`

Key API routes
- Client: `src/api/routes/client.py` (status, login, upload_book, load_books, generate_embeddings, ask)
- Admin: `src/api/routes/admin.py` (users, schema, recover)
- RBAC: `src/api/routes/rbac.py` (roles, permissions)

Important files (what they do)
- `src/api/main.py`: FastAPI app wiring + recovery code on startup.
- `src/api/controllers/auth.py`: JWT token creation/verify + login.
- `src/api/controllers/recovery.py`: recovery code + admin reset logic.
- `src/api/controllers/user.py`: user create/update/delete, bcrypt hashing.
- `src/app/generate_embeddings.py`: PDF parsing + embedding generation.
- `src/app/assistant.py`: Retrieval + prompting for Q/A.
- `src/app/utils.py`: env config, paths, Chroma client helper.
- `src/api/db.py`: SQLAlchemy session + base models.
- `src/api/models/*`: SQLAlchemy models (User/Role/Permission/RecoveryCode).

Data locations
- `data/`: PDFs + `users.db` (SQLite RBAC)
- `output/<BookName>/`: Chroma persistence per book

Env settings (from `.env`)
- `API_SECRET_KEY`, `API_TOKEN_ALGORITHM`, `API_TOKEN_EXPIRE_MINUTES`
- `API_RECOVERY_CODE_EXPIRE_MINUTES`
- `API_DB_NAME` (default `users.db`)
- `OLLAMA_URL`, `CHAT_MODEL`, `EMBEDDINGS_MODEL`
- `COLLECTION_NAME`, `DEFAULT_DB_FILENAME`, `N_DOCUMENTS`

Dependency notes
- Windows: prefer Python 3.11 for Chroma/hnswlib; pinned in `requirements.txt`.
