import argparse
import csv
import re
from pathlib import Path


PAGE_COLUMNS = (
    "slug",
    "page",
    "page path",
    "page_path",
    "url",
    "landing page",
    "landing_page",
    "post",
    "title",
)
VIEW_COLUMNS = (
    "views",
    "pageviews",
    "page views",
    "screenpageviews",
    "screen page views",
    "sessions",
)
RPM_COLUMNS = (
    "rpm",
    "page rpm",
    "page_rpm",
    "session rpm",
    "session_rpm",
    "revenue per mille",
)
REVENUE_COLUMNS = (
    "revenue",
    "estimated revenue",
    "total revenue",
    "earnings",
)


def normalize_header(value):
    value = value.strip().lower()
    value = re.sub(r"[\s\-]+", " ", value)
    value = value.replace("_", " ")
    return value


def clean_number(value):
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    text = text.replace(",", "")
    text = re.sub(r"[^0-9.\-]", "", text)
    if not text or text in {"-", ".", "-."}:
        return None

    try:
        return float(text)
    except ValueError:
        return None


def find_column(headers, candidates, required=True):
    normalized = {normalize_header(header): header for header in headers}
    normalized_candidates = {normalize_header(candidate) for candidate in candidates}

    for candidate in normalized_candidates:
        if candidate in normalized:
            return normalized[candidate]

    for normalized_header, original_header in normalized.items():
        if any(candidate in normalized_header for candidate in normalized_candidates):
            return original_header

    if required:
        raise ValueError(
            "Could not find a required column. Looked for one of: "
            + ", ".join(candidates)
        )
    return None


def read_rows(csv_path):
    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as file:
        sample = file.read(4096)
        file.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        reader = csv.DictReader(file, dialect=dialect)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No rows found in {csv_path}")

    return rows, reader.fieldnames or []


def analyze(csv_path, top_views, lowest_count, min_views):
    rows, headers = read_rows(csv_path)

    page_col = find_column(headers, PAGE_COLUMNS)
    view_col = find_column(headers, VIEW_COLUMNS)
    rpm_col = find_column(headers, RPM_COLUMNS, required=False)
    revenue_col = find_column(headers, REVENUE_COLUMNS, required=False)

    if rpm_col is None and revenue_col is None:
        raise ValueError(
            "Could not find an RPM column or a revenue column to compute RPM."
        )

    analyzed = []
    skipped = 0

    for row in rows:
        page = (row.get(page_col) or "").strip()
        views = clean_number(row.get(view_col))
        rpm = clean_number(row.get(rpm_col)) if rpm_col else None
        revenue = clean_number(row.get(revenue_col)) if revenue_col else None

        if not page or views is None or views < min_views:
            skipped += 1
            continue

        if rpm is None:
            if revenue is None:
                skipped += 1
                continue
            rpm = revenue / views * 1000 if views > 0 else None

        if rpm is None:
            skipped += 1
            continue

        analyzed.append(
            {
                "page": page,
                "views": views,
                "rpm": rpm,
                "revenue": revenue,
            }
        )

    top_by_views = sorted(analyzed, key=lambda item: item["views"], reverse=True)[:top_views]
    lowest_rpm = sorted(top_by_views, key=lambda item: item["rpm"])[:lowest_count]

    return {
        "rows": lowest_rpm,
        "top_by_views": top_by_views,
        "skipped": skipped,
        "columns": {
            "page": page_col,
            "views": view_col,
            "rpm": rpm_col,
            "revenue": revenue_col,
        },
    }


def write_csv(rows, output_path):
    with Path(output_path).open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["rank", "page", "views", "rpm", "revenue"])
        writer.writeheader()
        for index, row in enumerate(rows, start=1):
            writer.writerow(
                {
                    "rank": index,
                    "page": row["page"],
                    "views": round(row["views"], 2),
                    "rpm": round(row["rpm"], 4),
                    "revenue": "" if row["revenue"] is None else round(row["revenue"], 4),
                }
            )


def print_table(rows):
    print("\nLowest RPM pages among top-view pages")
    print("-" * 92)
    print(f"{'#':>2}  {'Views':>10}  {'RPM':>10}  Page")
    print("-" * 92)
    for index, row in enumerate(rows, start=1):
        page = row["page"]
        if len(page) > 62:
            page = page[:59] + "..."
        print(f"{index:>2}  {row['views']:>10.0f}  {row['rpm']:>10.2f}  {page}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find high-view pages with the lowest RPM from a CSV export."
    )
    parser.add_argument("csv_path", help="CSV dataset path.")
    parser.add_argument(
        "--top-views",
        type=int,
        default=50,
        help="Only inspect this many highest-view pages. Default: 50.",
    )
    parser.add_argument(
        "--lowest",
        type=int,
        default=20,
        help="Show this many lowest-RPM pages from the top-view set. Default: 20.",
    )
    parser.add_argument(
        "--min-views",
        type=float,
        default=1,
        help="Ignore rows below this view count. Default: 1.",
    )
    parser.add_argument(
        "--output",
        default="low_rpm_top_pages.csv",
        help="Output CSV path. Default: low_rpm_top_pages.csv.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = analyze(
        csv_path=args.csv_path,
        top_views=args.top_views,
        lowest_count=args.lowest,
        min_views=args.min_views,
    )

    print("Detected columns:")
    for label, column in result["columns"].items():
        print(f"- {label}: {column or 'not found'}")

    print_table(result["rows"])
    write_csv(result["rows"], args.output)
    print(f"\nSaved: {args.output}")
    print(f"Rows skipped because of missing/invalid data: {result['skipped']}")
