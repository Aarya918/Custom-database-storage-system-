# Custom Database Storage Engine (LSM-Tree)

A learning-scale key-value storage engine in Python. It demonstrates a write-ahead log (WAL), in-memory memtable, immutable JSON SSTables, reads, tombstones, flush, compaction, workload replay and charts.

## Setup
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the interactive database
```bash
python main.py
```
Try:
```
put name Abhishek
get name
put city Bengaluru
delete city
get city
flush
compact
exit
```

## Workload analysis
```bash
python run_workload.py workload.csv
python analyze.py results.csv --out plots
```
Charts are saved in `plots/`.

## Tests
```bash
python -m unittest -v
```

## Architecture
PUT/DELETE -> append WAL -> update memtable -> flush sorted JSON SSTable.
GET checks memtable first, then SSTables newest-to-oldest. DELETE writes a tombstone.
Compaction merges SSTables, retaining newest values and removing tombstones.

## Scope and limitations
This is a teaching prototype, not a production database. It is single-process and single-threaded. The demo uses JSON files and a simple WAL; it does not claim production-grade crash guarantees or a verified LevelDB performance comparison.
