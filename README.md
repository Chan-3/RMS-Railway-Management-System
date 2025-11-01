# Railway Management System (RMS)

The Railway Management System (RMS) is a web-based application designed to streamline key railway operations such as ticket booking, route planning, scheduling, employee assignment, and passenger management. Railways transport millions daily, and traditional manual handling often causes double bookings, scheduling conflicts, data inconsistency, and inefficiency.

RMS provides digitized workflows, structured storage, real-time retrieval, role-based access, and efficient reporting. This ensures greater accuracy, faster processing, reduced human error, and improved user experience for passengers, employees, supervisors, and administrators.

------------------------------------------------------------
1) Features by Role
------------------------------------------------------------

Admin
- Dashboard
- Manage Stations (create / edit / delete)
- Manage Routes (create / edit / delete)
- Manage Trains (create / edit / delete)
- Manage Passengers (view / search / delete / activate–deactivate)
- Manage Employees (create / edit / update role + salary / activate–deactivate / assign supervisor)
- View Reports (revenue / bookings / assignments)

Supervisor
- Dashboard
- Manage employees (view / edit role & salary)
- Assign / unassign employees to trains
- Create / delete schedules (filter by date)
- Update train operational status
- Filter bookings by name / train / date
- View + update employee reports status

Employee
- Dashboard
- View/update profile
- View trains and update status
- Update seat capacity (General / Sleeper / AC)
- View bookings for assigned train
- View assigned trains
- View scheduled shifts
- Submit/view reports

Passenger
- Dashboard
- Register/Login
- View/update profile
- Search trains by source → destination
- Book ticket (seat type, count, date, payment)
- Cancel ticket
- View booking history

------------------------------------------------------------
2) Tech Stack
------------------------------------------------------------

Backend: Flask  
Database: MySQL  
Auth: Session + role-based access  
Environment variables: python-dotenv  
Password hashing: Werkzeug  
DB Connector: mysql-connector-python  
Templates: Jinja2  

------------------------------------------------------------
3) Project Structure
------------------------------------------------------------

RMS-Railway-Management-System/
- app.py              → Main Flask entry point
- config.py           → App + DB configuration
- pswd.py             → Password hashing helper
- secretkey.py        → Generates secret.txt (copy key into .env)
- requirements.txt    → Python dependencies
- README.md           → Documentation

blueprints/           → Route handlers by role
- admin.py            → Admin routes
- auth.py             → Login/Register routes
- employee.py         → Employee routes
- passenger.py        → Passenger routes
- supervisor.py       → Supervisor routes
- main.py             → Public/Home routes

services/             → Business logic
- admin_service.py
- auth_service.py
- booking_service.py
- employee_service.py
- history_service.py
- search_service.py
- supervisor_service.py

utils/                → Helper utilities
- decorators.py       → Role-based access control

database/             → DB setup + SQL scripts
- connection.py       → DB connector
- schema.sql          → Table creation
- seed_data.sql       → Initial data
- functions.sql       → SQL functions
- procedures.sql      → Stored procedures
- triggers.sql        → DB triggers

templates/            → Jinja2 HTML templates (UI)
- home.html           → Landing page
- layout.html         → Base layout
- admin/              → Admin UI pages
- auth/               → Login/Register UI pages
- employee/           → Employee UI pages
- passenger/          → Passenger UI pages
- supervisor/         → Supervisor UI pages


------------------------------------------------------------
4) Setup
------------------------------------------------------------

Clone Project:
   
    git clone https://github.com/Chan-3/RMS-Railway-Management-System.git
    
    cd RMS-Railway-Management-System

Create Virtual Environment:
    
    python -m venv venv

Activate (Windows):
    
    venv\Scripts\Activate.ps1

Activate (Mac/Linux):
    
    source venv/bin/activate

Install Dependencies:
    
    pip install -r requirements.txt

------------------------------------------------------------
5) Database Setup (MySQL)
------------------------------------------------------------

OPTION A — From VS Code / CMD
    mysql -u <username> -p

    SOURCE database/schema.sql;
    SOURCE database/seed_data.sql;
    SOURCE database/functions.sql;
    SOURCE database/procedures.sql;
    SOURCE database/triggers.sql;

OPTION B — From MySQL CLI

    SOURCE /absolute/path/schema.sql;
    SOURCE /absolute/path/seed_data.sql;
    SOURCE /absolute/path/functions.sql;
    SOURCE /absolute/path/procedures.sql;
    SOURCE /absolute/path/triggers.sql;

------------------------------------------------------------
6) Environment Setup
------------------------------------------------------------

Create `.env` in root:

    FLASK_ENV=development
    SECRET_KEY=YOUR_SECRET_KEY
    DB_HOST=localhost
    DB_USER=YOUR_DB_USER
    DB_PASSWORD=YOUR_DB_PASSWORD
    DB_NAME=rms

Generate SECRET_KEY:
    python secretkey.py

→ This creates `secrets.txt`  
→ Open secret.txt → copy generated key → paste into `.env` under SECRET_KEY=YOUR_SECRET_KEY


------------------------------------------------------------
7) Role Usage Summary
------------------------------------------------------------

Passenger:
- Register / login
- Search → book → cancel
- View bookings
- Update profile

Supervisor:
- Manage scoped employees
- Assign trains
- Create/Delete schedules
- Update train status
- Filter bookings
- Handle employee reports

Employee:
- View trains
- Update train status + seat capacity
- View bookings
- View assignments + schedule
- Submit reports

Admin:
- Manage stations, routes, trains, employees, passengers
- View reports

------------------------------------------------------------
8) requirements.txt
------------------------------------------------------------

Purpose: Defines application dependencies for easy setup via  
    
    pip install -r requirements.txt  

Flask                       → Core backend framework  
python-dotenv               → Load .env config  
mysql-connector-python      → MySQL connector library  
Werkzeug                    → Security + hashing utilities  

