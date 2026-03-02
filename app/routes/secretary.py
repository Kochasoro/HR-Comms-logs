from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.memo import Memo
from app.services.memo_service import MemoService
from app.services.log_service import LogService
from datetime import datetime
from app.extensions import db
from flask import jsonify

secretary_bp = Blueprint("secretary", __name__, url_prefix="/secretary")


@secretary_bp.route("/")
def dashboard():
    # Get all memos
    memos = MemoService.get_all()
    
    # Just pass them to the template
    return render_template("secretary/dashboard.html", memos=memos)

# CREATE NEW MEMO

@secretary_bp.route("/new", methods=["GET", "POST"])
def new_memo():
    if request.method == "POST":
        data = {
            "memo_number": request.form["memo_number"],
            "subject": request.form["subject"],
            "source_type": request.form.get("source_type"),
            "from_office": request.form["from_office"],
            "forwarded_by": request.form["forwarded_by"],
            "remarks": request.form["remarks"],
            "notes": request.form["notes"]
        }

        memo = MemoService.create_memo(data)

        LogService.add_log(
            memo,
            request.form["remarks"],
            request.form["notes"]
        )

        return jsonify({
            "success": True,
            "memo_number": memo.memo_number,
            "subject": memo.subject
        })

    return render_template("secretary/new_memo.html")

@secretary_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_memo(id):

    # Fetch by PRIMARY KEY
    memo = Memo.query.get_or_404(id)

    if request.method == "POST":
        memo.memo_number = request.form["memo_number"]
        memo.subject = request.form["subject"]
        memo.source_type = request.form["source_type"]
        memo.from_office = request.form["from_office"]
        memo.forwarded_by = request.form["forwarded_by"]
        memo.remarks = request.form["remarks"]
        memo.notes = request.form["notes"]

        if request.form.get("date"):
            memo.date = datetime.strptime(
                request.form["date"], "%Y-%m-%d"
            ).date()

        db.session.commit()

        flash("Memo updated successfully")
        return redirect(url_for("secretary.dashboard"))

    return render_template("secretary/edit_memo.html", memo=memo)

# UPDATE EXISTING MEMO 
@secretary_bp.route("/update/<memo_number>", methods=["GET", "POST"])
def update_memo(memo_number):
    # Get the original memo
    memo = MemoService.get_by_number(memo_number)

    if not memo:
        flash("Original memo not found")
        return redirect(url_for("secretary.dashboard"))

    if request.method == "POST":
        # Create a new memo with the same data, plus updated remarks/notes
        new_data = {
            "memo_number": memo.memo_number,  # or generate new number automatically
            "subject": memo.subject,
            "source_type": memo.source_type,
            "from_office": memo.from_office,
            "forwarded_by": memo.forwarded_by,
            "remarks": request.form["remarks"],
            "notes": request.form["notes"]
        }

        MemoService.create_memo(new_data)

        flash("New memo created successfully")
        return redirect(url_for("secretary.dashboard"))

    # GET: Show form prefilled with original memo
    return render_template("secretary/update_memo.html", memo=memo)

@secretary_bp.route("/delete/<int:id>", methods=["POST"])
def delete_memo(id):
    memo = Memo.query.get_or_404(id)

    try:
        db.session.delete(memo)
        db.session.commit()
        flash("Memo deleted successfully")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting memo")

    return redirect(url_for("secretary.dashboard"))