from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI()

task_queue = []

class Task(BaseModel):
    """
    A class that ensures all variables are the needed type
    Args:
        BaseModel: parent class for all pydantic models
    """
    user_id: int
    text: str

@app.post("/tasks")
async def create_task(task: Task):
    """
    Puts user message into query 
    Args:
        Object of task class which confirms structure of added data

    Returns:
        Dictionary with task identifier and status of task
    """
    task_id = str(uuid.uuid4())
    new_task = {
        'task_id': task_id,
        'user_id': task.user_id,
        'text': task.text
    }
    task_queue.append(new_task)
    print(f'Task {task_id} was added to queue')
    return {'task_id': task_id, 'status': 'queued'}