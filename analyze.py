import argparse
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

def analyze(results="results.csv", out="plots"):
    df=pd.read_csv(results); out=Path(out); out.mkdir(exist_ok=True)
    counts=df["op"].value_counts().reindex(["GET","PUT","DELETE"],fill_value=0)
    print("Operation counts:\n",counts)
    print("Read %:",round(counts["GET"]/len(df)*100,1) if len(df) else "N/A")
    print("Write %:",round((counts["PUT"]+counts["DELETE"])/len(df)*100,1) if len(df) else "N/A")
    counts.plot(kind="bar",title="Read / Write Operation Distribution",xlabel="Operation",ylabel="Count")
    plt.tight_layout(); plt.savefig(out/"operation_distribution.png"); plt.close()
    reads=df[df.op=="GET"]
    if not reads.empty:
        reads["bucket"]=(reads["dataset_size"]//10)*10
        stats=reads.groupby("bucket")["latency_us"].quantile([.5,.95]).unstack()
        stats.columns=["p50_us","p95_us"]
        stats.plot(title="GET latency vs dataset size",xlabel="Dataset size bucket",ylabel="Latency (microseconds)")
        plt.tight_layout(); plt.savefig(out/"latency_vs_size.png"); plt.close()
    print("Charts saved in",out)

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("results",nargs="?",default="results.csv"); p.add_argument("--out",default="plots")
    a=p.parse_args(); analyze(a.results,a.out)
