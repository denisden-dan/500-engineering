import pytest
import csv
import sys
import subprocess
from pathlib import Path


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Create a temporary directory for test data."""
    return tmp_path / "data"


@pytest.fixture(autouse=True)
def setup_data_dir(tmp_data_dir):
    """Ensure temp data directory exists."""
    tmp_data_dir.mkdir(parents=True, exist_ok=True)
    yield tmp_data_dir


# Grouping and Normalisation Tests

def test_grouping_basic(tmp_data_dir):
    """Test basic grouping by (level, service, message)."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,auth,Login\n"
        "2026-07-18T10:01:00,INFO,auth,Login\n"
        "2026-07-18T10:02:00,ERROR,auth,Login\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 2

    info_group = next(r for r in rows if r["level"] == "INFO")
    assert info_group["count"] == "2"
    assert info_group["first_seen"] == "2026-07-18T10:00:00"
    assert info_group["last_seen"] == "2026-07-18T10:01:00"

    error_group = next(r for r in rows if r["level"] == "ERROR")
    assert error_group["count"] == "1"


def test_level_case_insensitive_normalized_to_uppercase(tmp_data_dir):
    """Test level field is case-insensitive and stored as uppercase."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,info,svc,msg\n"
        "2026-07-18T10:01:00,INFO,svc,msg\n"
        "2026-07-18T10:02:00,InFo,svc,msg\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 1
    assert rows[0]["level"] == "INFO"
    assert rows[0]["count"] == "3"


def test_whitespace_trimmed_from_text_fields(tmp_data_dir):
    """Test leading/trailing whitespace is trimmed from all text fields."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00, INFO ,  auth  ,  Login  \n"
        "2026-07-18T10:01:00,INFO,auth,Login\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 1
    assert rows[0]["count"] == "2"
    assert rows[0]["service"] == "auth"
    assert rows[0]["message"] == "Login"


def test_service_case_sensitive_after_trimming(tmp_data_dir):
    """Test service field is case-sensitive (after trimming)."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,Auth,msg\n"
        "2026-07-18T10:01:00,INFO,auth,msg\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 2


def test_message_case_sensitive_after_trimming(tmp_data_dir):
    """Test message field is case-sensitive (after trimming)."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,svc,Login\n"
        "2026-07-18T10:01:00,INFO,svc,login\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 2


# Aggregation Tests

def test_count_aggregation(tmp_data_dir):
    """Test count field aggregates correctly."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,auth,Login\n"
        "2026-07-18T10:01:00,INFO,auth,Login\n"
        "2026-07-18T10:02:00,INFO,auth,Login\n"
        "2026-07-18T10:03:00,INFO,auth,Login\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 1
    assert rows[0]["count"] == "4"


def test_first_seen_earliest_timestamp(tmp_data_dir):
    """Test first_seen captures the earliest valid timestamp."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:03:00,INFO,auth,msg\n"
        "2026-07-18T10:01:00,INFO,auth,msg\n"
        "2026-07-18T10:02:00,INFO,auth,msg\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert rows[0]["first_seen"] == "2026-07-18T10:01:00"


def test_last_seen_latest_timestamp(tmp_data_dir):
    """Test last_seen captures the latest valid timestamp."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:03:00,INFO,auth,msg\n"
        "2026-07-18T10:01:00,INFO,auth,msg\n"
        "2026-07-18T10:02:00,INFO,auth,msg\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert rows[0]["last_seen"] == "2026-07-18T10:03:00"


# Edge Cases

def test_missing_level_uses_unknown(tmp_data_dir):
    """Test missing level field defaults to UNKNOWN."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,,auth,msg\n"
        "2026-07-18T10:01:00,,auth,msg\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 1
    assert rows[0]["level"] == "UNKNOWN"
    assert rows[0]["count"] == "2"


def test_malformed_timestamp_skipped(tmp_data_dir):
    """Test rows with malformed timestamps are skipped."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,auth,msg\n"
        "not-a-date,INFO,auth,msg\n"
        "2026-07-18T10:01:00,INFO,auth,msg\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 1
    assert rows[0]["count"] == "2"
    assert rows[0]["first_seen"] == "2026-07-18T10:00:00"
    assert rows[0]["last_seen"] == "2026-07-18T10:01:00"


def test_empty_input_file_writes_header_only(tmp_data_dir):
    """Test empty input file writes only CSV header to output."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text("timestamp,level,service,message\n")

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    content = output_file.read_text()
    lines = content.strip().split("\n")
    assert len(lines) == 1
    assert "level" in lines[0]
    assert "service" in lines[0]
    assert "message" in lines[0]
    assert "count" in lines[0]


def test_all_rows_with_malformed_timestamps_empty_output(tmp_data_dir):
    """Test when all rows have malformed timestamps, only header is written."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "bad-date-1,INFO,auth,msg\n"
        "bad-date-2,ERROR,payment,err\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 0


# Missing Columns Tests

def test_missing_timestamp_column_fails(tmp_data_dir):
    """Test missing timestamp column causes failure with exit code 1."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "level,service,message\n"
        "INFO,auth,Login\n"
    )

    result = subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 1


def test_missing_service_column_fails(tmp_data_dir):
    """Test missing service column causes failure with exit code 1."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,message\n"
        "2026-07-18T10:00:00,INFO,Login\n"
    )

    result = subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 1


def test_missing_message_column_fails(tmp_data_dir):
    """Test missing message column causes failure with exit code 1."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service\n"
        "2026-07-18T10:00:00,INFO,auth\n"
    )

    result = subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 1


