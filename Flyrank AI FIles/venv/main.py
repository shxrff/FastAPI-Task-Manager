from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# In-memory "database" pre-filled with 3 example tasks
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Learn FastAPI", "done": True},
    {"id": 3, "title": "Build WhatsApp AI agent", "done": False}
]

class TaskCreate(BaseModel):
    title: str

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
    return tasks

@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    # Validate that the title is not empty or just whitespace
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
    
    # Calculate the next free ID automatically
    new_id = max((t["id"] for t in tasks), default=0) + 1
    
    new_task = {
        "id": new_id,
        "title": task_data.title.strip(),
        "done": False
    }
    
    tasks.append(new_task)
    return new_task