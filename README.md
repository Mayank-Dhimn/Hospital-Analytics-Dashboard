# Hospital Management and Healthcare Analytics
**Hospital Patient Admission Analysis Dashboard** – Excel + MySQL + Tableau

## Objective
Analyze hospital operations and patient statistics: registrations, doctors and departments, admissions and
discharges, department-wise statistics, monthly trends and average length of stay.

> All data is **synthetic** (randomly generated, fixed seed). It contains no real patients.

## What is inside
```
HospitalAnalytics/
├── data/            CSVs: departments, doctors, patients, admissions (+ tableau_admissions_flat.csv)
├── sql/             01_schema.sql  02_views.sql  03_data.sql  04_analysis_queries.sql
├── excel/           Hospital_Analytics.xlsx  (data + formula-driven analysis + charts)
├── tableau/         Tableau_Dashboard_Guide.md  (step-by-step; save your .twbx here)
└── scripts/         generate_data.py  build_excel.py  export_tableau_csv.py
```

| Item | Size |
|---|---|
| Departments | 8 (Cardiology, Orthopedics, Neurology, Pediatrics, General Medicine, Gynecology, Emergency, Oncology) |
| Doctors | 33 |
| Patients | 1,900 |
| Admissions | 3,400 (Jan 2025 – Oct 2026; 24 patients still admitted) |

## Database design (MySQL `hospital_db`)
```
departments (department_id PK, department_name, floor_no, total_beds)
doctors     (doctor_id PK, doctor_name, gender, department_id FK, specialization, experience_years, phone)
patients    (patient_id PK, patient_name, gender, dob, blood_group, phone, city, registration_date)
admissions  (admission_id PK, patient_id FK, doctor_id FK, department_id FK, admission_date, discharge_date,
             admission_type, diagnosis, ward_type, discharge_status, bill_amount)
```
Relationships: a department has many doctors; a patient has many admissions; a doctor treats many admissions.
`discharge_date` is NULL while the patient is still admitted. Length of stay = `DATEDIFF(discharge_date, admission_date)`.

## How to run

### 1. MySQL (Workbench)
Open and execute the files **in this order** (File → Open SQL Script → lightning icon):
1. `sql/01_schema.sql` – creates database `hospital_db` and the 4 tables
2. `sql/02_views.sql` – creates the 4 reporting views
3. `sql/03_data.sql` – loads all the data (about 5,300 rows)
4. `sql/04_analysis_queries.sql` – run query by query (select a query → Ctrl+Enter)

Requires **MySQL 8.0+** (uses window functions and CHECK constraints).

### 2. Excel
Open `excel/Hospital_Analytics.xlsx`.
- **Dashboard** – KPI cards and 4 charts
- **Dept Analysis** – admissions, discharged, average stay, revenue and mortality per department
- **Monthly Trend** – admissions, discharges, average stay, revenue, MoM growth, 3-month moving average
- **Stay Analysis** – stay by department and admission type, stay buckets, age groups, outcomes
- **Departments / Doctors / Patients / Admissions** – raw data (Admissions has computed columns L:O)

Everything is a live formula (COUNTIFS / AVERAGEIFS / SUMIFS). Blue cells are editable inputs.

### 3. Tableau
Follow `tableau/Tableau_Dashboard_Guide.md`. Connect to the MySQL view `vw_admission_details`
or to `data/tableau_admissions_flat.csv`.

### Re-generating the data (optional)
```bash
python scripts/generate_data.py        # rewrites data/*.csv and sql/03_data.sql
python scripts/export_tableau_csv.py
python scripts/build_excel.py          # needs: pip install pandas openpyxl
python scripts/build_excel.py excel/Hospital_Analytics_Refreshed.xlsx  # optional output path
```

## Features mapped to the objectives
| Feature | Where |
|---|---|
| Patient registration records | `patients` table, Excel *Patients* sheet, queries 1.1–1.3, monthly registrations |
| Doctor and department details | `doctors` / `departments`, queries 2.1–2.3 |
| Admission and discharge analysis | `admissions`, queries 3.1–3.7, Excel KPIs and outcome table |
| Department-wise patient statistics | `vw_department_stats`, *Dept Analysis* sheet, queries 4.1–4.3 |
| Monthly patient trends | `vw_monthly_trend`, *Monthly Trend* sheet, queries 5.1–5.4 |
| Average hospital stay analysis | `vw_avg_stay`, *Stay Analysis* sheet, queries 6.1–6.6 |

## Key results (from this dataset)
- 3,400 admissions, average stay **4.9 days**, total billing about Rs 27.1 crore, overall mortality 2.5 %.
- Longest stay and highest mortality: **Oncology** (9.4 days, 11.9 %). Shortest stay: **Emergency** (2.4 days).
- Busiest department: **General Medicine** (24 % of admissions).
- Patients aged 60+ stay about 5.6 days versus 3.9 days for children.
- Admissions peak between July and October.
