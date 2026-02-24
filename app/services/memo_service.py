from app.extensions import db
from app.models import Memo


class MemoService:

    @staticmethod
    def create_memo(data):
        memo = Memo(**data)
        db.session.add(memo)
        db.session.commit()
        return memo

    @staticmethod
    def get_by_number(memo_number):
        return Memo.query.filter_by(memo_number=memo_number).first()
    
    @staticmethod
    def get_all():   
        return Memo.query.order_by(Memo.id.asc()).all()
    
    @staticmethod
    def close_memo(memo):
        memo.status = "Closed"
        db.session.commit()