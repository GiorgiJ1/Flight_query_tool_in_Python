from validator import parse_time

FIELDS = ("flight_id", "origin", "destination",
          "departure_datetime", "arrival_datetime", "price")
TEXT_KEYS = ("flight_id", "origin", "destination")
TIME_KEYS = ("departure_datetime", "arrival_datetime")
NUMBER_KEYS = ("price", "min_price")


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def is_valid(qeury):
    if not isinstance(qeury, dict):
        return False

    for key, value in qeury.items():
        if key in TEXT_KEYS:
            ok = isinstance(value, str)
        elif key in TIME_KEYS:
            ok = isinstance(value, str) and parse_time(value) is not None
        elif key in NUMBER_KEYS:
            ok = is_number(value)
        elif key == "sort_by":
            ok = value in FIELDS
        elif key == "order":
            ok = value in ("asc", "desc")
        elif key == "limit":
            ok = (isinstance(value, int) and not isinstance(value, bool)
                  and value >= 0)
        else:
            ok = False
        if not ok:
            return False

    if "order" in qeury and "sort_by" not in qeury:
        return False
    return True


def fits(flight, qeury):
    for key in TEXT_KEYS:
        if key in qeury and flight[key] != qeury[key]:
            return False
    if "departure_datetime" in qeury:
        if flight["departure_datetime"] < qeury["departure_datetime"]:
            return False
    if "arrival_datetime" in qeury:
        if flight["arrival_datetime"] > qeury["arrival_datetime"]:
            return False
    if "price" in qeury and flight["price"] > qeury["price"]:
        return False
    if "min_price" in qeury and flight["price"] < qeury["min_price"]:
        return False
    return True


def run_query(db, query):
    if not is_valid(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    found = [flight for flight in db if fits(flight, query)]

    if "sort_by" in query:
        k = query["sort_by"]
        r = query.get("order", "asc") == "desc"
        found = sorted(found, key=lambda flight: flight[k], reverse=r)

    if "limit" in query:
        found = found[:query["limit"]]

    return {"query": query, "matches": found}


def run_queries(db, qeuries):
    if isinstance(qeuries, dict):
        queries = [qeuries]
    return [run_query(db, q) for q in qeuries]
