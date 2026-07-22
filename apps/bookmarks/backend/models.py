import sqlite3
from apps.bookmarks.backend import config


def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                icon TEXT DEFAULT '',
                tag TEXT DEFAULT '工具',
                position INTEGER DEFAULT 0
            )
        """)
        # seed data if empty
        cur = conn.execute("SELECT COUNT(*) FROM bookmarks")
        if cur.fetchone()[0] == 0:
            seeds = [
                ("动漫花园资源网", "https://dongmanhuayuan.myheartsite.com/", "🌸", "动漫"),
                ("嗷呜动漫", "https://www.aowu.tv/", "🎥", "动漫"),
                ("Chub.ai — 角色卡社区", "https://chub.ai/", "🤖", "AI"),
                ("Convertio — 在线文件转换", "https://convertio.co/", "🔄", "工具"),
            ]
            for i, (name, url, icon, tag) in enumerate(seeds):
                conn.execute(
                    "INSERT INTO bookmarks (name, url, icon, tag, position) VALUES (?,?,?,?,?)",
                    (name, url, icon, tag, i),
                )
        conn.commit()


def list_all():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, url, icon, tag FROM bookmarks ORDER BY position").fetchall()
    return [{"id": r[0], "name": r[1], "url": r[2], "icon": r[3], "tag": r[4]} for r in rows]


def add(name, url, icon, tag):
    with get_conn() as conn:
        cur = conn.execute("SELECT COALESCE(MAX(position), -1) + 1 FROM bookmarks")
        pos = cur.fetchone()[0]
        conn.execute(
            "INSERT INTO bookmarks (name, url, icon, tag, position) VALUES (?,?,?,?,?)",
            (name, url, icon, tag, pos),
        )
        conn.commit()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def update(bid, name, url, icon, tag):
    with get_conn() as conn:
        conn.execute(
            "UPDATE bookmarks SET name=?, url=?, icon=?, tag=? WHERE id=?",
            (name, url, icon, tag, bid),
        )
        conn.commit()


def delete(bid):
    with get_conn() as conn:
        conn.execute("DELETE FROM bookmarks WHERE id=?", (bid,))
        conn.commit()
