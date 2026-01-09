# Python Asyncio Standards

Rules for writing correct, safe async Python code.

## Structured Concurrency

Use `asyncio.TaskGroup` for managing task lifecycles:

- **Dependent tasks**: Let exceptions propagate to cancel the group
- **Independent tasks**: Wrap in a "firewall" so the group remains active

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(task_a())
    tg.create_task(task_b())
```

## Non-Blocking I/O

NEVER use blocking calls inside async functions:

| Blocking (Bad) | Non-blocking (Good) |
|----------------|---------------------|
| `time.sleep()` | `asyncio.sleep()` |
| `requests.get()` | `httpx.AsyncClient().get()` |
| `open().read()` | `aiofiles.open()` or thread pool |

## CPU-Bound Operations

Offload heavy CPU work to thread/process pool:

```python
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(None, heavy_computation, arg)
```

## Background Tasks

NEVER use "fire and forget" without holding a reference:

```python
# Bad - task may be garbage collected
asyncio.create_task(do_background_work())

# Good - keep reference
self._background_tasks.add(asyncio.create_task(do_background_work()))
```

## Synchronization

Use asyncio primitives, NOT threading:

- `asyncio.Lock()` not `threading.Lock()`
- `asyncio.Event()` not `threading.Event()`
- `asyncio.Semaphore()` not `threading.Semaphore()`

## Context Managers

Prefer `async with` for resource management:

```python
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.json()
```

## Fault Isolation (Firewall Pattern)

For independent tasks that must not crash siblings:

```python
async def safe_wrapper(task_id: str):
    """Firewall - exception stops here."""
    try:
        await independent_task(task_id)
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        # DO NOT re-raise - let other tasks continue

async def entry_point():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(safe_wrapper("A"))
        tg.create_task(safe_wrapper("B"))  # If this fails, A continues
        tg.create_task(safe_wrapper("C"))
```

## Exception Handling

- Catch `Exception`, not `BaseException`, for general handling
- Only catch `BaseException` at top-level entry point for final logging
- Log with stack trace using `logger.exception()`

## Prohibited

- NO `asyncio.run()` inside an already running event loop
- NO calling async functions without `await` (unless scheduling)
- NO blocking libraries in async paths (`requests`, `urllib`, `time.sleep`)
