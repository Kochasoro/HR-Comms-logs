# import os
# import shutil
# import sys



# def get_database_path():
#     appdata = os.getenv("APPDATA")
#     app_folder = os.path.join(appdata, "HR-LOGGER")

#     os.makedirs(app_folder, exist_ok=True)

#     user_db = os.path.join(app_folder, "app.db")

#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.abspath(os.path.dirname(__file__))

#     bundled_db = os.path.join(base_path, "instance", "app.db")

#     if not os.path.exists(user_db):
#         shutil.copyfile(bundled_db, user_db)

#     return user_db

# class Config:
#     SECRET_KEY = "devkey"
#     SQLALCHEMY_DATABASE_URI = f"sqlite:///{get_database_path()}"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False


import os

class Config:
    SECRET_KEY = "devkey"
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False