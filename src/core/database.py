import sqlite3
import os
from typing import List, Optional
from datetime import datetime

from src.models.project import Project
from src.config.settings import get_app_data_dir

class ProjectDB:
    def __init__(self):
        self.db_path = os.path.join(get_app_data_dir(), 'projects.db')
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, style TEXT, area TEXT, canvas_file TEXT,
                created_at TEXT, updated_at TEXT
            )
        ''')
        self.conn.commit()

    def add_project(self, name: str, style: str, area: str, canvas_file: str) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, style, area, canvas_file, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, style, area, canvas_file, now, now))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_projects(self) -> List[Project]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, style, area, canvas_file, created_at, updated_at 
            FROM projects ORDER BY updated_at DESC
        ''')
        return [Project(*row) for row in cursor.fetchall()]

    def update_project(self, project_id: int, name: str, style: str, area: str, canvas_file: Optional[str] = None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        if canvas_file is None:
            cursor.execute('''
                UPDATE projects SET name=?, style=?, area=?, updated_at=? WHERE id=?
            ''', (name, style, area, now, project_id))
        else:
            cursor.execute('''
                UPDATE projects SET name=?, style=?, area=?, canvas_file=?, updated_at=? WHERE id=?
            ''', (name, style, area, canvas_file, now, project_id))
        self.conn.commit()

    def delete_project(self, project_id: int):
        cursor = self.conn.cursor()
        cursor.execute('SELECT canvas_file FROM projects WHERE id=?', (project_id,))
        row = cursor.fetchone()
        if row and row[0]:
            base = row[0].rsplit('.', 1)[0]
            for p in (row[0], base + '.thumb.png'):
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except OSError:
                    pass
        cursor.execute('DELETE FROM projects WHERE id=?', (project_id,))
        self.conn.commit()

    def get_project(self, project_id: int) -> Optional[Project]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, style, area, canvas_file, created_at, updated_at 
            FROM projects WHERE id=?
        ''', (project_id,))
        row = cursor.fetchone()
        return Project(*row) if row else None

    def close(self):
        self.conn.close()