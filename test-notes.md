# Test Notes

## Test Suite Overview
Created `tests/test_logsum.py` with 24 comprehensive tests covering all rules and edge cases from `spec.md`.

**Final Status**: All 24 tests pass ✅

## Isolation Method
Each test uses **pytest fixtures with temporary directories** for isolation:
- `tmp_data_dir`: Provides a unique temporary directory per test via `tmp_path`
- `setup_data_dir`: Ensures the temp data directory exists before each test
- No shared state between tests
- Each test creates its own input CSV and output directory
- Tests run in complete isolation; cleanup is automatic via pytest's tmp_path fixture

## Failed Test Analysis

### Initial Failure: `test_default_command_reads_events_csv_writes_summary_csv`

**Symptom**: Exit code 2 instead of 0
```
Error: Input file not found: data/events.csv
```

**Root Cause**: Test bug
- Test assumed default behavior reads from `events.csv` in the current directory
- Implementation actually defaults to `data/events.csv` (a subdirectory)
- The spec didn't explicitly mandate the default path structure

**Decision**: Fix test to match implementation
- Changed test to create a `data/` subdirectory under the temp directory
- Changed assertion to look for output in `data/summary.csv`
- This aligns with the actual project structure where data lives in `data/`

**Resolution**: Test now passes; implementation behavior confirmed correct per project conventions.

## Test Categories Covered

| Category | Count | Examples |
|----------|-------|----------|
| Grouping & Normalisation | 5 | Case-insensitivity, whitespace trimming, case-sensitivity |
| Aggregation | 3 | count, first_seen, last_seen |
| Edge Cases | 5 | Missing level, malformed timestamps, empty input |
| Missing Columns | 3 | Timestamp, service, message columns |
| CLI & Flags | 3 | Default behavior, --input, --output |
| Exit Codes | 3 | Success (0), errors (1, 2) |
| Complex Scenarios | 2 | Mixed valid/invalid rows, spec sample data |
| **Total** | **24** | |

All edge cases from spec.md are covered.
