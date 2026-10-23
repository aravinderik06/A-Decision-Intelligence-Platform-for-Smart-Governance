import sqlite3
from pathlib import Path


DATABASE_DIR = Path("data/database")
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "smart_governance.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # ==============================================
    # OFFICERS
    # ==============================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS officers (
            officer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL,
            active INTEGER DEFAULT 1
        )
    """)

    # ==============================================
    # COMPLAINTS
    # ==============================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_text TEXT NOT NULL,
            area_id TEXT,
            complaint_date TEXT NOT NULL,
            status TEXT DEFAULT 'Submitted'
        )
    """)

    # ==============================================
    # PREDICTIONS
    # ==============================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            problem_category TEXT,
            classification_confidence REAL,
            severity_score REAL,
            priority TEXT,
            recommendation TEXT,
            suggested_action TEXT,
            reason TEXT,
            shap_explanation TEXT,
            FOREIGN KEY (complaint_id)
                REFERENCES complaints(complaint_id)
        )
    """)

    # ==============================================
    # OFFICER DECISIONS
    # ==============================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS officer_decisions (
            decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            officer_id INTEGER NOT NULL,
            decision TEXT NOT NULL,
            officer_reason TEXT,
            decision_date TEXT NOT NULL,
            FOREIGN KEY (complaint_id)
                REFERENCES complaints(complaint_id),
            FOREIGN KEY (officer_id)
                REFERENCES officers(officer_id)
        )
    """)

    connection.commit()
    connection.close()

    print("Database tables created successfully.")
    print(f"Database location: {DATABASE_PATH}")


if __name__ == "__main__":
    create_tables()