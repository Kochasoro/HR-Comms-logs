import os
from flask import Blueprint, current_app, jsonify, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.models.log_entry import LogEntry
from app.models.user import User
from app.models.settings import SystemSettings
from app.models.holiday import Holiday
from app.models.memo import Memo
from app.extensions import db
from datetime import date, datetime, timedelta
import pandas as pd
from io import BytesIO
from collections import defaultdict
from openpyxl import load_workbook
from werkzeug.utils import secure_filename
import os

from app.services.log_service import LogService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@login_required
def dashboard():
    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    sort = request.args.get("sort", "latest")

    query = LogEntry.query

    if sort == "oldest":
        query = query.order_by(LogEntry.encoded_at.asc())
    else:
        query = query.order_by(LogEntry.encoded_at.desc())

    logs = query.limit(3).all()

    today = date.today()
    start_week = today - timedelta(days=today.weekday())

    week_counts = []

    for i in range(7):
        day = start_week + timedelta(days=i)

        count = Memo.query.filter(
            Memo.date == day
        ).count()

        week_counts.append(count)

    return render_template(
        "admin/dashboard.html",
        logs=logs,
        week_counts=week_counts,
        current_sort=sort
    )

@admin_bp.route("/settings/general", methods=["GET", "POST"])
@login_required
def settings_general():

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    settings = SystemSettings.query.first()

    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()

    if request.method == "POST":

        form_type = request.form.get("form_type")

        # GENERAL SETTINGS
        if form_type == "general":

            settings.system_name = request.form.get("system_name")

            logo_file = request.files.get("logo")

            if logo_file and logo_file.filename:

                upload_folder = os.path.join(current_app.root_path, "static", "uploads")
                os.makedirs(upload_folder, exist_ok=True)

                logo_path = os.path.join(upload_folder, "system_logo.png")
                logo_file.save(logo_path)

                settings.logo = "uploads/system_logo.png"
                
            db.session.commit()
            flash("Settings updated")

        # ADD HOLIDAY
        elif form_type == "holiday":

            repeat = "repeat_yearly" in request.form  # ✅ True/False

            holiday = Holiday(
                date=datetime.strptime(request.form["date"], "%Y-%m-%d"),
                name=request.form["name"],
                type=request.form["type"],
                description=request.form["description"],
                repeat_yearly=repeat
            )

            db.session.add(holiday)
            db.session.commit()

            flash("Holiday added")

        return redirect(url_for("admin.settings_general"))

    holidays = Holiday.query.order_by(Holiday.date.asc()).all()

    return render_template(
        "admin/settings/general.html",
        settings=settings,
        holidays=holidays
    )

@admin_bp.route("/settings/holidays/delete/<int:id>", methods=["POST"])
@login_required
def delete_holiday(id):

    holiday = Holiday.query.get_or_404(id)

    db.session.delete(holiday)
    db.session.commit()

    flash("Holiday deleted")

    return redirect(url_for("admin.settings_general"))

@admin_bp.route("/users")
@login_required
def users():

    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("secretary.dashboard"))

    users = User.query.all()

    return render_template("admin/user.html", users=users)
@admin_bp.route("/import")
@login_required
def import_page():   # ✅ different name

    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("secretary.dashboard"))

    users = User.query.all()

    return render_template("admin/import.html", users=users)


@admin_bp.route("/import-memos", methods=["POST"])
@login_required
def import_memos():

    if current_user.role != "admin":
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    file = request.files.get("file")

    if not file:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    try:

        xls = pd.ExcelFile(file)

        month_map = {
            "Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
            "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12
        }

        imported = 0
        skipped = 0
        year = datetime.now().year

        for sheet_name in xls.sheet_names:

            # remove anything after |
            sheet_clean = sheet_name.split("|")[0].strip()

            if "-" not in sheet_clean:
                continue

            month_text, sheet_type = sheet_clean.split("-")

            month = month_map.get(month_text.capitalize())

            if not month:
                continue

            if "COMMUNICATION" in sheet_type.upper():
                source_type = "CM"
            elif "MEMO" in sheet_type.upper():
                source_type = "OP"
            else:
                continue

            df = pd.read_excel(
                xls,
                sheet_name=sheet_name,
                header=None,
                skiprows=5
            )

            for _, row in df.iterrows():

                def clean(val):
                    if pd.isna(val):
                        return None
                    return str(val).strip()

                def parse_date(val):
                    if pd.isna(val):
                        return None
                    if isinstance(val, datetime):
                        return val.date()
                    try:
                        return pd.to_datetime(val).date()
                    except:
                        return None

                serial_raw = clean(row[0])

                if not serial_raw:
                    skipped += 1
                    continue

                try:
                    serial = int(serial_raw)
                except:
                    skipped += 1
                    continue

                existing = Memo.query.filter_by(
                    serial_number=serial,
                    month=month,
                    year=year,
                    source_type=source_type
                ).first()

                if existing:
                    skipped += 1
                    continue

                memo = Memo(
                    serial_number=serial,
                    month=month,
                    year=year,

                    date=parse_date(row[1]),
                    from_office=clean(row[2]),
                    forwarded_by=clean(row[3]),
                    subject=clean(row[4]),

                    remarks=clean(row[5]),
                    notes=clean(row[6]),

                    released_date=parse_date(row[7]),
                    released_to=clean(row[8]),

                    source_type=source_type
                )

                db.session.add(memo)
                imported += 1

        db.session.commit()

        LogService.add_log(
            None,
            f"{current_user.username} imported memos",
            f"{imported} imported, {skipped} skipped",
            current_user.id
        )

        return jsonify({
            "success": True,
            "imported": imported,
            "skipped": skipped
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})
    

