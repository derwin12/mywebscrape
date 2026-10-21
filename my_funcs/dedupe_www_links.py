"""Remove sequences saved twice under www and non-www versions of one link.

Keeps the older row of each pair. Shows what it would delete unless --apply
is given.

    python my_funcs/dedupe_www_links.py [path/to/sequences.db] [--apply]
"""
import sqlite3
import sys

DUPES = """
SELECT keep.id, drop_.id, drop_.name, drop_.link
FROM sequence keep
JOIN sequence drop_
  ON keep.vendor_id = drop_.vendor_id
 AND keep.id <> drop_.id
 AND replace(keep.link, '://www.', '://') = replace(drop_.link, '://www.', '://')
 AND (keep.time_created < drop_.time_created
      OR (keep.time_created = drop_.time_created AND keep.id < drop_.id))
"""


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--apply"]
    apply = "--apply" in sys.argv
    db_path = args[0] if args else "app/sequences.db"

    con = sqlite3.connect(db_path)
    rows = con.execute(DUPES).fetchall()
    drop_ids = sorted({r[1] for r in rows})
    for _, drop_id, name, link in rows:
        print(f"{'Deleting' if apply else 'Would delete'} {drop_id}: {name} -> {link}")
    print(f"{len(drop_ids)} duplicate rows in {db_path}")

    if apply and drop_ids:
        con.executemany("DELETE FROM sequence WHERE id = ?", [(i,) for i in drop_ids])
        con.commit()
        print("Deleted. Run my_funcs/update_vendor_counts.py to refresh vendor counts.")
    con.close()


if __name__ == "__main__":
    main()
