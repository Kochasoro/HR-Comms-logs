from flask import Blueprint, render_template, request
from datetime import date, datetime
from app.models.holiday import Holiday
from app.models.memo import Memo
from app.services.memo_service import MemoService
from sqlalchemy import or_

main = Blueprint("main", __name__)

@main.route("/")
def home():
    search = request.args.get("search", "")
    date_filter = request.args.get("date", "")
    type_filter = request.args.get("type", "communication")

    query = Memo.query.filter_by(source_type=type_filter)

    # 🔍 search filter (EXPANDED)
    if search:
        query = query.filter(
            or_(
                Memo.subject.ilike(f"%{search}%"),
                Memo.memo_number.ilike(f"%{search}%"),
                Memo.from_office.ilike(f"%{search}%"),
                Memo.forwarded_by.ilike(f"%{search}%")
            )
        )

    # 📅 date filter
    month_filter = request.args.get("month")
    year_filter = request.args.get("year")

    if month_filter:
        query = query.filter(Memo.month == int(month_filter))

    if year_filter:
        query = query.filter(Memo.year == int(year_filter))

    memos = query.order_by(Memo.serial_number.desc()).all()

    holidays = Holiday.query.filter(
        Holiday.date >= date.today()
    ).order_by(Holiday.date.asc()).limit(3).all()

    return render_template(
        "home.html",
        memos=memos,
        holidays=holidays,
        selected_type=type_filter
    )