@admin_bp.route("/export-memos")
@login_required
def export_memos():

    if current_user.role != "admin":
        return jsonify({"success": False, "error": "Unauthorized"}), 403
        
    cm = request.args.get("cm") == "true"
    op = request.args.get("op") == "true"

    excel = request.args.get("excel") == "true"
    csv = request.args.get("csv") == "true"
    pdf = request.args.get("pdf") == "true"

    date_from = request.args.get("dateFrom")
    date_to = request.args.get("dateTo")

    query = Memo.query

    # ===== TYPE FILTER =====
    types = []
    if cm:
        types.append("CM")
    if op:
        types.append("OP")

    if types:
        query = query.filter(Memo.source_type.in_(types))

    # ===== DATE FILTER =====
    if date_from:
        query = query.filter(Memo.date >= date_from)

    if date_to:
        query = query.filter(Memo.date <= date_to)

    memos = query.order_by(Memo.date).all()

    # ===== CSV (unchanged) =====

    if csv:
        data = []
        for m in memos:
            data.append({
                "Serial No": f"{m.serial_number:04d}",
                "Date": m.date,
                "From": m.from_office,
                "Forwarded By": m.forwarded_by,
                "Subject": m.subject,
                "Remarks": m.remarks,
                "Notes": m.notes,
                "Released Date": m.released_date,
                "Released To": m.released_to,
                "Type": m.source_type
            })

        df = pd.DataFrame(data)

        output = BytesIO()
        output.write(df.to_csv(index=False).encode())
        output.seek(0)

        LogService.add_log(
            None,
            f"{current_user.username} exported memos as CSV",
            f"{len(memos)} memo(s) exported",
            current_user.id
        )

        return send_file(
            output,
            as_attachment=True,
            download_name="memos_export.csv",
            mimetype="text/csv"
        )
    # ===== EXCEL =====
    if excel:

        output = BytesIO()

        template_path = os.path.join(
            current_app.root_path,
            "templates",
            "memo_template.xlsx"
        )

        wb = load_workbook(template_path)
        template_ws = wb.active
        template_ws.title = "TEMPLATE"

        grouped = defaultdict(list)

        for m in memos:
            date_obj = datetime.strptime(str(m.date), "%Y-%m-%d")
            month = date_obj.strftime("%b").upper()

            type_label = "COMMUNICATION" if m.source_type == "CM" else "OP"
            key = f"{month}-{type_label}"

            grouped[key].append(m)

        for key in sorted(grouped.keys()):
            ws = wb.copy_worksheet(template_ws)
            ws.title = key

            ws["A2"] = key
            start_row = 6

            for i, m in enumerate(grouped[key]):
                row = start_row + i

                ws.cell(row=row, column=1, value=f"{m.serial_number:04d}")
                ws.cell(row=row, column=2, value=m.date)
                ws.cell(row=row, column=3, value=m.from_office)
                ws.cell(row=row, column=4, value=m.forwarded_by)
                ws.cell(row=row, column=5, value=m.subject)
                ws.cell(row=row, column=6, value=m.remarks)
                ws.cell(row=row, column=7, value=m.notes)
                ws.cell(row=row, column=8, value=m.released_date)
                ws.cell(row=row, column=9, value=m.released_to)

            ws.freeze_panes = "A3"

        wb.remove(template_ws)

        wb.save(output)
        output.seek(0)

        LogService.add_log(
            None,
            f"{current_user.username} exported memos as Excel",
            f"{len(memos)} memo(s) exported to XLSX",
            current_user.id
        )

        return send_file(
            output,
            as_attachment=True,
            download_name="memos_export.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # ===== PDF (OPTIONAL: KEEP SIMPLE OR REMOVE) =====
    if pdf:
        return {"error": "PDF export not supported with template yet"}, 400
    
@admin_bp.route("/users/create", methods=["POST"])
@login_required
def create_user():

    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("secretary.dashboard"))

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    user = User(username=username, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    LogService.add_log(
        user,
        f"{current_user.username} created a user account",
        f"Created user '{user.username}' with role '{user.role}'",
        current_user.id
    )

    flash("User created successfully")

    return redirect(url_for("admin.users"))

@admin_bp.route("/users/reset/<int:id>", methods=["POST"])
@login_required
def reset_password(id):

    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("secretary.dashboard"))

    user = User.query.get_or_404(id)

    new_password = request.form["password"]

    user.set_password(new_password)

    db.session.commit()
    LogService.add_log(
        user,
        f"{current_user.username} reset a user's password",
        f"Password reset for '{user.username}'",
        current_user.id
    )
    flash("Password reset successfully")

    return redirect(url_for("admin.users"))

@admin_bp.route("/users/delete/<int:id>", methods=["POST"])
@login_required
def delete_user(id):

    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("secretary.dashboard"))

    user = User.query.get_or_404(id)

    if user.role == "superadmin":
        flash("Superadmin cannot be deleted.")
        return redirect(url_for("admin.users"))

    if user.id == current_user.id:
        flash("You cannot delete your own account.")
        return redirect(url_for("admin.users"))
    
    deleted_username = user.username
    deleted_role = user.role

    db.session.delete(user)
    db.session.commit()
    LogService.add_log(
        None,
        f"{current_user.username} deleted a user account",
        f"Deleted user '{deleted_username}' with role '{deleted_role}'",
        current_user.id
    )
    flash("User deleted")

    return redirect(url_for("admin.users"))



@admin_bp.route("/logs")
@login_required
def logs_page():
    logs = LogEntry.query.order_by(LogEntry.encoded_at.desc()).all()
    return render_template("admin/logs.html", logs=logs)


