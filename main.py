from lsm_store import LSMStore

def main():
    db=LSMStore("data",memtable_limit=3)
    print("\n=== MINI LSM-TREE DATABASE ===")
    print("Commands: put KEY VALUE | get KEY | delete KEY | flush | compact | exit")
    while True:
        try: parts=input("lsm> ").strip().split()
        except (EOFError,KeyboardInterrupt): break
        if not parts: continue
        cmd=parts[0].lower()
        try:
            if cmd=="put" and len(parts)>=3:
                db.put(parts[1]," ".join(parts[2:])); print("Saved.")
            elif cmd=="get" and len(parts)==2:
                print("Value:",db.get(parts[1]))
            elif cmd=="delete" and len(parts)==2:
                db.delete(parts[1]); print("Deleted (tombstone written).")
            elif cmd=="flush": db.flush(); print("Memtable flushed to SSTable.")
            elif cmd=="compact": db.compact(); print("Compaction complete.")
            elif cmd=="exit": break
            else: print("Invalid command. Example: put name Abhishek")
        except Exception as e: print("Error:",e)
    db.close()
    print("Database closed.")

if __name__=="__main__": main()
