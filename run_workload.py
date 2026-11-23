import csv, sys, time
from lsm_store import LSMStore

def run(csv_path="workload.csv", db_path="workload_data"):
    db=LSMStore(db_path,memtable_limit=100)
    results=[]
    with open(csv_path,newline="",encoding="utf-8") as f:
        for row in csv.DictReader(f):
            op=row["op"].upper(); key=row["key"]; value=row.get("value","")
            start=time.perf_counter()
            if op=="PUT": db.put(key,value)
            elif op=="DELETE": db.delete(key)
            elif op=="GET": db.get(key)
            else: raise ValueError(f"Invalid operation: {op}")
            latency=(time.perf_counter()-start)*1_000_000
            results.append({"seq":row["seq"],"op":op,"key":key,
                            "latency_us":latency,
                            "dataset_size":len(db.memtable)})
    db.close()
    with open("results.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=results[0].keys()); w.writeheader(); w.writerows(results)
    print(f"Replayed {len(results)} operations. Results saved to results.csv")

if __name__=="__main__": run(*(sys.argv[1:]))
