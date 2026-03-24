from app.extensions import db

class Memo(db.Model):
    __tablename__ = "memos"

    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(20))  # OP or General

    memo_number = db.Column(db.String(50))

    serial_number = db.Column(db.Integer, nullable=True) 
    date = db.Column(db.Date) 

    from_office = db.Column(db.String(100))
    forwarded_by = db.Column(db.String(100))
    subject = db.Column(db.String(255))
    remarks = db.Column(db.String(100))
    notes = db.Column(db.String(100))
    released_date = db.Column(db.Date)
    released_to = db.Column(db.String(100))

    month = db.Column(db.Integer)          
    year = db.Column(db.Integer)     

    status = db.Column(db.String(20), default="Open")

    logs = db.relationship("LogEntry", backref="memo", lazy=True)