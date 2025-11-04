import asyncio
import redis.asyncio as aioredis
import sys

class Worker:
    def __init__(self, worker_id:str):
        self.task_queue = None
        self.worker_id = worker_id


    async def connect_to_queue(self):
        self.task_queue = aioredis.from_url("redis://localhost:6379", decode_responses=True)
        try:
            await self.task_queue.xgroup_create("tasks", "workers", id="0", mkstream=True)
            print("Created consumer group")
        except:
            print("Customer group already exists")

    async def rag(self, text: str):
        await asyncio.sleep(2)
        return f"Rag answers on: {text}"
    
    async def process_task(self, task_data:dict):
        task_id = task_data['task_id']
        text = task_data['text']

        print(f'{self.worker_id} is processing {task_id}')

        await self.task_queue.hset(f'task:{task_id}', 'status', 'processing')

        try:
            answer = await self.rag(text)
            await self.task_queue.hset(f'task:{task_id}', mapping={'status': 'comple',
                                                                   'result': answer})
            print(f'{self.worker_id}: {task_id} completed')

        except:
            await self.task_queue.hset(f'task:{task_id}', 'status', 'failed')
            print(f'{self.worker_id}: {task_id} failed')

    async def run(self):
        print(f'{self.worker_id} is running')

        while True:
            try:
                messages = await self.task_queue.xreadgroup(
                    groupname='workers',
                    consumername=self.worker_id,
                    streams={'tasks':'>'},
                    count=1,
                    block=5000
                )

                if not messages:
                    continue

                for stream_name, message_stream in messages:
                    for message_id, task_data in message_stream:
                        await self.process_task(task_data)
                        await self.task_queue.xack("tasks", "workers", message_id)
            except:
                print(f"{self.worker_id} error in worker loop")

async def main():
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "worker-1"
    worker = Worker(worker_id)
    await worker.connect_to_queue()
    await worker.run()

if "__main__" == __name__:
    asyncio.run(main())