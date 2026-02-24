from app.extensions import db

class Office(db.Model):
    __tablename__ = "offices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))