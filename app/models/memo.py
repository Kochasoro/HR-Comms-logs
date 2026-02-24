from app.extensions import db

class Memo(db.Model):
    __tablename__ = "memos"

    id = db.Column(db.Integer, primary_key=True)

    memo_number = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(255))

    source_type = db.Column(db.String(20))  # OP or General
    from_office = db.Column(db.String(100))
    forwarded_by = db.Column(db.String(100))
    remarks = db.Column(db.String(100))
    notes = db.Column(db.String(100))

    date_received = db.Column(db.Date)

    status = db.Column(db.String(20), default="Open")

    logs = db.relationship("LogEntry", backref="memo", lazy=True)