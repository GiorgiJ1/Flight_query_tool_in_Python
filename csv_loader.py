import csv
import os

from validator import validate_row, to_record


def parse_files(paths, arp):
    r = []
    errors = []
    seen = set()

    for path in paths:
        n = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            for number, line in enumerate(f, 1):
                text = line.rstrip("\r\n")
                if number == 1:
                    continue
                if text.strip() == "" or text.strip().startswith("#"):
                    continue

                try:
                    fields = next(csv.reader([text]))
                except (csv.Error, StopIteration):
                    fields = []

                code = validate_row(fields, arp)
                if code is None:
                    record = to_record(fields)
                    key = (record["flight_id"], record["departure_datetime"])
                    if key in seen:
                        code = "DUPLICATE_FLIGHT"
                    else:
                        seen.add(key)
                        r.append(record)

                if code is not None:
                    errors.append(f"{n}:{number}: {code} | {text}")

    return r, errors
