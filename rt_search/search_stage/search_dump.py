import sqlite3
import json
import queue
import threading

from rt_search.utils.types import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rt_search.analysis_stage.subspaces.searchable import Searchable
    from rt_search.search_stage.data_manager import DataManager


class DBWriter(threading.Thread):
    def __init__(self, db_path, q, batch_size=10):
        super().__init__(daemon=True)
        self.db_path = db_path
        self.q = q
        self.batch_size = batch_size
        self.stop_signal = False

    def run(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS results (
                constant TEXT PRIMARY KEY,
                CMF TEXT,
                results TEXT
            )
        """)
        conn.commit()

        buffer = []
        while not self.stop_signal or not self.q.empty():
            try:
                item = self.q.get(timeout=0.5)
                buffer.append(item)
                if len(buffer) >= self.batch_size:
                    self.__flush(cur, conn, buffer)
                    buffer.clear()
            except queue.Empty:
                if buffer:
                    self.__flush(cur, conn, buffer)
                    buffer.clear()
        conn.close()

    @staticmethod
    def __flush(cur, conn, buffer: List[Tuple[str, CMF, "DataManager"]]):
        cur.executemany(
            "INSERT OR REPLACE INTO results (constant, CMF, results) VALUES (?, ?, ?)",
            [(const, str(cmf), json.dumps(res.as_json_serializable())) for const, cmf, res in buffer]
        )
        conn.commit()
