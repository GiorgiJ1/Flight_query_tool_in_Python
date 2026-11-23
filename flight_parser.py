import argparse
import json
import logging
import os
import sys
from datetime import datetime

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "251ADB123"
FIRST_NAME = "Giorgi"
LAST_NAME = "Janikashvili"


def get_args(argv):
    parser = argparse.ArgumentParser(description="Flight query tool")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", help="parse one CSV file")
    source.add_argument("-d", metavar="FOLDER", help="parse all CSV files in a folder")
    source.add_argument("-j", metavar="FILE", help="load an existing JSON database")
    parser.add_argument("-a", metavar="FILE", help="airport list file")
    parser.add_argument("-o", metavar="FILE", help="output path for the database")
    parser.add_argument("-q", metavar="FILE", help="query file")
    parser.add_argument("-r", metavar="FOLDER", default=".", help="response folder")
    args = parser.parse_args(argv)

    if args.j is None and args.a is None:
        parser.error("-a is required with -i and -d")
    if args.j is not None and args.o is not None:
        parser.error("-o cannot be used with -j")
    return args


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_db(path):
    d = read_json(path)
    if not isinstance(d, list) or not all(isinstance(x, dict) for x in d):
        raise ValueError(f"{path} is not a JSON aray of objects")
    return d


def load_queries(path):
    d = read_json(path)
    if not isinstance(d, (dict, list)):
        raise ValueError(f"{path} is not a query object or an aray")
    return d


def find_csv_files(folder):
    names = sorted(n for n in os.listdir(folder) if n.endswith(".csv"))
    paths = [os.path.join(folder, n) for n in names]
    paths = [p for p in paths if os.path.isfile(p)]
    if not paths:
        raise ValueError(f"no csv files in {folder}")
    return paths


def write_errors(errors, log_path):
    l = logging.getLogger("flight_parser")
    l.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    l.addHandler(handler)
    try:
        for message in errors:
            l.warning(message)
    finally:
        l.removeHandler(handler)
        handler.close()


def main(argv=None):
    try:
        args = get_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0

    try:
        if args.j is not None:
            db = load_db(args.j)
        else:
            airp = load_airports(args.a)
            if args.i is not None:
                paths = [args.i]
            else:
                paths = find_csv_files(args.d)
            db, errors = parse_files(paths, airp)

            out_path = args.o or "db.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
            folder = os.path.dirname(out_path)
            write_errors(errors, os.path.join(folder, "errors.log"))
            print(f"{len(db)} valid rows, {len(errors)} invalid rows")

        if args.q is not None:
            q = load_queries(args.q)
            answ = run_queries(db, q)
            stamp = datetime.now().strftime("%Y%m%d_%H%M")
            name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
            with open(os.path.join(args.r, name), "w", encoding="utf-8") as f:
                json.dump(answ, f, indent=2)
    except (OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
