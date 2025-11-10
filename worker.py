import asyncio
import redis.asyncio as aioredis
import sys
import json
import logging
from os import getenv
from rag.rag import answer
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Worker:
    def __init__(self, worker_id: str):
        self.task_queue = None
        self.worker_id = worker_id
        self.redis_url = getenv("REDIS_URL", "redis://redis:6379")

    async def connect_to_queue(self):
        self.task_queue = aioredis.from_url(self.redis_url, decode_responses=True)
        try:
            await self.task_queue.xgroup_create("tasks", "workers", id="0", mkstream=True)
            logger.info("Created consumer group")
        except Exception as e:
            logger.info(f"Consumer group already exists or error: {e}")

    async def rag(self, text: str):
        try:
            return await answer(text)
        except Exception as e:
            logger.exception(f"{self.worker_id}: RAG error: {e}")
            return f"Error: {str(e)}"
    
    async def process_task(self, task_data: dict):
        task_id = task_data.get('task_id')
        text = task_data.get('text', '')
        user_id = task_data.get('user_id')

        if not task_id or not user_id:
            logger.error(f"Invalid task data: {task_data}")
            return

        logger.info(f'{self.worker_id} is processing {task_id}')

        await self.task_queue.hset(f'task:{task_id}', 'status', 'processing')

        try:
            answer = await self.rag(text)
            await self.task_queue.hset(f'task:{task_id}', mapping={
                'status': 'complete',
                'result': answer
            })
            await self.task_queue.publish(
                "results",
                json.dumps({
                    "task_id": task_id,
                    "user_id": int(user_id),
                    "result": answer
                })
            )
            logger.info(f'{self.worker_id}: {task_id} completed')

        except Exception as e:
            logger.exception(f'{self.worker_id}: {task_id} failed with error: {e}')
            await self.task_queue.hset(f'task:{task_id}', 'status', 'failed')

    async def run(self):
        logger.info(f'{self.worker_id} is running')

        while True:
            try:
                messages = await self.task_queue.xreadgroup(
                    groupname='workers',
                    consumername=self.worker_id,
                    streams={'tasks': '>'},
                    count=1,
                    block=5000
                )

                if not messages:
                    continue

                for stream_name, message_stream in messages:
                    for message_id, task_data in message_stream:
                        await self.process_task(task_data)
                        await self.task_queue.xack("tasks", "workers", message_id)
                        
            except asyncio.CancelledError:
                logger.info(f"{self.worker_id} was cancelled")
                break
            except Exception as e:
                logger.exception(f"{self.worker_id} error in worker loop: {e}")
                await asyncio.sleep(2)  # Wait before retrying

async def main():
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "worker-1"
    worker = Worker(worker_id)
    await worker.connect_to_queue()
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())