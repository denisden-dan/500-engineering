import sys
import csv
from datetime import datetime
from collections import defaultdict


def parse_args():
    """Parse command-line arguments."""
    input_file = "data/events.csv"
    output_file = "data/summary.csv"
    positional = []

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--input":
            i += 1
            if i < len(args):
                input_file = args[i]
            i += 1
        elif args[i] == "--output":
            i += 1
            if i < len(args):
                output_file = args[i]
            i += 1
        else:
            positional.append(args[i])
            i += 1

    if len(positional) >= 1:
        input_file = positional[0]
    if len(positional) >= 2:
        output_file = positional[1]

    return input_file, output_file


def normalize_text(value):
    """Trim and return text, or empty string if None."""
    return value.strip() if value else ""


def parse_timestamp(ts_str):
    """Parse ISO 8601 timestamp. Return datetime or None if malformed."""
    if not ts_str or not ts_str.strip():
        return None
    try:
        return datetime.fromisoformat(ts_str.strip())
    except (ValueError, TypeError):
        return None


def main():
    input_file, output_file = parse_args()

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                print("Error: Empty input file or missing header", file=sys.stderr)
                sys.exit(1)

            required_cols = {"timestamp", "level", "service", "message"}
            if not required_cols.issubset(set(reader.fieldnames)):
                print(f"Error: Missing required columns. Required: {required_cols}", file=sys.stderr)
                sys.exit(1)

            groups = defaultdict(lambda: {"count": 0, "first_seen": None, "last_seen": None})

            for row in reader:
                ts_str = normalize_text(row.get("timestamp", ""))
                level = normalize_text(row.get("level", "")) or "UNKNOWN"
                level = level.upper()
                service = normalize_text(row.get("service", ""))
                message = normalize_text(row.get("message", ""))

                ts = parse_timestamp(ts_str)
                if ts is None:
                    continue

                key = (level, service, message)
                groups[key]["count"] += 1

                if groups[key]["first_seen"] is None or ts < groups[key]["first_seen"]:
                    groups[key]["first_seen"] = ts
                if groups[key]["last_seen"] is None or ts > groups[key]["last_seen"]:
                    groups[key]["last_seen"] = ts

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: Failed to read input file: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["level", "service", "message", "count", "first_seen", "last_seen"])

            for (level, service, message), agg in sorted(groups.items()):
                writer.writerow([
                    level,
                    service,
                    message,
                    agg["count"],
                    agg["first_seen"].isoformat(),
                    agg["last_seen"].isoformat(),
                ])

    except Exception as e:
        print(f"Error: Failed to write output file: {e}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
