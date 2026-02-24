from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.memo_service import MemoService
from app.services.log_service import LogService

secretary_bp = Blueprint("secretary", __name__, url_prefix="/secretary")


@secretary_bp.route("/")
def dashboard():
    memos = MemoService.get_all()   # 👈 add this
    return render_template("secretary/dashboard.html", memos=memos)

# CREATE NEW MEMO
@secretary_bp.route("/new", methods=["GET", "POST"])
def new_memo():
    if request.method == "POST":
        data = {
            "memo_number": request.form["memo_number"],
            "subject": request.form["subject"],
            "source_type": request.form["source_type"],
            "from_office": request.form["from_office"],
            "forwarded_by": request.form["forwarded_by"]
        }

        memo = MemoService.create_memo(data)

        LogService.add_log(
            memo,
            request.form["remarks"],
            request.form["notes"]
        )

        flash("Memo created successfully")
        return redirect(url_for("secretary.dashboard"))

    return render_template("secretary/new_memo.html")


# UPDATE EXISTING MEMO (add log only)
@secretary_bp.route("/update", methods=["GET", "POST"])
def update_memo():
    if request.method == "POST":
        memo_number = request.form["memo_number"]

        memo = MemoService.get_by_number(memo_number)

        if not memo:
            flash("Memo not found")
            return redirect(url_for("secretary.update_memo"))

        LogService.add_log(
            memo,
            request.form["remarks"],
            request.form["notes"]
        )

        flash("Update added")
        return redirect(url_for("secretary.dashboard"))

    return render_template("secretary/update_memo.html")