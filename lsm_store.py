import json, os
from pathlib import Path

class LSMStore:
    """Learning-scale LSM key-value store: WAL -> memtable -> JSON SSTables."""
    def __init__(self, path="data", memtable_limit=3, sync=True):
        self.path=Path(path); self.path.mkdir(parents=True, exist_ok=True)
        self.wal=self.path/"wal.log"
        self.memtable={}
        self.seq=0
        self.memtable_limit=memtable_limit
        self.sync=sync
        self.sstables=sorted(self.path.glob("sstable_*.json"), reverse=True)
        self._recover()

    def _append_wal(self, record):
        with self.wal.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record)+"\n")
            f.flush()
            if self.sync: os.fsync(f.fileno())

    def _recover(self):
        if not self.wal.exists(): return
        lines=self.wal.read_text(encoding="utf-8").splitlines()
        for i,line in enumerate(lines):
            try: rec=json.loads(line)
            except json.JSONDecodeError:
                if i == len(lines)-1: break  # ignore a crash-truncated final record
                raise ValueError(f"Corrupt WAL record at line {i+1}")
            self.seq=max(self.seq, rec["seq"])
            if rec["op"]=="PUT": self.memtable[rec["key"]]=rec["value"]
            elif rec["op"]=="DELETE": self.memtable[rec["key"]]=None

    def put(self,key,value):
        self._validate_key(key)
        if not isinstance(value,str): raise TypeError("value must be a string")
        self.seq+=1
        self._append_wal({"seq":self.seq,"op":"PUT","key":key,"value":value})
        self.memtable[key]=value
        if len(self.memtable)>=self.memtable_limit: self.flush()

    def delete(self,key):
        self._validate_key(key)
        self.seq+=1
        self._append_wal({"seq":self.seq,"op":"DELETE","key":key,"value":None})
        self.memtable[key]=None
        if len(self.memtable)>=self.memtable_limit: self.flush()

    @staticmethod
    def _validate_key(key):
        if not isinstance(key,str) or not key: raise ValueError("key must be a non-empty string")

    def get(self,key):
        self._validate_key(key)
        if key in self.memtable: return self.memtable[key]
        for file in self.sstables:  # newest first
            data=json.loads(file.read_text(encoding="utf-8"))
            entries=dict(data["entries"])
            if key in entries: return entries[key]
        return None

    def flush(self):
        if not self.memtable: return
        file_id=max([int(p.stem.split("_")[1]) for p in self.path.glob("sstable_*.json")]+[0])+1
        entries=sorted(self.memtable.items())
        payload={"file_id":file_id,"entries":entries,"entry_count":len(entries)}
        tmp=self.path/f"sstable_{file_id}.tmp"
        final=self.path/f"sstable_{file_id}.json"
        with tmp.open("w",encoding="utf-8") as f:
            json.dump(payload,f,indent=2); f.flush()
            if self.sync: os.fsync(f.fileno())
        os.replace(tmp,final)
        self.sstables.insert(0,final)
        self.memtable.clear()
        # WAL is rotated only after SSTable is safely written.
        self.wal.write_text("",encoding="utf-8")

    def compact(self):
        if len(self.sstables)<2: return
        merged={}
        # Oldest to newest: later assignment wins.
        for file in reversed(self.sstables):
            data=json.loads(file.read_text(encoding="utf-8"))
            merged.update(dict(data["entries"]))
        merged={k:v for k,v in merged.items() if v is not None}
        file_id=max([int(p.stem.split("_")[1]) for p in self.path.glob("sstable_*.json")]+[0])+1
        final=self.path/f"sstable_{file_id}.json"
        tmp=self.path/f"sstable_{file_id}.tmp"
        with tmp.open("w",encoding="utf-8") as f:
            json.dump({"file_id":file_id,"entries":sorted(merged.items()),"entry_count":len(merged)},f,indent=2)
            f.flush()
            if self.sync: os.fsync(f.fileno())
        os.replace(tmp,final)
        old=self.sstables[:]
        self.sstables=[final]
        for file in old: file.unlink(missing_ok=True)

    def close(self):
        # WAL already protects unflushed memtable contents.
        pass
