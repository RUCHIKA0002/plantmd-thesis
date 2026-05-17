import sqlite3
import json
import datetime

DB_PATH = "scans.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            disease_name TEXT,
            status TEXT,
            severity TEXT,
            confidence INTEGER,
            urgency TEXT,
            affected_parts TEXT,
            full_result TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_scan(result: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO scans VALUES (NULL,?,?,?,?,?,?,?,?)",
        (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            result.get("disease_name", "Unknown"),
            result.get("status", "unknown"),
            result.get("severity", "N/A"),
            result.get("confidence", 0),
            result.get("urgency", "N/A"),
            ", ".join(result.get("affected_parts", [])),
            json.dumps(result),
        ),
    )
    conn.commit()
    conn.close()

def get_all_scans():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM scans ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_scan_stats():
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
    diseased = conn.execute(
        "SELECT COUNT(*) FROM scans WHERE status='diseased'"
    ).fetchone()[0]
    healthy = conn.execute(
        "SELECT COUNT(*) FROM scans WHERE status='healthy'"
    ).fetchone()[0]
    avg_conf = conn.execute(
        "SELECT AVG(confidence) FROM scans"
    ).fetchone()[0]
    conn.close()
    return {
        "total": total,
        "diseased": diseased,
        "healthy": healthy,
        "avg_confidence": round(avg_conf or 0, 1),
    }