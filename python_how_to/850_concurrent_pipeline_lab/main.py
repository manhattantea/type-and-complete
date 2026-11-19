# python 850_concurrent_pipeline_lab/main.py

import asyncio

from pipeline import PipelineStats, WorkItem, WorkResult


def main() -> None:

    # This Lab entry drives 850_concurrent_pipeline_lab/pipeline.py: a bounded
    # asyncio.Queue(maxsize=4) paired with an asyncio.TaskGroup and per-item
    # asyncio.timeout(0.05) isolation.
    #
    # First implement producer, worker, and run_pipeline in pipeline.py, then
    # import run_pipeline here and feed a 16-item batch with one deliberately
    # slow item (delay_s=0.08) to prove backpressure and timeout isolation work
    # without cancelling the other 15 items.

    print("=== 850 Concurrent Pipeline Lab ===")
    stats = PipelineStats()
    sample = WorkItem(item_id=0, payload=10)
    print(f"Starter contract check: {stats}, sample={sample}")

    # Import run_pipeline from pipeline and build 16 WorkItem instances in a
    # list comprehension: item_id=i, payload=(i + 1) * 10 for i in range(16),
    # giving i == 5 delay_s=0.08 and all others delay_s=0.01.

    # Run results: list[WorkResult] = asyncio.run(run_pipeline(items, worker_count=4)).
    # Assert len(results) == 16 and [r.item_id for r in results] == list(range(16)).
    # Populate stats.submitted = len(items),
    # stats.completed = sum(not r.timed_out for r in results), and
    # stats.timed_out = sum(r.timed_out for r in results).
    # Assert stats.completed == 15 and stats.timed_out == 1, then print stats
    # and the first 6 WorkResult entries to inspect which worker_id handled each.


if __name__ == "__main__":
    main()
