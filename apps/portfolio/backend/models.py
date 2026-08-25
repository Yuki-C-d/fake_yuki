"""作品表 SQLite 操作 — 每次调用开新连接，contextlib.closing 保证关闭"""
import sqlite3
from contextlib import closing

from apps.portfolio.backend import config


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_conn()) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS works (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                media_type TEXT NOT NULL,
                file_path TEXT UNIQUE NOT NULL,
                thumb_path TEXT,
                file_size INTEGER,
                width INTEGER,
                height INTEGER,
                position INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # migration: 旧表补 position 列，按创建顺序初始化
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(works)")]
        if "position" not in cols:
            conn.execute("ALTER TABLE works ADD COLUMN position INTEGER")
            conn.execute("UPDATE works SET position = id")


def _to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    # sqlite CURRENT_TIMESTAMP 是 UTC "YYYY-MM-DD HH:MM:SS"，转 ISO-8601 给 JS 解析
    if d.get("created_at"):
        d["created_at"] = d["created_at"].replace(" ", "T") + "Z"
    return d


def list_works() -> list[dict]:
    with closing(get_conn()) as conn, conn:
        rows = conn.execute(
            "SELECT * FROM works ORDER BY position ASC, id ASC"
        ).fetchall()
        return [_to_dict(r) for r in rows]


def get_work(work_id: int) -> dict | None:
    with closing(get_conn()) as conn, conn:
        row = conn.execute("SELECT * FROM works WHERE id = ?", (work_id,)).fetchone()
        return _to_dict(row) if row else None


def add_work(title: str, description: str, media_type: str, file_path: str,
             thumb_path: str | None, file_size: int,
             width: int | None, height: int | None) -> dict:
    with closing(get_conn()) as conn, conn:
        next_pos = conn.execute(
            "SELECT COALESCE(MAX(position), 0) + 1 FROM works"
        ).fetchone()[0]
        cur = conn.execute(
            """INSERT INTO works (title, description, media_type, file_path,
                                  thumb_path, file_size, width, height, position)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, description, media_type, file_path, thumb_path,
             file_size, width, height, next_pos),
        )
        conn.commit()
    return get_work(cur.lastrowid)


def update_work(work_id: int, title: str, description: str) -> dict | None:
    with closing(get_conn()) as conn, conn:
        conn.execute(
            "UPDATE works SET title = ?, description = ? WHERE id = ?",
            (title, description, work_id),
        )
        conn.commit()
    return get_work(work_id)


def delete_work(work_id: int) -> dict | None:
    """删除并返回被删行（调用方据此清理磁盘文件）"""
    with closing(get_conn()) as conn, conn:
        row = conn.execute("SELECT * FROM works WHERE id = ?", (work_id,)).fetchone()
        if not row:
            return None
        conn.execute("DELETE FROM works WHERE id = ?", (work_id,))
        return _to_dict(row)


def move_work(work_id: int, direction: str) -> bool | None:
    """与相邻作品交换 position。返回 True=成功, False=已在边界, None=不存在"""
    with closing(get_conn()) as conn, conn:
        row = conn.execute(
            "SELECT position FROM works WHERE id = ?", (work_id,)
        ).fetchone()
        if not row:
            return None
        pos = row["position"]
        if direction == "up":
            other = conn.execute(
                "SELECT id, position FROM works WHERE position < ? "
                "ORDER BY position DESC LIMIT 1", (pos,)
            ).fetchone()
        else:
            other = conn.execute(
                "SELECT id, position FROM works WHERE position > ? "
                "ORDER BY position ASC LIMIT 1", (pos,)
            ).fetchone()
        if not other:
            return False
        conn.execute(
            "UPDATE works SET position = ? WHERE id = ?", (other["position"], work_id)
        )
        conn.execute(
            "UPDATE works SET position = ? WHERE id = ?", (pos, other["id"])
        )
        conn.commit()
        return True
