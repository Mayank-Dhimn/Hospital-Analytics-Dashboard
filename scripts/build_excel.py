"""Builds excel/Hospital_Analytics.xlsx : data sheets + formula-driven analysis + charts."""
import os
import sys
from datetime import date
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DATA = os.path.join(ROOT, 'data')
if len(sys.argv) > 2:
    raise SystemExit('Usage: python scripts/build_excel.py [output_path]')
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) == 2 else os.path.join(ROOT, 'excel', 'Hospital_Analytics.xlsx')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

dep = pd.read_csv(os.path.join(DATA, 'departments.csv'))
doc = pd.read_csv(os.path.join(DATA, 'doctors.csv'))
pat = pd.read_csv(os.path.join(DATA, 'patients.csv'), parse_dates=['dob', 'registration_date'])
adm = pd.read_csv(os.path.join(DATA, 'admissions.csv'), parse_dates=['admission_date', 'discharge_date'])

NAVY, LIGHT, GREY = '1F3A5F', 'EAF0F8', 'F5F5F5'
F = 'Arial'
f_norm = Font(name=F, size=10)
f_bold = Font(name=F, size=10, bold=True)
f_head = Font(name=F, size=10, bold=True, color='FFFFFF')
f_title = Font(name=F, size=16, bold=True, color=NAVY)
f_sub = Font(name=F, size=10, italic=True, color='666666')
f_input = Font(name=F, size=10, color='0000FF')
fill_head = PatternFill('solid', fgColor=NAVY)
fill_light = PatternFill('solid', fgColor=LIGHT)
thin = Side(style='thin', color='BBBBBB')
border = Border(left=thin, right=thin, top=thin, bottom=thin)
DATE_FMT = 'dd-mmm-yyyy'

wb = Workbook()
ws_dash = wb.active
ws_dash.title = 'Dashboard'


def style_header(ws, row, ncols, start_col=1):
    for c in range(start_col, start_col + ncols):
        cell = ws.cell(row=row, column=c)
        cell.font, cell.fill, cell.border = f_head, fill_head, border
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)


def write_df(ws, df, date_cols=()):
    ws.append(list(df.columns))
    style_header(ws, 1, len(df.columns))
    for row in df.itertuples(index=False):
        vals = []
        for col, v in zip(df.columns, row):
            if pd.isna(v):
                vals.append(None)
            elif col in date_cols:
                vals.append(v.date())
            else:
                vals.append(v.item() if hasattr(v, 'item') else v)
        ws.append(vals)
    for r in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for c in r:
            c.font = f_norm
    for i, col in enumerate(df.columns, 1):
        letter = get_column_letter(i)
        width = max(len(str(col)), *(len(str(x)) for x in df[col].head(300))) + 3
        ws.column_dimensions[letter].width = min(max(width, 11), 32)
        if col in date_cols:
            for c in ws[letter][1:]:
                c.number_format = DATE_FMT
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions


# ------------------------------------------------------------------ data sheets
ws_dep = wb.create_sheet('Departments'); write_df(ws_dep, dep)
ws_doc = wb.create_sheet('Doctors'); write_df(ws_doc, doc)
ws_pat = wb.create_sheet('Patients'); write_df(ws_pat, pat, date_cols=('dob', 'registration_date'))
ws_adm = wb.create_sheet('Admissions')
write_df(ws_adm, adm, date_cols=('admission_date', 'discharge_date'))

NA = len(adm)            # admissions rows
NP = len(pat)
ND = len(dep)
LAST = NA + 1            # last data row on Admissions
PLAST = NP + 1

# computed columns on Admissions (L..O)
extra = ['department_name', 'stay_days', 'admit_month', 'patient_age']
for i, h in enumerate(extra, 12):
    ws_adm.cell(row=1, column=i, value=h)
style_header(ws_adm, 1, len(extra), start_col=12)
for r in range(2, LAST + 1):
    ws_adm.cell(row=r, column=12, value=f'=INDEX(Departments!$B$2:$B${ND+1},MATCH(D{r},Departments!$A$2:$A${ND+1},0))')
    ws_adm.cell(row=r, column=13, value=f'=IF(F{r}="","",F{r}-E{r})')
    ws_adm.cell(row=r, column=14, value=f'=DATE(YEAR(E{r}),MONTH(E{r}),1)')
    ws_adm.cell(row=r, column=15,
                value=f'=INT((E{r}-INDEX(Patients!$D$2:$D${PLAST},MATCH(B{r},Patients!$A$2:$A${PLAST},0)))/365.25)')
    ws_adm.cell(row=r, column=14).number_format = 'mmm-yyyy'
    for c in range(12, 16):
        ws_adm.cell(row=r, column=c).font = f_norm
