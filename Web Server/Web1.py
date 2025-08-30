from flask import Flask, request, redirect, url_for, render_template_string, flash, send_file, jsonify
import csv
import datetime
import os
import json
from io import StringIO

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")  # for flashes

FILENAME = "attendance.csv"
STUDENTS_FILE = "students.json"
ADMIN_PIN = os.environ.get("ADMIN_PIN", "1234")  # demo PIN; set env var in production


# ---------- Storage Helpers ----------
def init_files():
    if not os.path.exists(FILENAME):
        with open(FILENAME, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Student ID", "Name", "Status"])
    if not os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "101": "Alice",
                "102": "Bob",
                "103": "Charlie",
                "104": "Diana",
                "105": "Ethan"
            }, f, indent=2)

def load_students():
    with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_students(students):
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2, ensure_ascii=False)

def already_checked_in(student_id, date_iso):
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                if row["Date"] == date_iso and row["Student ID"] == student_id and row["Status"] == "Present":
                    return True
    except FileNotFoundError:
        return False
    return False

def mark_attendance(student_id, name, status="Present"):
    today = datetime.date.today().isoformat()
    # Prevent duplicates for Present
    if status == "Present" and already_checked_in(student_id, today):
        return False, f"{name} is already marked Present today."
    with open(FILENAME, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([today, student_id, name, status])
    return True, f"Welcome, {name}! You're marked {status}."


# ---------- Templates ----------
BASE_CSS = """
:root {
  --gap: 14px;
  --radius: 16px;
  --pad: 16px;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: black;
  color: white;
}

.header {
  position: sticky;
  top: 0;
  background: #5D3FD3;
  border-bottom: 1px solid #444;
  padding: 18px var(--pad);
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 2;
}

.title {
  font-size: 22px;
  font-weight: 800;
  color: white;
  text-align: center;
  flex: 1;
}

.header img {
  height: 50px;
}

.container {
  max-width: 960px;
  margin: 0 auto;
  padding: 18px;
}

.search {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #555;
  border-radius: 10px;
  font-size: 16px;
  background: #222;
  color: white;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--gap);
  margin-top: 18px;
}

.card-btn {
  background: #444;
  border: 2px solid #666;
  border-radius: var(--radius);
  padding: 16px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  width: 100%;
  color: white;
  transition: transform .06s ease;
}

.card-btn:hover { transform: translateY(-2px); }
.card-btn:active { transform: translateY(0px) scale(.99); }

.subtle { color: #aaa; font-size: 13px; }

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  background: #4444ff;
  border: 1px solid #6666ff;
  color: white;
  font-weight: 600;
  font-size: 12px;
}

.row { display: flex; gap: 10px; align-items: center; }

.actions { margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap; }

.btn {
  background: #666;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 700;
}

.btn.secondary {
  background: #333;
  color: white;
  border: 1px solid #555;
}

.flash {
  background: #222;
  border: 1px solid #444;
  border-left: 6px solid #22c55e;
  padding: 12px 14px;
  border-radius: 10px;
  margin: 10px 0;
  color: white;
}

.flash.err { border-left-color: #ef4444; }

.table {
  width: 100%;
  border-collapse: collapse;
  background: #111;
  border: 1px solid #333;
  border-radius: 12px;
  overflow: hidden;
}

.table th, .table td {
  padding: 12px;
  border-bottom: 1px solid #333;
  text-align: left;
  color: white;
}

.table th {
  background: #222;
  font-weight: 800;
}

.footer {
  text-align: center;
  color: #aaa;
  padding: 22px;
}

.small { font-size: 12px; color: #888; }

.kiosk-hint { color: #aaa; font-size: 12px; }
"""

INDEX_TMPL = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Attendance Kiosk</title>
<style>{{ css }}</style>
</head>
<body>
<div class="header">
  <img src="{{ url_for('static', filename='logo.png') }}" alt="Logo" class="logo" />
  <div class="title">📌 Tap Your Name to Check In</div>
  <a class="btn secondary admin-btn" href="{{ url_for('admin') }}">Admin</a>
</div>
  </div>
  <div class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for cat, msg in messages %}
          <div class="flash {{ 'err' if cat=='error' else '' }}">{{ msg }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <input id="search" class="search" placeholder="Search your name..." oninput="filter()" autofocus />

    <div id="grid" class="grid">
      {% for sid, name in students.items() %}
        <form class="card" method="POST" action="{{ url_for('checkin', student_id=sid) }}">
          <button class="card-btn" type="submit">🙋 {{ name }}</button>
          <div class="row" style="margin-top:6px;">
            <span class="subtle">ID: {{ sid }}</span>
            {% if checked_in_today.get(sid) %}
              <span class="badge">Present Today</span>
            {% endif %}
          </div>
        </form>
      {% endfor %}
    </div>

    <div class="footer">
      <div class="small kiosk-hint">Tip: Press F11 (Windows) or Ctrl+Cmd+F (Mac) for fullscreen kiosk.</div>
    </div>
  </div>

<script>
function norm(s){ return s.toLowerCase().trim(); }
function filter(){
  const q = norm(document.getElementById('search').value);
  const cards = document.querySelectorAll('.card');
  cards.forEach(c=>{
    const text = norm(c.innerText);
    c.style.display = text.includes(q) ? '' : 'none';
  });
}
</script>
</body>
</html>
"""

ADMIN_TMPL = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Admin • Attendance</title>
<style>{{ css }}</style>
</head>

<body>
  <div class="header">
  <img src="{{ url_for('static', filename='logo.png') }}" alt="Logo" class="logo" />
  <div class="title">⚙️ Admin</div>
  <a class="btn secondary admin-btn" href="{{ url_for('index') }}">Home</a>
</div>
</div>
  <div class="container">

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for cat, msg in messages %}
          <div class="flash {{ 'err' if cat=='error' else '' }}">{{ msg }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% if not authed %}
      <form method="POST" action="{{ url_for('admin') }}">
        <div class="row">
          <input class="search" style="max-width:280px" type="password" name="pin" placeholder="Enter Admin PIN" />
          <button class="btn" type="submit">Unlock</button>
        </div>
        <div class="small" style="margin-top:8px;">(Set <code>ADMIN_PIN</code> env var in production)</div>
      </form>
    {% else %}
      <h3>Add Student</h3>
      <form method="POST" action="{{ url_for('add_student') }}" class="row" style="gap:8px; flex-wrap:wrap;">
        <input class="search" style="max-width:200px" name="sid" placeholder="Student ID" />
        <input class="search" style="max-width:260px" name="name" placeholder="Student Name" />
        <button class="btn" type="submit">Add</button>
      </form>

      <div class="actions">
        <a class="btn secondary" href="{{ url_for('download_csv') }}">Download CSV</a>
        <form method="POST" action="{{ url_for('mark_all_absent') }}" onsubmit="return confirm('Mark all not-present students as Absent for today?');">
          <button class="btn" type="submit">Mark Missing as Absent (Today)</button>
        </form>
      </div>

      <h3 style="margin-top:20px;">Students</h3>
      <table class="table">
        <thead><tr><th>ID</th><th>Name</th><th>Actions</th></tr></thead>
        <tbody>
        {% for sid, name in students.items() %}
          <tr>
            <td>{{ sid }}</td>
            <td>{{ name }}</td>
            <td>
              <form method="POST" action="{{ url_for('delete_student', student_id=sid) }}" onsubmit="return confirm('Delete {{ name }}?');" style="display:inline;">
                <button class="btn secondary" type="submit">Delete</button>
              </form>
            </td>
          </tr>
        {% endfor %}
        </tbody>
      </table>

      <h3 style="margin-top:20px;">Today’s Attendance ({{ today }})</h3>
      <table class="table">
        <thead><tr><th>Time</th><th>ID</th><th>Name</th><th>Status</th></tr></thead>
        <tbody>
        {% for row in todays %}
          <tr>
            <td>{{ row.time }}</td>
            <td>{{ row.sid }}</td>
            <td>{{ row.name }}</td>
            <td>{{ row.status }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    {% endif %}
  </div>
</body>
</html>
"""


# ---------- Routes ----------
@app.route("/")
def index():
    students = load_students()
    today = datetime.date.today().isoformat()
    checked = {sid: already_checked_in(sid, today) for sid in students.keys()}
    return render_template_string(INDEX_TMPL, css=BASE_CSS, students=students, checked_in_today=checked)

@app.post("/checkin/<student_id>")
def checkin(student_id):
    students = load_students()
    if student_id not in students:
        flash("Student not found.", "error")
        return redirect(url_for("index"))
    ok, msg = mark_attendance(student_id, students[student_id], "Present")
    flash(msg, "ok" if ok else "error")
    return redirect(url_for("index"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    authed = False
    if request.method == "POST":
        pin = request.form.get("pin", "")
        if pin == ADMIN_PIN:
            authed = True
            # remember via session cookie
            request.environ["authed"] = True
            resp = redirect(url_for("admin"))
            resp.set_cookie("authed", "1", samesite="Lax")
            return resp
        else:
            flash("Wrong PIN.", "error")

    # cookie-based simple auth (demo)
    if request.cookies.get("authed") == "1":
        authed = True

    students = load_students()
    today_iso = datetime.date.today().isoformat()
    todays = []
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                if row["Date"] == today_iso:
                    # we don’t have times stored; show “—”
                    todays.append({
                        "time": "—",
                        "sid": row["Student ID"],
                        "name": row["Name"],
                        "status": row["Status"]
                    })
    except FileNotFoundError:
        pass

    return render_template_string(
        ADMIN_TMPL,
        css=BASE_CSS,
        authed=authed,
        students=students,
        today=today_iso,
        todays=todays
    )

@app.post("/admin/add-student")
def add_student():
    if request.cookies.get("authed") != "1":
        flash("Unauthorized.", "error"); return redirect(url_for("admin"))
    sid = (request.form.get("sid") or "").strip()
    name = (request.form.get("name") or "").strip()
    if not sid or not name:
        flash("Please provide both ID and Name.", "error"); return redirect(url_for("admin"))
    students = load_students()
    if sid in students:
        flash("That ID already exists.", "error"); return redirect(url_for("admin"))
    students[sid] = name
    save_students(students)
    flash(f"Added {name}.", "ok")
    return redirect(url_for("admin"))

@app.post("/admin/delete/<student_id>")
def delete_student(student_id):
    if request.cookies.get("authed") != "1":
        flash("Unauthorized.", "error"); return redirect(url_for("admin"))
    students = load_students()
    if student_id in students:
        name = students.pop(student_id)
        save_students(students)
        flash(f"Deleted {name}.", "ok")
    else:
        flash("Student not found.", "error")
    return redirect(url_for("admin"))

@app.get("/download.csv")
def download_csv():
    # Stream the existing CSV
    return send_file(FILENAME, as_attachment=True, download_name="attendance.csv")

@app.post("/admin/mark-missing-absent")
def mark_all_absent():
    if request.cookies.get("authed") != "1":
        flash("Unauthorized.", "error"); return redirect(url_for("admin"))
    students = load_students()
    today = datetime.date.today().isoformat()
    # Build set of students present today
    present = set()
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                if row["Date"] == today and row["Status"] == "Present":
                    present.add(row["Student ID"])
    except FileNotFoundError:
        pass

    # Append Absent rows for those not in present
    wrote = 0
    with open(FILENAME, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for sid, name in students.items():
            if sid not in present:
                w.writerow([today, sid, name, "Absent"])
                wrote += 1
    flash(f"Marked {wrote} students Absent for today.", "ok")
    return redirect(url_for("admin"))


# API (optional): Get students / add via JSON
@app.get("/api/students")
def api_students():
    return jsonify(load_students())

@app.post("/api/students")
def api_add_student():
    if request.headers.get("X-Admin-Pin") != ADMIN_PIN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(force=True)
    sid = str(data.get("id", "")).strip()
    name = str(data.get("name", "")).strip()
    if not sid or not name:
        return jsonify({"error": "missing fields"}), 400
    students = load_students()
    if sid in students:
        return jsonify({"error": "id exists"}), 409
    students[sid] = name
    save_students(students)
    return jsonify({"ok": True})


if __name__ == "__main__":
    init_files()
    # Run on all interfaces for LAN kiosk use
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)