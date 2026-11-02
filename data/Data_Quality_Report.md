# Tableau Admissions CSV: Data-Quality Report

Validated file: `tableau_admissions_flat.csv`  
Record level: one row per admission  
Validation date: 2026-11-02

## Result

**PASS after correction.** The export contains 3,400 rows and 26 columns. Admission IDs are unique, there are no
duplicate rows, ages are valid at admission, stays are non-negative, and every record has a valid age group. All
department, doctor, gender, admission type, ward type, and discharge status values are populated.

The only blank values are intentional for 24 active admissions: their discharge date, stay duration, and bill have
not yet been recorded. The dashboard should preserve these nulls. Revenue and average stay measures naturally exclude
them.

## Field inventory and missing values

The type column describes the value representation read from the CSV with pandas. Dates are stored as ISO
`YYYY-MM-DD` text in the CSV and should be changed to **Date** in Tableau.

| Field | CSV value type | Blank values |
|---|---|---:|
| `admission_id` | Integer | 0 |
| `patient_id` | Integer | 0 |
| `doctor_id` | Integer | 0 |
| `department_id` | Integer | 0 |
| `admission_date` | ISO date text | 0 |
| `discharge_date` | ISO date text | 24 |
| `admission_type` | Text | 0 |
| `diagnosis` | Text | 0 |
| `ward_type` | Text | 0 |
| `discharge_status` | Text | 0 |
| `bill_amount` | Decimal number | 24 |
| `patient_name` | Text | 0 |
| `patient_gender` | Text | 0 |
| `city` | Text | 0 |
| `blood_group` | Text | 0 |
| `department_name` | Text | 0 |
| `total_beds` | Integer | 0 |
| `doctor_name` | Text | 0 |
| `specialization` | Text | 0 |
| `admission_month` | ISO date text | 0 |
| `admission_year` | Integer | 0 |
| `month_name` | Text | 0 |
| `weekday_name` | Text | 0 |
| `stay_days` | Decimal number | 24 |
| `patient_age` | Integer | 0 |
| `age_group` | Text | 0 |

## Validation checks

| Check | Result |
|---|---|
| Row / column count | 3,400 / 26 |
| Duplicate rows / duplicate `admission_id` | 0 / 0 |
| Admission date range | 2025-01-01 to 2026-10-31 |
| `admission_month` date range | 2025-01-01 to 2026-10-01 |
| Invalid or negative patient ages | 0; range 0-92 at admission |
| Missing age groups | 0 |
| Discharge before admission | 0 |
| Negative stays / stay calculation mismatches | 0 / 0 |
| Negative bill amounts | 0 |
| Active-admission status/date mismatches | 0 |
| Admission rows lost or duplicated by export joins | 0 |
| Departments / doctors | 8 / 33 |
| Unique admitted patients / diagnoses | 1,557 / 34 |

Expected value categories:

- Gender: `Female`, `Male`
- Admission type: `Emergency`, `Planned`, `Referral`
- Ward type: `General`, `Semi-Private`, `Private`, `ICU`
- Discharge status: `Admitted`, `Recovered`, `Referred`, `LAMA`, `Deceased`

Discharge status counts: Recovered 3,001; Referred 155; LAMA 136; Deceased 84; Admitted 24.

## Tableau reference metrics

These are unfiltered values for checking the KPI calculations:

| Metric | Value |
|---|---:|
| Total admissions | 3,400 |
| Unique patients represented in the admissions CSV | 1,557 |
| Total billed revenue | Rs 270,719,700 |
| Average stay for discharged admissions | 4.87 days |
| Deceased admissions / mortality percentage | 84 / 2.47% |
| Currently admitted patients | 23 unique patients (24 active admissions) |
| Average patient age at admission | 42.60 years |

Notes: the separate source `patients.csv` has 1,900 registered people; 1,557 of them occur in the admissions file.
There are 24 active admission rows belonging to 23 unique patients. They are intentionally excluded from revenue and
average-stay calculations because their bills and discharge durations do not yet exist.

## Issue found and correction made

The original patient generator anchored birth dates to 2026-06-15 even though admissions start in January 2025. This
produced 35 negative ages and 35 missing age groups for early admissions. The generator now anchors the generated
birth date to the dataset's start date, preventing a patient from being born after an admission. The dataset was
regenerated with its fixed random seed, preserving its 3,400 admissions and 1,900 registered patients, then the
Tableau CSV was re-exported. The exporter now raises an error if its joins lose or duplicate admission rows, if a
stay is negative, or if an age or age group is invalid.

## Reproduce the corrected data and export

From the project root, run:

```text
python scripts/generate_data.py
python scripts/export_tableau_csv.py
```

`generate_data.py` also rewrites `sql/03_data.sql`, the generated seed script. This does not connect to or overwrite a
running MySQL database.
