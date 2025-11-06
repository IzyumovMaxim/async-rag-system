from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import redis.asyncio as aioredis
from os import getenv

app = FastAPI()

REDIS_URL = getenv("REDIS_URL", "redis://redis:6379")
task_queue = aioredis.from_url(REDIS_URL, decode_responses=True)

class Task(BaseModel):
    """
    A class that ensures all variables are the needed type
    Args:
        BaseModel: parent class for all pydantic models
    """
    user_id: int
    chat_id: int
    text: str

@app.post("/tasks")
async def create_task(task: Task):
    """
    Puts user message into queue 
    Args:
        Object of task class which confirms structure of added data

    Returns:
        Dictionary with task identifier and status of task
    """
    task_id = str(uuid.uuid4())
    new_task = {
        'task_id': task_id,
        'user_id': task.user_id,
        'chat_id': task.chat_id,
        'text': task.text
    }
    await task_queue.xadd("tasks", new_task)
    await task_queue.hset(f"task:{task_id}", mapping={
        'status': 'queued', 
        'chat_id': task.chat_id, 
        'result': ''
    })
    print(f'Task {task_id} was added to queue')
    return {'task_id': task_id, 'status': 'queued'}

@app.get("/tasks/{id}")
async def get_task_status(id: str):
    task_hash = await task_queue.hgetall(f"task:{id}")
    if not task_hash:
        return {"error": "Task not found"}
    return task_hash

@app.get("/health")
async def health():
    try:
        ok = await task_queue.ping()
        if ok:
            return {"status": "healthy", "detail": "Redis is working"}
        else:
            return {"status": "unhealthy", "detail": "Redis did not respond"}
    except Exception as e:
        return {"status": "unhealthy", "detail": str(e)}