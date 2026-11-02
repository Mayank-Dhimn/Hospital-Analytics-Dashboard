"""
Generates a synthetic (fake) hospital dataset.
Outputs: data/*.csv  and  sql/03_data.sql   (run from the project root)
All names, phone numbers and records are randomly generated - no real patients.
"""
import csv
import os
import random
from datetime import date, timedelta

random.seed(2026)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DATA = os.path.join(ROOT, 'data')
SQLD = os.path.join(ROOT, 'sql')
os.makedirs(DATA, exist_ok=True)
os.makedirs(SQLD, exist_ok=True)

START, END = date(2025, 1, 1), date(2026, 10, 31)

FIRST_M = ['Aarav', 'Vivaan', 'Aditya', 'Arjun', 'Rohan', 'Karan', 'Manish', 'Harpreet', 'Gurpreet', 'Rahul',
           'Amit', 'Sandeep', 'Vikas', 'Naveen', 'Deepak', 'Mohit', 'Ankit', 'Suresh', 'Rajesh', 'Jaspreet',
           'Sahil', 'Pankaj', 'Yash', 'Nikhil', 'Tarun']
FIRST_F = ['Ananya', 'Diya', 'Priya', 'Neha', 'Simran', 'Kavita', 'Pooja', 'Riya', 'Sneha', 'Manpreet',
           'Harleen', 'Anjali', 'Meera', 'Komal', 'Nisha', 'Swati', 'Jyoti', 'Ritu', 'Sunita', 'Preeti',
           'Kiran', 'Isha', 'Tanvi', 'Aman', 'Ravneet']
LAST = ['Sharma', 'Singh', 'Kaur', 'Verma', 'Gupta', 'Kumar', 'Mehta', 'Bansal', 'Chopra', 'Arora',
        'Sethi', 'Bhatia', 'Malhotra', 'Gill', 'Sandhu', 'Dhillon', 'Jain', 'Aggarwal', 'Thakur', 'Rana']
CITIES = ['Ludhiana', 'Chandigarh', 'Jalandhar', 'Amritsar', 'Patiala', 'Mohali', 'Bathinda', 'Khanna']
CITY_W = [38, 14, 12, 10, 8, 8, 5, 5]
BLOOD = ['O+', 'A+', 'B+', 'AB+', 'O-', 'A-', 'B-', 'AB-']
BLOOD_W = [36, 22, 28, 7, 2, 2, 2, 1]

# name, floor, beds, avg stay (days), stay spread, avg bill, share of admissions, diagnoses
DEPTS = [
    ('Cardiology',       2, 40, 5.0, 2.0, 95000, 14, ['Heart Attack', 'Angina', 'Heart Failure', 'Arrhythmia', 'Hypertension Crisis']),
    ('Orthopedics',      3, 45, 6.0, 2.5, 120000, 15, ['Fracture', 'Joint Replacement', 'Ligament Injury', 'Spinal Disc Issue']),
    ('Neurology',        4, 30, 6.5, 3.0, 85000, 8,  ['Stroke', 'Epilepsy', 'Migraine Crisis', 'Neuropathy']),
    ('Pediatrics',       1, 35, 3.5, 1.5, 22000, 14, ['Pneumonia', 'Viral Fever', 'Gastroenteritis', 'Asthma']),
    ('General Medicine', 1, 60, 4.0, 1.8, 28000, 22, ['Typhoid', 'Dengue', 'Diabetes Complication', 'Infection', 'Jaundice']),
    ('Gynecology',       2, 30, 3.0, 1.2, 55000, 9,  ['Normal Delivery', 'C-Section', 'Fibroid', 'PCOS Complication']),
    ('Emergency',        0, 25, 2.0, 1.2, 30000, 10, ['Road Accident', 'Poisoning', 'Burns', 'Acute Abdomen']),
    ('Oncology',         5, 25, 9.0, 4.0, 210000, 8,  ['Chemotherapy Cycle', 'Tumor Surgery', 'Radiation Therapy', 'Palliative Care']),
]
DOC_PER_DEPT = [5, 5, 3, 4, 6, 3, 4, 3]  # 33 doctors
SPECIAL = {
    'Cardiology': ['Interventional Cardiologist', 'Cardiac Surgeon', 'Cardiologist'],
    'Orthopedics': ['Orthopedic Surgeon', 'Spine Specialist', 'Sports Injury Specialist'],
    'Neurology': ['Neurologist', 'Neurosurgeon'],
    'Pediatrics': ['Pediatrician', 'Neonatologist'],
    'General Medicine': ['Physician', 'Diabetologist', 'Infectious Disease Specialist'],
    'Gynecology': ['Gynecologist', 'Obstetrician'],
    'Emergency': ['Emergency Physician', 'Trauma Specialist'],
    'Oncology': ['Medical Oncologist', 'Surgical Oncologist', 'Radiation Oncologist'],
}
MONTH_W = {1: 1.10, 2: 0.95, 3: 0.95, 4: 0.90, 5: 0.90, 6: 0.95, 7: 1.10, 8: 1.20, 9: 1.25, 10: 1.10, 11: 1.0, 12: 1.05}
# Dengue / viral season (Aug-Oct) pushes General Medicine & Pediatrics up
SEASON_DEPT = {('General Medicine', 8): 1.4, ('General Medicine', 9): 1.6, ('General Medicine', 10): 1.4,
               ('Pediatrics', 8): 1.3, ('Pediatrics', 9): 1.4, ('Pediatrics', 10): 1.2,
               ('Orthopedics', 1): 1.2, ('Orthopedics', 12): 1.2, ('Cardiology', 12): 1.25, ('Cardiology', 1): 1.25}


