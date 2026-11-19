# 🏥 Blood Bank & Organ Donors Management System

A desktop application for managing blood bank operations and organ donor registrations, built with Python and CustomTkinter.

## 📋 Features

- **Admin Authentication** — Secure login with bcrypt password hashing
- **Blood Donor Management** — Register, view, edit, and delete blood donors
- **Blood Donation Tracking** — Maintain complete donation history
- **Blood Inventory** — Track available blood units by blood group
- **Organ Donor Management** — Register organ donors with consent tracking
- **Blood & Organ Requests** — Manage and prioritize blood/organ requests
- **Dashboard** — Summary statistics and quick actions
- **Search & Filtering** — Find donors and requests quickly
- **Reports & CSV Export** — Export data for analysis
- **Activity Logs** — Audit trail of system actions

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| GUI | CustomTkinter |
| Database | SQLite |
| Security | bcrypt |
| Packaging | PyInstaller |

## 🚀 Setup & Run

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📦 Build Executable

```bash
pyinstaller --noconfirm --onefile --windowed --name "BloodBankManager" main.py
```

The `.exe` will be generated in the `dist/` folder.

## 🔐 Default Credentials

- **Username:** admin
- **Password:** admin123

## 👥 Team

- Member A — Backend Lead + Blood Modules
- Member B — Frontend Lead + Organ Modules

## 📁 Project Structure

```
BloodBank-OrganDonor/
├── main.py                  # App entry point
├── config.py                # Configuration
├── database/                # Database layer
├── models/                  # Data access layer
├── services/                # Business logic
├── views/                   # UI screens
├── components/              # Reusable UI widgets
├── utils/                   # Helpers & validators
├── assets/                  # Images & icons
└── tests/                   # Unit tests
```

## 📄 License

This project is developed for educational purposes as part of a Software Engineering lab course.
