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
    """Seed the database with sample memos (March–April 2026)."""

    if force:
        Memo.query.delete()
        db.session.commit()
        click.echo("⚠️ Existing memos deleted.")

    elif Memo.query.first():
        click.echo("Memos already exist. Use --force to reseed.")
        return

    # -------------------------
    # DATA POOLS
    # -------------------------
    subjects = [
        "Hiring of Administrative Aide",
        "Budget Request for Office Supplies",
        "Submission of Project Proposal",
        "Request for Vehicle Use",
        "Staff Meeting Schedule",
        "IT Equipment Procurement",
        "Training Seminar Approval",
        "Quarterly Performance Review",
        "Legal Case Filing Review",
        "Contract Agreement Processing",
        "Client Consultation Schedule",
        "Document Authentication Request",
        "Case Status Follow-up",
        "Office Renovation Proposal",
        "Procurement of Medical Supplies"
    ]

    remarks_list = [
        "For review", "For signature of attorney", "Please evaluate",
        "For approval", "For appropriate action", "Please coordinate",
        "For record purposes", "Urgent review required",
        "Kindly prioritize", "Awaiting compliance"
    ]

    notes_list = [
        "", "Urgent matter", "Follow up next week",
        "Coordinate with accounting", "Pending documents",
        "Requires legal review", "Client waiting for update",
        "Attach supporting files", ""
    ]

    offices = [
        "HR Department", "Finance Office", "Planning Division",
        "Administrative Office", "Records Section",
        "Legal Department", "Procurement Unit"
    ]

    released_people = [
        "Juan Dela Cruz", "Maria Santos", "Pedro Reyes",
        "Ana Lopez", "Carlos Mendoza", ""
    ]

    forwarded_roles = [
        "Clerk", "Secretary", "Records Officer", "Admin Staff"
    ]

    # -------------------------
    # DATE RANGE
    # -------------------------
    start_date = date(2026, 3, 1)
    end_date = date(2026, 4, 30)
    delta_days = (end_date - start_date).days

    temp_memos = []

    # -------------------------
    # GENERATE RAW DATA FIRST
    # -------------------------
    for i in range(50):
        source_type = random.choice(["OP", "communication"])

        memo_number = None
        from_office = random.choice(offices)
        forwarded_by = random.choice(forwarded_roles)

        if source_type == "OP":
            memo_number = f"OP-2026-{random.randint(100, 999)}"
            from_office = "OP"
            forwarded_by = "Record"

        memo_date = start_date + timedelta(days=random.randint(0, delta_days))

        memo_month = memo_date.month
        memo_year = memo_date.year

        released_to = random.choice(released_people)
        released_date = None

        if released_to != "":
            release_offset = random.randint(1, 5)
            temp_date = memo_date + timedelta(days=release_offset)
            released_date = temp_date if temp_date <= end_date else end_date

        temp_memos.append({
            "source_type": source_type,
            "memo_number": memo_number,
            "date": memo_date,
            "month": memo_month,
            "year": memo_year,
            "from_office": from_office,
            "forwarded_by": forwarded_by,
            "subject": random.choice(subjects),
            "remarks": random.choice(remarks_list),
            "notes": random.choice(notes_list),
            "released_to": released_to if released_to else None,
            "released_date": released_date
        })

    # -------------------------
    # SORT BY DATE (IMPORTANT)
    # -------------------------
    temp_memos.sort(key=lambda x: x["date"])

    # -------------------------
    # SERIAL NUMBER PER MONTH
    # -------------------------
    counters = {}  # {(year, month): count}

    for data in temp_memos:
        key = (data["year"], data["month"])

        if key not in counters:
            counters[key] = 1
        else:
            counters[key] += 1

        serial_number = counters[key]

        memo = Memo(
            source_type=data["source_type"],
            memo_number=data["memo_number"],
            date=data["date"],
            month=data["month"],
            year=data["year"],
            serial_number=serial_number,  # 🔥 HERE
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
    click.echo("✅ 50 memos seeded with monthly serial numbers!")