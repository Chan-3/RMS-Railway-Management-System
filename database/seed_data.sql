-- =====================================================================
-- RMS SEED DATA  (FULL — Single File)
-- =====================================================================
USE rms;

-- =====================================================================
-- STATIONS
-- =====================================================================
INSERT INTO station (station_name, city, state) VALUES
('Bengaluru City', 'Bengaluru', 'Karnataka'),
('Mysuru',         'Mysuru',    'Karnataka'),
('Hubballi',       'Hubballi',  'Karnataka'),
('Mangaluru',      'Mangaluru', 'Karnataka'),
('Shivamogga',     'Shivamogga','Karnataka'),
('Chennai',        'Chennai',   'Tamil Nadu'),
('Hyderabad',      'Hyderabad', 'Telangana'),
('Mumbai',         'Mumbai',    'Maharashtra'),
('Kochi',          'Kochi',     'Kerala');

-- =====================================================================
-- ROUTES
-- (Bengaluru → various)
-- =====================================================================
INSERT INTO route (source_id, destination_id, distance_km, duration) VALUES
(1, 2, 145, '2h'),
(1, 3, 410, '8h'),
(1, 4, 350, '7h'),
(1, 5, 300, '6h'),
(1, 6, 350, '6.5h'),
(1, 7, 570, '10h'),
(1, 8, 980, '18h'),
(1, 9, 500, '9h');

-- =====================================================================
-- TRAINS (Name + Route)
-- =====================================================================
INSERT INTO train (name, route_id) VALUES
('Karnataka Express', 1),
('Udaya Express',     2),
('Malnad Express',    3),
('Namma Express',     5),
('South Star',        7);

-- =====================================================================
-- TRAIN CAPACITY
-- =====================================================================
INSERT INTO train_capacity (train_id, seat_type, total_seats) VALUES
(1, 'GENERAL', 200),
(1, 'SLEEPER', 100),
(1, 'AC',       50),

(2, 'GENERAL', 250),
(2, 'SLEEPER', 120),
(2, 'AC',       60),

(3, 'GENERAL', 180),
(3, 'SLEEPER', 90),
(3, 'AC',       40),

(4, 'GENERAL', 200),
(4, 'SLEEPER', 120),
(4, 'AC',       60),

(5, 'GENERAL', 220),
(5, 'SLEEPER', 150),
(5, 'AC',       80);

-- =====================================================================
-- FARE RATES
-- =====================================================================
INSERT INTO fare_rate (seat_type, rate) VALUES
('GENERAL', 1.5),
('SLEEPER', 2.0),
('AC',      3.0);

-- =====================================================================
-- ADMIN
-- (Password hashing will be done in application)
-- =====================================================================
INSERT INTO admin (email, username, password) VALUES
('admin@rms.local', 'admin', 'admin123');

-- =====================================================================
-- SUPERVISORS
-- =====================================================================
INSERT INTO employee (first_name, last_name, email, role, salary, password, supervisor_id)
VALUES
('Sneha',  'Bhat',   'sneha@rms.local',  'SUPERVISOR', 55000, 'emp123', NULL),
('Sahana', 'Menon',  'sahana@rms.local', 'SUPERVISOR', 60000, 'emp123', NULL);

-- =====================================================================
-- EMPLOYEES (all role = EMPLOYEE)
-- Sneha (emp_id = 1) supervises these
-- =====================================================================
INSERT INTO employee (first_name, last_name, email, role, salary, password, supervisor_id)
VALUES
('Ravi',   'Verma',  'ravi@rms.local',   'EMPLOYEE', 30000, 'emp123', 1),
('Arjun',  'Sharma', 'arjun@rms.local',  'EMPLOYEE', 32000, 'emp123', 1),
('Kiran',  'Patil',  'kiran@rms.local',  'EMPLOYEE', 31000, 'emp123', 1),
('Kavya',  'Nair',   'kavya@rms.local',  'EMPLOYEE', 33000, 'emp123', 1);

-- =====================================================================
-- EMPLOYEES for Sahana (emp_id = 2)
-- =====================================================================
INSERT INTO employee (first_name, last_name, email, role, salary, password, supervisor_id)
VALUES
('Vijay',  'Gowda',   'vijay@rms.local',  'EMPLOYEE', 34000, 'emp123', 2),
('Suresh', 'Shetty',  'suresh@rms.local', 'EMPLOYEE', 36000, 'emp123', 2),
('Priya',  'Kumar',   'priya@rms.local',  'EMPLOYEE', 35000, 'emp123', 2),
('Krithi','Joshi',   'krithi@rms.local', 'EMPLOYEE', 34500, 'emp123', 2);

-- =====================================================================
-- DONE
-- =====================================================================
SELECT '✅ RMS Seed Data Inserted Successfully' AS status;
