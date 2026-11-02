-- Views used by Tableau (connect Tableau to these) and by the analysis queries
USE hospital_db;

-- One flat row per admission with every field Tableau needs
CREATE OR REPLACE VIEW vw_admission_details AS
SELECT
    a.admission_id,
    a.admission_date,
    a.discharge_date,
    DATE_FORMAT(a.admission_date, '%Y-%m-01')            AS admission_month,
    YEAR(a.admission_date)                               AS admission_year,
    MONTHNAME(a.admission_date)                          AS month_name,
    DAYNAME(a.admission_date)                            AS weekday_name,
    DATEDIFF(a.discharge_date, a.admission_date)         AS stay_days,
    a.admission_type,
    a.diagnosis,
    a.ward_type,
    a.discharge_status,
    a.bill_amount,
    p.patient_id,
    p.patient_name,
    p.gender                                             AS patient_gender,
    p.city,
    p.blood_group,
    TIMESTAMPDIFF(YEAR, p.dob, a.admission_date)         AS patient_age,
    CASE
        WHEN TIMESTAMPDIFF(YEAR, p.dob, a.admission_date) < 15 THEN '0-14'
        WHEN TIMESTAMPDIFF(YEAR, p.dob, a.admission_date) < 35 THEN '15-34'
        WHEN TIMESTAMPDIFF(YEAR, p.dob, a.admission_date) < 60 THEN '35-59'
        ELSE '60+'
    END                                                  AS age_group,
    d.department_id,
    d.department_name,
    d.total_beds,
    doc.doctor_id,
    doc.doctor_name,
    doc.specialization
FROM admissions a
JOIN patients    p   ON p.patient_id    = a.patient_id
JOIN departments d   ON d.department_id = a.department_id
JOIN doctors     doc ON doc.doctor_id   = a.doctor_id;

-- Department-wise statistics
CREATE OR REPLACE VIEW vw_department_stats AS
SELECT
    d.department_id,
    d.department_name,
    d.total_beds,
    COUNT(a.admission_id)                                                   AS total_admissions,
    SUM(a.discharge_date IS NOT NULL)                                       AS total_discharges,
    ROUND(AVG(DATEDIFF(a.discharge_date, a.admission_date)), 2)             AS avg_stay_days,
    ROUND(SUM(a.bill_amount), 2)                                            AS total_revenue,
    ROUND(AVG(a.bill_amount), 2)                                            AS avg_bill,
    SUM(a.discharge_status = 'Deceased')                                    AS deaths,
    ROUND(100 * SUM(a.discharge_status = 'Deceased') / COUNT(a.admission_id), 2) AS mortality_pct
FROM departments d
LEFT JOIN admissions a ON a.department_id = d.department_id
GROUP BY d.department_id, d.department_name, d.total_beds;

-- Monthly patient trend
CREATE OR REPLACE VIEW vw_monthly_trend AS
SELECT
    DATE_FORMAT(admission_date, '%Y-%m-01')                     AS month_start,
    COUNT(*)                                                    AS admissions,
    SUM(discharge_date IS NOT NULL)                             AS discharges,
    ROUND(AVG(DATEDIFF(discharge_date, admission_date)), 2)     AS avg_stay_days,
    ROUND(SUM(bill_amount), 2)                                  AS revenue
FROM admissions
GROUP BY DATE_FORMAT(admission_date, '%Y-%m-01');

-- Average stay broken down by department and admission type
CREATE OR REPLACE VIEW vw_avg_stay AS
SELECT
    d.department_name,
    a.admission_type,
    COUNT(*)                                                    AS discharged_patients,
    ROUND(AVG(DATEDIFF(a.discharge_date, a.admission_date)), 2) AS avg_stay_days,
    MIN(DATEDIFF(a.discharge_date, a.admission_date))           AS min_stay_days,
    MAX(DATEDIFF(a.discharge_date, a.admission_date))           AS max_stay_days
FROM admissions a
JOIN departments d ON d.department_id = a.department_id
WHERE a.discharge_date IS NOT NULL
GROUP BY d.department_name, a.admission_type;
