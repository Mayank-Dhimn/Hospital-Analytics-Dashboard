# Hospital Analytics Dashboard: Tableau Build Guide

This guide builds a new workbook from `data/tableau_admissions_flat.csv`. It does not use or reuse any Salesforce
workbook content. The CSV contains one row per admission and is synthetic; it has no real patient information.

## What the data means

- One row represents one hospital admission. A patient may therefore appear on more than one row.
- `patient_id` has 1,557 distinct values in the admissions file. The separate `patients.csv` contains 1,900
  registered patients, including people with no admission. The Tableau CSV can only count patients who were admitted.
- The 24 rows with a blank `discharge_date`, `stay_days`, and `bill_amount` are currently admitted. They are expected,
  not missing-data errors. Revenue covers billed admissions and does not include those active stays.
- Patient age is age on that admission date. Stay duration is calculated only for discharged admissions.

## 1. Close the unrelated workbook without saving

1. If `Salesforce Sales Cloud - Weighted Sales Pipeline` is open, choose **File > Close**.
2. If Tableau asks whether to save changes, choose **Don't Save**. This only discards changes made in that unrelated
   workbook; it does not delete the workbook file or affect the Hospital Analytics project.
3. If Tableau opens to its start page instead, continue to the next section. Do not copy sheets or dashboards from the
   Salesforce workbook.

## 2. Create a new workbook and connect the CSV

1. Choose **File > New**. Confirm that the new workbook has a blank data source and no Salesforce sheets.
2. On the start page, under **Connect**, choose **Text File**.
3. Browse to `HospitalAnalytics\data\tableau_admissions_flat.csv` and choose **Open**.
4. On the **Data Source** page, confirm the preview has **3,400 rows and 26 columns**. The first field is
   `admission_id`; the last is `age_group`.
5. If Tableau shows a data interpreter or field preview prompt, leave the header row enabled and confirm the field
   names are the first row.
6. Click **Sheet 1** at the bottom to start building worksheets.

The project CSV is in the `data` folder. If the project is moved, reconnect to the copy in the moved project folder.

## 3. Check and correct data types

On the **Data Source** page or the Data pane, check the type icon beside each field. Click the icon to change a type.
Use these types:

| Fields | Tableau data type |
|---|---|
| `admission_id`, `patient_id`, `doctor_id`, `department_id`, `total_beds`, `admission_year`, `patient_age` | Number (Whole) |
| `admission_date`, `discharge_date`, `admission_month` | Date |
| `bill_amount`, `stay_days` | Number (Decimal) |
| All remaining fields | String |

Tableau may first interpret date values as strings. Change all three date fields listed above to **Date**. Keep the
IDs as numbers; Tableau can use them as dimensions for distinct counts. Do not replace blank dates, stays, or bills:
the blanks represent active admissions.

## 4. Create the calculated fields

For each field below, choose **Analysis > Create Calculated Field…**, enter the exact name and formula, then click
**OK**. Field names in formulas are case-sensitive as written here; the formulas use the actual CSV column names.
If Tableau marks a formula invalid, check the source field spelling and data type.

| Calculated field name | Formula | Meaning |
|---|---|---|
| `Total Admissions` | `COUNTD([admission_id])` | Distinct admission records |
| `Total Patients` | `COUNTD([patient_id])` | Unique patients represented in the admission file |
| `Total Revenue` | `SUM([bill_amount])` | Sum of non-null bills, in rupees |
| `Average Stay Duration` | `AVG([stay_days])` | Mean stay for discharged admissions; null stays are excluded |
| `Mortality Percentage` | `COUNTD(IF [discharge_status] = 'Deceased' THEN [admission_id] END) / COUNTD([admission_id])` | Deceased admissions divided by all admissions |
| `Currently Admitted Patients` | `COUNTD(IF [discharge_status] = 'Admitted' THEN [patient_id] END)` | Unique patients whose status is Admitted |
| `Average Patient Age` | `AVG([patient_age])` | Mean age at the time of admission |
| `Admission Month` | `DATETRUNC('month', [admission_date])` | Month-start date for trend and heatmap charts |
| `Stay Duration Category` | `IF ISNULL([stay_days]) THEN 'Currently Admitted' ELSEIF [stay_days] <= 2 THEN '1-2 days' ELSEIF [stay_days] <= 5 THEN '3-5 days' ELSEIF [stay_days] <= 9 THEN '6-9 days' ELSE '10+ days' END` | Stay buckets with a separate category for active stays |

Click **Default Properties > Number Format** for `Total Revenue` and choose **Number (Custom)** with zero decimal
places and a thousands separator. Format `Mortality Percentage` as **Percentage** with one decimal place.
Format `Average Stay Duration` and `Average Patient Age` to one decimal place.

Optional donut-chart helper: create a calculated field named `Donut Hole` with formula `1`. It is only a constant axis
used to create a donut; it does not represent hospital data.

## 5. Build the six KPI worksheets

