# FRC 1164 Attendance System

![Logo](assets/logo.png)

A lightweight, Windows-10-compatible attendance tracking system for **FRC Team 1164 Project NEO**.  
Built with **Python + Tkinter**, this app provides a simple full-screen interface for team members to check in, while giving admins full control over attendance records, student management, and system settings.

---

## ✨ Features

### 👨‍👩‍👦 Student Check-In
- Tap your name to mark attendance.
- Tap again to remove yourself from today's attendance.
- Guest sign-in for visitors not on the roster.

### 📊 Admin Panel
- PIN-protected admin access.
- View, and download attendance logs as CSV spreadsheet.
- Add, edit, or remove students.
- Customize header color and logo.

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

## 🚀 Getting Started

### Requirements
- Python 3.7 or newer (3.7/3.8 recommended for Windows 7)
- [Pillow](https://pypi.org/project/pillow/) for image support

### Installation with Installer
1. Install Python 3.7 or newer from [Python.org](https://www.python.org/downloads/)
2. Download the Installer from the releases page
3. Run the Installer

### Instalation with the standalone executable
1. Install Python 3.7 or newer from [Python.org](https://www.python.org/downloads/)
2. Download the newest release from the releases page
3. Download or create your own "assets" and "data" folders and place them in the same directory as the executable.

### 📊 Admin Panel
- Default PIN is 1234
- PIN can be changed from within the admin panel settings tab by pressing the change PIN button

### 🖥 Fullscreen & Scrolling
- The app will auto launch in fullscreen mode
- Fullscreen can be exited/entered by pressing F11 or Esc

## Credits
- Developed by JZRod with lots of help from ChatGPT, Replit AI, Github Copilot, and Claude AI
- Developed for FRC team 1164 Project NEO
