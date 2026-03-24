from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.memo import Memo
from app.services.memo_service import MemoService
from app.services.log_service import LogService
from app.utils.decorators import role_required
from datetime import datetime
from app.extensions import db
from flask import jsonify, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime

secretary_bp = Blueprint("secretary", __name__, url_prefix="/secretary")



@secretary_bp.route("/")
@role_required("secretary")
def dashboard():
    memos = MemoService.get_all()
    return render_template("home.html", memos=memos)

@secretary_bp.route("/new", methods=["POST"])
def new_memo():
    try:
        print("FORM:", request.form)

        # 📅 Parse main date
        raw_date = request.form.get("date")
        parsed_date = None
        if raw_date:
            try:
                parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError:
                parsed_date = None

        # 📅 Parse released date (MISSING BEFORE ❗)
        raw_release_date = request.form.get("released_date")
        parsed_release_date = None
        if raw_release_date:
            try:
                parsed_release_date = datetime.strptime(raw_release_date, "%Y-%m-%d").date()
            except ValueError:
                parsed_release_date = None

        data = {
            "memo_number": request.form.get("memo_number"),
            "date": parsed_date,
            "subject": request.form.get("subject"),
            "source_type": request.form.get("source_type"),
            "from_office": request.form.get("from_office"),
            "forwarded_by": request.form.get("forwarded_by"),

            # ✅ Incoming
            "remarks": request.form.get("remarks"),
            "notes": request.form.get("notes"),

            # ✅ Released section (NOW COMPLETE)
            "released_to": request.form.get("released_to"),
            "released_date": parsed_release_date,
            "status": request.form.get("status")
        }

        memo = MemoService.create_memo(data)

        LogService.add_log(
            memo,
            request.form.get("remarks"),
            request.form.get("notes")
        )

        return jsonify({"success": True})

    except Exception as e:
        print("🔥 ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    
@secretary_bp.route("/edit/<int:id>", methods=["POST"])
def edit_memo(id):
    memo = Memo.query.get_or_404(id)

    try:
        memo.memo_number = request.form.get("memo_number")
        memo.subject = request.form.get("subject")
        memo.source_type = request.form.get("source_type")
        memo.from_office = request.form.get("from_office")
        memo.forwarded_by = request.form.get("forwarded_by")
        memo.remarks = request.form.get("remarks")
        memo.notes = request.form.get("notes")

        # ✅ ADD THESE
        memo.released_to = request.form.get("released_to")
        memo.status = request.form.get("status")

        raw_release_date = request.form.get("released_date")
        if raw_release_date:
            memo.released_date = datetime.strptime(raw_release_date, "%Y-%m-%d").date()

        raw_date = request.form.get("date")
        if raw_date:
            memo.date = datetime.strptime(raw_date, "%Y-%m-%d").date()

        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        print("🔥 EDIT ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# UPDATE EXISTING MEMO 
@secretary_bp.route("/update/<int:id>", methods=["POST"])
def update_memo(id):

    original = Memo.query.get_or_404(id)

    try:
        raw_date = request.form.get("date")
        parsed_date = None

        if raw_date:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()

        raw_release_date = request.form.get("released_date")
        parsed_release_date = None

        if raw_release_date:
            parsed_release_date = datetime.strptime(raw_release_date, "%Y-%m-%d").date()

        new_data = {
            "memo_number": request.form.get("memo_number") or original.memo_number,
            "date": parsed_date or original.date,
            "subject": request.form.get("subject") or original.subject,
            "source_type": request.form.get("source_type") or original.source_type,
            "from_office": request.form.get("from_office") or original.from_office,
            "forwarded_by": request.form.get("forwarded_by") or original.forwarded_by,

            # ✅ ADD THESE
            "released_to": request.form.get("released_to") or original.released_to,
            "released_date": parsed_release_date or original.released_date,
            "status": request.form.get("status") or original.status,

            "remarks": request.form.get("remarks"),
            "notes": request.form.get("notes")
        }

        MemoService.create_memo(new_data)

        return jsonify({"success": True})

    except Exception as e:
        print("🔥 UPDATE ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@secretary_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_memo(id):
    # permission check
    if current_user.role != "admin":
        return jsonify(error="Forbidden"), 403

    memo = Memo.query.get_or_404(id)
    try:
        db.session.delete(memo)
        db.session.commit()
        return jsonify(success=True)  # return JSON success
    except Exception:
        db.session.rollback()
        return jsonify(error="Database delete failed"), 500
