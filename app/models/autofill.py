from app.extensions import db

class MemoAutocomplete(db.Model):
    __tablename__ = "memo_autocomplete"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # "from" or "forwarded"
    value = db.Column(db.String(255), nullable=False, unique=True)