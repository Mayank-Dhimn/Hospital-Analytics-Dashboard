"""Creates data/tableau_admissions_flat.csv - same columns as the MySQL view vw_admission_details.
Use it in Tableau if you do not want to connect to MySQL directly."""
import os
import pandas as pd

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
a = pd.read_csv(f'{root}/admissions.csv', parse_dates=['admission_date', 'discharge_date'])
p = pd.read_csv(f'{root}/patients.csv', parse_dates=['dob'])
d = pd.read_csv(f'{root}/departments.csv')
c = pd.read_csv(f'{root}/doctors.csv')

m = (a.merge(p[['patient_id', 'patient_name', 'gender', 'city', 'blood_group', 'dob']], on='patient_id')
      .merge(d[['department_id', 'department_name', 'total_beds']], on='department_id', validate='many_to_one')
      .merge(c[['doctor_id', 'doctor_name', 'specialization']], on='doctor_id', validate='many_to_one'))
if len(m) != len(a):
    raise ValueError(f'Export join lost admission rows: {len(a)} source rows, {len(m)} exported rows')
if m['admission_id'].duplicated().any():
    raise ValueError('Export contains duplicate admission_id values')
m = m.rename(columns={'gender': 'patient_gender'})
m['admission_month'] = m.admission_date.dt.to_period('M').dt.start_time.dt.date
m['admission_year'] = m.admission_date.dt.year
m['month_name'] = m.admission_date.dt.month_name()
m['weekday_name'] = m.admission_date.dt.day_name()
m['stay_days'] = (m.discharge_date - m.admission_date).dt.days
if m['stay_days'].dropna().lt(0).any():
    raise ValueError('Export contains discharge dates before admission dates')
age = m.admission_date.dt.year - m.dob.dt.year - ((m.admission_date.dt.month * 100 + m.admission_date.dt.day) <
                                                  (m.dob.dt.month * 100 + m.dob.dt.day))
m['patient_age'] = age
if not m['patient_age'].between(0, 120).all():
    raise ValueError('Export contains missing or invalid patient ages (expected 0-120 at admission)')
m['age_group'] = pd.cut(age, [-1, 14, 34, 59, 200], labels=['0-14', '15-34', '35-59', '60+']).astype(str)
if m['age_group'].eq('nan').any():
    raise ValueError('Export could not assign an age_group to every admission')
m = m.drop(columns=['dob'])
m.to_csv(f'{root}/tableau_admissions_flat.csv', index=False)
print(len(m), 'rows ->', 'data/tableau_admissions_flat.csv')
