import tkinter as tk
from tkinter import messagebox, ttk
import csv
import datetime
import os

FILENAME = "attendance.csv"

# Initialize CSV file if not exists
def init_file():
    if not os.path.exists(FILENAME):
        with open(FILENAME, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Student ID", "Name", "Status"])

# Dictionary of students
students = {}

def add_student():
    sid = entry_id.get().strip()
    name = entry_name.get().strip()

    if not sid or not name:
        messagebox.showwarning("⚠️ Input Error", "Please enter both ID and Name.")
        return
    
    students[sid] = name
    refresh_student_list()
    refresh_checkin_buttons()
    messagebox.showinfo("✅ Success", f"Student {name} added!")
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)

def mark_attendance(sid, status="Present"):
    if sid not in students:
        messagebox.showerror("Error", "Student not found.")
        return

    name = students[sid]
    today = datetime.date.today().isoformat()

    with open(FILENAME, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([today, sid, name, status])

    messagebox.showinfo("🎉 Done", f"Attendance marked: {name} - {status}")

def refresh_student_list():
    for row in student_list.get_children():
        student_list.delete(row)
    for sid, name in students.items():
        student_list.insert("", tk.END, values=(sid, name))

def refresh_checkin_buttons():
    for widget in frame_checkin_buttons.winfo_children():
        widget.destroy()
    for sid, name in students.items():
        btn = tk.Button(frame_checkin_buttons, text=f"👩‍🎓 {name}", 
                        font=("Arial", 14, "bold"), bg="lightgreen",
                        width=20, height=2,
                        command=lambda s=sid: mark_attendance(s, "Present"))
        btn.pack(pady=5)

def view_attendance():
    for row in tree.get_children():
        tree.delete(row)
    
    with open(FILENAME, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            tree.insert("", tk.END, values=row)


# ------------------- GUI -------------------
root = tk.Tk()
root.title("🎓 Student-Friendly Attendance System")
root.geometry("800x600")

init_file()

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# --- Tab 1: Add Student ---
frame1 = tk.Frame(notebook, padx=15, pady=15)
notebook.add(frame1, text="➕ Add Student")

tk.Label(frame1, text="Student ID:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
entry_id = tk.Entry(frame1, font=("Arial", 12))
entry_id.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame1, text="Student Name:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5)
entry_name = tk.Entry(frame1, font=("Arial", 12))
entry_name.grid(row=1, column=1, padx=5, pady=5)

btn_add = tk.Button(frame1, text="✅ Add Student", font=("Arial", 12, "bold"), bg="lightblue", command=add_student)
btn_add.grid(row=2, column=0, columnspan=2, pady=15)

student_list = ttk.Treeview(frame1, columns=("ID", "Name"), show="headings", height=8)
student_list.heading("ID", text="Student ID")
student_list.heading("Name", text="Name")
student_list.grid(row=3, column=0, columnspan=2, pady=10)

# --- Tab 2: Self Check-In Mode ---
frame2 = tk.Frame(notebook, padx=15, pady=15)
notebook.add(frame2, text="🙋 Self Check-In")

tk.Label(frame2, text="Click your name to mark yourself Present", font=("Arial", 14, "bold")).pack(pady=10)

canvas = tk.Canvas(frame2)
scrollbar = ttk.Scrollbar(frame2, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas)

scroll_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

frame_checkin_buttons = scroll_frame  # holds dynamic student buttons

# --- Tab 3: View Records ---
frame3 = tk.Frame(notebook, padx=15, pady=15)
notebook.add(frame3, text="📖 View Attendance")

tree = ttk.Treeview(frame3, columns=("Date", "ID", "Name", "Status"), show="headings")
tree.heading("Date", text="Date")
tree.heading("ID", text="Student ID")
tree.heading("Name", text="Name")
tree.heading("Status", text="Status")
tree.pack(fill="both", expand=True)

btn_view = tk.Button(frame3, text="🔄 Refresh Records", font=("Arial", 12), command=view_attendance)
btn_view.pack(pady=10)

root.mainloop()