Create one worksheet per KPI. Rename the sheet tab using the names below. On each sheet, drag the stated calculated
field to **Marks > Text**. Set **Marks** to **Text**, then choose **Text > …** to edit the label. Use a large, bold
value (about 22–28 pt), center-align it, and display a short title above or within the label.

| Worksheet | Field on Marks > Text | Number format |
|---|---|---|
| `KPI Admissions` | `Total Admissions` | Whole number, comma separator |
| `KPI Patients` | `Total Patients` | Whole number, comma separator |
| `KPI Revenue` | `Total Revenue` | Currency (Custom), `Rs` or `₹`, no decimals |
| `KPI Avg Stay` | `Average Stay Duration` | Number, 1 decimal, suffix `days` in the label |
| `KPI Mortality` | `Mortality Percentage` | Percentage, 1 decimal |
| `KPI Admitted` | `Currently Admitted Patients` | Whole number, comma separator |

Do not add a dimension to **Rows** or **Columns** on a KPI sheet; each should display a single value.

## 6. Build the twelve chart worksheets

For each chart, choose **New Worksheet**, rename its tab, drag the fields as shown, and set the mark type using the
**Marks** drop-down. For bars, use **Show Mark Labels** on the toolbar. Give every worksheet a clear title and use
**Fit > Entire View** when appropriate.

### 1. Admissions by Department — horizontal bar

- **Rows:** `department_name`
- **Columns:** `Total Admissions`
- **Marks:** Bar; drag `department_name` to **Color** and `Total Admissions` to **Label**.
- Sort departments descending by `Total Admissions` using the toolbar sort button.

### 2. Monthly Admissions Trend — line

- **Columns:** `Admission Month`; choose the continuous (green) **Month** date option.
- **Rows:** `Total Admissions`
- **Marks:** Line.
- Format the horizontal axis as `MMM YYYY`. Keep years visible so January in different years is not combined.

### 3. Revenue by Department — horizontal bar

- **Rows:** `department_name`
- **Columns:** `Total Revenue`
- **Marks:** Bar; put `Total Revenue` on **Label**, format it as rupees, and sort descending.
- The value excludes the 24 unbilled active admissions.

### 4. Average Stay by Department — horizontal bar

- **Rows:** `department_name`
- **Columns:** `Average Stay Duration`
- **Marks:** Bar; put `Average Stay Duration` on **Label**, format to one decimal, and sort descending.
- Tableau's `AVG` ignores null `stay_days`, so this is discharged admissions only.

### 5. Admissions by Type — donut

- Drag `Donut Hole` to **Columns** twice. Right-click the second `Donut Hole` pill and choose **Dual Axis**; right-click
  an axis and choose **Synchronize Axis**, then hide the headers.
- On the first **Marks** card, choose **Pie**. Drag `admission_type` to **Color**, `Total Admissions` to **Angle**, and
  `Total Admissions` to **Label**.
- On the second **Marks** card, choose **Pie**, remove any dimensions, set **Color** to white, and reduce **Size** to
  make a small inner circle. The first pie remains visible as a ring around it.
- Put `admission_type` and `Total Admissions` in the tooltip. Use **Fit > Entire View**.

### 6. Patient Age Distribution — histogram

- Right-click `patient_age` in the Data pane and choose **Create > Bins…**. Set bin size to **5** years and click
  **OK**.
- **Columns:** `patient_age (bin)` (the generated field).
- **Rows:** `Total Admissions`
- **Marks:** Bar.
- Title the chart **Admissions by Patient Age at Admission**. Because the CSV has one row per admission, the bar height
  counts admission records, not unique people. Use `Average Patient Age` for the overall age KPI.

### 7. Gender Distribution — donut

- Use the same two-axis donut construction described for Admissions by Type.
- First **Marks** card: **Pie**; `patient_gender` on **Color**, `Total Patients` on **Angle** and **Label**.
- Second **Marks** card: **Pie**, no dimensions, white **Color**, smaller **Size**.
- The chart represents distinct patients in the admission data, not the 1,900 registered-patient source table.

### 8. Discharge Status — bar

- **Rows:** `discharge_status`
- **Columns:** `Total Admissions`
- **Marks:** Bar; `Total Admissions` on **Label**, `discharge_status` on **Color**.
- Sort descending. Keep `Admitted` as a visible status; it represents current admissions.

### 9. Stay Duration Distribution — bar

- **Columns:** `Stay Duration Category`
- **Rows:** `Total Admissions`
- **Marks:** Bar; put `Total Admissions` on **Label**.
- Use **Sort** to order `1-2 days`, `3-5 days`, `6-9 days`, `10+ days`, and `Currently Admitted`. Do not include
  active stays in a numeric duration bin.

### 10. Top 10 Diagnoses — horizontal bar

- **Rows:** `diagnosis`
- **Columns:** `Total Admissions`
- On the `diagnosis` filter, open the **Top** tab, choose **By field**, and set **Top 10** by **Count (Distinct)** of
  `admission_id`. Apply the filter.
