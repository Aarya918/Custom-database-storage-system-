
import csv
import math
import random
import statistics
import tempfile
import time
from pathlib import Path

import matplotlib.pyplot as plt
from lsm_store import LSMStore

SIZES = [100, 500, 1000, 5000]
REPEATS = 200
OPERATIONS = ["GET", "PUT", "DELETE"]


def p95(values):
    values = sorted(values)
    index = max(0, math.ceil(0.95 * len(values)) - 1)
    return values[index]


def time_operation(func):
    start = time.perf_counter_ns()
    func()
    return (time.perf_counter_ns() - start) / 1000


def benchmark_size(size):
    rng = random.Random(1000 + size)
    samples = {op: [] for op in OPERATIONS}

    with tempfile.TemporaryDirectory() as folder:
        db = LSMStore(folder, memtable_limit=size + REPEATS + 20)

        # Populate the database (not included in measured timings).
        for i in range(size):
            db.put(f"key-{i:06d}", f"value-{i}")

        # Flush initial data to SSTable for GET measurements.
        db.flush()

        # GET existing keys.
        for _ in range(REPEATS):
            index = rng.randrange(size)
            key = f"key-{index:06d}"
            samples["GET"].append(
                time_operation(lambda key=key: db.get(key))
            )

        # PUT: update an existing key.
        for i in range(REPEATS):
            samples["PUT"].append(
                time_operation(
                    lambda i=i: db.put("key-000000", f"updated-{i}")
                )
            )

        # DELETE: prepare a new key before timing its deletion.
        for i in range(REPEATS):
            key = f"delete-{i:06d}"
            db.put(key, "temporary")
            samples["DELETE"].append(
                time_operation(lambda key=key: db.delete(key))
            )

    summary = []
    raw = []

    for operation, values in samples.items():
        summary.append({
            "dataset_size": size,
            "operation": operation,
            "samples": len(values),
            "avg_latency_us": statistics.mean(values),
            "p50_latency_us": statistics.median(values),
            "p95_latency_us": p95(values),
        })

        for iteration, latency in enumerate(values, start=1):
            raw.append({
                "dataset_size": size,
                "operation": operation,
                "iteration": iteration,
                "latency_us": latency,
            })

    return summary, raw


def save_csv(filename, rows, columns):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def make_graph(summary, metric, filename, title):
    plt.figure(figsize=(9, 5))

    for operation in OPERATIONS:
        rows = [
            row for row in summary
            if row["operation"] == operation
        ]
        x = [row["dataset_size"] for row in rows]
        y = [row[metric] for row in rows]
        plt.plot(x, y, marker="o", label=operation)

    plt.xlabel("Dataset size (records)")
    plt.ylabel(f"{metric.replace('_', ' ').upper()} (microseconds)")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()


def main():
    Path("plots").mkdir(exist_ok=True)
    all_summary = []
    all_raw = []

    print("LSM-Tree benchmark started")
    print(f"Samples per operation: {REPEATS}")

    for size in SIZES:
        print(f"\nBenchmarking {size} records...")
        summary, raw = benchmark_size(size)
        all_summary.extend(summary)
        all_raw.extend(raw)
        print(f"Finished {size} records")

    summary_columns = [
        "dataset_size", "operation", "samples",
        "avg_latency_us", "p50_latency_us", "p95_latency_us"
    ]

    raw_columns = [
        "dataset_size", "operation", "iteration", "latency_us"
    ]

    save_csv("benchmark_results.csv", all_summary, summary_columns)
    save_csv("benchmark_raw.csv", all_raw, raw_columns)

    make_graph(
        all_summary,
        "p50_latency_us",
        "plots/latency_vs_dataset_size_p50.png",
        "LSM-Tree p50 Latency vs Dataset Size"
    )

    make_graph(
        all_summary,
        "p95_latency_us",
        "plots/latency_vs_dataset_size_p95.png",
        "LSM-Tree p95 Latency vs Dataset Size"
    )

    # The benchmark performs equal numbers of GET, PUT and DELETE samples.
    counts = {"GET": 800, "PUT": 800, "DELETE": 800}

    plt.figure(figsize=(7, 5))
    plt.bar(counts.keys(), counts.values())
    plt.xlabel("Operation")
    plt.ylabel("Measured operation count")
    plt.title("Benchmark Operation Distribution")
    plt.tight_layout()
    plt.savefig("plots/benchmark_operation_distribution.png", dpi=150)
    plt.close()

    print("\nBenchmark finished successfully!")
    print("Created benchmark_results.csv")
    print("Created benchmark_raw.csv")
    print("Created p50 and p95 graphs")
    print("Created operation distribution graph")


if __name__ == "__main__":
    main()
