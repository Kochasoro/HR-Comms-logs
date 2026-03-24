from flask import Blueprint, render_template, request
from datetime import date
from app.models.holiday import Holiday
from app.services.memo_service import MemoService

main = Blueprint("main", __name__)

@main.route("/")
def home():
    # 👇 get selected type from URL
    type_filter = request.args.get("type", "general")  # default = general

    if type_filter == "General":
        memos = MemoService.get_by_type("General")
    elif type_filter == "OP":
        memos = MemoService.get_by_type("OP")
    else:
        memos = MemoService.get_by_type("General")  # fallback

    holidays = Holiday.query.filter(
        Holiday.date >= date.today()
    ).order_by(Holiday.date.asc()).limit(3).all()

    return render_template(
        "home.html",
        memos=memos,
        holidays=holidays,
        selected_type=type_filter  # 👈 pass this for button highlight
    )
