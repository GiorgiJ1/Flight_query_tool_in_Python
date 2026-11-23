import math
import re
from datetime import datetime

ID_PATTERN = re.compile(r"[A-Za-z0-9]{2,8}")
CODE_PATTERN = re.compile(r"[A-Z]{3}")
TIME_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}")


def load_airports(path):
    codes = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                codes.add(line)
    return codes


def parse_time(text):
    if not TIME_PATTERN.fullmatch(text):
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def bad_airport(code, airports):
    return not CODE_PATTERN.fullmatch(code) or code not in airports


def validate_row(fields, airports):
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    row = [x.strip() for x in fields]
    if "" in row:
        return "MISSING_FIELD"

    flight_id, origin, des, dep, arr, price = row

    if not ID_PATTERN.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"
    if bad_airport(origin, airports):
        return "INVALID_ORIGIN"
    if bad_airport(des, airports):
        return "INVALID_DESTINATION"
    if origin == des:
        return "SAME_ORIGIN_DESTINATION"

    dep_time = parse_time(dep)
    if dep_time is None:
        return "INVALID_DEPARTURE"
    arr_time = parse_time(arr)
    if arr_time is None:
        return "INVALID_ARRIVAL"
    if arr_time <= dep_time:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        val = float(price)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(val):
        return "INVALID_PRICE"
    if val <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields):
    row = [x.strip() for x in fields]
    return {
        "flight_id": row[0],
        "origin": row[1],
        "destination": row[2],
        "departure_datetime": row[3],
        "arrival_datetime": row[4],
        "price": float(row[5]),
    }
