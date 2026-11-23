
import csv
import matplotlib.pyplot as plt
from pathlib import Path

# Read the existing results
with open("results.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Extract sequence numbers and latency values
seq = [int(row["seq"]) for row in rows]
latency = [float(row["latency_us"]) for row in rows]
operations = [row["op"] for row in rows]

# Create plots folder if necessary
Path("plots").mkdir(exist_ok=True)

# Draw latency graph
plt.figure(figsize=(9, 5))

for operation in sorted(set(operations)):
    x = [seq[i] for i in range(len(seq)) if operations[i] == operation]
    y = [latency[i] for i in range(len(seq)) if operations[i] == operation]
    plt.plot(x, y, marker="o", label=operation)

plt.xlabel("Operation sequence")
plt.ylabel("Latency (microseconds)")
plt.title("Database Operation Latency")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("plots/latency_by_sequence.png")
plt.show()

print("Latency graph created successfully!")
