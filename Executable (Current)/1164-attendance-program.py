import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import csv
import datetime
import os
import json
from PIL import Image, ImageTk, ImageOps
import sys

# ---------------- Config ----------------
DATA_FOLDER = "data"
ASSETS_FOLDER = "assets"
FILENAME = os.path.join(DATA_FOLDER, "attendance.csv")  # Move attendance.csv to the data folder
STUDENTS_FILE = os.path.join(DATA_FOLDER, "students.json")  # Move students.json to the data folder
LOGO_FILE = os.path.join(ASSETS_FOLDER, "logo.png")  # Move logo.png to the assets folder
GEAR_FILE = os.path.join(ASSETS_FOLDER, "gear.png")  # Move gear.png to the assets folder
ADMIN_PIN = "1164"
HEADER_HEIGHT = 150  # Increased header height
HEADER_COLOR = "#5D3FD3"  # Updated header color

# ---------------- Storage Helpers ----------------
def init_files():
    # Ensure the data folder exists
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(FILENAME):
        with open(FILENAME, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Name", "Status"])
    if not os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(["placeholder1", "placeholder2", "placeholder3", "placeholder4"], f, indent=2)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller .exe"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_students():
    with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_students(students):
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2, ensure_ascii=False)

def already_checked_in(name, date_iso):
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                if row["Date"] == date_iso and row["Name"] == name and row["Status"] == "Present":
                    return True
    except FileNotFoundError:
        return False
    return False

