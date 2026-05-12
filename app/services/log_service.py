from datetime import date, timedelta
from app.extensions import db
from app.models import LogEntry
from app.services.serial_service import SerialService

class LogService:

    @staticmethod
    def add_log(memo, remarks, notes="", user_id=None):

        cutoff_date = date.today() - timedelta(days=90)

        LogEntry.query.filter(
            LogEntry.date < cutoff_date
        ).delete()

        serial = SerialService.next_serial()

        log = LogEntry(
            serial_number=serial,
            date=date.today(),
            remarks=remarks,
            notes=notes,
            memo_id=memo.id if memo else None,
            user_id=user_id
        )

        db.session.add(log)
        db.session.commit()

        return log