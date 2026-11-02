-- Hospital Management & Healthcare Analytics - database schema (MySQL 8.0+)
-- Run order: 01_schema.sql -> 02_views.sql -> 03_data.sql -> 04_analysis_queries.sql

DROP DATABASE IF EXISTS hospital_db;
CREATE DATABASE hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospital_db;

CREATE TABLE departments (
    department_id   INT PRIMARY KEY,
    department_name VARCHAR(60) NOT NULL UNIQUE,
    floor_no        INT NOT NULL,
    total_beds      INT NOT NULL CHECK (total_beds > 0)
);

CREATE TABLE doctors (
    doctor_id        INT PRIMARY KEY,
    doctor_name      VARCHAR(100) NOT NULL,
    gender           ENUM('Male','Female') NOT NULL,
    department_id    INT NOT NULL,
    specialization   VARCHAR(80) NOT NULL,
    experience_years INT NOT NULL CHECK (experience_years >= 0),
    phone            VARCHAR(15),
    CONSTRAINT fk_doctor_dept FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE patients (
    patient_id        INT PRIMARY KEY,
    patient_name      VARCHAR(100) NOT NULL,
    gender            ENUM('Male','Female') NOT NULL,
    dob               DATE NOT NULL,
    blood_group       VARCHAR(3) NOT NULL,
    phone             VARCHAR(15),
    city              VARCHAR(60),
    registration_date DATE NOT NULL
);

CREATE TABLE admissions (
    admission_id     INT PRIMARY KEY,
    patient_id       INT NOT NULL,
    doctor_id        INT NOT NULL,
    department_id    INT NOT NULL,
    admission_date   DATE NOT NULL,
    discharge_date   DATE NULL,                       -- NULL = patient still admitted
    admission_type   ENUM('Emergency','Planned','Referral') NOT NULL,
    diagnosis        VARCHAR(100) NOT NULL,
    ward_type        ENUM('General','Semi-Private','Private','ICU') NOT NULL,
    discharge_status ENUM('Admitted','Recovered','Referred','LAMA','Deceased') NOT NULL,
    bill_amount      DECIMAL(12,2) NULL,
    CONSTRAINT fk_adm_patient FOREIGN KEY (patient_id)    REFERENCES patients(patient_id),
    CONSTRAINT fk_adm_doctor  FOREIGN KEY (doctor_id)     REFERENCES doctors(doctor_id),
    CONSTRAINT fk_adm_dept    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    CONSTRAINT chk_dates CHECK (discharge_date IS NULL OR discharge_date >= admission_date),
    INDEX idx_adm_date (admission_date),
    INDEX idx_adm_dept (department_id),
    INDEX idx_adm_patient (patient_id)
);
