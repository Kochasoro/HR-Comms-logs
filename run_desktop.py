import os
import sys
from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash

# Handle base directory (works for EXE and dev)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DB_PATH = os.path.join(BASE_DIR, "app.db")

app = create_app()

# Initialize DB and seed once
with app.app_context():
    db.create_all()

    if not User.query.first():
        print("Seeding default users...")

        db.session.add_all([
            User(username="Superadmin", password_hash=generate_password_hash("OJTAccess"), role="admin"),
            User(username="Admin", password_hash=generate_password_hash("Password"), role="admin"),
            User(username="secretary", password_hash=generate_password_hash("secret123"), role="secretary"),
        ])

        db.session.commit()
        print("Seed complete.")

# Run Flask
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )