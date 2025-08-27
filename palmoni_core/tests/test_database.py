import pytest
import tempfile
import duckdb
from pathlib import Path

from palmoni_core.core.database import SnippetDatabase


class TestSnippetDatabase:
    def create_test_database(self, temp_dir: str) -> Path:
        """Helper to create a test database with sample data."""
        db_path = Path(temp_dir) / "test.db"
        conn = duckdb.connect(str(db_path))
        
        # Create table
        conn.execute("""
            CREATE TABLE snippets (
                trigger TEXT PRIMARY KEY,
                expansion TEXT NOT NULL,
                category TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data
        test_snippets = [
            ("py::class", "class Test:\n    pass", "python"),
            ("git::st", "git status", "git"),
            ("test::long", "a" * 60, "test")
        ]
        
        for trigger, expansion, category in test_snippets:
            conn.execute("""
                INSERT INTO snippets (trigger, expansion, category)
                VALUES (?, ?, ?)
            """, [trigger, expansion, category])
        
        conn.close()
        return db_path
    
    def test_init_with_existing_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = self.create_test_database(temp_dir)
            
            db = SnippetDatabase(db_path)
            assert db.db_path == db_path
    
    def test_init_with_missing_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "missing.db"
            
            with pytest.raises(FileNotFoundError):
                SnippetDatabase(db_path)
    
    def test_load_all_snippets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = self.create_test_database(temp_dir)
            db = SnippetDatabase(db_path)
            
            snippets = db.load_all_snippets()
            
            assert len(snippets) == 3
            assert snippets["py::class"] == "class Test:\n    pass"
            assert snippets["git::st"] == "git status"
            assert snippets["test::long"] == "a" * 60
    
    def test_get_snippet_count(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = self.create_test_database(temp_dir)
            db = SnippetDatabase(db_path)
            
            count = db.get_snippet_count()
            assert count == 3
    
    def test_load_all_snippets_empty_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty database
            db_path = Path(temp_dir) / "empty.db"
            conn = duckdb.connect(str(db_path))
            conn.execute("""
                CREATE TABLE snippets (
                    trigger TEXT PRIMARY KEY,
                    expansion TEXT NOT NULL,
                    category TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.close()
            
            db = SnippetDatabase(db_path)
            snippets = db.load_all_snippets()
            
            assert snippets == {}
    
    def test_get_snippet_count_empty_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty database
            db_path = Path(temp_dir) / "empty.db"
            conn = duckdb.connect(str(db_path))
            conn.execute("""
                CREATE TABLE snippets (
                    trigger TEXT PRIMARY KEY,
                    expansion TEXT NOT NULL,
                    category TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.close()
            
            db = SnippetDatabase(db_path)
            count = db.get_snippet_count()
            
            assert count == 0