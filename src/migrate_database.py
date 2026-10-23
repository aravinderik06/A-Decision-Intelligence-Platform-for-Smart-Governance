
# ============================================================
# SMART GOVERNANCE - DATABASE MIGRATION
# Adds officer_id to an existing officer_decisions table.
# Preserves all existing database records.
# ============================================================

from database import get_connection


def migrate_database():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Check the existing officer_decisions columns.
        cursor.execute("PRAGMA table_info(officer_decisions)")
        columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        if "officer_id" not in columns:
            cursor.execute(
                """
                ALTER TABLE officer_decisions
                ADD COLUMN officer_id INTEGER
                """
            )
            print("Added officer_id column successfully.")
        else:
            print("officer_id column already exists.")

        connection.commit()

        # Verify the migration.
        cursor.execute("PRAGMA table_info(officer_decisions)")
        updated_columns = [
            row["name"]
            for row in cursor.fetchall()
        ]

        print("Current officer_decisions columns:")
        for column in updated_columns:
            print(f"- {column}")

        print("\nDatabase migration completed.")

    finally:
        connection.close()


if __name__ == "__main__":
    migrate_database()
