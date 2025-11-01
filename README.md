# Railway Management System (RMS)

The Railway Management System (RMS) is a web-based software solution designed to simplify and automate the management of major railway operations. Railways transport millions of passengers daily, and traditional manual workflows often lead to booking conflicts, delayed operations, inefficient staff allocation, and incomplete record keeping. RMS addresses these challenges by offering a unified digital platform for passengers, administrators, supervisors, and staff.

The system provides secure ticket booking, route planning, schedule management, and centralized database operations. Staff and supervisors can review operational tasks, update route or train information, report issues, and monitor schedules. Administrators can oversee the entire network including employees, stations, trains, and revenue reporting. RMS ultimately ensures faster processing, improved transparency, accuracy in decision-making, and better passenger service delivery.

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
- View Reports: revenue, bookings, employee–train assignment

Supervisor
- Dashboard
- Manage employees (view / update role & salary)
- Train assignments (assign employee → train / remove assignment)
- Work scheduling (create / delete / view by date)
- Train status updates
- View bookings (filter by name / train / date)
- Review employee reports (view / update status)

Employee
- Dashboard
- View/update profile
- View trains and update status
- Update seat capacity (General / Sleeper / AC)
- View bookings for assigned train
- View assigned trains
- View scheduled shifts
- Submit/view reports to supervisor

Passenger
- Dashboard
- Register/Login
- View/update profile
- Search trains by source → destination
- Book ticket (seat type, count, date, payment mode)
- Cancel ticket
- View booking history

------------------------------------------------------------
2) Tech Stack
------------------------------------------------------------

Backend: Flask  
Database: MySQL  
Auth: Session + role-based access  
Environment variable support: python-dotenv  
Password hashing: Werkzeug  
DB Connector: mysql-connector-python  
Templates: Jinja2  

------------------------------------------------------------
3) Project Structure (with inline explanation)
------------------------------------------------------------

------------------------------------------------------------
3) Project Structure
------------------------------------------------------------

RMS-Railway-Management-System/     (root project directory)
│ app.py                           (main Flask entry point to start the server)
│ config.py                        (application + DB configuration settings)
│ pswd.py                          (helper script to hash default passwords)
│ secretkey.py                     (script to generate SECRET_KEY value)
│ requirements.txt                 (Python dependencies list)
│ README.md                        (project documentation)
│
├─ blueprints/                     (role-based route controllers)
│   admin.py                       (admin routes)
│   auth.py                        (authentication routes: login/register/logout)
│   employee.py                    (employee routes)
│   passenger.py                   (passenger routes)
│   supervisor.py                  (supervisor routes)
│   main.py                        (public/home route)
│
├─ services/                       (business logic for modules)
│   admin_service.py               (admin operations logic)
│   auth_service.py                (user auth + session handling)
│   booking_service.py             (ticket booking operations)
│   employee_service.py            (employee operations)
│   history_service.py             (booking history)
│   search_service.py              (train search logic)
│   supervisor_service.py          (supervisor operations)
│
├─ utils/                          (helper modules)
│   decorators.py                  (role-based access control helper)
│
├─ database/                       (database build + connection)
│   connection.py                  (MySQL connection helper)
│   schema.sql                     (table creation)
│   seed_data.sql                  (initial records)
│   functions.sql                  (SQL functions)
│   procedures.sql                 (stored procedures)
│   triggers.sql                   (triggers)
│   path.txt                       (reference path info)
│
└─ templates/                      (HTML Jinja2 templates)
    home.html                      (public landing page)
    layout.html                    (base UI layout for pages)
    │
    ├─ admin/                      (admin UI pages)
    ├─ auth/                       (login/register pages)
    ├─ employee/                   (employee UI pages)
    ├─ passenger/                  (passenger UI pages)
    └─ supervisor/                 (supervisor UI pages)


------------------------------------------------------------
4) Setup
------------------------------------------------------------

Clone project (Git):
git clone https://github.com/Chan-3/RMS-Railway-Management-System.git
cd RMS-Railway-Management-System

Create virtual environment:
python -m venv venv

Activate (Windows):
venv\Scripts\Activate.ps1

Activate (Mac/Linux):
source venv/bin/activate

Install requirements:
pip install -r requirements.txt

------------------------------------------------------------
5) Database Setup (MySQL)
------------------------------------------------------------

Database can be initialized in two ways.

----------------------------------------
Method-1: Using VS Code terminal / CMD
----------------------------------------

mysql -u <username> -p

Inside MySQL:
CREATE DATABASE IF NOT EXISTS rms;
USE rms;

Execute SQL files in order:
SOURCE database/schema.sql;
SOURCE database/seed_data.sql;
SOURCE database/functions.sql;
SOURCE database/procedures.sql;
SOURCE database/triggers.sql;

----------------------------------------
Method-2: Using MySQL CLI directly
----------------------------------------

CREATE DATABASE IF NOT EXISTS rms;
USE rms;

Then run:
SOURCE /absolute/path/to/schema.sql;
SOURCE /absolute/path/to/seed_data.sql;
SOURCE /absolute/path/to/functions.sql;
SOURCE /absolute/path/to/procedures.sql;
SOURCE /absolute/path/to/triggers.sql;

------------------------------------------------------------
6) Environment Setup
------------------------------------------------------------

Create `.env` in project root:

FLASK_ENV=development
SECRET_KEY=YOUR_SECRET_KEY
DB_HOST=localhost
DB_USER=YOUR_DB_USER
DB_PASSWORD=YOUR_DB_PASSWORD
DB_NAME=rms

(Do NOT commit `.env`)

------------------------------------------------------------
7) Generate Secret Key
------------------------------------------------------------

python secretkey.py  
Copy the key → paste into .env under SECRET_KEY=

------------------------------------------------------------
8) Hash Default Passwords
------------------------------------------------------------

python pswd.py  
(Generates hashed passwords for admin/supervisor/employee)

------------------------------------------------------------
9) Run Application
------------------------------------------------------------

python app.py  
Open in browser:  
http://127.0.0.1:5000  

------------------------------------------------------------
10) Role Usage Summary
------------------------------------------------------------

Passenger:
- Register / login
- Search → book → cancel
- View history
- Update profile

Supervisor:
- Manage employees (scoped)
- Assign trains
- Create/delete schedules
- Update train status
- Booking filter
- Manage employee reports

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
11) requirements.txt
------------------------------------------------------------

Purpose: Lists required Python packages.  
Used for environment setup with:  
pip install -r requirements.txt  

Flask  
(Framework for building the backend server and routing)

python-dotenv  
(Reads configuration values securely from .env file)

mysql-connector-python  
(Enables connection between Python backend and MySQL database)

Werkzeug  
(Provides utilities including password hashing + security helpers)

------------------------------------------------------------
.end
------------------------------------------------------------
