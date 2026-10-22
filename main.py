from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

import sqlite3
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Database initialization function for Stage 0
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL
        )
    """)
    
    # Seed three example tasks only if the table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        initial_tasks = [
            ("Buy groceries", 0),
            ("Learn FastAPI", 1),
            ("Build WhatsApp AI agent", 0)
        ]
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", initial_tasks)
        conn.commit()
        
    conn.close()

# Initialize the database on startup
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

@app.get("/tasks")
def get_tasks():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/tasks/{id}")
def get_task(id: int):
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})
    return dict(row)

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
    
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Insert new task (done defaults to 0/False)
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task_data.title.strip(), 0))
    conn.commit()
    
    # Get the auto-generated id
    new_id = cursor.lastrowid
    
    # Fetch and return the newly created task
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row)

@app.put("/tasks/{id}")
def update_task(id: int, task_update: TaskUpdate):
    if task_update.title is None and task_update.done is None:
        raise HTTPException(status_code=400, detail={"error": "Update body cannot be empty"})
        
    if task_update.title is not None and not task_update.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})

    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})
        
    current_title = row["title"]
    current_done = row["done"]
    
    new_title = task_update.title.strip() if task_update.title is not None else current_title
    new_done = int(task_update.done) if task_update.done is not None else current_done
    
    # Execute update
    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (new_title, new_done, id))
    conn.commit()
    
    # Fetch updated row
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    updated_row = cursor.fetchone()
    conn.close()
    
    return dict(updated_row)

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    
    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})
        
    # Execute delete
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return
