-- Analysis queries (MySQL 8.0+). Each one answers a question from the project objectives.
USE hospital_db;

-- ==========================================================
-- 1. PATIENT REGISTRATION RECORDS
-- ==========================================================

-- 1.1 Latest 20 registered patients
SELECT patient_id, patient_name, gender, TIMESTAMPDIFF(YEAR, dob, CURDATE()) AS age_today,
       blood_group, city, registration_date
FROM patients
ORDER BY registration_date DESC, patient_id DESC
LIMIT 20;

-- 1.2 New registrations per month
SELECT DATE_FORMAT(registration_date, '%Y-%m') AS month, COUNT(*) AS new_patients
FROM patients
GROUP BY DATE_FORMAT(registration_date, '%Y-%m')
ORDER BY month;

-- 1.3 Patients by gender and by city
SELECT gender, COUNT(*) AS patients FROM patients GROUP BY gender;
SELECT city, COUNT(*) AS patients FROM patients GROUP BY city ORDER BY patients DESC;

-- ==========================================================
-- 2. DOCTOR AND DEPARTMENT DETAILS
-- ==========================================================

-- 2.1 Doctors with their department, specialization and experience
SELECT doc.doctor_id, doc.doctor_name, d.department_name, doc.specialization, doc.experience_years
FROM doctors doc
JOIN departments d ON d.department_id = doc.department_id
ORDER BY d.department_name, doc.experience_years DESC;

-- 2.2 Doctors per department and average experience
SELECT d.department_name, COUNT(doc.doctor_id) AS doctors, ROUND(AVG(doc.experience_years), 1) AS avg_experience
FROM departments d
LEFT JOIN doctors doc ON doc.department_id = d.department_id
GROUP BY d.department_name
ORDER BY doctors DESC;

-- 2.3 Top 10 doctors by patients treated
SELECT doc.doctor_name, d.department_name, COUNT(*) AS patients_treated,
       ROUND(AVG(DATEDIFF(a.discharge_date, a.admission_date)), 2) AS avg_stay_days
FROM admissions a
JOIN doctors doc ON doc.doctor_id = a.doctor_id
JOIN departments d ON d.department_id = a.department_id
GROUP BY doc.doctor_id, doc.doctor_name, d.department_name
ORDER BY patients_treated DESC
LIMIT 10;

-- ==========================================================
-- 3. PATIENT ADMISSION AND DISCHARGE ANALYSIS
-- ==========================================================

-- 3.1 Overall KPIs
SELECT COUNT(*)                                   AS total_admissions,
       SUM(discharge_date IS NOT NULL)            AS total_discharges,
       SUM(discharge_status = 'Admitted')         AS currently_admitted,
       ROUND(AVG(DATEDIFF(discharge_date, admission_date)), 2) AS avg_stay_days,
       ROUND(SUM(bill_amount), 0)                 AS total_revenue
FROM admissions;

-- 3.2 Admission type split
SELECT admission_type, COUNT(*) AS admissions,
       ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM admissions), 1) AS pct
FROM admissions
GROUP BY admission_type;

-- 3.3 Discharge outcome split
SELECT discharge_status, COUNT(*) AS patients,
       ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM admissions), 2) AS pct
FROM admissions
GROUP BY discharge_status
ORDER BY patients DESC;

-- 3.4 Top 10 diagnoses
SELECT diagnosis, COUNT(*) AS cases FROM admissions GROUP BY diagnosis ORDER BY cases DESC LIMIT 10;

-- 3.5 Admissions by age group and gender
SELECT age_group, patient_gender, COUNT(*) AS admissions
FROM vw_admission_details
GROUP BY age_group, patient_gender
ORDER BY age_group, patient_gender;

-- 3.6 Patients readmitted more than once (repeat patients)
SELECT p.patient_id, p.patient_name, COUNT(*) AS admissions
FROM admissions a
JOIN patients p ON p.patient_id = a.patient_id
GROUP BY p.patient_id, p.patient_name
HAVING COUNT(*) >= 3
ORDER BY admissions DESC, p.patient_id
LIMIT 20;

-- 3.7 Patients currently admitted
SELECT a.admission_id, p.patient_name, d.department_name, a.admission_date,
       DATEDIFF(CURDATE(), a.admission_date) AS days_since_admission
FROM admissions a
JOIN patients p ON p.patient_id = a.patient_id
JOIN departments d ON d.department_id = a.department_id
WHERE a.discharge_date IS NULL
ORDER BY a.admission_date;

-- ==========================================================
-- 4. DEPARTMENT-WISE PATIENT STATISTICS
-- ==========================================================

-- 4.1 Full department summary (uses the view)
SELECT * FROM vw_department_stats ORDER BY total_admissions DESC;

