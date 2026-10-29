"""Remove sequences a vendor's scraper has not seen for more than 180 days.

Scrapers bump time_updated each time they see a link, so a link that
vendor no longer lists stops being updated. Each row is compared with the
newest time_updated of its own vendor, not with today, so a vendor whose
scraper is broken (and so updates nothing) loses no rows.

GoogleDrive is never touched: several scrapers share that vendor name
but only gdNew runs on a schedule, so the others' rows would look stale.

A vendor that would lose more than half its rows is skipped with a
warning: that usually means its scraper is missing part of the site, not
that the vendor pulled most of its catalog.

Scrapers can also quietly miss listings that are still for sale, so with
--verify each stale link is fetched and only clearly dead ones are
deleted: a 404/410, a "not found" page, a redirect to a "delete" page, or
a redirect to a link that already has its own row. Anything else (still
live, moved elsewhere, timeouts, blocked) is listed and left alone.

Shows what it would delete unless --apply is given.

    python my_funcs/prune_stale_links.py [path/to/sequences.db] [--days N] [--verify] [--apply]
"""
import argparse
import re
import sqlite3
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import httpx

MAX_SHARE = 0.5  # skip a vendor that would lose more than this share of its rows

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
}
NOT_FOUND_TITLE = re.compile(r"not found|\b404\b|sequence - delete", re.I)

STALE = """
WITH last_seen AS (
    SELECT vendor_id, max(time_updated) AS newest, count(*) AS total
    FROM sequence
    GROUP BY vendor_id
)
SELECT s.id, v.name, s.name, s.link, s.time_updated, l.newest, l.total
FROM sequence s
JOIN last_seen l ON l.vendor_id = s.vendor_id
JOIN vendor v ON v.id = s.vendor_id
WHERE s.time_updated < datetime(l.newest, ?)
  AND v.name <> 'GoogleDrive'
ORDER BY v.name, s.time_updated
"""


def normalize(link: str) -> str:
    """Compare links ignoring case, a leading www. and a trailing slash."""
    return link.lower().replace("://www.", "://").rstrip("/")


def check_link(link: str, known_links: Counter) -> tuple[bool, str]:
    """Fetch a link and return (clearly dead, reason)."""
    if known_links[normalize(link)] > 1:
        return True, "duplicate of another row with the same link"
    for _ in range(2):
        try:
            response = httpx.get(link, headers=HEADERS, timeout=25, follow_redirects=True)
            break
        except httpx.HTTPError as exc:
            error = type(exc).__name__
    else:
        return False, f"error {error}"

    status = response.status_code
    if status in (404, 410):
        return True, f"HTTP {status}"
    if status != 200:
        return False, f"HTTP {status}"

    match = re.search(r"<title[^>]*>(.*?)</title>", response.text, re.S | re.I)
    title = match.group(1).strip() if match else ""
    if NOT_FOUND_TITLE.search(title):
        return True, f"not found page ({title[:60]})"

    final = str(response.url)
    if normalize(final) == normalize(link):
        return False, "still live"
    if "/delete." in final:
        return True, f"redirects to delete page {final}"
    if normalize(final) in known_links:
        return True, f"duplicate of {final}"
    return False, f"moved to {final}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("db_path", nargs="?", default="app/sequences.db")
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument("--verify", action="store_true", help="fetch each link first")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    verb = "Deleting" if args.apply else "Would delete"

    con = sqlite3.connect(args.db_path)
    rows = con.execute(STALE, (f"-{args.days} days",)).fetchall()
    stale = Counter(r[1] for r in rows)
    totals = {r[1]: r[6] for r in rows}
    skipped = {v for v, n in stale.items() if n > MAX_SHARE * totals[v]}
    for vendor in sorted(skipped):
        print(
            f"WARNING: skipping {vendor}: {stale[vendor]} of {totals[vendor]} rows look "
            "stale; check its scraper"
        )
    rows = [r for r in rows if r[1] not in skipped]

    if args.verify:
        known_links = Counter(normalize(r[0]) for r in con.execute("SELECT link FROM sequence"))
        print(f"Checking {len(rows)} links...")
        with ThreadPoolExecutor(8) as pool:
            results = list(pool.map(lambda r: check_link(r[3], known_links), rows))
        for row, (dead, reason) in zip(rows, results):
            if not dead:
                print(f"Keeping {row[0]} [{row[1]}] {row[2]} -> {row[3]}: {reason}")
        dead_rows = [row for row, (dead, _) in zip(rows, results) if dead]
        for row, (dead, reason) in zip(rows, results):
            if dead:
                print(f"{verb} {row[0]} [{row[1]}] {row[2]} -> {row[3]}: {reason}")
        print(f"{len(rows) - len(dead_rows)} stale links kept because they did not look dead")
        rows = dead_rows
    else:
        for seq_id, vendor, name, link, seen, newest, _ in rows:
            print(
                f"{verb} {seq_id} [{vendor}] {name} -> {link} "
                f"(last seen {seen}, vendor newest {newest})"
            )

    for vendor, count in Counter(r[1] for r in rows).most_common():
        print(f"{count:6} {vendor}")
    print(f"{len(rows)} rows to delete (not seen for over {args.days} days) in {args.db_path}")

    if args.apply and rows:
        con.executemany("DELETE FROM sequence WHERE id = ?", [(r[0],) for r in rows])
        con.commit()
        print("Deleted. Run my_funcs/update_vendor_counts.py to refresh vendor counts.")
    con.close()


if __name__ == "__main__":
    main()
