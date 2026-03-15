from app.extensions import db

class SystemSettings(db.Model):
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)

    system_name = db.Column(db.String(200))
    timezone = db.Column(db.String(100))
    logo = db.Column(db.String(255))  # file path