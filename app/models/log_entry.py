from app.extensions import db
from datetime import datetime

class LogEntry(db.Model):
    __tablename__ = "log_entries"

    id = db.Column(db.Integer, primary_key=True)

    serial_number = db.Column(db.Integer, unique=True, nullable=False)

    date = db.Column(db.Date)
    remarks = db.Column(db.String(255))
    notes = db.Column(db.Text)

    encoded_at = db.Column(db.DateTime, default=datetime.utcnow)

    memo_id = db.Column(db.Integer, db.ForeignKey("memos.id"))

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", name="fk_log_entries_user_id"),
        nullable=True  
    )
    user = db.relationship("User", backref="logs")