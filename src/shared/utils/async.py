import asyncio
import hashlib


class AsyncManager:
    def __init__(self):
        self._tasks = {}
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        

    def schedule_task(self,key, coro):
        """Schedules an async task and stores it with a unique key."""
        if key not in self._tasks:
            self._tasks[key] = self._loop.create_task(coro)

    # Run the event loop to process scheduled tasks
    def process_tasks(self):
        """Process pending tasks on the event loop."""
        pending = [task for task in self._tasks.values() if not task.done()]
        if pending:
            self._loop.run_until_complete(asyncio.gather(*pending))

    # Generate a unique key for tasks
    def generate_task_key(*args):
        """Generate a unique hash-based key for a task."""
        return hashlib.sha256("-".join(map(str, args)).encode()).hexdigest()

async_manager = AsyncManager()