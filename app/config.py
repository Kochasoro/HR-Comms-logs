import os
import shutil
import sys

def get_database_path():
    appdata = os.getenv("APPDATA")
    app_folder = os.path.join(appdata, "HR-LOGGER")
    os.makedirs(app_folder, exist_ok=True)

    user_db = os.path.join(app_folder, "app.db")

    if getattr(sys, 'frozen', False):
        # Running as EXE
        base_path = sys._MEIPASS
        bundled_db = os.path.join(base_path, "instance", "app.db")
    else:
        # Running in dev
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        bundled_db = os.path.join(project_root, "instance", "app.db")

    # First run: copy DB
    if not os.path.exists(user_db):
        if os.path.exists(bundled_db):
            shutil.copyfile(bundled_db, user_db)
            print("Copied DB to APPDATA")
        else:
            print("No bundled DB found, creating new one")

    return user_db

class Config:
    SECRET_KEY = "devkey"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{get_database_path()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# import os

# class Config:
#     SECRET_KEY = "devkey"
#     SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False