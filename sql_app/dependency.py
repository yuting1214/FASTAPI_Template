import asyncio

# Dependency to simulate an asynchronous task
async def simulate_task():
    await asyncio.sleep(2)
    print("Simulated task executed")

# Dependency to execute a task before endpoint1
async def before_endpoint1():
    await simulate_task()
    print("Before Endpoint 1")

# Dependency to execute a task after endpoint1
async def after_endpoint1():
    await simulate_task()
    print("After Endpoint 1")

# Dependency generator function
async def endpoint_tasks(task_name: str):
    await simulate_task()
    print(f"Before {task_name}")
    yield  # Yield to the main logic of the endpoint
    await simulate_task()
    print(f"After {task_name}")

# Factory function to create the dependency callable
def get_endpoint_tasks(task_name: str):
    async def dependency():
        async for _ in endpoint_tasks(task_name):
            pass
    return dependency