-- 4.2 Share of total admissions per department
SELECT department_name, total_admissions,
       ROUND(100 * total_admissions / SUM(total_admissions) OVER (), 1) AS pct_of_total
FROM vw_department_stats
ORDER BY total_admissions DESC;

-- 4.3 Department x ward type matrix
SELECT department_name,
       SUM(ward_type = 'General')      AS general,
       SUM(ward_type = 'Semi-Private') AS semi_private,
       SUM(ward_type = 'Private')      AS private,
       SUM(ward_type = 'ICU')          AS icu
FROM vw_admission_details
GROUP BY department_name;

-- ==========================================================
-- 5. MONTHLY PATIENT TRENDS
-- ==========================================================

-- 5.1 Monthly admissions with month-over-month growth
SELECT month_start, admissions,
       LAG(admissions) OVER (ORDER BY month_start) AS prev_month,
       ROUND(100 * (admissions - LAG(admissions) OVER (ORDER BY month_start))
             / LAG(admissions) OVER (ORDER BY month_start), 1) AS mom_growth_pct
FROM vw_monthly_trend
ORDER BY month_start;

-- 5.2 Seasonal pattern: average admissions per calendar month across years
SELECT MONTH(admission_date) AS month_no, MONTHNAME(admission_date) AS month_name,
       COUNT(*) AS admissions
FROM admissions
GROUP BY MONTH(admission_date), MONTHNAME(admission_date)
ORDER BY month_no;

-- 5.3 Monthly admissions by department (pivot-style)
SELECT DATE_FORMAT(a.admission_date, '%Y-%m') AS month,
       SUM(d.department_name = 'Cardiology')       AS cardiology,
       SUM(d.department_name = 'Orthopedics')      AS orthopedics,
       SUM(d.department_name = 'Neurology')        AS neurology,
       SUM(d.department_name = 'Pediatrics')       AS pediatrics,
       SUM(d.department_name = 'General Medicine') AS general_medicine,
       SUM(d.department_name = 'Gynecology')       AS gynecology,
       SUM(d.department_name = 'Emergency')        AS emergency,
       SUM(d.department_name = 'Oncology')         AS oncology
FROM admissions a
JOIN departments d ON d.department_id = a.department_id
GROUP BY DATE_FORMAT(a.admission_date, '%Y-%m')
ORDER BY month;

-- 5.4 Busiest weekday
SELECT DAYNAME(admission_date) AS weekday, COUNT(*) AS admissions
FROM admissions
GROUP BY DAYOFWEEK(admission_date), DAYNAME(admission_date)
ORDER BY DAYOFWEEK(admission_date);

-- ==========================================================
-- 6. AVERAGE HOSPITAL STAY ANALYSIS
-- ==========================================================

-- 6.1 Average stay by department (discharged patients only)
SELECT department_name, ROUND(AVG(stay_days), 2) AS avg_stay_days, MAX(stay_days) AS longest_stay
FROM vw_admission_details
WHERE stay_days IS NOT NULL
GROUP BY department_name
ORDER BY avg_stay_days DESC;

-- 6.2 Average stay by department and admission type
SELECT * FROM vw_avg_stay ORDER BY department_name, admission_type;

-- 6.3 Length-of-stay buckets
SELECT CASE WHEN stay_days <= 2 THEN '1-2 days'
            WHEN stay_days <= 5 THEN '3-5 days'
            WHEN stay_days <= 9 THEN '6-9 days'
            ELSE '10+ days' END AS stay_bucket,
       COUNT(*) AS patients
FROM vw_admission_details
WHERE stay_days IS NOT NULL
GROUP BY stay_bucket
ORDER BY MIN(stay_days);

-- 6.4 Average stay by age group
SELECT age_group, ROUND(AVG(stay_days), 2) AS avg_stay_days, COUNT(*) AS patients
FROM vw_admission_details
WHERE stay_days IS NOT NULL
GROUP BY age_group
ORDER BY age_group;

-- 6.5 Average stay by ward type
SELECT ward_type, ROUND(AVG(stay_days), 2) AS avg_stay_days, ROUND(AVG(bill_amount), 0) AS avg_bill
FROM vw_admission_details
WHERE stay_days IS NOT NULL
GROUP BY ward_type
ORDER BY avg_stay_days DESC;

-- 6.6 Department performance vs the hospital-wide average stay
SELECT department_name, avg_stay_days,
       ROUND((SELECT AVG(DATEDIFF(discharge_date, admission_date)) FROM admissions), 2) AS hospital_avg,
       CASE WHEN avg_stay_days > (SELECT AVG(DATEDIFF(discharge_date, admission_date)) FROM admissions)
            THEN 'Above average' ELSE 'Below average' END AS comparison
FROM vw_department_stats
ORDER BY avg_stay_days DESC;