# CLI Tests

def test_default_command_reads_events_csv_writes_summary_csv(tmp_data_dir):
    """Test default CLI behavior: reads from data/events.csv, writes to data/summary.csv."""
    # The implementation defaults to data/ subdirectory
    data_dir = tmp_data_dir / "data"
    data_dir.mkdir(exist_ok=True)

    events_file = data_dir / "events.csv"
    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,auth,Login\n"
    )

    # Run with defaults from parent directory
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "src" / "logsum.py")],
        cwd=tmp_data_dir
    )
    assert result.returncode == 0

    # Check summary.csv was created in data/
    summary_file = data_dir / "summary.csv"
    assert summary_file.exists()
    rows = list(csv.DictReader(summary_file.open()))
    assert len(rows) == 1


def test_input_flag_reads_from_custom_path(tmp_data_dir):
    """Test --input flag reads from specified path."""
    custom_input = tmp_data_dir / "custom_events.csv"
    output_file = tmp_data_dir / "summary.csv"

    custom_input.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,auth,Login\n"
    )

    result = subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(custom_input), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0
    assert output_file.exists()


def test_output_flag_writes_to_custom_path(tmp_data_dir):
    """Test --output flag writes to specified path."""
    events_file = tmp_data_dir / "events.csv"
    custom_output = tmp_data_dir / "custom_summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,auth,Login\n"
    )

    result = subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(custom_output)],
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0
    assert custom_output.exists()
    assert not (tmp_data_dir / "summary.csv").exists()


# Exit Code Tests

def test_exit_code_0_on_success(tmp_data_dir):
    """Test exit code 0 on successful execution."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,auth,Login\n"
    )

    result = subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0


def test_exit_code_2_on_file_read_failure(tmp_data_dir):
    """Test exit code 2 when input file cannot be read."""
    nonexistent_file = tmp_data_dir / "nonexistent.csv"
    output_file = tmp_data_dir / "summary.csv"

    result = subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(nonexistent_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 2


def test_exit_code_2_on_file_write_failure(tmp_data_dir):
    """Test exit code 2 when output file cannot be written."""
    events_file = tmp_data_dir / "events.csv"
    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,auth,Login\n"
    )

    # Try to write to a non-existent directory
    output_file = tmp_data_dir / "nonexistent_dir" / "summary.csv"

    result = subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 2


# Complex Scenarios

def test_multiple_groups_with_mixed_valid_invalid_timestamps(tmp_data_dir):
    """Test processing with multiple groups and some invalid timestamps."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,auth,Login\n"
        "bad-timestamp,INFO,auth,Login\n"
        "2026-07-18T10:01:00,INFO,auth,Login\n"
        "2026-07-18T10:02:00,ERROR,payment,Invalid\n"
        "malformed,ERROR,payment,Invalid\n"
        "2026-07-18T10:03:00,ERROR,payment,Invalid\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 2

    info_row = next(r for r in rows if r["level"] == "INFO")
    assert info_row["count"] == "2"

    error_row = next(r for r in rows if r["level"] == "ERROR")
    assert error_row["count"] == "2"


def test_sample_data_from_spec(tmp_data_dir):
    """Test with the sample data mentioned in the spec."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,INFO,auth,User login successful\n"
        "2026-07-18T10:01:00,INFO,auth,User login successful\n"
        "2026-07-18T10:02:00,ERROR,payment,Invalid card\n"
        "not-a-date,WARN,api,Request timeout\n"
        "2026-07-18T10:03:00,error,api,Database connection failed\n"
        "2026-07-18T10:04:00,ERROR,api,Database connection failed\n"
        "2026-07-18T10:05:00,INFO,cache,Cache miss\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 4

    auth_logins = next(r for r in rows if r["level"] == "INFO" and r["service"] == "auth")
    assert auth_logins["count"] == "2"

    payment_errors = next(r for r in rows if r["level"] == "ERROR" and r["service"] == "payment")
    assert payment_errors["count"] == "1"

    api_errors = next(r for r in rows if r["level"] == "ERROR" and r["service"] == "api")
    assert api_errors["count"] == "2"
    assert api_errors["first_seen"] == "2026-07-18T10:03:00"
    assert api_errors["last_seen"] == "2026-07-18T10:04:00"

    cache = next(r for r in rows if r["service"] == "cache")
    assert cache["count"] == "1"


def test_whitespace_only_level_treated_as_missing(tmp_data_dir):
    """Test that whitespace-only level is treated as missing after trimming."""
    events_file = tmp_data_dir / "events.csv"
    output_file = tmp_data_dir / "summary.csv"

    events_file.write_text(
        "timestamp,level,service,message\n"
        "2026-07-18T10:00:00,   ,auth,msg\n"
        "2026-07-18T10:01:00,,auth,msg\n"
    )

    subprocess.run(
        [sys.executable, "src/logsum.py", "--input", str(events_file), "--output", str(output_file)],
        cwd=Path(__file__).parent.parent,
        check=True
    )

    rows = list(csv.DictReader(output_file.open()))
    assert len(rows) == 1
    assert rows[0]["level"] == "UNKNOWN"
    assert rows[0]["count"] == "2"
