import tempfile, unittest
from lsm_store import LSMStore

class TestLSM(unittest.TestCase):
    def test_put_get_delete_and_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            db=LSMStore(d,memtable_limit=2)
            db.put("a","one"); db.put("b","two") # auto flush
            self.assertEqual(db.get("a"),"one")
            db.put("a","new"); self.assertEqual(db.get("a"),"new")
            db.delete("b"); self.assertIsNone(db.get("b"))
            db2=LSMStore(d,memtable_limit=10)
            self.assertEqual(db2.get("a"),"new")
            self.assertIsNone(db2.get("b"))
    def test_compaction(self):
        with tempfile.TemporaryDirectory() as d:
            db=LSMStore(d,memtable_limit=1)
            db.put("x","old"); db.put("x","new"); db.delete("x")
            db.compact(); self.assertIsNone(db.get("x"))
if __name__=="__main__": unittest.main()
