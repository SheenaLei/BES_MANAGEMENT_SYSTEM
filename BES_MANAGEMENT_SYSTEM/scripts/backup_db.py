# scripts/backup_db.py
import subprocess
import os
from datetime import datetime
from app.config import BACKUP_FOLDER, SQLALCHEMY_DATABASE_URI
from app.db import SessionLocal
from urllib.parse import urlparse
from pathlib import Path

BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)

def parse_mysql_uri(uri: str):
    # expected mysql+pymysql://user:pass@host:port/db
    if uri.startswith("mysql+pymysql://"):
        uri = uri.replace("mysql+pymysql://", "mysql://")
    parsed = urlparse(uri)
    user = parsed.username
    password = parsed.password
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 3306
    db = parsed.path.lstrip("/")
    return user, password, host, port, db

def backup():
    user, password, host, port, dbname = parse_mysql_uri(SQLALCHEMY_DATABASE_URI)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{dbname}_{ts}.sql"
    out_path = Path(BACKUP_FOLDER) / filename

    # mysqldump must be available in PATH
    cmd = [
        "mysqldump",
        "-h", host,
        "-P", str(port),
        "-u", user,
        f"-p{password}",
        dbname
    ]
    with open(out_path, "wb") as f:
        proc = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            print("Backup failed:", proc.stderr.decode())
            return False
    # record in backups table (optional)
    try:
        db = SessionLocal()
        db.execute("INSERT INTO backups (filename, created_at) VALUES (%s, NOW())", (str(out_path),))
        db.commit()
        db.close()
    except Exception:
        pass
    print(f"Backup saved to: {out_path}")
    return True

if __name__ == "__main__":
    backup()