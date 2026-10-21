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
    return tasks

@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
    
    new_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {
        "id": new_id,
        "title": task_data.title.strip(),
        "done": False
    }
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{id}")
def update_task(id: int, task_update: TaskUpdate):
    for task in tasks:
        if task["id"] == id:
            # Validate that at least one field is provided and not empty
            if task_update.title is None and task_update.done is None:
                raise HTTPException(status_code=400, detail={"error": "Update body cannot be empty"})
            
            if task_update.title is not None:
                if not task_update.title.strip():
                    raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
                task["title"] = task_update.title.strip()
                
            if task_update.done is not None:
                task["done"] = task_update.done
                
            return task
            
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    for index, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(index)
            return
            
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})