for letter, w in zip('LMNO', (20, 11, 12, 12)):
    ws_adm.column_dimensions[letter].width = w
ws_adm.auto_filter.ref = f'A1:O{LAST}'

# short range helpers
R = lambda col: f'Admissions!${col}$2:${col}${LAST}'
DEPT, STAY, MONTH, AGE = R('L'), R('M'), R('N'), R('O')
ATYPE, STATUS, BILL, ADATE, DDATE, WARD = R('G'), R('J'), R('K'), R('E'), R('F'), R('I')


def title(ws, text, sub=None):
    ws['A1'] = text
    ws['A1'].font = f_title
    if sub:
        ws['A2'] = sub
        ws['A2'].font = f_sub


def table(ws, top, headers, rows_formulas, fmts=None, start_col=1):
    """headers: list; rows_formulas: list of lists (values or formulas)."""
    for j, h in enumerate(headers):
        ws.cell(row=top, column=start_col + j, value=h)
    style_header(ws, top, len(headers), start_col)
    for i, row in enumerate(rows_formulas, 1):
        for j, v in enumerate(row):
            c = ws.cell(row=top + i, column=start_col + j, value=v)
            c.font, c.border = f_norm, border
            if fmts and fmts[j]:
                c.number_format = fmts[j]
    return top + len(rows_formulas)


# ------------------------------------------------------------------ Department Analysis
ws_d = wb.create_sheet('Dept Analysis', 1)
title(ws_d, 'Department-wise Patient Statistics',
      'All figures are formulas over the Admissions sheet. Stay = discharge date - admission date (discharged patients only).')
hdr = ['Department', 'Total Beds', 'Admissions', 'Discharged', 'Avg Stay (days)', 'Total Revenue (Rs)',
       'Avg Bill (Rs)', 'Deaths', 'Mortality %', '% of All Admissions']
rows = []
for i in range(ND):
    r = 5 + i
    rows.append([
        f'=Departments!B{i+2}', f'=Departments!D{i+2}',
        f'=COUNTIFS({DEPT},A{r})',
        f'=COUNTIFS({DEPT},A{r},{STAY},">=0")',
        f'=AVERAGEIFS({STAY},{DEPT},A{r})',
        f'=SUMIFS({BILL},{DEPT},A{r})',
        f'=AVERAGEIFS({BILL},{DEPT},A{r})',
        f'=COUNTIFS({DEPT},A{r},{STATUS},"Deceased")',
        f'=IF(C{r}=0,0,H{r}/C{r})',
        f'=C{r}/$C${5+ND}'])
end = table(ws_d, 4, hdr, rows, [None, '0', '#,##0', '#,##0', '0.00', '#,##0', '#,##0', '0', '0.0%', '0.0%'])
tot = end + 1
ws_d.cell(row=tot, column=1, value='Hospital total')
ws_d.cell(row=tot, column=2, value=f'=SUM(B5:B{end})')
ws_d.cell(row=tot, column=3, value=f'=SUM(C5:C{end})')
ws_d.cell(row=tot, column=4, value=f'=SUM(D5:D{end})')
ws_d.cell(row=tot, column=5, value=f'=AVERAGE({STAY})')
ws_d.cell(row=tot, column=6, value=f'=SUM(F5:F{end})')
ws_d.cell(row=tot, column=7, value=f'=AVERAGE({BILL})')
ws_d.cell(row=tot, column=8, value=f'=SUM(H5:H{end})')
ws_d.cell(row=tot, column=9, value=f'=H{tot}/C{tot}')
ws_d.cell(row=tot, column=10, value=f'=SUM(J5:J{end})')
for c, fm in zip(range(1, 11), [None, '0', '#,##0', '#,##0', '0.00', '#,##0', '#,##0', '0', '0.0%', '0.0%']):
    cell = ws_d.cell(row=tot, column=c)
    cell.font, cell.fill, cell.border = f_bold, fill_light, border
    if fm:
        cell.number_format = fm
