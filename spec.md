# Goal
Build a tiny CLI that reads `events.csv` and writes `summary.csv` with one row per event group.

# Inputs
- Input file: `events.csv`
- Columns: `timestamp`, `level`, `service`, `message`
- Encoding: UTF-8

# Outputs
- Output file: `summary.csv`
- One row per grouped event
- Columns: group key fields plus aggregation fields

# Normalisation rules
- Trim leading/trailing whitespace from all text fields.
- Treat `level` as case-insensitive and store it in uppercase.
- Treat `service` as case-sensitive after trimming.
- Treat `message` as case-sensitive after trimming.

# Grouping rule
Group rows by exact tuple:
- `level`
- `service`
- `message`

# Aggregation
For each group, write:
- `count`
- `first_seen`
- `last_seen`

Where:
- `count` = number of rows in the group
- `first_seen` = earliest valid timestamp in the group
- `last_seen` = latest valid timestamp in the group

# Edge cases
- Missing `level`: use `UNKNOWN`.
- Malformed timestamp: skip the row and continue.
- Empty input file: write only the CSV header.
- Missing required columns: fail with a non-zero exit code.

# CLI
- Default command reads `events.csv` and writes `summary.csv`.
- Optional flags:
  - `--input PATH`
  - `--output PATH`
- Exit codes:
  - `0` success
  - `1` invalid input or missing columns
  - `2` file read/write failure

# Out of scope
- No database support.
- No network access.
- No third-party dependencies unless explicitly approved.
- No filtering, time-zone conversion, or advanced analytics.

## Signed off
Initials: AI
Date: 2026-07-18

## Implementation notes
- Added sample data covering duplicate grouping and missing-level handling.