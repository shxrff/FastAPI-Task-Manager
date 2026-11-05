import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# Load environment variables from .env (Stage 1 requirement)
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

def get_connection():
    # Helper to connect to PostgreSQL using the secret from .env
    return psycopg.connect(DATABASE_URL)

# Database initialization function for Stage 1
def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Create tasks table if it doesn't exist (using SERIAL for PostgreSQL)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL
                )
            """)
            
            # 2. Seed three example tasks ONLY if the table is empty
            cur.execute("SELECT COUNT(*) FROM tasks;")
            count = cur.fetchone()[0]
            
            if count == 0:
                initial_tasks = [
                    ("Buy groceries", False),
                    ("Learn FastAPI", True),
                    ("Build WhatsApp AI agent", False)
                ]
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    initial_tasks
                )
                conn.commit()

# Initialize and seed the database on startup
init_db()

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

# (Your full route definitions are kept below so your app structure remains intact)

@app.get("/tasks")
def get_tasks():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id;")
            rows = cur.fetchall()
            return [{"id": r[0], "title": r[1], "done": r[2]} for r in rows]

@app.get("/tasks/{id}")
def get_task(id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (id,))
            row = cur.fetchone()
            
    if row is None:
        raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})
    return {"id": row[0], "title": row[1], "done": row[2]}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
                (task_data.title.strip(), False)
            )
            row = cur.fetchone()
            conn.commit()
            
    return {"id": row[0], "title": row[1], "done": row[2]}

@app.put("/tasks/{id}")
def update_task(id: int, task_update: TaskUpdate):
    if task_update.title is None and task_update.done is None:
        raise HTTPException(status_code=400, detail={"error": "Update body cannot be empty"})
        
    if task_update.title is not None and not task_update.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (id,))
            row = cur.fetchone()
            
            if row is None:
                raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})
                
            current_title = row[1]
            current_done = row[2]
            
            new_title = task_update.title.strip() if task_update.title is not None else current_title
            new_done = task_update.done if task_update.done is not None else current_done
            
            cur.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
                (new_title, new_done, id)
            )
            updated_row = cur.fetchone()
            conn.commit()
            
    return {"id": updated_row[0], "title": updated_row[1], "done": updated_row[2]}

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM tasks WHERE id = %s;", (id,))
            row = cur.fetchone()
            
            if row is None:
                raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})
                
            cur.execute("DELETE FROM tasks WHERE id = %s;", (id,))
            conn.commit()
    return
