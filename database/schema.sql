/* =========================================================
   RMS DATABASE SCHEMA
========================================================= */

DROP DATABASE IF EXISTS rms;
CREATE DATABASE rms;
USE rms;


/* ------------------------
   PASSENGER
   Stores registered passengers
-------------------------*/
CREATE TABLE passenger (
    passenger_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name   VARCHAR(100) NOT NULL,
    last_name    VARCHAR(100),
    email        VARCHAR(100) UNIQUE NOT NULL,
    phone        VARCHAR(15) NOT NULL,
    gender       ENUM('MALE','FEMALE','OTHER') NOT NULL,
    age          INT,
    active TINYINT(1) DEFAULT 1,
    password     VARCHAR(255) NOT NULL
);


/* ------------------------
   ADMIN
   Stores admin accounts
-------------------------*/
CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    email    VARCHAR(120) UNIQUE,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);


/* ------------------------
   EMPLOYEE
   Stores employees + hierarchy (self FK)
-------------------------*/
CREATE TABLE employee (
    emp_id        INT AUTO_INCREMENT PRIMARY KEY,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100),
    email         VARCHAR(120) UNIQUE,
    role          VARCHAR(50) NOT NULL,
    salary        DECIMAL(10,2),
    supervisor_id INT,
    active TINYINT(1) DEFAULT 1,
    password      VARCHAR(255) NOT NULL DEFAULT 'emp123',
    FOREIGN KEY (supervisor_id) REFERENCES employee(emp_id)
);


/* ------------------------
   STATION
   Station master list
-------------------------*/
CREATE TABLE station (
    station_id   INT AUTO_INCREMENT PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    city         VARCHAR(100),
    state        VARCHAR(50) NOT NULL DEFAULT ''
);


/* ------------------------
   ROUTE
   Maps source → destination
-------------------------*/
CREATE TABLE route (
    route_id       INT AUTO_INCREMENT PRIMARY KEY,
    source_id      INT,
    destination_id INT,
    distance_km    INT NOT NULL,
    duration       VARCHAR(50),
    FOREIGN KEY (source_id)      REFERENCES station(station_id),
    FOREIGN KEY (destination_id) REFERENCES station(station_id)
);


/* ------------------------
   TRAIN
   Train master details
-------------------------*/
CREATE TABLE train (
    train_id INT AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(100) NOT NULL,
    route_id INT,
    status   ENUM('ON-TIME','DELAYED','CANCELLED') DEFAULT 'ON-TIME',
    FOREIGN KEY (route_id) REFERENCES route(route_id)
);


/* ------------------------
   TRAIN CAPACITY
   Seats per train + class
-------------------------*/
CREATE TABLE train_capacity (
    tc_id       INT AUTO_INCREMENT PRIMARY KEY,
    train_id    INT NOT NULL,
    seat_type   ENUM('GENERAL','SLEEPER','AC') NOT NULL,
    total_seats INT NOT NULL,
    UNIQUE KEY uniq_train_seat (train_id, seat_type),
    FOREIGN KEY (train_id) REFERENCES train(train_id)
);


/* ------------------------
   FARE RATE
   Base rate per seat type
-------------------------*/
CREATE TABLE fare_rate (
    seat_type ENUM('GENERAL','SLEEPER','AC') PRIMARY KEY,
    rate      DECIMAL(5,2) NOT NULL
);


/* ------------------------
   BOOKING
   Passenger booking records
-------------------------*/
CREATE TABLE booking (
    booking_id      INT AUTO_INCREMENT PRIMARY KEY,
    passenger_id    INT,
    train_id        INT,
    route_id        INT,
    travel_date     DATE,
    seat_type       ENUM('GENERAL','SLEEPER','AC') NOT NULL,
    passenger_count INT NOT NULL,
    pnr             VARCHAR(15) UNIQUE,
    status          VARCHAR(20) DEFAULT 'CONFIRMED',
    cancel_time     DATETIME DEFAULT NULL,
    FOREIGN KEY (passenger_id) REFERENCES passenger(passenger_id),
    FOREIGN KEY (train_id)     REFERENCES train(train_id),
    FOREIGN KEY (route_id)     REFERENCES route(route_id)
);


/* ------------------------
   PAYMENT
   One payment per booking
-------------------------*/
CREATE TABLE payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    mode       ENUM('UPI','CASH'),
    amount     DECIMAL(10,2),
    status     ENUM('SUCCESS','FAILED'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id)
);


/* ------------------------
   EMPLOYEE–TRAIN ASSIGNMENT
   Which employee works on which train
-------------------------*/
CREATE TABLE IF NOT EXISTS employee_train_assignment (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    emp_id      INT NOT NULL,
    train_id    INT NOT NULL,
    assigned_by INT,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_emp_train (emp_id, train_id),
    FOREIGN KEY (emp_id)      REFERENCES employee(emp_id),
    FOREIGN KEY (train_id)    REFERENCES train(train_id),
    FOREIGN KEY (assigned_by) REFERENCES employee(emp_id)
);


/* ------------------------
   WORK SCHEDULE
   Maintains employee shift data
-------------------------*/
CREATE TABLE IF NOT EXISTS work_schedule (
    shift_id     INT AUTO_INCREMENT PRIMARY KEY,
    emp_id       INT NOT NULL,
    train_id     INT,
    shift_date   DATE NOT NULL,
    start_time   TIME NOT NULL,
    end_time     TIME NOT NULL,
    role_on_shift VARCHAR(50),
    notes        VARCHAR(255),
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_emp_date (emp_id, shift_date),
    FOREIGN KEY (emp_id)   REFERENCES employee(emp_id),
    FOREIGN KEY (train_id) REFERENCES train(train_id)
);


/* ------------------------
   SUPERVISOR REPORT
   Issues raised by employees
-------------------------*/
CREATE TABLE IF NOT EXISTS supervisor_report (
    report_id     INT AUTO_INCREMENT PRIMARY KEY,
    emp_id        INT NOT NULL,
    supervisor_id INT NOT NULL,
    subject       VARCHAR(120) NOT NULL,
    message       TEXT NOT NULL,
    status        ENUM('NEW','SEEN','RESOLVED') DEFAULT 'NEW',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id)        REFERENCES employee(emp_id),
    FOREIGN KEY (supervisor_id) REFERENCES employee(emp_id)
);