def wchoice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]


def person_name(gender):
    return f"{random.choice(FIRST_M if gender == 'Male' else FIRST_F)} {random.choice(LAST)}"


def phone():
    return '9' + ''.join(random.choice('0123456789') for _ in range(9))


# ---------- departments ----------
departments = []
for i, d in enumerate(DEPTS, 1):
    departments.append({'department_id': i, 'department_name': d[0], 'floor_no': d[1], 'total_beds': d[2]})

# ---------- doctors ----------
doctors = []
did = 1
used = set()
for di, (dept, n) in enumerate(zip(DEPTS, DOC_PER_DEPT), 1):
    for k in range(n):
        gender = random.choice(['Male', 'Female'])
        while True:
            nm = 'Dr. ' + person_name(gender)
            if nm not in used:
                used.add(nm)
                break
        doctors.append({
            'doctor_id': did, 'doctor_name': nm, 'gender': gender, 'department_id': di,
            'specialization': SPECIAL[dept[0]][k % len(SPECIAL[dept[0]])],
            'experience_years': random.randint(4, 30), 'phone': phone()})
        did += 1
docs_by_dept = {}
for d in doctors:
    docs_by_dept.setdefault(d['department_id'], []).append(d)

# ---------- admissions first (drives patients' registration dates) ----------
days = (END - START).days + 1
day_weights = []
for i in range(days):
    dt = START + timedelta(days=i)
    w = MONTH_W[dt.month] * (0.85 if dt.weekday() == 6 else 1.0) * (1 + 0.15 * (i / days))  # slow growth
    day_weights.append(w)

N_ADM = 3400
N_PAT = 1900
dept_share = [d[6] for d in DEPTS]

patient_pool = []  # (patient_id, gender, dob)
patients = []
for pid in range(1, N_PAT + 1):
    gender = wchoice(['Male', 'Female'], [52, 48])
    age_band = wchoice(['child', 'young', 'adult', 'senior'], [14, 24, 37, 25])
    age = {'child': random.randint(0, 14), 'young': random.randint(15, 35),
           'adult': random.randint(36, 59), 'senior': random.randint(60, 90)}[age_band]
    dob = date(START.year, START.month, START.day) - timedelta(days=age * 365 + random.randint(0, 364))
    patients.append({'patient_id': pid, 'patient_name': person_name(gender), 'gender': gender, 'dob': dob,
                     'blood_group': wchoice(BLOOD, BLOOD_W), 'phone': phone(),
                     'city': wchoice(CITIES, CITY_W), 'registration_date': None, 'age_band': age_band})

# Pediatrics gets children, Gynecology gets women of childbearing age, others anyone
kids = [p for p in patients if p['age_band'] == 'child']
women = [p for p in patients if p['gender'] == 'Female' and p['age_band'] in ('young', 'adult')]
seniors = [p for p in patients if p['age_band'] in ('adult', 'senior')]

