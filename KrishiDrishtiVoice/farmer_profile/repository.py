import os
import sqlite3
from pathlib import Path
from typing import Any
from contextlib import contextmanager


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "krishidrishti_profiles.sqlite3"


def get_db_path() -> Path:
    return Path(os.getenv("KRISHIDRISHTI_PROFILE_DB", str(DEFAULT_DB_PATH)))


@contextmanager
def connect():
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                mobile TEXT,
                email TEXT,
                age INTEGER,
                gender TEXT,
                village TEXT,
                gram_panchayat TEXT,
                taluk TEXT,
                district TEXT,
                state TEXT,
                pin_code TEXT,
                preferred_language TEXT DEFAULT 'English',
                response_mode TEXT DEFAULT 'Text',
                text_size TEXT DEFAULT 'Medium',
                voice_response INTEGER DEFAULT 0,
                notifications INTEGER DEFAULT 1,
                photo_path TEXT
            );
            CREATE TABLE IF NOT EXISTS farms (
                id INTEGER PRIMARY KEY,
                farmer_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                location TEXT,
                area REAL,
                area_unit TEXT,
                ownership TEXT,
                soil_type TEXT,
                irrigation_type TEXT,
                water_source TEXT,
                notes TEXT,
                latitude REAL,
                longitude REAL,
                boundary_coordinates TEXT,
                FOREIGN KEY(farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY,
                farmer_id INTEGER NOT NULL,
                farm_id INTEGER,
                name TEXT NOT NULL,
                variety TEXT,
                season TEXT,
                sowing_date TEXT,
                cultivated_area REAL,
                growth_stage TEXT,
                expected_harvest TEXT,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY(farmer_id) REFERENCES farmers(id) ON DELETE CASCADE,
                FOREIGN KEY(farm_id) REFERENCES farms(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS consultations (
                id INTEGER PRIMARY KEY,
                farmer_id INTEGER,
                topic TEXT,
                farm_id INTEGER,
                crop_id INTEGER,
                language TEXT,
                question TEXT,
                answer TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY,
                farmer_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0
            );
            """
        )
        columns = {row[1] for row in db.execute("PRAGMA table_info(farms)").fetchall()}
        for name, definition in (("latitude", "REAL"), ("longitude", "REAL"), ("boundary_coordinates", "TEXT")):
            if name not in columns:
                try:
                    db.execute(f"ALTER TABLE farms ADD COLUMN {name} {definition}")
                except sqlite3.OperationalError:
                    # Read-only packaged/demo databases remain usable; a writable
                    # deployment will apply the migration on its next startup.
                    pass


def get_profile() -> dict[str, Any] | None:
    with connect() as db:
        row = db.execute("SELECT * FROM farmers ORDER BY id LIMIT 1").fetchone()
    return dict(row) if row else None


def save_profile(profile: dict[str, Any]) -> int:
    initialize_database()
    if "name" in profile and not str(profile["name"]).strip():
        raise ValueError("Farmer name is required")
    current = get_profile()
    fields = list(profile)
    values = [profile[field] for field in fields]
    with connect() as db:
        if current:
            assignments = ", ".join(f"{field} = ?" for field in fields)
            db.execute(f"UPDATE farmers SET {assignments} WHERE id = ?", (*values, current["id"]))
            return int(current["id"])
        placeholders = ", ".join("?" for _ in fields)
        columns = ", ".join(fields)
        cursor = db.execute(f"INSERT INTO farmers ({columns}) VALUES ({placeholders})", values)
        return int(cursor.lastrowid)


def list_farms() -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute("SELECT * FROM farms ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


def save_farm(farm: dict[str, Any], farm_id: int | None = None) -> int:
    initialize_database()
    profile = get_profile()
    if profile:
        farmer_id = profile["id"]
    else:
        with connect() as db:
            cursor = db.execute("INSERT INTO farmers (name) VALUES (?)", ("Farmer",))
            farmer_id = int(cursor.lastrowid)
    fields = dict(farm)
    fields["farmer_id"] = farmer_id
    with connect() as db:
        existing_columns = {row[1] for row in db.execute("PRAGMA table_info(farms)").fetchall()}
        fields = {key: value for key, value in fields.items() if key in existing_columns}
        if farm_id:
            assignments = ", ".join(f"{field} = ?" for field in fields)
            db.execute(f"UPDATE farms SET {assignments} WHERE id = ?", (*[fields[f] for f in fields], farm_id))
            return farm_id
        columns = ", ".join(fields)
        placeholders = ", ".join("?" for _ in fields)
        cursor = db.execute(f"INSERT INTO farms ({columns}) VALUES ({placeholders})", [fields[f] for f in fields])
        return int(cursor.lastrowid)


def delete_farm(farm_id: int) -> None:
    with connect() as db:
        db.execute("DELETE FROM farms WHERE id = ?", (farm_id,))


def list_crops() -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute(
            "SELECT c.*, f.name AS farm_name FROM crops c LEFT JOIN farms f ON f.id = c.farm_id ORDER BY c.id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def save_crop(crop: dict[str, Any], crop_id: int | None = None) -> int:
    initialize_database()
    profile = get_profile()
    if profile:
        farmer_id = profile["id"]
    else:
        with connect() as db:
            cursor = db.execute("INSERT INTO farmers (name) VALUES (?)", ("Farmer",))
            farmer_id = int(cursor.lastrowid)
    fields = dict(crop)
    fields["farmer_id"] = farmer_id
    with connect() as db:
        if crop_id:
            assignments = ", ".join(f"{field} = ?" for field in fields)
            db.execute(f"UPDATE crops SET {assignments} WHERE id = ?", (*[fields[f] for f in fields], crop_id))
            return crop_id
        columns = ", ".join(fields)
        placeholders = ", ".join("?" for _ in fields)
        cursor = db.execute(f"INSERT INTO crops ({columns}) VALUES ({placeholders})", [fields[f] for f in fields])
        return int(cursor.lastrowid)


def delete_crop(crop_id: int) -> None:
    with connect() as db:
        db.execute("DELETE FROM crops WHERE id = ?", (crop_id,))


def save_consultation(topic: str, question: str, answer: str, farm_id: int | None, crop_id: int | None, language: str) -> None:
    profile = get_profile()
    with connect() as db:
        db.execute(
            "INSERT INTO consultations (farmer_id, topic, farm_id, crop_id, language, question, answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (profile["id"] if profile else None, topic, farm_id, crop_id, language, question, answer),
        )


def list_consultations() -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute(
            "SELECT c.*, f.name AS farm_name, cr.name AS crop_name FROM consultations c "
            "LEFT JOIN farms f ON f.id = c.farm_id LEFT JOIN crops cr ON cr.id = c.crop_id "
            "ORDER BY c.created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def delete_consultation(consultation_id: int) -> None:
    with connect() as db:
        db.execute("DELETE FROM consultations WHERE id = ?", (consultation_id,))


def list_notifications() -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute("SELECT * FROM notifications ORDER BY created_at DESC").fetchall()
    return [dict(row) for row in rows]


def mark_notification_read(notification_id: int) -> None:
    with connect() as db:
        db.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))


def mark_all_notifications_read() -> None:
    with connect() as db:
        db.execute("UPDATE notifications SET is_read = 1")


def delete_notification(notification_id: int) -> None:
    with connect() as db:
        db.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
