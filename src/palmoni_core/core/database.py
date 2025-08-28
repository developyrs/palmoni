import duckdb
import logging
from pathlib import Path
from typing import Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class SnippetDatabase:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
    
    @contextmanager
    def _get_connection(self):
        conn = duckdb.connect(str(self.db_path))
        try:
            yield conn
        finally:
            conn.close()
    
    def load_all_snippets(self) -> Dict[str, str]:
        with self._get_connection() as conn:
            result = conn.execute("SELECT trigger, expansion FROM snippets").fetchall()
            return {trigger: expansion for trigger, expansion in result}
    
    def get_snippet_count(self) -> int:
        with self._get_connection() as conn:
            result = conn.execute("SELECT COUNT(*) FROM snippets").fetchone()
            return result[0] if result else 0