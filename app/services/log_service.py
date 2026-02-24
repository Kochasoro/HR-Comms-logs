from datetime import date
from app.extensions import db
from app.models import LogEntry
from app.services.serial_service import SerialService


class LogService:

    @staticmethod
    def add_log(memo, remarks, notes=""):
        serial = SerialService.next_serial()

        log = LogEntry(
            serial_number=serial,
            date=date.today(),
            remarks=remarks,
            notes=notes,
            memo_id=memo.id
        )

        db.session.add(log)
        db.session.commit()

        return log