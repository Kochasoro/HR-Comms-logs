from flask import Blueprint, jsonify, render_template, request
from datetime import date, datetime
from app.models.holiday import Holiday
from app.models.memo import Memo
from app.extensions import db
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

    query = Memo.query

    # TYPE FILTER
    if type_filter in ["CM", "OP"]:

        query = query.filter(Memo.source_type == type_filter)

    elif type_filter == "incoming":

        query = query.filter(
            Memo.source_type == "CM",
            or_(
                Memo.released_date.is_(None),
                Memo.released_to.is_(None),
                Memo.released_to == ""
            )
        )

    elif type_filter == "outgoing":

        query = query.filter(
            Memo.source_type == "CM",
            Memo.released_date.isnot(None),
            Memo.released_to.isnot(None),
            Memo.released_to != ""
        )

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

    # FILTERS
    selected_offices = request.args.getlist("office")
    selected_forwarded = request.args.getlist("forwarded")
    selected_released = request.args.getlist("released")

    if selected_offices:
        query = query.filter(Memo.from_office.in_(selected_offices))

    if selected_forwarded:
        query = query.filter(Memo.forwarded_by.in_(selected_forwarded))

    if selected_released:
        query = query.filter(Memo.released_to.in_(selected_released))

    # SORTING
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

    # EXECUTE QUERY LAST
    memos = query.all()

    holidays_raw = Holiday.query.all()
    holidays = []

    for h in holidays_raw:

        if h.repeat_yearly:

            next_date = h.date.replace(year=today.year)

            if next_date < today:
                next_date = h.date.replace(year=today.year + 1)

        else:

            if h.date < today:
                continue

            next_date = h.date

        h.display_date = next_date
        holidays.append(h)

    holidays.sort(key=lambda x: x.display_date)
    holidays = holidays[:3]

    from_offices = db.session.query(Memo.from_office)\
        .filter(Memo.from_office.isnot(None))\
        .distinct()\
        .order_by(Memo.from_office.asc())\
        .all()

    forwarded_people = db.session.query(Memo.forwarded_by)\
        .filter(Memo.forwarded_by.isnot(None))\
        .distinct()\
        .order_by(Memo.forwarded_by.asc())\
        .all()

    released_people = db.session.query(Memo.released_to)\
        .filter(Memo.released_to.isnot(None))\
        .distinct()\
        .order_by(Memo.released_to.asc())\
        .all()

    return render_template(
        "home.html",
        memos=memos,
        holidays=holidays,
        selected_type=type_filter,
        selected_month=month_filter,
        selected_year=year_filter,

        from_offices=from_offices,
        forwarded_people=forwarded_people,
        released_people=released_people
    )

@main.route("/thread/<thread_id>")
def get_thread_memos(thread_id):

    try:

        memos = (
            Memo.query
            .filter_by(thread_id=thread_id)
            .order_by(Memo.date.asc())
            .all()
        )

        data = []

        for memo in memos:

            data.append({

                "serial": f"{memo.serial_number:04d}"
                    if memo.serial_number
                    else "-",

                "subject": memo.subject,

                "date":
                    memo.date.strftime("%Y-%m-%d")
                    if memo.date
                    else None,

                "remarks": memo.remarks,

                "from":
                    memo.from_office
                    if memo.from_office
                    else "-",

                "forwarded":
                    memo.forwarded_by
                    if memo.forwarded_by
                    else "-",

                "notes":
                    memo.notes
                    if memo.notes
                    else "-",

                "released_to":
                    memo.released_to
                    if memo.released_to
                    else "-",

                "released_date":
                    memo.released_date.strftime("%Y-%m-%d")
                    if memo.released_date
                    else None,

                "status":
                    memo.status
                    if memo.status
                    else None
            })

        return jsonify(data)

    except Exception as e:

        import traceback

        print("THREAD FETCH ERROR:")
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500