"""API de gestion d'une liste de todos, stockée dans SQL Server."""

import os
from contextlib import contextmanager
from typing import Literal

import pymssql
from fastapi import APIRouter, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Paramètres de connexion, fournis par les variables d'environnement du compose.yaml
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "1433"))
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("MSSQL_SA_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "TodoDb")

# Colonnes renvoyées, avec des noms en minuscules pour le JSON
COLUMNS = "Id AS id, Title AS title, Status AS status, CreatedAt AS created_at"
OUTPUT_COLUMNS = (
    "INSERTED.Id AS id, INSERTED.Title AS title, "
    "INSERTED.Status AS status, INSERTED.CreatedAt AS created_at"
)

# Les trois statuts possibles d'une tâche
Status = Literal["todo", "in_progress", "done"]

app = FastAPI(title="Todo API")
router = APIRouter(prefix="/api")


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    status: Status = "todo"


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    status: Status | None = None


@contextmanager
def get_conn():
    """Ouvre une connexion à SQL Server et la ferme à la fin."""
    conn = pymssql.connect(
        server=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        as_dict=True,
        login_timeout=10,
    )
    try:
        yield conn
    finally:
        conn.close()


@app.exception_handler(pymssql.Error)
async def db_error_handler(request: Request, exc: pymssql.Error):
    print(f"Erreur base de données : {exc}", flush=True)
    return JSONResponse(status_code=503, content={"detail": "Base de données indisponible"})


@router.get("/health")
def health():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 AS ok")
        cur.fetchone()
    return {"status": "ok"}


@router.get("/todos")
def list_todos():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT {COLUMNS} FROM dbo.Todos ORDER BY Id")
        return cur.fetchall()


@router.get("/stats")
def stats():
    """Nombre de tâches par statut, pour le camembert."""
    counts = {"todo": 0, "in_progress": 0, "done": 0}
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT Status AS status, COUNT(*) AS count FROM dbo.Todos GROUP BY Status")
        for row in cur.fetchall():
            counts[row["status"]] = row["count"]
    return {**counts, "total": sum(counts.values())}


@router.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO dbo.Todos (Title, Status) OUTPUT {OUTPUT_COLUMNS} VALUES (%s, %s)",
            (todo.title.strip(), todo.status),
        )
        row = cur.fetchone()
        conn.commit()
        return row


@router.patch("/todos/{todo_id}")
def update_todo(todo_id: int, changes: TodoUpdate):
    sets, params = [], []
    if changes.title is not None:
        sets.append("Title = %s")
        params.append(changes.title.strip())
    if changes.status is not None:
        sets.append("Status = %s")
        params.append(changes.status)
    if not sets:
        raise HTTPException(status_code=400, detail="Rien à modifier")

    params.append(todo_id)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE dbo.Todos SET {', '.join(sets)} OUTPUT {OUTPUT_COLUMNS} WHERE Id = %s",
            tuple(params),
        )
        row = cur.fetchone()
        conn.commit()
    if row is None:
        raise HTTPException(status_code=404, detail="Todo introuvable")
    return row


@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM dbo.Todos WHERE Id = %s", (todo_id,))
        deleted = cur.rowcount
        conn.commit()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Todo introuvable")
    return Response(status_code=204)


app.include_router(router)