# ward type x department matrix
ws_d.cell(row=tot + 3, column=1, value='Admissions by Department and Ward Type').font = f_bold
wards = ['General', 'Semi-Private', 'Private', 'ICU']
mrows = []
for i in range(ND):
    r = tot + 5 + i
    mrows.append([f'=A{5+i}'] + [f'=COUNTIFS({DEPT},$A{r},{WARD},{get_column_letter(2+k)}${tot+4})' for k in range(4)]
                 + [f'=SUM(B{r}:E{r})'])
table(ws_d, tot + 4, ['Department'] + wards + ['Total'], mrows)
ws_d.column_dimensions['A'].width = 22
for c in 'BCDEFGHIJ':
    ws_d.column_dimensions[c].width = 15
ws_d.row_dimensions[4].height = 32
ws_d.freeze_panes = 'B5'
D_FIRST, D_LAST = 5, end

# ------------------------------------------------------------------ Monthly Trend
ws_m = wb.create_sheet('Monthly Trend', 2)
title(ws_m, 'Monthly Patient Trends', 'Month starts are inputs (blue); every other cell is a formula.')
months = pd.period_range(adm.admission_date.min(), adm.admission_date.max(), freq='M')
hdr = ['Month', 'Admissions', 'Discharges', 'Avg Stay (days)', 'Revenue (Rs)', 'New Registrations',
       'MoM Growth %', '3-Month Moving Avg']
mrows = []
for i, p in enumerate(months):
    r = 5 + i
    mrows.append([
        p.start_time.date(),
        f'=COUNTIFS({MONTH},A{r})',
        f'=COUNTIFS({DDATE},">="&A{r},{DDATE},"<"&EDATE(A{r},1))',
        f'=IFERROR(AVERAGEIFS({STAY},{MONTH},A{r}),0)',
        f'=SUMIFS({BILL},{MONTH},A{r})',
        f'=COUNTIFS(Patients!$H$2:$H${PLAST},">="&A{r},Patients!$H$2:$H${PLAST},"<"&EDATE(A{r},1))',
        '' if i == 0 else f'=IF(B{r-1}=0,0,(B{r}-B{r-1})/B{r-1})',
        '' if i < 2 else f'=AVERAGE(B{r-2}:B{r})'])
mend = table(ws_m, 4, hdr, mrows, ['mmm-yyyy', '#,##0', '#,##0', '0.00', '#,##0', '#,##0', '0.0%', '0.0'])
for r in range(5, mend + 1):
    ws_m.cell(row=r, column=1).font = f_input
ws_m.cell(row=mend + 2, column=1, value='Notes: (1) The last month may contain patients still admitted, so Discharges can lag Admissions. (2) Jan-2025 registrations include patients already on record when the data starts.').font = f_sub
ws_m.column_dimensions['A'].width = 12
for c in 'BCDEFGH':
    ws_m.column_dimensions[c].width = 16
ws_m.row_dimensions[4].height = 32
ws_m.freeze_panes = 'B5'
M_FIRST, M_LAST = 5, mend

# ------------------------------------------------------------------ Stay Analysis
ws_s = wb.create_sheet('Stay Analysis', 3)
title(ws_s, 'Average Hospital Stay Analysis', 'Average of (discharge date - admission date) for discharged patients.')
types = ['Emergency', 'Planned', 'Referral']
srows = []
for i in range(ND):
    r = 5 + i
    srows.append([f"='Dept Analysis'!A{5+i}"] +
                 [f'=IFERROR(AVERAGEIFS({STAY},{DEPT},$A{r},{ATYPE},{get_column_letter(2+k)}$4),"-")' for k in range(3)] +
                 [f'=IFERROR(AVERAGEIFS({STAY},{DEPT},$A{r}),0)',
                  f'=MAXIFS({STAY},{DEPT},$A{r})'.replace('MAXIFS', '_xlfn.MAXIFS')])
s_end = table(ws_s, 4, ['Department'] + types + ['All Types', 'Longest Stay (days)'], srows,
              [None, '0.00', '0.00', '0.00', '0.00', '0'])
ws_s.cell(row=s_end + 1, column=1, value='Hospital average')
for k in range(3):
    col = get_column_letter(2 + k)
    ws_s.cell(row=s_end + 1, column=2 + k, value=f'=AVERAGEIFS({STAY},{ATYPE},{col}$4)')
