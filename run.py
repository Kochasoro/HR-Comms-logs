import os
import shutil
import threading
import time

from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models.user import User

from werkzeug.security import generate_password_hash


app = create_app()


# =========================
# DB PATH
# =========================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DB_PATH = os.path.join(BASE_DIR, "instance", "app.db")

BACKUP_DIR = os.path.join(BASE_DIR, "backups")

os.makedirs(BACKUP_DIR, exist_ok=True)

BACKUP_A = os.path.join(BACKUP_DIR, "app_backup_A.db")
BACKUP_B = os.path.join(BACKUP_DIR, "app_backup_B.db")

STATE_FILE = os.path.join(BACKUP_DIR, "backup_state.txt")


# =========================
# BACKUP CHECK
# =========================
def should_backup():

    if not os.path.exists(STATE_FILE):
        return True

    try:

        with open(STATE_FILE, "r") as f:
            last_time = f.read().strip().split(",")[0]

        last = datetime.strptime(
            last_time,
            "%Y-%m-%d %H:%M:%S"
        )
        # =========================
        # BACKUP INTERVAL
        # =========================

        # 🔥 TEST MODE (EVERY 1 MINUTE)
        # BACKUP_INTERVAL = timedelta(minutes=1)

        # 🔒 PRODUCTION MODE (EVERY 3 DAYS)
        BACKUP_INTERVAL = timedelta(days=3)

        return datetime.now() - last >= BACKUP_INTERVAL
    
    except Exception:
        return True


# =========================
# ROTATING SLOT
# =========================
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


# =========================
# SAVE BACKUP
# =========================
def backup_db():

    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    slot = get_backup_slot()

    target = BACKUP_A if slot == "A" else BACKUP_B

    try:

        shutil.copy2(DB_PATH, target)

        with open(STATE_FILE, "w") as f:

            f.write(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{slot}"
            )

        print(
            f"💾 Backup saved "
            f"({slot}) "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )

    except Exception as e:

        print("Backup failed:", e)


# =========================
# BACKGROUND LOOP
# =========================
def backup_loop():

    while True:

        try:

            if should_backup():
                backup_db()

        except Exception as e:

            print("Backup loop error:", e)

        time.sleep(60)


# =========================
# INIT APP
# =========================
with app.app_context():

    # CREATE TABLES
    db.create_all()

    # SEED USERS
    if not User.query.first():

        print("🌱 Seeding users...")

        db.session.add_all([

            User(
                username="Superadmin",
                password_hash=generate_password_hash("OJTAccess"),
                role="admin"
            ),

            User(
                username="Admin",
                password_hash=generate_password_hash("Password"),
                role="admin"
            ),

            User(
                username="secretary",
                password_hash=generate_password_hash("secret123"),
                role="secretary"
            ),

        ])

        db.session.commit()

        print("✅ Seed complete.")


# =========================
# RUN APP
# =========================
if __name__ == "__main__":

    # START BACKUP THREAD
    threading.Thread(
        target=backup_loop,
        daemon=True
    ).start()

    app.run(debug=True)