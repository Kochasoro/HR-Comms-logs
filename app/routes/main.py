from flask import Blueprint, render_template, request
from datetime import date, datetime
from app.models.holiday import Holiday
from app.models.memo import Memo
from app.services.memo_service import MemoService
from sqlalchemy import or_

main = Blueprint("main", __name__)

from datetime import date

@main.route("/")
def home():
    search = request.args.get("search", "")
    type_filter = request.args.get("type", "CM")
    sort = request.args.get("sort", "")

    today = date.today()
    month_filter = request.args.get("month") or today.month
    year_filter = request.args.get("year") or today.year

    query = Memo.query.filter_by(source_type=type_filter)

    if search:
        query = query.filter(
            or_(
                Memo.subject.ilike(f"%{search}%"),
                Memo.memo_number.ilike(f"%{search}%"),
                Memo.from_office.ilike(f"%{search}%"),
                Memo.forwarded_by.ilike(f"%{search}%")
            )
        )

    query = query.filter(Memo.month == int(month_filter))
    query = query.filter(Memo.year == int(year_filter))

    sort = request.args.get("sort", "")

    if sort == "serial_desc":
        query = query.order_by(Memo.serial_number.desc())

    elif sort == "serial_asc":
        query = query.order_by(Memo.serial_number.asc())

    elif sort == "date_desc":
        query = query.order_by(Memo.date.desc())

    elif sort == "date_asc":
        query = query.order_by(Memo.date.asc())

    elif sort == "alpha_subject":
        query = query.order_by(Memo.subject.asc())

    elif sort == "alpha_forwarded":
        query = query.order_by(Memo.forwarded_by.asc())

    else:
        query = query.order_by(Memo.serial_number.desc())

    memos = query.all()

    holidays = Holiday.query.filter(
        Holiday.date >= today
    ).order_by(Holiday.date.asc()).limit(3).all()

    return render_template(
        "home.html",
        memos=memos,
        holidays=holidays,
        selected_type=type_filter,
        selected_month=month_filter,
        selected_year=year_filter
    )