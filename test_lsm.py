
import json
import tempfile
import unittest
from pathlib import Path

from lsm_store import LSMStore


class TestLSM(unittest.TestCase):

    def test_put_get_update_delete(self):
        with tempfile.TemporaryDirectory() as d:
            db = LSMStore(d, memtable_limit=100)

            db.put("a", "one")
            self.assertEqual(db.get("a"), "one")

            db.put("a", "new")
            self.assertEqual(db.get("a"), "new")

            db.delete("a")
            self.assertIsNone(db.get("a"))

    def test_missing_key_returns_none(self):
        with tempfile.TemporaryDirectory() as d:
            db = LSMStore(d)
            self.assertIsNone(db.get("does_not_exist"))

    def test_flush_creates_sstable(self):
        with tempfile.TemporaryDirectory() as d:
            db = LSMStore(d, memtable_limit=2)

            db.put("a", "one")
            db.put("b", "two")

            files = list(Path(d).glob("sstable_*.json"))
            self.assertGreaterEqual(len(files), 1)
            self.assertEqual(db.get("a"), "one")
            self.assertEqual(db.get("b"), "two")

    def test_persistence_after_reopen(self):
        with tempfile.TemporaryDirectory() as d:
            db = LSMStore(d, memtable_limit=2)
            db.put("a", "one")
            db.put("b", "two")  # triggers flush

            db2 = LSMStore(d, memtable_limit=100)
            self.assertEqual(db2.get("a"), "one")
            self.assertEqual(db2.get("b"), "two")

    def test_wal_recovery_without_flush(self):
        with tempfile.TemporaryDirectory() as d:
            db = LSMStore(d, memtable_limit=100)
            db.put("recovered", "yes")

            # Create a new instance to simulate reopening the database.
            db2 = LSMStore(d, memtable_limit=100)
            self.assertEqual(db2.get("recovered"), "yes")

    def test_truncated_final_wal_record_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            db = LSMStore(d, memtable_limit=100)
            db.put("safe", "value")

            # Simulate a crash during the final WAL write.
            with db.wal.open("a", encoding="utf-8") as f:
                f.write('{"seq":2,"op":"PUT","key":"broken"')

            db2 = LSMStore(d, memtable_limit=100)
            self.assertEqual(db2.get("safe"), "value")
            self.assertIsNone(db2.get("broken"))

    def test_compaction_removes_deleted_keys(self):
        with tempfile.TemporaryDirectory() as d:
            db = LSMStore(d, memtable_limit=1)

            db.put("x", "old")   # SSTable 1
            db.put("x", "new")   # SSTable 2
            db.delete("x")       # SSTable 3

            db.compact()

            self.assertIsNone(db.get("x"))

            # Reopen after compaction.
            db2 = LSMStore(d, memtable_limit=100)
            self.assertIsNone(db2.get("x"))

    def test_sstable_entries_are_sorted(self):
        with tempfile.TemporaryDirectory() as d:
            db = LSMStore(d, memtable_limit=3)

            db.put("z", "last")
            db.put("a", "first")
            db.put("m", "middle")

            files = list(Path(d).glob("sstable_*.json"))
            self.assertEqual(len(files), 1)

            payload = json.loads(files[0].read_text(encoding="utf-8"))
            keys = [key for key, value in payload["entries"]]

            self.assertEqual(keys, sorted(keys))


if __name__ == "__main__":
    unittest.main(verbosity=2)
