from app.extensions import db

class Holiday(db.Model):
    __tablename__ = "holidays"

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(200), nullable=False)

    type = db.Column(db.String(50))  # Regular, Special, Local
    description = db.Column(db.Text)