- **Marks:** Bar; `Total Admissions` on **Label**; sort descending.

### 11. Top Doctors by Admissions — horizontal bar

- **Rows:** `doctor_name`
- **Columns:** `Total Admissions`
- On the `doctor_name` filter, choose **Top > By field > Top 10** by **Count (Distinct)** of `admission_id`.
- **Marks:** Bar; `Total Admissions` on **Label**. Add `department_name` to **Tooltip** and sort descending.

### 12. Department vs Month — heatmap

- **Columns:** `Admission Month`; choose the discrete (blue) **Month** date option so each month is a separate column.
- **Rows:** `department_name`
- **Marks:** choose **Square**.
- Drag `Total Admissions` to **Color** and **Label**. Use **Color > Edit Colors** and choose a single-hue sequential
  palette. Keep year in the month labels.

## 7. Assemble the dashboard

1. Choose **Dashboard > New Dashboard** and rename the tab `Hospital Analytics`.
2. In the **Size** control, choose **Fixed Size** and a large desktop size such as **1600 x 1400**. The dashboard can
   scroll vertically on a smaller screen.
3. Choose **Tiled** layout. Add a **Text** object at the top with the title **Hospital Analytics Dashboard** and a
   subtitle: *Admissions, outcomes, revenue and length of stay | Synthetic data*.
4. Add all six KPI worksheets in a **Horizontal** layout container beneath the title, ordered:
   Admissions, Patients, Revenue, Avg Stay, Mortality, Currently Admitted. Give the cards a white background and equal
   widths.
5. Add the six filter cards described in the next section in one compact row under the KPI cards.
6. Add the 12 chart worksheets in a **3-column by 4-row** grid. Arrange them:
   - Row 1: Admissions by Department | Monthly Admissions Trend | Revenue by Department
   - Row 2: Average Stay by Department | Admissions by Type | Patient Age Distribution
   - Row 3: Gender Distribution | Discharge Status | Stay Duration Distribution
   - Row 4: Top 10 Diagnoses | Top Doctors by Admissions | Department vs Month heatmap
7. For each sheet, open its drop-down menu on the dashboard and choose **Fit > Entire View** (or **Fit Width** for
   long horizontal bars). Hide legends that repeat information already clear from labels.
8. Use **Dashboard > Actions… > Add Action > Filter** if you want clicking a department to filter other charts. Set
   **Source Sheets** to Admissions by Department and **Target Sheets** to the charts; set **Clearing the selection**
   to **Show all values**.

## 8. Add interactive filters

Add these six actual CSV fields as filters:

1. Open a chart worksheet, drag the field to **Filters**, choose all values, and click **OK**.
2. Right-click the filter pill and choose **Show Filter**.
3. On the dashboard, use the filter card menu and choose **Apply to Worksheets > All Using This Data Source**. Repeat
   for each field.

| Filter card label | Source field | Suggested display |
|---|---|---|
| Admission Date | `admission_date` | Range of Dates |
| Department | `department_name` | Multiple Values (Dropdown) |
| Gender | `patient_gender` | Multiple Values (Dropdown) |
| Admission Type | `admission_type` | Multiple Values (Dropdown) |
| Discharge Status | `discharge_status` | Multiple Values (Dropdown) |
| Ward Type | `ward_type` | Multiple Values (Dropdown) |

Ensure the filters also apply to KPI worksheets, so KPI values update with the dashboard selections.

## 9. Format and check the dashboard

- Use a clean light background (`#F5F5F5`), white chart and KPI tiles, navy titles (`#1F3A5F`), blue/teal chart colors,
  and orange only for highlights. Use red sparingly for the Deceased status.
- Use one font throughout, such as Arial. Make the dashboard title 20–24 pt, chart titles 12–14 pt, and labels large
  enough to read. Avoid 3-D charts and excessive gridlines.
- Edit tooltips from **Worksheet > Tooltip**. Include the relevant actual fields: department/type/status/doctor,
  `Total Admissions`, `Total Revenue`, `Average Stay Duration`, and date as relevant to that chart.
- Verify all 12 charts and six KPI sheets are present, filters change the displayed values, and no title or tooltip
  mentions Salesforce.
- Compare the unfiltered KPI cards to the data-quality report. Small differences can occur only if number formats
  round a value; the underlying calculated measures should agree.

## 10. Save the packaged workbook

1. Choose **File > Save As…**.
2. Browse to the project's `tableau` folder.
3. Enter `Hospital_Analytics.twbx` as the file name and choose **Tableau Packaged Workbook (`*.twbx`)** as the file
   type. A packaged workbook includes the CSV extract so the workbook can be moved more easily.
4. Click **Save**. Reopen the saved file once to confirm it opens with the dashboard and data.

Tableau Desktop is installed on this computer, but no programmatic `.twb`/`.twbx` generation was used: Tableau's
workbook format and dashboard metadata are application-managed, so a handcrafted file would not be a reliable valid
workbook. Build and save it from Tableau Desktop using these steps.
