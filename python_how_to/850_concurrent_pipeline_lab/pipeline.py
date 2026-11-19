# Stage models, bounded queue, and TaskGroup orchestration for 850_concurrent_pipeline_lab.

# A concurrent pipeline connects a fast producer to N slower workers through a
# bounded asyncio.Queue(maxsize=4). Why bounded? With maxsize=0 (unbounded), a
# producer reading from a fast source can buffer millions of WorkItem objects in
# RAM before workers finish the first batch. Setting maxsize=4 enforces automatic
# backpressure: once 4 items sit in the queue, await queue.put(item) suspends
# the producer coroutine until a worker frees a slot with await queue.get().
#
#     Suppose maxsize=2 and items = [item0, item1, item2]:
#         Producer puts item0 and item1 immediately (queue holds 2/2).
#         On put(item2), the producer pauses at await without spinning CPU.
#         Worker 0 calls get() -> pulls item0 -> producer wakes and puts item2.
#
# Two reliability rules keep async pipelines from hanging or aborting siblings:
# - Sentinel shutdown (None poison pills): workers loop forever pulling from the
#   queue. Once the producer finishes real items, it enqueues worker_count None
#   tokens so each worker pulls one None, calls queue.task_done(), and exits.
# - Always call queue.task_done() inside finally: if processing an item raises
#   or hits asyncio.timeout(), skipping task_done() leaves await queue.join()
#   deadlocked forever. Catching TimeoutError per item isolates slow work into
#   WorkResult(..., timed_out=True) instead of cancelling sibling workers inside
#   asyncio.TaskGroup!

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class WorkItem:
    item_id: int
    payload: int
    delay_s: float = 0.01


@dataclass(slots=True, frozen=True)
class WorkResult:
    item_id: int
    output: int
    worker_id: int
    timed_out: bool = False


@dataclass(slots=True)
class PipelineStats:
    submitted: int = 0
    completed: int = 0
    timed_out: int = 0


# Define async def producer(items: Sequence[WorkItem], queue: asyncio.Queue[WorkItem | None], worker_count: int) -> None:
# Loop for item in items: and await queue.put(item) (with maxsize=4, this
# naturally pauses whenever 4 items are buffered).
# After all real items are queued, loop for _ in range(worker_count): and
# await queue.put(None) so every worker receives one clean shutdown sentinel.


# Define async def worker(worker_id: int, queue: asyncio.Queue[WorkItem | None], results: list[WorkResult]) -> None:
# Run a while True: loop fetching item = await queue.get().
# Wrap the body after get() in try ... finally: queue.task_done().
# If item is None, break out of the loop cleanly.
# Otherwise, run work inside try: async with asyncio.timeout(0.05):
# - await asyncio.sleep(item.delay_s)
# - append WorkResult(item_id=item.item_id, output=item.payload * 2, worker_id=worker_id) to results
#   (between await points in single-threaded asyncio, results.append(...) cannot race!)
# Catch except TimeoutError: and append
# WorkResult(item_id=item.item_id, output=0, worker_id=worker_id, timed_out=True).


# Define async def run_pipeline(items: Sequence[WorkItem], worker_count: int = 3) -> list[WorkResult]:
# Create queue: asyncio.Queue[WorkItem | None] = asyncio.Queue(maxsize=4) and
# results: list[WorkResult] = [].
# Enter async with asyncio.TaskGroup() as tg: and spawn:
# - tg.create_task(producer(items, queue, worker_count))
# - for wid in range(worker_count): tg.create_task(worker(wid, queue, results))
# After the TaskGroup exits (or after await queue.join()), return results sorted
# by item_id: return sorted(results, key=lambda r: r.item_id).
