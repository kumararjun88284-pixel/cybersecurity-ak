# 🔐 LogDetect

**A beginner-friendly cybersecurity desktop application for analysing login logs.**

Built with **pure Python** — no third-party packages required. Uses only the standard library: `tkinter`, `csv`, and `pathlib`.

> ⚠️ Educational purposes only. LogDetect never connects to any real system or network.

---

## Features

- 📂 **Import a CSV login log** — load any file with `timestamp`, `username`, `ip_address`, and `status` columns
- 📊 **Summary statistics** — live cards showing total attempts, successes, failures, unique IPs, and unique users
- 🚨 **Suspicious IP detection** — automatically flags IP addresses with 3 or more failed login attempts
- 📋 **Scrollable log table** — view all entries with colour-coded rows (green = success, red = failed)
- 🔃 **Sortable columns** — click any column heading to sort ascending or descending
- 🔍 **Filters** — filter entries by status (ALL / SUCCESS / FAILED), username, or IP address in real time
- 💾 **Export Report** — save a plain-text security report summarising findings
- ✕ **Clear** — reset all data and start fresh
- ✅ **Input validation** — handles empty files, missing columns, unknown status values, and malformed rows gracefully

---

## Screenshots

```
┌──────────────────────────────────────────────────────────────────┐
│ 🔐 LogDetect   Cybersecurity Login Log Analyser        [Import]  │
├────────────┬─────────────────────────────────────────────────────┤
│ SUMMARY    │  Filter: Status [ALL▼]  Username [      ]  IP [   ] │
│            ├─────────────────────────────────────────────────────┤
│ 40 Total   │  Timestamp          Username   IP Address   Status   │
│ 14 Success │  2024-06-01 08:01   alice      192.168.1.10 SUCCESS  │
│ 26 Failed  │  2024-06-01 08:02   bob        192.168.1.11 FAILED   │
│  8 Uniq IP │  ...                                                 │
│            ├─────────────────────────────────────────────────────┤
│ ⚠ Susp IPs │  Showing all 40 row(s).                             │
│ 203.0.113  └─────────────────────────────────────────────────────┘
└────────────┘
```

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.9 or higher |
| tkinter | Included with Python |
| csv | Included with Python |
| pathlib | Included with Python |

> **No `pip install` needed.**
> `tkinter` ships with the standard Python installer on Windows and macOS.
> On Linux, install it with: `sudo apt install python3-tk`

---

## Getting Started

### 1. Clone or download the files

```
logdetect_app.py   ← main application
sample_log.csv     ← fictional demo data
README.md
```

### 2. Run the application

```bash
python logdetect_app.py
```

### 3. Load the demo data

Click **📂 Import CSV** and open `sample_log.csv` from the same folder.

### 4. Explore

- Use the **Status**, **Username**, and **IP** filters to narrow down entries
- Click any **column heading** to sort the table
- Check the left panel for suspicious IPs
- Click **💾 Export Report** to save a `.txt` summary

---

## CSV Format

Your CSV file must contain exactly these four columns (header names are case-insensitive):

| Column | Description | Example |
|---|---|---|
| `timestamp` | Date and time of the login attempt | `2024-06-01 08:01:22` |
| `username` | The account name used | `alice` |
| `ip_address` | Source IP address | `192.168.1.10` |
| `status` | Outcome — must be `SUCCESS` or `FAILED` | `FAILED` |

**Example CSV:**

```csv
timestamp,username,ip_address,status
2024-06-01 08:01:22,alice,192.168.1.10,SUCCESS
2024-06-01 08:02:45,bob,192.168.1.11,FAILED
2024-06-01 08:03:10,bob,192.168.1.11,FAILED
```

---

## Validation & Error Handling

| Scenario | Behaviour |
|---|---|
| Empty file | Error dialog — file rejected |
| Missing required columns | Error dialog — lists which columns are absent |
| Unknown `status` value | Row is skipped; warning shown after import |
| Empty `timestamp`, `username`, or `ip_address` | Row is skipped; warning shown |
| Completely malformed row | Row is skipped; warning shown |
| No valid rows after parsing | Warning dialog — no data loaded |
| File cannot be opened | Error dialog with OS message |

---

## Suspicious IP Logic

An IP address is flagged as **suspicious** when it appears in **3 or more FAILED login rows**. Suspicious IPs are:

- Listed in the left panel, ranked by failure count
- Counted in the **Suspicious IPs (≥3✗)** summary tile
- Included in the exported report with a `[!]` marker

---

## Sample Data Overview

`sample_log.csv` contains **40 fictional login entries** across 17 usernames and 15 IP addresses, designed to cover all test scenarios:

| IP Address | User | Failed Attempts | Flagged? |
|---|---|---|---|
| `203.0.113.55` | mallory | 6 | ✅ Yes |
| `10.10.10.100` | ivan | 5 | ✅ Yes |
| `172.16.0.21` | frank | 4 | ✅ Yes |
| `192.168.1.11` | bob | 3 | ✅ Yes |
| `198.51.100.10` | pat | 3 | ✅ Yes |
| Others | various | ≤2 | ❌ No |

---

## Project Structure

```
logdetect_app.py
│
├── parse_csv()          — reads & validates CSV; collects per-row warnings
├── analyse()            — computes statistics and detects suspicious IPs
├── export_report()      — writes a plain-text report to disk
│
└── LogDetectApp (class)
    ├── _build_topbar()      — title bar with action buttons
    ├── _build_summary_panel() — stat tiles + suspicious IP list
    ├── _build_filter_bar()  — status/username/IP filters
    ├── _build_table()       — sortable, scrollable Treeview log table
    └── _build_statusbar()   — contextual feedback at the bottom
```

---

## Keyboard & UI Tips

| Action | How |
|---|---|
| Sort a column | Click its heading (click again to reverse) |
| Filter by username | Type in the **Username** box — updates instantly |
| Filter by IP | Type in the **IP** box — supports partial matches |
| Reset all filters | Click **Reset Filters** |
| Select multiple rows | Hold `Ctrl` or `Shift` and click |

---

## Disclaimer

LogDetect uses **entirely fictional data** and is designed as a **cybersecurity learning tool** for students and beginners. It does not:

- Connect to any network, server, or external service
- Read system logs, auth logs, or any real credentials
- Perform any live monitoring or intrusion detection

---

## License

This project is released for educational use. Feel free to modify and learn from it.