ws_s.cell(row=s_end + 1, column=5, value=f'=AVERAGE({STAY})')
ws_s.cell(row=s_end + 1, column=6, value=f'=MAX({STAY})')
for c in range(1, 7):
    cell = ws_s.cell(row=s_end + 1, column=c)
    cell.font, cell.fill, cell.border = f_bold, fill_light, border
    if c in (2, 3, 4, 5):
        cell.number_format = '0.00'

# stay buckets
top = s_end + 4
ws_s.cell(row=top - 1, column=1, value='Length-of-stay distribution (discharged patients)').font = f_bold
buckets = [('1-2 days', 1, 2), ('3-5 days', 3, 5), ('6-9 days', 6, 9), ('10+ days', 10, 9999)]
brows = []
for i, (lab, lo, hi) in enumerate(buckets):
    r = top + 1 + i
    brows.append([lab, lo, hi, f'=COUNTIFS({STAY},">="&B{r},{STAY},"<="&C{r})', f'=D{r}/SUM($D${top+1}:$D${top+4})'])
b_end = table(ws_s, top, ['Stay Bucket', 'From (days)', 'To (days)', 'Patients', '% of Discharged'], brows,
              [None, '0', '0', '#,##0', '0.0%'])
for r in range(top + 1, b_end + 1):
    ws_s.cell(row=r, column=2).font = f_input
    ws_s.cell(row=r, column=3).font = f_input

# age groups
top2 = b_end + 3
ws_s.cell(row=top2 - 1, column=1, value='Average stay by patient age group').font = f_bold
ages = [('0-14', 0, 14), ('15-34', 15, 34), ('35-59', 35, 59), ('60+', 60, 200)]
arows = []
for i, (lab, lo, hi) in enumerate(ages):
    r = top2 + 1 + i
    arows.append([lab, lo, hi, f'=COUNTIFS({AGE},">="&B{r},{AGE},"<="&C{r})',
                  f'=IFERROR(AVERAGEIFS({STAY},{AGE},">="&B{r},{AGE},"<="&C{r}),0)'])
a_end = table(ws_s, top2, ['Age Group', 'From (years)', 'To (years)', 'Admissions', 'Avg Stay (days)'], arows,
              [None, '0', '0', '#,##0', '0.00'])
for r in range(top2 + 1, a_end + 1):
    ws_s.cell(row=r, column=2).font = f_input
    ws_s.cell(row=r, column=3).font = f_input

# admission type + outcome (feeds dashboard pie)
top3 = a_end + 3
ws_s.cell(row=top3 - 1, column=1, value='Admission type and discharge outcome').font = f_bold
trows = [[t, f'=COUNTIFS({ATYPE},A{top3+1+i})', f'=B{top3+1+i}/SUM($B${top3+1}:$B${top3+3})'] for i, t in enumerate(types)]
t_end = table(ws_s, top3, ['Admission Type', 'Admissions', '% of Total'], trows, [None, '#,##0', '0.0%'])
outs = ['Recovered', 'Referred', 'LAMA', 'Deceased', 'Admitted']
orows = [[o, f'=COUNTIFS({STATUS},D{top3+1+i})', f'=E{top3+1+i}/SUM($E${top3+1}:$E${top3+5})']
         for i, o in enumerate(outs)]
# outcome table sits next to admission type table (columns D..F)
for j, h in enumerate(['Discharge Outcome', 'Patients', '% of Total']):
    ws_s.cell(row=top3, column=4 + j, value=h)
style_header(ws_s, top3, 3, 4)
for i, o in enumerate(outs):
    r = top3 + 1 + i
    vals = [o, f'=COUNTIFS({STATUS},D{r})', f'=E{r}/SUM($E${top3+1}:$E${top3+5})']
    for j, v in enumerate(vals):
        c = ws_s.cell(row=r, column=4 + j, value=v)
        c.font, c.border = f_norm, border
        c.number_format = [None, '#,##0', '0.0%'][j] or 'General'
ws_s.column_dimensions['A'].width = 24
for c in 'BCDEF':
    ws_s.column_dimensions[c].width = 17
ws_s.row_dimensions[4].height = 32
TYPE_FIRST, TYPE_LAST = top3 + 1, top3 + 3

# ------------------------------------------------------------------ Dashboard
ws = ws_dash
ws.sheet_view.showGridLines = False
title(ws, 'Hospital Patient Admission Analysis Dashboard',
      'Synthetic data  |  Jan 2025 - Oct 2026  |  all KPIs are live formulas')
