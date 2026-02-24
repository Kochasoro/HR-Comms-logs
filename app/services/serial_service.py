from app.extensions import db
from app.models import LogEntry
from sqlalchemy import func


class SerialService:

    @staticmethod
    def next_serial():
        last = db.session.query(func.max(LogEntry.serial_number)).scalar()

        if not last:
            return 1

        return last + 1