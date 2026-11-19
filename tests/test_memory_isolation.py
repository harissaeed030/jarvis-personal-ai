"""SQLite-level regression tests for the D1 owner-scope migration/query contract.

These tests do not replace authenticated production API tests; they exercise the
same SQLite schema and isolation semantics used by the Worker.
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path


class MemoryIsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "jarvis.sqlite"
        self.db = sqlite3.connect(self.db_path)
        self.db.execute("CREATE TABLE conversations (id TEXT PRIMARY KEY, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        self.db.execute("CREATE TABLE user_memories (id TEXT PRIMARY KEY, content TEXT NOT NULL UNIQUE, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        self.db.execute("INSERT INTO conversations (id, role, content) VALUES ('old-1','user','legacy chat')")
        self.db.execute("INSERT INTO user_memories (id, content) VALUES ('old-m1','legacy memory')")
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def migrate(self, owner):
        for table in ("conversations", "user_memories"):
            columns = {row[1] for row in self.db.execute(f"PRAGMA table_info({table})")}
            if "owner_id" not in columns:
                self.db.execute(f"ALTER TABLE {table} ADD COLUMN owner_id TEXT NOT NULL DEFAULT 'legacy'")
            self.db.execute(f"UPDATE {table} SET owner_id=? WHERE owner_id='legacy' OR owner_id IS NULL", (owner,))
        self.db.execute("CREATE TABLE IF NOT EXISTS jarvis_schema_migrations (name TEXT PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        done = self.db.execute("SELECT name FROM jarvis_schema_migrations WHERE name='memory_owner_unique_v1'").fetchone()
        if not done:
            self.db.execute("CREATE TABLE user_memories_scoped (id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(owner_id,content))")
            self.db.execute("INSERT OR IGNORE INTO user_memories_scoped (id,owner_id,content,created_at) SELECT id,owner_id,content,created_at FROM user_memories")
            self.db.execute("DROP TABLE user_memories")
            self.db.execute("ALTER TABLE user_memories_scoped RENAME TO user_memories")
            self.db.execute("INSERT INTO jarvis_schema_migrations (name) VALUES ('memory_owner_unique_v1')")
        self.db.commit()

    def test_legacy_rows_are_preserved_and_scoped_to_existing_owner(self):
        self.migrate("owner-a")
        self.assertEqual(self.db.execute("SELECT content FROM conversations WHERE owner_id=?", ("owner-a",)).fetchone()[0], "legacy chat")
        self.assertEqual(self.db.execute("SELECT content FROM user_memories WHERE owner_id=?", ("owner-a",)).fetchone()[0], "legacy memory")

    def test_conversations_and_memory_are_isolated_between_owners(self):
        self.migrate("owner-a")
        self.db.execute("INSERT INTO conversations (id,role,content,owner_id) VALUES ('a1','user','private A','owner-a')")
        self.db.execute("INSERT INTO conversations (id,role,content,owner_id) VALUES ('b1','user','private B','owner-b')")
        self.db.execute("INSERT INTO user_memories (id,content,owner_id) VALUES ('a2','shared text','owner-a')")
        self.db.execute("INSERT INTO user_memories (id,content,owner_id) VALUES ('b2','shared text','owner-b')")
        self.db.commit()
        self.assertEqual([r[0] for r in self.db.execute("SELECT content FROM conversations WHERE owner_id='owner-a' ORDER BY id")], ["legacy chat", "private A"])
        self.assertEqual([r[0] for r in self.db.execute("SELECT content FROM user_memories WHERE owner_id='owner-b'")], ["shared text"])
        self.db.execute("DELETE FROM user_memories WHERE owner_id='owner-a'")
        self.db.commit()
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM user_memories WHERE owner_id='owner-b'").fetchone()[0], 1)

    def test_memory_create_read_update_delete_survives_reopen(self):
        self.migrate("owner-a")
        self.db.execute("INSERT INTO user_memories (id,content,owner_id) VALUES ('m1','first','owner-a')")
        self.db.commit()
        self.db.close()
        reopened = sqlite3.connect(self.db_path)
        self.assertEqual(reopened.execute("SELECT content FROM user_memories WHERE id='m1' AND owner_id='owner-a'").fetchone()[0], "first")
        reopened.execute("UPDATE user_memories SET content='updated' WHERE id='m1' AND owner_id='owner-a'")
        reopened.commit()
        self.assertEqual(reopened.execute("SELECT content FROM user_memories WHERE id='m1' AND owner_id='owner-a'").fetchone()[0], "updated")
        reopened.execute("DELETE FROM user_memories WHERE id='m1' AND owner_id='owner-a'")
        reopened.commit()
        self.assertEqual(reopened.execute("SELECT COUNT(*) FROM user_memories WHERE id='m1'").fetchone()[0], 0)
        reopened.close()


if __name__ == "__main__":
    unittest.main()