def mark_attendance(name, status="Present"):
    today = datetime.date.today().isoformat()
    if status == "Present" and already_checked_in(name, today):
        return False, f"{name} is already marked Present today."
    with open(FILENAME, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([today, name, status])
    return True, f"Welcome, {name}! You're marked {status}."

# ---------------- GUI App ----------------
class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance System")
        self.root.configure(bg="black")  # Make the window background black so gaps are black

        # Fullscreen toggle
        self.fullscreen = True
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.toggle_fullscreen)

        # Header frame
        header = tk.Frame(root, bg=HEADER_COLOR, height=HEADER_HEIGHT)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Layout header with grid so we can center title and align a bigger logo
        header.rowconfigure(0, weight=1)
        header.columnconfigure(0, minsize=HEADER_HEIGHT)  # Space for logo
        header.columnconfigure(1, weight=1)               # Center area for title
        header.columnconfigure(2, minsize=120)            # Space for admin button

        # Logo left (centered vertically, preserving aspect ratio)
        try:
            max_logo = HEADER_HEIGHT - 40  # Slightly smaller than the header height for padding
            img = Image.open(LOGO_FILE)
            img.thumbnail((max_logo, max_logo), Image.LANCZOS)  # Preserve aspect ratio
            self.logo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(header, image=self.logo, bg=HEADER_COLOR)
            # Place logo in left column and center it vertically
            logo_label.grid(row=0, column=0, padx=12, sticky="ns")  # Use sticky="ns" for vertical centering
        except Exception:
            fallback_font_size = max(16, HEADER_HEIGHT // 6)
            logo_label = tk.Label(header, text="LOGO", bg=HEADER_COLOR, fg="white",
                                  font=("Arial", fallback_font_size))
            logo_label.grid(row=0, column=0, padx=12, sticky="ns")  # Use sticky="ns" for vertical centering

        # Title center (will be centered in the available middle column)
        self.title_label = tk.Label(header, text="📌 Tap Your Name to Check In",
                                    bg=HEADER_COLOR, fg="white", font=("Arial", 20, "bold"))  # Decreased font size to 20 and changed color to white
        self.title_label.grid(row=0, column=1, sticky="nsew")

        # Admin button right with gear icon and thin white outline
        try:
            # Load the gear icon
            gear_icon = Image.open(GEAR_FILE)  # Use the updated path for gear.png
            gear_icon = gear_icon.convert("RGBA")  # Ensure the image has an alpha channel for transparency
            gear_icon.thumbnail((25, 25), Image.LANCZOS)  # Resize the gear icon to 25x25 pixels (smaller)

            # Convert the image to a PhotoImage for tkinter
            self.gear_icon = ImageTk.PhotoImage(gear_icon)

            # Create the admin button with the gear icon
            self.admin_btn = tk.Button(
                header,
                image=self.gear_icon,
                text=" Admin",
                compound="left",  # Place the icon to the left of the text
                command=self.admin_panel,
                bg=HEADER_COLOR,
                fg="white",
                font=("Arial", 14, "bold"),
                borderwidth=0,  # Remove the default border
                highlightthickness=2,  # Thin white outline thickness
                highlightbackground="white",  # White outline color
                highlightcolor="white"  # White outline color when focused
            )
        except Exception as e:
            # Fallback to a text-only button if the gear icon fails to load
            print(f"Error loading gear icon: {e}")
            self.admin_btn = tk.Button(
                header,
                text="Admin",
                command=self.admin_panel,
                bg=HEADER_COLOR,
                fg="white",
                font=("Arial", 14, "bold"),
                borderwidth=0,
                highlightthickness=2,  # Thin white outline thickness
                highlightbackground="white",  # White outline color
                highlightcolor="white"  # White outline color when focused
            )

        # Place the admin button in the header
        self.admin_btn.grid(row=0, column=2, padx=10, sticky="e")

        # Guest sign-in bar spanning across top (under header)
        self.guest_frame = tk.Frame(root, bg="black")  # Matches the overall black background
        self.guest_frame.pack(fill="x", pady=(10, 0))  # Add space between the header and the guest frame
        self.guest_btn = tk.Button(
            self.guest_frame,
            text="👤  Guest Sign In  —  Tap to Enter Your Name",
            command=self.guest_sign_in,
            bg="#333",  # Matches student card background
            fg="white",  # Adjusted text color for better contrast
            font=("Arial", 14, "bold"),  # Match font size with student buttons
            height=2   # Match height with student buttons
        )
        self.guest_btn.pack(fill="x", padx=12, pady=12)  # Add padding for consistent spacing

        # Main container for student buttons
        self.container = tk.Frame(root, bg="black")
        self.container.pack(fill="both", expand=True)

        self.students = load_students()
        self.build_student_buttons()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def build_student_buttons(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        today = datetime.date.today().isoformat()

        COLS = 4  # Number of buttons per row
        for c in range(COLS):
            self.container.grid_columnconfigure(c, weight=1)  # Ensure columns expand evenly

        # Arrange buttons in a grid
        row, col = 0, 0
        for name in self.students:
            checked = already_checked_in(name, today)
            text = f"🙋 {name}" + (" ✅" if checked else "")
            btn = tk.Button(
                self.container,
                text=text,
                width=20,
                height=2,
                command=lambda n=name: self.checkin(n),
                bg="#333",
                fg="white",
                font=("Arial", 14, "bold"),
                justify="center",
                wraplength=180
            )
            btn.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
            col += 1
            if col >= COLS:  # Wrap to the next row after 4 buttons
                col = 0
                row += 1

        # Ensure empty columns on the last row expand evenly
        for c in range(COLS):
            self.container.grid_columnconfigure(c, weight=1)

    def checkin(self, name):
        ok, msg = mark_attendance(name)
        if ok:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showwarning("Already Checked In", msg)
        self.build_student_buttons()

    def admin_panel(self):
        pin = simpledialog.askstring("Admin Login", "Enter Admin PIN:", show="*")
        if pin != ADMIN_PIN:
            messagebox.showerror("Error", "Wrong PIN")
            return

        admin_win = tk.Toplevel(self.root)
        admin_win.title("Admin Panel")
        admin_win.geometry("800x600")

        # Table for attendance
        frame = tk.Frame(admin_win, bg="black")
        frame.pack(fill="both", expand=True)

        cols = ("Date", "Name", "Status")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        tree.pack(fill="both", expand=True)

        # Reload table with CSV data
        with open(FILENAME, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                tree.insert("", "end", values=(row["Date"], row["Name"], row["Status"]))

        # Buttons side by side
        btn_frame = tk.Frame(admin_win, bg="black")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Student", command=lambda: self._add_student_and_refresh(admin_win),
                  bg="purple", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Delete Student", command=lambda: self._delete_student_and_refresh(admin_win),
                  bg="red", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Download CSV", command=self.download_csv,
                  bg="green", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Close", command=admin_win.destroy,
                  bg="gray", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=5)

    # --- Admin helper functions ---
    def _add_student_and_refresh(self, admin_win):
        name = simpledialog.askstring("Add Student", "Enter Student Name:")
        if name:
            self.students.append(name)
            save_students(self.students)
            self.build_student_buttons()
            messagebox.showinfo("Added", f"Student {name} added.")
            tree = admin_win.winfo_children()[0].winfo_children()[0]  # Get the tree view
            self.refresh_admin_panel(tree)

    def _delete_student_and_refresh(self, admin_win):
        name = simpledialog.askstring("Delete Student", "Enter Student Name to delete:")
        if name in self.students:
            self.students.remove(name)
            save_students(self.students)
            self.build_student_buttons()
            messagebox.showinfo("Deleted", f"Student {name} removed.")
            tree = admin_win.winfo_children()[0].winfo_children()[0]  # Get the tree view
            self.refresh_admin_panel(tree)
        else:
            messagebox.showerror("Error", "Student not found.")

    def download_csv(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            with open(FILENAME, "r", encoding="utf-8") as f_in, open(save_path, "w", encoding="utf-8") as f_out:
                f_out.write(f_in.read())
            messagebox.showinfo("Success", f"CSV saved to {save_path}")

    def guest_sign_in(self):
        name = simpledialog.askstring("Guest Sign In", "Enter your name:")
        if name:
            ok, msg = mark_attendance(name)
            if ok:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showwarning("Already Checked In", msg)
            self.build_student_buttons()
            # Refresh the admin panel if it's open
            for window in self.root.winfo_children():
                if isinstance(window, tk.Toplevel) and window.title() == "Admin Panel":
                    tree = window.winfo_children()[0].winfo_children()[0]  # Get the tree view
                    self.refresh_admin_panel(tree)

    def _remove_from_todays_attendance(self, tree, admin_win):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No entry selected.")
            return

        # Get selected row data
        item = tree.item(selected_item[0])
        values = item["values"]
        if len(values) < 3:
            messagebox.showerror("Error", "Invalid selection.")
            return

        date, name, status = values

        # Check if the selected entry is for today
        today = datetime.date.today().isoformat()
        if date != today:
            messagebox.showerror("Error", "You can only remove entries from today's attendance.")
            return

        # Remove the entry from the CSV file
        updated_rows = []
        entry_removed = False
        try:
            with open(FILENAME, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row == ["Date", "Name", "Status"]:  # Keep the header row
                        updated_rows.append(row)
                    elif row[0] == date and row[1] == name and row[2] == status and not entry_removed:
                        # Skip the first matching entry (remove it)
                        entry_removed = True
                    else:
                        updated_rows.append(row)

            # Write the updated rows back to the CSV file
            with open(FILENAME, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(updated_rows)

            # Refresh the admin panel
            if entry_removed:
                messagebox.showinfo("Success", f"Removed {name} from today's attendance.")
            else:
                messagebox.showwarning("Warning", "No matching entry found to remove.")
            self.refresh_admin_panel(tree)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def refresh_admin_panel(self, tree):
        # Clear the current tree view
        for item in tree.get_children():
            tree.delete(item)

        # Reload table with CSV data
        with open(FILENAME, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                tree.insert("", "end", values=(row["Date"], row["Name"], row["Status"]))


# ---------------- Run App ----------------
if __name__ == "__main__":
    init_files()
    root = tk.Tk()

    # Set window icon
    try:
        icon_path = os.path.join(ASSETS_FOLDER, "icon.ico")
        root.iconbitmap(icon_path)  # Best for Windows
    except Exception as e:
        print("Could not set window icon:", e)

    app = AttendanceApp(root)
    root.mainloop()
