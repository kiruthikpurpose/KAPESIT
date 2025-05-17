import sqlite3
import json
class DataStore:
    def __init__(self, db_path='datastore.db'):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    def _init_db(self):
        c = self.conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT)')
        self.conn.commit()
    def put(self, key, value):
        c = self.conn.cursor()
        c.execute('REPLACE INTO data (key, value) VALUES (?, ?)', (key, json.dumps(value)))
        self.conn.commit()
    def get(self, key):
        c = self.conn.cursor()
        c.execute('SELECT value FROM data WHERE key=?', (key,))
        row = c.fetchone()
        return json.loads(row[0]) if row else None
    def delete(self, key):
        c = self.conn.cursor()
        c.execute('DELETE FROM data WHERE key=?', (key,))
        self.conn.commit() 