kpis = [
    ('Total Admissions', f'=COUNTA(Admissions!$A$2:$A${LAST})', '#,##0'),
    ('Registered Patients', f'=COUNTA(Patients!$A$2:$A${PLAST})', '#,##0'),
    ('Doctors', f'=COUNTA(Doctors!$A$2:$A${len(doc)+1})', '#,##0'),
    ('Avg Stay (days)', f'=AVERAGE({STAY})', '0.0'),
    ('Total Revenue (Rs lakh)', f'=SUM({BILL})/100000', '#,##0.0'),
    ('Currently Admitted', f'=COUNTIF({STATUS},"Admitted")', '#,##0'),
    ('Mortality Rate', f'=COUNTIF({STATUS},"Deceased")/COUNTA(Admissions!$A$2:$A${LAST})', '0.0%'),
]
for i, (lab, fml, fm) in enumerate(kpis):
    col = 1 + i * 2
    ws.merge_cells(start_row=4, start_column=col, end_row=4, end_column=col + 1)
    ws.merge_cells(start_row=5, start_column=col, end_row=5, end_column=col + 1)
    a, b = ws.cell(row=4, column=col, value=lab), ws.cell(row=5, column=col, value=fml)
    a.font, a.fill = Font(name=F, size=9, bold=True, color='FFFFFF'), fill_head
    b.font, b.fill, b.number_format = Font(name=F, size=18, bold=True, color=NAVY), fill_light, fm
    for c in (a, b):
        c.alignment = Alignment(horizontal='center', vertical='center')
    ws.cell(row=4, column=col + 1).fill = fill_head
    ws.cell(row=5, column=col + 1).fill = fill_light
ws.row_dimensions[5].height = 34
for i in range(1, 15):
    ws.column_dimensions[get_column_letter(i)].width = 11.5

# chart 1: admissions by department
c1 = BarChart(); c1.type = 'col'; c1.title = 'Admissions by Department'
c1.add_data(Reference(ws_d, min_col=3, min_row=4, max_row=D_LAST), titles_from_data=True)
c1.set_categories(Reference(ws_d, min_col=1, min_row=D_FIRST, max_row=D_LAST))
c1.legend = None; c1.height, c1.width = 7.5, 15.5
c1.y_axis.title = 'Patients'; c1.y_axis.delete = False; c1.x_axis.delete = False
ws.add_chart(c1, 'A7')

# chart 2: monthly trend
c2 = LineChart(); c2.title = 'Monthly Admissions vs Discharges'
c2.add_data(Reference(ws_m, min_col=2, max_col=3, min_row=4, max_row=M_LAST), titles_from_data=True)
c2.set_categories(Reference(ws_m, min_col=1, min_row=M_FIRST, max_row=M_LAST))
c2.height, c2.width = 7.5, 15.5
c2.x_axis.number_format = 'mmm-yy'; c2.y_axis.delete = False; c2.x_axis.delete = False
ws.add_chart(c2, 'H7')

# chart 3: avg stay by department
c3 = BarChart(); c3.type = 'bar'; c3.title = 'Average Stay by Department (days)'
c3.add_data(Reference(ws_d, min_col=5, min_row=4, max_row=D_LAST), titles_from_data=True)
c3.set_categories(Reference(ws_d, min_col=1, min_row=D_FIRST, max_row=D_LAST))
c3.legend = None; c3.height, c3.width = 7.5, 15.5
c3.y_axis.delete = False; c3.x_axis.delete = False
ws.add_chart(c3, 'A23')

# chart 4: admission type pie
c4 = PieChart(); c4.title = 'Admission Type Share'
c4.add_data(Reference(ws_s, min_col=2, min_row=top3, max_row=TYPE_LAST), titles_from_data=True)
c4.set_categories(Reference(ws_s, min_col=1, min_row=TYPE_FIRST, max_row=TYPE_LAST))
c4.dataLabels = DataLabelList(); c4.dataLabels.showPercent = True
c4.height, c4.width = 7.5, 15.5
ws.add_chart(c4, 'H23')

ws['A39'] = 'Sheets: Dept Analysis | Monthly Trend | Stay Analysis | Departments | Doctors | Patients | Admissions (raw data + computed columns L:O)'
ws['A39'].font = f_sub

for w in (ws_dep, ws_doc, ws_pat, ws_adm):
    w.sheet_properties.tabColor = '888888'
for w in (ws_dash, ws_d, ws_m, ws_s):
    w.sheet_properties.tabColor = NAVY

wb.save(OUT)
print('saved', OUT)
