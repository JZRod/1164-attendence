import tkinter as tk
from tkinter import messagebox
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

# Dictionary of students (preload if needed)
students = {
    "101": "Alice",
    "102": "Bob",
    "103": "Charlie",
    "104": "Diana",
    "105": "Ethan"
}

def mark_attendance(sid, status="Present"):
    if sid not in students:
        messagebox.showerror("Error", "Student not found.")
        return

    name = students[sid]
    today = datetime.date.today().isoformat()

    with open(FILENAME, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([today, sid, name, status])

    messagebox.showinfo("✅ Check-In Complete", f"Welcome, {name}!\nYou are marked {status}.")

def refresh_checkin_buttons():
    for widget in frame_buttons.winfo_children():
        widget.destroy()
    for sid, name in students.items():
        btn = tk.Button(frame_buttons, text=f"🙋 {name}",
                        font=("Arial", 18, "bold"), bg="lightgreen",
                        width=20, height=2,
                        command=lambda s=sid: mark_attendance(s, "Present"))
        btn.pack(pady=10)

def exit_kiosk(event=None):
    root.destroy()


# ------------------- GUI (Kiosk Mode) -------------------
root = tk.Tk()
root.title("🎓 Attendance Kiosk Mode")
root.attributes("-fullscreen", True)   # Fullscreen
root.configure(bg="white")

init_file()

# Exit with Ctrl+Q
root.bind("<Control-q>", exit_kiosk)

# Title
title = tk.Label(root, text="📌 Tap Your Name to Check In", 
                 font=("Arial", 28, "bold"), bg="white")
title.pack(pady=20)

# Scrollable frame for student buttons
canvas = tk.Canvas(root, bg="white")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg="white")

scroll_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

frame_buttons = scroll_frame  # Holds dynamic buttons
refresh_checkin_buttons()

# Exit hint (hidden from students)
hint = tk.Label(root, text="(Press Ctrl+Q to Exit)", font=("Arial", 10), bg="white", fg="gray")
hint.pack(side="bottom", pady=5)

root.mainloop()