# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / 'inspiration_gallery.db'

styles = [
    ('vangogh', '梵高', 1),
    ('ink', '水墨', 1),
    ('cezanne', '塞尚', 1),
    ('monet', '莫奈', 1),
    ('ukiyoe', '浮世绘', 1),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executemany(
    """
    INSERT OR IGNORE INTO styles (code, name, is_active)
    VALUES (?, ?, ?)
    """,
    styles,
)

conn.commit()

cur.execute("SELECT id, code, name, is_active FROM styles ORDER BY id")
rows = cur.fetchall()
print(rows)

conn.close()
