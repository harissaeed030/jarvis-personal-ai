"""SQLite regression tests for JARVIS' non-destructive D1 owner-scope migration.

These tests exercise migration and persistence semantics, not authenticated
production HTTP calls.
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

    def account_scope(self, candidate):
        self.db.execute("CREATE TABLE IF NOT EXISTS jarvis_account_scope (id INTEGER PRIMARY KEY CHECK(id=1), owner_id TEXT NOT NULL)")
        self.db.execute("INSERT OR IGNORE INTO jarvis_account_scope (id,owner_id) VALUES (1,?)", (candidate,))
        self.db.commit()
        return self.db.execute("SELECT owner_id FROM jarvis_account_scope WHERE id=1").fetchone()[0]

    def migrate(self, owner):
        owner = self.account_scope(owner)
        for table in ("conversations", "user_memories"):
            columns = {row[1] for row in self.db.execute(f"PRAGMA table_info({table})")}
            if "owner_id" not in columns:
                self.db.execute(f"ALTER TABLE {table} ADD COLUMN owner_id TEXT NOT NULL DEFAULT 'legacy'")
            self.db.execute(f"UPDATE {table} SET owner_id=? WHERE owner_id='legacy' OR owner_id IS NULL", (owner,))
        self.db.execute("CREATE TABLE IF NOT EXISTS jarvis_schema_migrations (name TEXT PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        self.db.execute("CREATE TABLE IF NOT EXISTS user_memories_scoped (id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(owner_id,content))")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO user_memories_scoped (id,owner_id,content,created_at) SELECT id,owner_id,content,created_at FROM user_memories WHERE NOT EXISTS (SELECT 1 FROM jarvis_schema_migrations WHERE name='memory_owner_copy_v2')")
            self.db.execute("INSERT OR IGNORE INTO jarvis_schema_migrations (name) VALUES ('memory_owner_copy_v2')")

    def test_owner_scope_survives_password_rotation(self):
        first = self.account_scope("initial-owner-id")
        after_password_change = self.account_scope("different-candidate-id")
        self.assertEqual(first, after_password_change)

    def test_legacy_rows_are_preserved_and_scoped_to_existing_owner(self):
        self.migrate("owner-a")
        self.assertEqual(self.db.execute("SELECT content FROM conversations WHERE owner_id=?", ("owner-a",)).fetchone()[0], "legacy chat")
        self.assertEqual(self.db.execute("SELECT content FROM user_memories_scoped WHERE owner_id=?", ("owner-a",)).fetchone()[0], "legacy memory")
        # The source table is deliberately retained; migration is non-destructive.
        self.assertEqual(self.db.execute("SELECT content FROM user_memories WHERE id='old-m1'").fetchone()[0], "legacy memory")

    def test_conversations_and_memory_are_isolated_between_owners(self):
        self.migrate("owner-a")
        self.db.execute("INSERT INTO conversations (id,role,content,owner_id) VALUES ('a1','user','private A','owner-a')")
        self.db.execute("INSERT INTO conversations (id,role,content,owner_id) VALUES ('b1','user','private B','owner-b')")
        self.db.execute("INSERT INTO user_memories_scoped (id,content,owner_id) VALUES ('a2','shared text','owner-a')")
        self.db.execute("INSERT INTO user_memories_scoped (id,content,owner_id) VALUES ('b2','shared text','owner-b')")
        self.db.commit()
        self.assertEqual([r[0] for r in self.db.execute("SELECT content FROM conversations WHERE owner_id='owner-a' ORDER BY id")], ["private A", "legacy chat"])
        self.assertEqual([r[0] for r in self.db.execute("SELECT content FROM user_memories_scoped WHERE owner_id='owner-b'")], ["shared text"])
        self.db.execute("DELETE FROM user_memories_scoped WHERE owner_id='owner-a'")
        self.db.commit()
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM user_memories_scoped WHERE owner_id='owner-b'").fetchone()[0], 1)

    def test_memory_create_read_update_delete_survives_reopen(self):
        self.migrate("owner-a")
        self.db.execute("INSERT INTO user_memories_scoped (id,content,owner_id) VALUES ('m1','first','owner-a')")
        self.db.commit()
        self.db.close()
        reopened = sqlite3.connect(self.db_path)
        self.assertEqual(reopened.execute("SELECT content FROM user_memories_scoped WHERE id='m1' AND owner_id='owner-a'").fetchone()[0], "first")
        reopened.execute("UPDATE user_memories_scoped SET content='updated' WHERE id='m1' AND owner_id='owner-a'")
        reopened.commit()
        self.assertEqual(reopened.execute("SELECT content FROM user_memories_scoped WHERE id='m1' AND owner_id='owner-a'").fetchone()[0], "updated")
        reopened.execute("DELETE FROM user_memories_scoped WHERE id='m1' AND owner_id='owner-a'")
        reopened.commit()
        self.assertEqual(reopened.execute("SELECT COUNT(*) FROM user_memories_scoped WHERE id='m1'").fetchone()[0], 0)
        reopened.close()

    def test_migration_is_idempotent_and_deleted_items_are_not_resurrected(self):
        self.migrate("owner-a")
        self.db.execute("INSERT INTO user_memories_scoped (id,content,owner_id) VALUES ('new1','new memory','owner-a')")
        self.db.execute("DELETE FROM user_memories_scoped WHERE id='old-m1'")
        self.db.commit()
        self.migrate("owner-a")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM user_memories_scoped WHERE id='new1'").fetchone()[0], 1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM user_memories_scoped WHERE id='old-m1'").fetchone()[0], 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM jarvis_schema_migrations WHERE name='memory_owner_copy_v2'").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
