from getpass import getpass

from passlib.context import CryptContext

from database import get_connection


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


OFFICERS = [
    {
        "name": "Roads Officer",
        "username": "roads_officer",
        "department": "Roads / Engineering",
        "role": "Department Officer"
    },
    {
        "name": "Water Supply Officer",
        "username": "water_officer",
        "department": "Water Supply",
        "role": "Department Officer"
    },
    {
        "name": "Drainage Officer",
        "username": "drainage_officer",
        "department": "Drainage & Sewerage",
        "role": "Department Officer"
    },
    {
        "name": "Waste Management Officer",
        "username": "waste_officer",
        "department": "Waste Management",
        "role": "Department Officer"
    },
    {
        "name": "Healthcare Officer",
        "username": "health_officer",
        "department": "Healthcare",
        "role": "Department Officer"
    },
    {
        "name": "Education Officer",
        "username": "education_officer",
        "department": "Education",
        "role": "Department Officer"
    },
    {
        "name": "Street Lighting Officer",
        "username": "lighting_officer",
        "department": "Street Lighting",
        "role": "Department Officer"
    },
    {
        "name": "General Officer",
        "username": "general_officer",
        "department": "General Administration",
        "role": "Department Officer"
    }
]


def create_officers():
    connection = get_connection()
    try:
        cursor = connection.cursor()

        for officer in OFFICERS:
            cursor.execute(
                "SELECT 1 FROM officers WHERE username = ?",
                (officer["username"],)
            )
            if cursor.fetchone():
                print(f"Already exists: {officer['username']}")
                continue

            password = getpass(
                f"Set password for {officer['username']}: "
            )
            confirmation = getpass("Confirm password: ")
            if not password:
                raise ValueError("Officer passwords cannot be empty.")
            if password != confirmation:
                raise ValueError("Officer passwords do not match.")

            password_hash = pwd_context.hash(password)
            cursor.execute(
                """
                INSERT INTO officers (
                    name,
                    username,
                    password_hash,
                    department,
                    role
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    officer["name"],
                    officer["username"],
                    password_hash,
                    officer["department"],
                    officer["role"]
                )
            )
            print(
                f"Created: {officer['username']} "
                f"→ {officer['department']}"
            )

        connection.commit()
    finally:
        connection.close()

    print("\nOfficer setup complete.")


if __name__ == "__main__":
    create_officers()