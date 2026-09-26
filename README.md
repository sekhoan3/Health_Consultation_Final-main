# MediConsult — Health Consultation Platform

A lightweight health consultation web application built with Python Flask and SQLite3. Patients can submit consultations and book appointments, doctors can review and respond, and admins have full system control through a dedicated admin panel.

\---

## Features

* **Patient** — submit consultation requests, book appointments, manage health profile
* **Doctor** — review patient consultations, view schedule, update consultation status
* **Admin** — full user management (CRUD), assign doctors to consultations, update appointment statuses, system-wide stats dashboard
* Multi-step consultation form with symptom tags and severity selector
* Modern responsive UI with sidebar navigation and Lucide icons
* SQLite3 database — no external database setup required
* Session-based authentication with role-based access control

\---

## Project Structure

```
heatlh\\\_platform\\\_sample/
├── app.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── view\\\_db.py                    # Terminal database viewer
├── crud\\\_demo.py                  # CRUD operations demo
│
├── backend/
│   ├── database.py               # DB init, table creation, demo seed
│   ├── auth.py                   # Register and login logic
│   ├── models.py                 # Patient, doctor, consultation, appointment queries
│   ├── routes.py                 # Main Flask routes (patient \\\& doctor)
│   ├── admin\\\_models.py           # Admin-specific database queries
│   ├── admin\\\_routes.py           # Admin panel routes (/admin/\\\*)
│   └── health\\\_platform.db        # SQLite3 database file (auto-created)
│
└── frontend/
    ├── static/
    │   ├── css/main.css          # All styles
    │   └── js/main.js            # Sidebar, flash messages, interactions
    └── templates/
        ├── base.html             # Base layout with sidebar
        ├── auth/
        │   ├── login.html
        │   ├── register.html
        │   └── complete\\\_profile.html
        ├── dashboard/
        │   ├── patient\\\_dashboard.html
        │   └── doctor\\\_dashboard.html
        ├── consultations/
        │   ├── list.html
        │   ├── new.html          # 4-step wizard form
        │   └── view.html
        ├── appointments/
        │   ├── list.html
        │   └── new.html
        ├── profile/
        │   └── index.html
        └── admin/
            ├── dashboard.html
            ├── users.html
            ├── user\\\_form.html
            ├── consultations.html
            └── appointments.html
```

\---

## Requirements

* Python 3.10 or higher
* pip

No external database, no Docker, no environment variables required.

\---

## Setup Instructions

### 1\. Clone the repository

```bash
git clone https://github.com/ShiroGami541/Health\\\_Platform\\\_Sample.git
cd Health\\\_Platform\\\_Sample
```

### 2\. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\\\\Scripts\\\\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3\. Install dependencies

```bash
pip install -r requirements.txt
```

Only one dependency is required:

```
flask==3.1.3
```

### 4\. Run the application

```bash
python app.py
```

The database is created and seeded automatically on first run. You will see:

```
Health Consultation Platform
Running at: http://127.0.0.1:5000
Demo credentials:
  Admin   -> admin@health.com   / admin123
  Doctor  -> doctor@health.com  / doctor123
  Patient -> patient@health.com / patient123
```

### 5\. Open in browser

```
http://127.0.0.1:5000
```

\---

## Demo Accounts

|Role|Email|Password|
|-|-|-|
|Admin|admin@health.com|admin123|
|Doctor|doctor@health.com|doctor123|
|Patient|patient@health.com|patient123|

\---

## Pages and Routes

|Route|Access|Description|
|-|-|-|
|`/`|Public|Redirects to login|
|`/login`|Public|Sign in|
|`/register`|Public|Create account (step 1 of 2)|
|`/register/profile`|Authenticated|Complete profile (step 2 of 2)|
|`/dashboard`|Authenticated|Role-based dashboard|
|`/consultations`|Authenticated|List consultations|
|`/consultations/new`|Patient|4-step consultation wizard|
|`/consultations/<id>`|Authenticated|View consultation detail|
|`/appointments`|Authenticated|List appointments|
|`/appointments/new`|Patient|Book an appointment|
|`/profile`|Authenticated|View and edit profile|
|`/admin/`|Admin only|Admin dashboard with stats|
|`/admin/users`|Admin only|Manage all users|
|`/admin/users/new`|Admin only|Create a new user|
|`/admin/users/<id>/edit`|Admin only|Change user role|
|`/admin/users/<id>/delete`|Admin only|Delete a user|
|`/admin/consultations`|Admin only|Assign doctors, update statuses|
|`/admin/appointments`|Admin only|Update appointment statuses|

\---

## Utility Scripts

### View the database in terminal

```bash
python view\\\_db.py
```

Displays all tables and their data with colored output.

### Run CRUD demo

```bash
python crud\\\_demo.py
```

Demonstrates INSERT, SELECT, UPDATE, DELETE against the live database.

\---

## Database Schema

**users** — base account for all roles  
**patients** — extended profile linked to a user  
**doctors** — professional profile linked to a user  
**consultations** — patient health requests with symptoms and history  
**appointments** — scheduled visits between patient and doctor

\---

## Tech Stack

|Layer|Technology|
|-|-|
|Backend|Python 3, Flask 3.1|
|Database|SQLite3 (built into Python)|
|Frontend|Jinja2 templates, HTML5, CSS3|
|Icons|Lucide Icons (CDN)|
|Auth|Flask sessions, SHA-256 hashing|

\---

## Stopping the Server

Press **Ctrl + C** in the terminal where the app is running.