admissions = []
first_seen = {}
for aid in range(1, N_ADM + 1):
    # choose admission date
    adate = START + timedelta(days=random.choices(range(days), weights=day_weights, k=1)[0])
    # department weighted by share & season
    ws = [dept_share[i] * SEASON_DEPT.get((DEPTS[i][0], adate.month), 1.0) for i in range(len(DEPTS))]
    di = random.choices(range(len(DEPTS)), weights=ws, k=1)[0]
    dname = DEPTS[di][0]
    if dname == 'Pediatrics':
        pat = random.choice(kids)
    elif dname == 'Gynecology':
        pat = random.choice(women)
    elif dname in ('Cardiology', 'Oncology', 'Neurology'):
        pat = random.choice(seniors)
    else:
        pat = random.choice(patients)
    doc = random.choice(docs_by_dept[di + 1])

    if dname == 'Emergency':
        atype = wchoice(['Emergency', 'Referral'], [92, 8])
    else:
        atype = wchoice(['Emergency', 'Planned', 'Referral'], [30, 55, 15])

    mean, sd = DEPTS[di][3], DEPTS[di][4]
    los = max(1, round(random.gauss(mean, sd)))
    if atype == 'Emergency':
        los = max(1, los + random.choice([0, 0, 1]))
    ddate = adate + timedelta(days=los)

    status = wchoice(['Recovered', 'Referred', 'LAMA', 'Deceased'], [90.5, 4.5, 3.5, 1.5])
    if dname == 'Oncology':
        status = wchoice(['Recovered', 'Referred', 'LAMA', 'Deceased'], [78, 6, 6, 10])
    if dname == 'Emergency':
        status = wchoice(['Recovered', 'Referred', 'LAMA', 'Deceased'], [82, 8, 5, 5])
    ward = wchoice(['General', 'Semi-Private', 'Private', 'ICU'], [48, 24, 18, 10])
    if dname in ('Emergency', 'Cardiology') and random.random() < 0.25:
        ward = 'ICU'
    mult = {'General': 0.85, 'Semi-Private': 1.0, 'Private': 1.3, 'ICU': 1.7}[ward]
    bill = DEPTS[di][5] * mult * (los / mean) ** 0.7 * random.uniform(0.7, 1.35)
    bill = int(round(bill / 100.0) * 100)

    if ddate > END:  # still admitted at the end of the dataset
        ddate, status, bill_val = None, 'Admitted', None
    else:
        bill_val = bill
    admissions.append({
        'admission_id': aid, 'patient_id': pat['patient_id'], 'doctor_id': doc['doctor_id'],
        'department_id': di + 1, 'admission_date': adate, 'discharge_date': ddate,
        'admission_type': atype, 'diagnosis': random.choice(DEPTS[di][7]), 'ward_type': ward,
        'discharge_status': status, 'bill_amount': bill_val})
    first_seen[pat['patient_id']] = min(first_seen.get(pat['patient_id'], adate), adate)

admissions.sort(key=lambda a: (a['admission_date'], a['admission_id']))
for new_id, a in enumerate(admissions, 1):
    a['admission_id'] = new_id

# registration date: on or before first admission (some earlier); patients never admitted register randomly
for p in patients:
    fs = first_seen.get(p['patient_id'])
    if fs:
        p['registration_date'] = fs - timedelta(days=random.choice([0, 0, 0, 0, 1, 2, 5, 14, 40]))
        if p['registration_date'] < START:
            p['registration_date'] = START
    else:
        p['registration_date'] = START + timedelta(days=random.randint(0, days - 1))
    del p['age_band']

# ---------- write CSVs ----------
def write_csv(name, rows, cols):
    with open(os.path.join(DATA, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow(['' if r[c] is None else (r[c].isoformat() if isinstance(r[c], date) else r[c]) for c in cols])

DEPT_COLS = ['department_id', 'department_name', 'floor_no', 'total_beds']
DOC_COLS = ['doctor_id', 'doctor_name', 'gender', 'department_id', 'specialization', 'experience_years', 'phone']
PAT_COLS = ['patient_id', 'patient_name', 'gender', 'dob', 'blood_group', 'phone', 'city', 'registration_date']
ADM_COLS = ['admission_id', 'patient_id', 'doctor_id', 'department_id', 'admission_date', 'discharge_date',
            'admission_type', 'diagnosis', 'ward_type', 'discharge_status', 'bill_amount']
write_csv('departments.csv', departments, DEPT_COLS)
write_csv('doctors.csv', doctors, DOC_COLS)
write_csv('patients.csv', patients, PAT_COLS)
write_csv('admissions.csv', admissions, ADM_COLS)


# ---------- write SQL inserts ----------
def sql_val(v):
    if v is None:
        return 'NULL'
    if isinstance(v, date):
        return f"'{v.isoformat()}'"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def inserts(table, rows, cols, batch=200):
    out = []
    for i in range(0, len(rows), batch):
        chunk = rows[i:i + batch]
        vals = ',\n'.join('(' + ', '.join(sql_val(r[c]) for c in cols) + ')' for r in chunk)
        out.append(f"INSERT INTO {table} ({', '.join(cols)}) VALUES\n{vals};\n")
    return '\n'.join(out)


with open(os.path.join(SQLD, '03_data.sql'), 'w', encoding='utf-8') as f:
    f.write('-- Synthetic data for the hospital_db database (generated by scripts/generate_data.py)\n')
    f.write('USE hospital_db;\n\nSET FOREIGN_KEY_CHECKS = 0;\n')
    f.write('TRUNCATE TABLE admissions;\nTRUNCATE TABLE patients;\nTRUNCATE TABLE doctors;\nTRUNCATE TABLE departments;\n')
    f.write('SET FOREIGN_KEY_CHECKS = 1;\n\n')
    f.write(inserts('departments', departments, DEPT_COLS) + '\n')
    f.write(inserts('doctors', doctors, DOC_COLS) + '\n')
    f.write(inserts('patients', patients, PAT_COLS) + '\n')
    f.write(inserts('admissions', admissions, ADM_COLS))

print('departments', len(departments), '| doctors', len(doctors), '| patients', len(patients),
      '| admissions', len(admissions))
print('still admitted:', sum(1 for a in admissions if a['discharge_date'] is None))
