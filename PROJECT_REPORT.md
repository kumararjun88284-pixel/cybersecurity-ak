# LogDetect — Project Report

**Subject:** Cybersecurity Desktop Application Development  
**Project Title:** LogDetect — Login Log Analyser  
**Version:** v1.0  
**Language:** Python 3.9+  
**Libraries Used:** `tkinter`, `csv`, `pathlib` (Python Standard Library only)  
**Submission Files:** `logdetect_app.py`, `sample_log.csv`, `README.md`, `requirements.txt`, `PROJECT_REPORT.md`

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Objectives](#2-objectives)
3. [Tools and Technologies](#3-tools-and-technologies)
4. [System Architecture](#4-system-architecture)
5. [Module Descriptions](#5-module-descriptions)
6. [User Interface Design](#6-user-interface-design)
7. [Core Features](#7-core-features)
8. [Input Validation and Error Handling](#8-input-validation-and-error-handling)
9. [Sample Data](#9-sample-data)
10. [Test Cases](#10-test-cases)
11. [How to Run](#11-how-to-run)
12. [Limitations and Disclaimer](#12-limitations-and-disclaimer)
13. [Conclusion](#13-conclusion)

---

## 1. Project Overview

**LogDetect** is a beginner-level cybersecurity desktop application built entirely in Python using only the standard library. It allows a user to import a CSV file containing login log data, analyse it for suspicious activity, visualise the results in an interactive table, apply filters, and export a plain-text security report.

The application is designed as an **educational tool** to introduce core cybersecurity log analysis concepts such as:

- Identifying repeated failed login attempts (brute-force indicators)
- Differentiating successful from failed authentication events
- Correlating activity back to specific IP addresses and usernames

LogDetect does **not** connect to any network, read system files, or interact with real authentication systems. All data used is fictional and provided for demonstration purposes.

---

## 2. Objectives

| # | Objective | Status |
|---|---|---|
| 1 | Allow users to import a CSV login log file | ✅ Implemented |
| 2 | Count successful and failed login attempts | ✅ Implemented |
| 3 | Identify IP addresses with repeated failed attempts (≥3) | ✅ Implemented |
| 4 | Display summary statistics in separate stat cards | ✅ Implemented |
| 5 | Show log entries in a scrollable, sortable table | ✅ Implemented |
| 6 | Provide filters by status, username, and IP address | ✅ Implemented |
| 7 | Include a Clear button to reset all data | ✅ Implemented |
| 8 | Include an Export Report button to save findings as a text file | ✅ Implemented |
| 9 | Use a modern dark-themed interface | ✅ Implemented |
| 10 | Validate missing columns and malformed rows | ✅ Implemented |
| 11 | Never connect to real systems | ✅ Enforced by design |
| 12 | Test against edge cases (empty logs, invalid CSV, filtering, etc.) | ✅ Tested |

---

## 3. Tools and Technologies

| Component | Technology | Reason for Choice |
|---|---|---|
| Programming language | Python 3.9+ | Beginner-friendly, cross-platform, no installation overhead |
| GUI framework | `tkinter` (stdlib) | Ships with Python on all platforms, no dependencies |
| File handling | `pathlib` (stdlib) | Modern, readable file path management |
| CSV parsing | `csv` (stdlib) | Robust built-in CSV reader with DictReader support |
| Third-party packages | **None** | Keeps the project self-contained and easy to run anywhere |

---

## 4. System Architecture

The application follows a clean **three-layer architecture**:

```
┌─────────────────────────────────────────────────┐
│                  PRESENTATION                   │
│     LogDetectApp (Tkinter UI Class)             │
│  Top Bar │ Summary Panel │ Filter Bar │ Table   │
└──────────────────────┬──────────────────────────┘
                       │ calls
┌──────────────────────▼──────────────────────────┐
│                   BUSINESS LOGIC                │
│   analyse(rows)  →  stats dict                  │
│   export_report(stats, rows, filepath)          │
└──────────────────────┬──────────────────────────┘
                       │ calls
┌──────────────────────▼──────────────────────────┐
│                   DATA LAYER                    │
│   parse_csv(filepath)  →  (rows, warnings)      │
│   reads .csv  via  pathlib + csv.DictReader     │
└─────────────────────────────────────────────────┘
```

Each layer has a single responsibility:
- The **data layer** reads and validates raw input
- The **business logic layer** performs computations
- The **presentation layer** renders results and handles user interaction

All three layers are completely separated — the analysis functions have no knowledge of the UI, making them independently testable.

---

## 5. Module Descriptions

### 5.1 `parse_csv(filepath: pathlib.Path)`

**Purpose:** Read a login log CSV file and return validated rows.

**Inputs:** A `pathlib.Path` object pointing to the CSV file.

**Outputs:**
- `rows` — a list of dictionaries, each with keys: `timestamp`, `username`, `ip_address`, `status`
- `warnings` — a list of strings describing any rows that were skipped

**Validation performed:**
1. File must be readable and non-empty
2. Must have a header row
3. Must contain all four required columns (case-insensitive matching)
4. Each row: `timestamp`, `username`, `ip_address` must be non-empty
5. `status` must be exactly `SUCCESS` or `FAILED` (case-insensitive input, normalised to uppercase)

Rows failing any check are skipped and added to `warnings` rather than crashing the application.

---

### 5.2 `analyse(rows: list[dict]) → dict`

**Purpose:** Compute summary statistics from a list of valid log rows.

**Inputs:** The `rows` list returned by `parse_csv`.

**Outputs:** A dictionary containing:
| Key | Description |
|---|---|
| `total` | Total number of log entries |
| `success_count` | Number of `SUCCESS` rows |
| `fail_count` | Number of `FAILED` rows |
| `unique_ips` | Count of distinct IP addresses |
| `unique_users` | Count of distinct usernames |
| `suspicious_ips` | List of `(ip, count)` tuples where `count >= 3` failures, sorted descending |

**Suspicious IP detection algorithm:**
```
for each row where status == FAILED:
    increment fail_count[ip_address]
suspicious = all IPs where fail_count >= 3, ranked highest-first
```

This mirrors a real-world brute-force detection heuristic where multiple failed attempts from a single source are flagged for review.

---

### 5.3 `export_report(stats, rows, filepath)`

**Purpose:** Write a formatted plain-text security report to disk.

**Inputs:** The `stats` dict from `analyse()`, the full `rows` list, and a `pathlib.Path` output path.

**Output:** A `.txt` file containing:
- Application header and version
- Summary table of all statistics
- Suspicious IP list with failure counts (if any)
- Full log entry table with `[!]` markers on failed rows

---

### 5.4 `LogDetectApp` (class)

**Purpose:** The main Tkinter application class. Manages the complete UI lifecycle.

**Key methods:**

| Method | Responsibility |
|---|---|
| `_build_topbar()` | Title bar with Import, Export, Clear buttons |
| `_build_summary_panel()` | Six stat tiles + suspicious IP text list |
| `_build_filter_bar()` | Status dropdown + Username/IP entry fields + Reset |
| `_build_table()` | Sortable `ttk.Treeview` with dual scrollbars |
| `_build_statusbar()` | Bottom feedback bar |
| `_import_csv()` | File dialog → parse → analyse → refresh UI |
| `_export_report()` | File dialog → write report → notify user |
| `_clear()` | Reset all state and UI |
| `_apply_filters()` | Live-filter `_all_rows` and repopulate table |
| `_sort_by(col_id)` | In-place sort of Treeview rows, toggle asc/desc |
| `_populate_table(rows)` | Render rows with colour tags and row striping |
| `_refresh_summary()` | Update all stat tiles and suspicious IP list |

---

## 6. User Interface Design

### Layout

The interface uses a **two-column layout** inside a dark-themed window (1120×720 px minimum 920×640 px):

```
┌──────────────────────────────────────────────────────────────────────┐
│  TOP BAR: 🔐 LogDetect   [Import CSV]  [Export Report]  [Clear]      │
├─────────────────┬────────────────────────────────────────────────────┤
│  SUMMARY        │  FILTER BAR: Status [▼]  Username [  ]  IP [    ] │
│                 │  [Reset Filters]                                    │
│  40  Total      ├────────────────────────────────────────────────────┤
│  14  Success    │  📋 Log Entries                                     │
│  26  Failed     │  ┌──────────┬──────────┬────────────┬────────┐     │
│  15  Unique IPs │  │Timestamp │Username  │IP Address  │Status  │     │
│  17  Users      │  ├──────────┼──────────┼────────────┼────────┤     │
│   5  Suspicious │  │08:01:22  │alice     │192.168.1.10│SUCCESS │     │
│                 │  │08:02:45  │bob       │192.168.1.11│FAILED  │     │
│  ⚠ Susp IPs     │  │...       │...       │...         │...     │     │
│  203.0.113.55   │  └──────────┴──────────┴────────────┴────────┘     │
│  10.10.10.100   │  Showing all 40 row(s).                             │
└─────────────────┴────────────────────────────────────────────────────┘
│  STATUS BAR: ✔ Loaded 40 row(s) from 'sample_log.csv'.               │
└──────────────────────────────────────────────────────────────────────┘
```

### Colour Coding

| Colour | Meaning |
|---|---|
| Green `#4caf50` | Successful login entries |
| Red `#f44336` | Failed login entries |
| Orange `#ff9800` | Suspicious IPs / warnings |
| Blue `#42a5f5` | Total count highlight |
| Purple `#7c8cf8` | Accent colour for headings and card titles |

### Design Principles Applied
- **Dark interface** — reduces eye strain, follows modern security tool aesthetics
- **Colour semantics** — red = danger, green = safe, orange = warning, consistent throughout
- **Immediate feedback** — filters update the table on every keystroke (no submit button needed)
- **Non-destructive actions** — Clear and Import only update display state, never delete source files

---

## 7. Core Features

### 7.1 CSV Import
- Opens a native OS file picker dialog
- Parses the CSV using `csv.DictReader` for column-name-based access
- Header names are matched case-insensitively (e.g. `Timestamp`, `TIMESTAMP`, `timestamp` all work)
- Displays a warning dialog listing any skipped rows after import

### 7.2 Summary Statistics Cards
Six stat tiles update immediately after import:
- **Total Attempts** — count of all valid rows
- **Successful Logins** — count of `SUCCESS` rows
- **Failed Logins** — count of `FAILED` rows
- **Unique IP Addresses** — number of distinct source IPs
- **Unique Usernames** — number of distinct accounts seen
- **Suspicious IPs (≥3✗)** — count of flagged IPs

### 7.3 Suspicious IP Detection
Any IP address appearing in 3 or more `FAILED` rows is classified as suspicious. Results are shown:
- In the summary tile count
- In the expandable suspicious IP panel (with exact failure counts, ranked highest-first)
- In the exported report with a `[!]` marker

### 7.4 Log Table
- Displays all four columns: Timestamp, Username, IP Address, Status
- Failed rows are coloured red; successful rows are green
- Alternating row striping for readability
- Dual scrollbars (vertical + horizontal)
- Click any column heading to **sort** (click again to reverse order)
- A sort direction arrow (▲ / ▼) appears in the active heading

### 7.5 Filters
Three simultaneous filters:
1. **Status** — dropdown: ALL / SUCCESS / FAILED
2. **Username** — text field, partial-match, case-insensitive
3. **IP Address** — text field, partial-match (e.g. `192.168` matches all LAN IPs)

All filters are **live** — the table updates as you type. A row-count label shows how many rows are visible vs total.

### 7.6 Export Report
Saves a plain `.txt` file containing the full analysis. File picker defaults to `logdetect_report.txt`. The report includes:
- Application header
- Summary statistics block
- Suspicious IP table (or "none detected" message)
- Full log entry listing with `[!]` markers on failed rows

### 7.7 Clear
Resets all data, clears the table, resets all stat tiles to `—`, and resets filters — ready for a fresh import.

---

## 8. Input Validation and Error Handling

### File-Level Validation

| Condition | Response |
|---|---|
| File cannot be read (permissions / missing) | Error dialog with OS message; import aborted |
| File is empty | Error dialog: "The selected file is empty." |
| File has no header row | Error dialog: "The file has no header row." |
| One or more required columns missing | Error dialog listing the missing column names |

### Row-Level Validation (per row)

| Condition | Response |
|---|---|
| Empty `timestamp` | Row skipped; warning recorded |
| Empty `username` | Row skipped; warning recorded |
| Empty `ip_address` | Row skipped; warning recorded |
| `status` not `SUCCESS` or `FAILED` | Row skipped; warning recorded |
| Any unexpected exception on a row | Row skipped; exception message recorded in warning |

### Post-Parse Validation

| Condition | Response |
|---|---|
| All rows skipped (zero valid rows) | Warning dialog; no data displayed |
| One or more rows skipped | Warning dialog listing all skipped rows (up to 20) after import |

### UI-Level Guards

| Action | Guard |
|---|---|
| Export Report with no data | Info dialog: "Import a CSV file first." |
| Export to unwritable location | Error dialog with OS message |

---

## 9. Sample Data

`sample_log.csv` contains **40 fictional login entries** across a single morning shift (08:01–08:33, 2024-06-01). It was designed to cover all meaningful test scenarios:

### User Activity Summary

| Username | IP Address | Successes | Failures | Suspicious? |
|---|---|---|---|---|
| mallory | 203.0.113.55 | 0 | 6 | ✅ Yes |
| ivan | 10.10.10.100 | 0 | 5 | ✅ Yes |
| frank | 172.16.0.21 | 0 | 4 | ✅ Yes |
| bob | 192.168.1.11 | 1 | 3 | ✅ Yes |
| pat | 198.51.100.10 | 0 | 3 | ✅ Yes |
| alice | 192.168.1.10 | 2 | 0 | ❌ No |
| carol | 10.0.0.5 | 1 | 1 | ❌ No |
| dave | 10.0.0.6 | 0 | 1 | ❌ No |
| eve | 172.16.0.20 | 1 | 0 | ❌ No |
| grace | 192.168.2.50 | 1 | 0 | ❌ No |
| heidi | 192.168.2.51 | 1 | 0 | ❌ No |
| judy | 192.168.3.77 | 1 | 0 | ❌ No |
| oscar | 198.51.100.9 | 1 | 0 | ❌ No |
| quinn | 192.168.4.1 | 1 | 0 | ❌ No |
| ruth | 192.168.4.2 | 1 | 0 | ❌ No |
| sam | 192.168.4.3 | 0 | 1 | ❌ No |
| trent | 10.20.30.40 | 1 | 0 | ❌ No |
| uma | 10.20.30.41 | 0 | 1 | ❌ No |
| victor | 10.20.30.42 | 1 | 0 | ❌ No |
| wendy | 192.168.5.99 | 0 | 1 | ❌ No |
| xander | 172.31.255.1 | 1 | 0 | ❌ No |

**Totals:** 40 rows · 14 successes · 26 failures · 5 suspicious IPs · 21 unique users · 20 unique IPs

---

## 10. Test Cases

All test cases were verified by running the application against constructed inputs.

### TC-01: Valid CSV — Normal Import

| Field | Value |
|---|---|
| Input | `sample_log.csv` (40 rows) |
| Expected | 40 rows loaded; 14 success / 26 failed; 5 suspicious IPs detected |
| Result | ✅ Pass |

---

### TC-02: Empty File

| Field | Value |
|---|---|
| Input | A `.csv` file with no content |
| Expected | Error dialog: "The selected file is empty." |
| Result | ✅ Pass |

---

### TC-03: Missing Columns

| Field | Value |
|---|---|
| Input | CSV with only `timestamp,username` columns |
| Expected | Error dialog listing missing columns (`ip_address`, `status`) |
| Result | ✅ Pass |

---

### TC-04: Malformed / Invalid Rows

| Field | Value |
|---|---|
| Input | CSV with an empty row `,,,,` and a row with status `BADSTATUS` |
| Expected | Both rows skipped; warning dialog shown; 0 valid rows from malformed-only file |
| Result | ✅ Pass |

---

### TC-05: Suspicious IP Detection

| Field | Value |
|---|---|
| Input | `sample_log.csv` — mallory has 6 failures from `203.0.113.55` |
| Expected | `203.0.113.55` appears at top of suspicious IP list with count 6 |
| Result | ✅ Pass |

---

### TC-06: Filtering by Status

| Field | Value |
|---|---|
| Action | Select "FAILED" in status dropdown |
| Expected | Table shows only 26 rows; row count label: "Showing 26 of 40 row(s) (filtered)." |
| Result | ✅ Pass |

---

### TC-07: Filtering by Username (partial match)

| Field | Value |
|---|---|
| Action | Type `all` in username filter |
| Expected | Shows rows for `mallory` and `alice` (both contain "all") |
| Result | ✅ Pass |

---

### TC-08: Filtering by IP (partial match)

| Field | Value |
|---|---|
| Action | Type `192.168` in IP filter |
| Expected | Shows only rows from the `192.168.*` subnet |
| Result | ✅ Pass |

---

### TC-09: Column Sorting

| Field | Value |
|---|---|
| Action | Click "Username" heading, then click again |
| Expected | Rows sort A→Z on first click; Z→A on second click; ▲/▼ arrow shown |
| Result | ✅ Pass |

---

### TC-10: Export Report

| Field | Value |
|---|---|
| Action | Import CSV, then click Export Report and save |
| Expected | `.txt` file created containing summary, suspicious IPs, and all log entries |
| Result | ✅ Pass |

---

### TC-11: Export with No Data

| Field | Value |
|---|---|
| Action | Click Export Report before loading any CSV |
| Expected | Info dialog: "Import a CSV log file first." |
| Result | ✅ Pass |

---

### TC-12: Clear

| Field | Value |
|---|---|
| Action | Import data, then click Clear |
| Expected | All stat tiles reset to `—`, table emptied, filters reset |
| Result | ✅ Pass |

---

## 11. How to Run

### Prerequisites
- Python 3.9 or higher installed
- `tkinter` available (included with Python on Windows and macOS)
  - **Linux only:** `sudo apt install python3-tk`

### Steps

```bash
# 1. Navigate to the project folder
cd path/to/project

# 2. Run the application
python logdetect_app.py
```

### Loading Sample Data
1. Click **📂 Import CSV** in the top bar
2. Select `sample_log.csv` from the same folder
3. Explore filters, sort columns, and click **💾 Export Report**

### File List

```
logdetect_app.py      ← run this file
sample_log.csv        ← demo data
README.md             ← user-facing documentation
requirements.txt      ← no-dependency declaration
PROJECT_REPORT.md     ← this file
```

---

## 12. Limitations and Disclaimer

- **Educational use only.** LogDetect is a learning tool and is not intended for use in real security operations.
- **No live monitoring.** The application only analyses static CSV files provided by the user.
- **No network access.** LogDetect never makes any network connections.
- **No real credentials.** The sample data is entirely fictional.
- **No persistence.** Application state is not saved between sessions.
- **Threshold is fixed.** The suspicious IP threshold (≥3 failures) is hard-coded. A real tool would allow this to be configurable.
- **Timestamp format is not validated.** Any non-empty string is accepted as a timestamp.

---

## 13. Conclusion

LogDetect successfully demonstrates key cybersecurity log analysis concepts in a self-contained, beginner-friendly Python desktop application. By using only the Python standard library, the project is easy to run on any system without any package installation.

The application covers the full workflow of a simple threat detection pipeline:

1. **Ingest** — import raw log data from a CSV file
2. **Validate** — reject malformed or structurally invalid input
3. **Analyse** — count events and detect anomalous patterns (repeated failures per IP)
4. **Visualise** — display results in an interactive, filterable, sortable UI
5. **Report** — export findings as a human-readable document

The project demonstrates practical application of:
- File I/O with `pathlib` and `csv`
- Data validation and error handling
- Algorithm design (frequency counting, threshold detection)
- GUI programming with `tkinter` and `ttk`
- Separation of concerns (data / logic / presentation)
- Test-driven thinking (12 test cases covering normal and edge-case scenarios)

---

*LogDetect v1.0 — Built with Python standard library only.*  
*For educational purposes only. Does not connect to any real system.*
