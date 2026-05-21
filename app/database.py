from pathlib import Path
import json
import sqlite3
from datetime import datetime, UTC

from app.config import BASE_DIR, DATABASE_PATH, LEGACY_ROOT_FILES, ensure_directories
from app.security import hash_password


class Database:
    def __init__(self) -> None:
        ensure_directories()
        self.connection = sqlite3.connect(DATABASE_PATH)
        self.connection.row_factory = sqlite3.Row
        self._create_schema()
        self._migrate_legacy_users()

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT,
                face_image_path TEXT,
                face_embedding TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS auth_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                method TEXT NOT NULL,
                success INTEGER NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def upsert_user(self, username: str, password_hash: str | None = None) -> None:
        now = datetime.now(UTC).isoformat()
        existing = self.get_user(username)
        if existing is None:
            self.connection.execute(
                """
                INSERT INTO users (username, password_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (username, password_hash, now, now),
            )
        else:
            self.connection.execute(
                """
                UPDATE users
                SET password_hash = COALESCE(?, password_hash),
                    updated_at = ?
                WHERE username = ?
                """,
                (password_hash, now, username),
            )
        self.connection.commit()

    def update_face_data(self, username: str, image_path: str, embedding: list[float]) -> None:
        now = datetime.now(UTC).isoformat()
        self.connection.execute(
            """
            UPDATE users
            SET face_image_path = ?, face_embedding = ?, updated_at = ?
            WHERE username = ?
            """,
            (image_path, json.dumps(embedding), now, username),
        )
        self.connection.commit()

    def get_user(self, username: str) -> sqlite3.Row | None:
        cursor = self.connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        )
        return cursor.fetchone()

    def record_auth_attempt(
        self,
        username: str,
        method: str,
        success: bool,
        reason: str,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO auth_attempts (username, method, success, reason, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                method,
                int(success),
                reason,
                datetime.now(UTC).isoformat(),
            ),
        )
        self.connection.commit()

    def _migrate_legacy_users(self) -> None:
        for legacy_file in self._find_legacy_user_files():
            username, password = self._read_legacy_user_file(legacy_file)
            if username is None or password is None:
                continue

            self.upsert_user(username, hash_password(password))
            legacy_file.unlink(missing_ok=True)

    def _find_legacy_user_files(self) -> list[Path]:
        legacy_files: list[Path] = []
        for file_path in BASE_DIR.iterdir():
            if not file_path.is_file():
                continue
            if file_path.name in LEGACY_ROOT_FILES:
                continue
            if file_path.suffix:
                continue
            legacy_files.append(file_path)
        return legacy_files

    @staticmethod
    def _read_legacy_user_file(file_path: Path) -> tuple[str | None, str | None]:
        lines = file_path.read_text(encoding="utf-8").splitlines()
        if len(lines) != 2:
            return None, None

        username = lines[0].strip()
        password = lines[1].strip()
        if not username or not password:
            return None, None
        if username != file_path.name:
            return None, None
        return username, password
