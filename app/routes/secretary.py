import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.autofill import MemoAutocomplete
from app.models.memo import Memo
from app.services.memo_service import MemoService
from app.services.log_service import LogService
from app.utils.decorators import role_required
from datetime import datetime
from app.extensions import db
from flask import jsonify, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from flask_login import current_user

secretary_bp = Blueprint("secretary", __name__, url_prefix="/secretary")





@secretary_bp.route("/new", methods=["POST"])
@login_required
def new_memo():
    try:
        print("FORM:", request.form)
        thread_id = str(uuid.uuid4())
        
        raw_date = request.form.get("date")
        parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date() if raw_date else None

        raw_release_date = request.form.get("released_date")
        parsed_release_date = datetime.strptime(raw_release_date, "%Y-%m-%d").date() if raw_release_date else None

        source_type = request.form.get("source_type")

        if not source_type:
            return jsonify({"success": False, "error": "Source type is required"}), 400

        today = datetime.now()
        month = today.month
        year = today.year

        last_memo = Memo.query.filter_by(
            month=month,
            year=year,
            source_type=source_type
        ).order_by(Memo.serial_number.desc()).first()

        next_serial = (last_memo.serial_number or 0) + 1 if last_memo else 1

        memo_number = request.form.get("memo_number")

        if source_type != "OP":
            memo_number = None
        else:
            existing = Memo.query.filter_by(
                memo_number=memo_number,
                source_type="OP"
            ).first()

            if existing:
                return jsonify({
                    "success": False,
                    "error": "Memorandum number already exists!"
                }), 400

        data = {
            "memo_number": memo_number,
            "serial_number": next_serial,
            "month": month,
            "year": year,
            "thread_id": thread_id,

            "date": parsed_date,
            "subject": request.form.get("subject"),
            "source_type": source_type,
            "from_office": request.form.get("from_office"),
            "forwarded_by": request.form.get("forwarded_by"),

            "remarks": request.form.get("remarks"),
            "notes": request.form.get("notes"),

            "released_to": request.form.get("released_to"),
            "released_date": parsed_release_date,
            "status": request.form.get("status")
        }

        memo = MemoService.create_memo(data)

        LogService.add_log(
            memo,
            f"{current_user.username} created memo #{memo.serial_number:04d} {memo.source_type}",
            f"Status: {memo.status}",
            current_user.id
        )
        return jsonify({
            "success": True,
            "memo": {
                "id": memo.id,
                "serial_number": f"{memo.serial_number:04d}",
                "source_type": memo.source_type,
                "memo_number": memo.memo_number,

                "subject": memo.subject,
                "from": memo.from_office,
                "forwarded_by": memo.forwarded_by,

                "remarks": memo.remarks,
                "notes": memo.notes,

                "released_to": memo.released_to,
                "status": memo.status,

                "date": memo.date.strftime("%Y-%m-%d") if memo.date else "",
                "released_date": memo.released_date.strftime("%Y-%m-%d") if memo.released_date else ""
            }
        })
    except Exception as e:
        print("🔥 ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    
@secretary_bp.route("/edit/<int:id>", methods=["POST"])
@login_required
def edit_memo(id):
    memo = Memo.query.get_or_404(id)

    thread_memos = Memo.query.filter_by(thread_id=memo.thread_id).all()    
    original_data = {
        "memo_number": memo.memo_number,
        "subject": memo.subject,
        "from_office": memo.from_office,
        "forwarded_by": memo.forwarded_by,
        "remarks": memo.remarks,
        "notes": memo.notes,
        "released_to": memo.released_to,
        "status": memo.status,
        "released_date": memo.released_date,
        "date": memo.date
    }
    try:
        memo.memo_number = request.form.get("memo_number")
        memo.subject = request.form.get("subject")
        memo.from_office = request.form.get("from_office")
        memo.forwarded_by = request.form.get("forwarded_by")
        memo.remarks = request.form.get("remarks")
        memo.notes = request.form.get("notes")
        memo.released_to = request.form.get("released_to")
        memo.status = request.form.get("status")

        raw_release_date = request.form.get("released_date")

        if raw_release_date and raw_release_date not in ["None", ""]:
            memo.released_date = datetime.strptime(raw_release_date, "%Y-%m-%d").date()
        else:
            memo.released_date = None

        raw_date = request.form.get("date")

        if raw_date and raw_date not in ["None", ""]:
            memo.date = datetime.strptime(raw_date, "%Y-%m-%d").date()

        db.session.commit()
        
        def normalize(val):
            if val in ["", None]:
                return None
            if hasattr(val, "strftime"):  # date/datetime
                return val.strftime("%b %d, %Y")
            return str(val)

        changes = []
        fields = [
            "memo_number", "subject", "from_office", "forwarded_by",
            "remarks", "notes", "released_to", "status",
            "released_date", "date"
        ]
        for m in thread_memos:
            m.subject = request.form.get("subject")
            m.from_office = request.form.get("from_office")
            m.forwarded_by = request.form.get("forwarded_by")
            
        for field in fields:
            old = normalize(original_data[field])
            new = normalize(getattr(memo, field))

            if old != new:
                changes.append(
                    f"{field.replace('_', ' ').title()}: '{old}' → '{new}'"
                )

        remarks_text = f"{current_user.username} edited memo #{memo.serial_number:04d}"

        if changes:
            LogService.add_log(
                memo,
                remarks_text,
                ", ".join(changes),
                current_user.id
            )
        return jsonify({"success": True})

    except Exception as e:
        print("🔥 EDIT ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@secretary_bp.route("/update/<int:id>", methods=["POST"])
@login_required
def update_memo(id):

    original = Memo.query.get_or_404(id)

    try:

        raw_date = request.form.get("date")

        parsed_date = None
        if raw_date and raw_date != "None" and raw_date.strip():
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        else:
            parsed_date = original.date

        if not parsed_date:
            return jsonify({
                "success": False,
                "error": "Date is required"
            }), 400

        month = parsed_date.month
        year = parsed_date.year

        raw_release_date = request.form.get("released_date")

        parsed_release_date = None
        if raw_release_date and raw_release_date != "None" and raw_release_date.strip():
            parsed_release_date = datetime.strptime(raw_release_date, "%Y-%m-%d").date()
        else:
            parsed_release_date = original.released_date


        source_type = request.form.get("source_type") or original.source_type

        last_memo = Memo.query.filter_by(
            month=month,
            year=year,
            source_type=source_type
        ).order_by(Memo.serial_number.desc()).first()

        next_serial = (last_memo.serial_number or 0) + 1 if last_memo else 1

        memo_number = original.memo_number if source_type == "OP" else None

        new_data = {
            "memo_number": memo_number,
            "serial_number": next_serial,
            "month": month,
            "year": year,
            "thread_id": original.thread_id,

            "date": parsed_date,
            "subject": request.form.get("subject") or original.subject,
            "source_type": source_type,
            "from_office": request.form.get("from_office") or original.from_office,
            "forwarded_by": request.form.get("forwarded_by") or original.forwarded_by,

            "released_to": request.form.get("released_to") or original.released_to,
            "released_date": parsed_release_date,
            "status": request.form.get("status") or original.status,

            "remarks": request.form.get("remarks"),
            "notes": request.form.get("notes")
        }

        new_memo = MemoService.create_memo(new_data)

        LogService.add_log(
            new_memo,
            f"{current_user.username} created new version #{new_memo.serial_number:04d}",
            f"Based on previous memo #{original.serial_number:04d}",
            current_user.id
        )
        return jsonify({
            "success": True,
            "redirect": url_for("main.home")
        })
    except Exception as e:
        import traceback
        print("🔥 UPDATE ERROR:")
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@secretary_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_memo(id):
    if current_user.role != "admin":
        return jsonify(error="Forbidden"), 403

    memo = Memo.query.get_or_404(id)
    try:
        LogService.add_log(
            memo,
            f"{current_user.username} deleted memo #{memo.serial_number:04d}",
            f"Subject: {memo.subject}",
            current_user.id
        )
        db.session.delete(memo)
        db.session.commit()
        return jsonify(success=True)  # return JSON success
    except Exception:
        db.session.rollback()
        return jsonify(error="Database delete failed"), 500




# autocomplete

@secretary_bp.route("/autocomplete/<type>", methods=["GET"])
def get_autocomplete(type):
    items = MemoAutocomplete.query.filter_by(type=type).all()
    return jsonify([i.value for i in items])

@secretary_bp.route(
    "/autocomplete",
    methods=["POST"],
    endpoint="save_autocomplete"
)
def save_autocomplete():
    data = request.json
    value = data.get("value")
    type_ = data.get("type")

    if not value:
        return jsonify({"error": "Empty"}), 400

    exists = MemoAutocomplete.query.filter_by(
        value=value,
        type=type_
    ).first()
    if not exists:
        new_item = MemoAutocomplete(type=type_, value=value)
        db.session.add(new_item)
        db.session.commit()

    return jsonify({"success": True})

@secretary_bp.route(
    "/autocomplete",
    methods=["DELETE"],
    endpoint="delete_autocomplete"
)
def delete_autocomplete():
    data = request.json
    value = data.get("value")

    item = MemoAutocomplete.query.filter_by(value=value).first()
    if item:
        db.session.delete(item)
        db.session.commit()

    return jsonify({"success": True})





    


@secretary_bp.route("/search-memos")
@login_required
def search_memos():

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    memos = (
        Memo.query
        .filter(
            db.or_(
                Memo.subject.ilike(f"%{query}%"),
                Memo.from_office.ilike(f"%{query}%"),
                Memo.forwarded_by.ilike(f"%{query}%"),
                Memo.memo_number.ilike(f"%{query}%")
            )
        )
        .order_by(Memo.date.desc())
        .limit(20)
        .all()
    )

    data = []

    for memo in memos:

        data.append({

            "id": memo.id,

            "subject": memo.subject,

            "number":
                memo.memo_number
                if memo.memo_number
                else f"{memo.serial_number:04d}",

            "date":
                memo.date.strftime("%Y-%m-%d")
                if memo.date else "",

            "from":
                memo.from_office,

            "forwarded":
                memo.forwarded_by,

            "source_type":
                memo.source_type,

            "remarks":
                memo.remarks,

            "notes":
                memo.notes,

            "released_to":
                memo.released_to,

            "released_date":
                memo.released_date.strftime("%Y-%m-%d")
                if memo.released_date else ""
        })

    return jsonify(data)
