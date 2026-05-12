from app.extensions import db
class MemoAutocomplete(db.Model):
    __tablename__ = "memo_autocomplete"

    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String(100), nullable=False)

    value = db.Column(db.String(255), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("type", "value"),
    )