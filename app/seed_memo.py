import uuid

import click
from flask.cli import with_appcontext
from datetime import date, timedelta
import random

from app.extensions import db
from app.models.memo import Memo

@click.command("seed-memos")
@click.option("--force", is_flag=True, help="Force reseed (delete existing memos)")
@with_appcontext
def seed_memos(force):
    """Seed the database with sample memos (Feb–April 2026 with updates)."""

    if force:
        Memo.query.delete()
        db.session.commit()
        click.echo("⚠️ Existing memos deleted.")

    elif Memo.query.first():
        click.echo("Memos already exist. Use --force to reseed.")
        return

    import random
    from datetime import date, timedelta

    # -------------------------
    # DATA POOLS
    # -------------------------
    subjects = [
        "Employee Attendance Concern",
        "Budget Request for Office Supplies",
        "IT Equipment Procurement",
        "Legal Case Filing Review",
        "Contract Agreement Processing"
    ]

    offices = ["HR Office", "Finance Office", "Records Section"]
    people = ["Maria Santos", "Juan Dela Cruz", "Pedro Reyes"]

    # -------------------------
    # DATE RANGE (FEB → APRIL)
    # -------------------------
    start_date = date(2026, 2, 1)
    end_date = date(2026, 4, 30)
    delta_days = (end_date - start_date).days

    temp_memos = []

    # -------------------------
    # GENERATE DATA
    # -------------------------
    for i in range(30):

        source_type = random.choice(["CM", "OP"])
        thread_id = str(uuid.uuid4())
        memo_date = start_date + timedelta(days=random.randint(0, delta_days))
        subject = random.choice(subjects)

        if source_type == "OP":
            memo_number = f"OP-2026-{random.randint(100, 999)}"
            from_office = "OP"
            forwarded_by = "Record"
        else:
            memo_number = None
            from_office = random.choice(offices)
            forwarded_by = random.choice(people)

        # -------------------------
        # FIRST ENTRY
        # -------------------------
        base_entry = {
            "thread_id": thread_id, 
            "source_type": source_type,
            "memo_number": memo_number,
            "date": memo_date,
            "month": memo_date.month,
            "year": memo_date.year,
            "from_office": from_office,
            "forwarded_by": forwarded_by,
            "subject": subject,
            "remarks": "Received",
            "notes": "Initial entry",
            "released_to": None,
            "released_date": None
        }

        temp_memos.append(base_entry)

        # -------------------------
        # UPDATE ENTRY
        # -------------------------
        if random.random() < 0.6:  # 60% chance

            update_date = memo_date + timedelta(days=random.randint(1, 3))
            if update_date > end_date:
                update_date = end_date

            updated_entry = {
                "thread_id": thread_id,
                "source_type": source_type,
                "memo_number": memo_number,  # 🔥 SAME memo number
                "date": update_date,
                "month": update_date.month,
                "year": update_date.year,
                "from_office": from_office,
                "forwarded_by": forwarded_by,
                "subject": subject,
                "remarks": "Approved / Passed",
                "notes": "Processed by attorney",
                "released_to": "Records",
                "released_date": update_date
            }

            temp_memos.append(updated_entry)

    # -------------------------
    # SORT BY DATE
    # -------------------------
    temp_memos.sort(key=lambda x: x["date"])

    # -------------------------
    # SERIAL NUMBER PER MONTH
    # -------------------------
    counters = {}  # {(type, year, month): count}

    for data in temp_memos:
        key = (data["source_type"], data["year"], data["month"])

        counters[key] = counters.get(key, 0) + 1

        memo = Memo(
            thread_id=data["thread_id"],  
            source_type=data["source_type"],
            memo_number=data["memo_number"],
            date=data["date"],
            month=data["month"],
            year=data["year"],
            serial_number=counters[key], 
            from_office=data["from_office"],
            forwarded_by=data["forwarded_by"],
            subject=data["subject"],
            remarks=data["remarks"],
            notes=data["notes"],
            released_to=data["released_to"],
            released_date=data["released_date"]
        )

        db.session.add(memo)
        
    db.session.commit()
    click.echo("✅ Seeded memos (Feb–April) with realistic updates!")