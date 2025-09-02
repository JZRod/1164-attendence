# FRC 1164 Attendance System

![Logo](assets/logo.png)

A lightweight, Windows-7-compatible attendance tracking system for **FRC Team 1164**.  
Built with **Python + Tkinter**, this app provides a simple full-screen interface for team members to check in, while giving admins full control over attendance records, student management, and system settings.

---

## ✨ Features

### 👨‍👩‍👦 Student Check-In
- Tap your name to mark attendance.
- Tap again to remove yourself from today's attendance.
- Guest sign-in for visitors not on the roster.

### 📊 Admin Panel
- PIN-protected admin access.
- View, refresh, and download attendance logs as CSV.
- Add, edit, or remove students.
- Customize header color and logo.
- Close buttons on every admin panel tab.

### 🎨 Customization
- Change team logo directly from settings.
- Select your preferred header color.
- Full-screen interface (F11 / Esc to toggle).
- Automatic scaling and scrolling when needed.

### 💾 Data Management
- Attendance records stored in `data/attendance.csv`.
- Student list stored in `data/students.json`.
- Configurable options in `data/config.json`.
- Assets (logos, icons) stored in `assets/`.

---

## 📂 Project Structure
├── assets/ # Logos and icons
│ ├── logo.png
│ └── gear.png
├── data/ # Persistent app data
│ ├── attendance.csv
│ ├── students.json
│ └── config.json
├── FRC-1164-Attendance-System.py # Main application
└── README.md # You are here


---

## 🚀 Getting Started

### Requirements
- Python 3.7 or newer (3.7/3.8 recommended for Windows 7)
- [Pillow](https://pypi.org/project/pillow/) for image support

### Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/JZRod/1164-attendence.git
   cd 1164-attendence
