import os
import shutil
from datetime import datetime, date

from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash


app = create_app()


# =========================
# DB PATH (DEV DEFAULT)
# =========================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

BACKUP_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

BACKUP_A = os.path.join(BACKUP_DIR, "app_backup_A.db")
BACKUP_B = os.path.join(BACKUP_DIR, "app_backup_B.db")
STATE_FILE = os.path.join(BACKUP_DIR, "backup_state.txt")


# =========================
# BACKUP LOGIC
# =========================
def should_backup():
    if not os.path.exists(STATE_FILE):
        return True

    try:
        with open(STATE_FILE, "r") as f:
            last_date = f.read().strip().split(",")[0]

        last = datetime.strptime(last_date, "%Y-%m-%d").date()
        return (date.today() - last).days >= 3

    except Exception:
        return True


def get_backup_slot():
    if not os.path.exists(STATE_FILE):
        return "A"

    try:
        with open(STATE_FILE, "r") as f:
            parts = f.read().strip().split(",")

        if len(parts) < 2:
            return "A"

        return "B" if parts[1] == "A" else "A"

    except Exception:
        return "A"


def backup_db():
    if not os.path.exists(DB_PATH):
        return

    slot = get_backup_slot()
    target = BACKUP_A if slot == "A" else BACKUP_B

    shutil.copy2(DB_PATH, target)

    with open(STATE_FILE, "w") as f:
        f.write(f"{date.today()},{slot}")

    print(f"💾 Backup saved (slot {slot})")


# =========================
# INIT HOOK
# =========================
with app.app_context():

    # 🔥 BACKUP (DEV SAFE)
    if should_backup():
        backup_db()

    # 🔥 CREATE TABLES (DEV ONLY)
    db.create_all()

    # 🔥 SEED USERS (ONLY IF EMPTY)
    if not User.query.first():
        print("🌱 Seeding users...")

        db.session.add_all([
            User(username="Superadmin", password_hash=generate_password_hash("OJTAccess"), role="admin"),
            User(username="Admin", password_hash=generate_password_hash("Password"), role="admin"),
            User(username="secretary", password_hash=generate_password_hash("secret123"), role="secretary"),
        ])

        db.session.commit()
        print("✅ Seed complete.")


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)