import sys
import time
from datetime import datetime

import httpx

from app import Sequence, Vendor, db
from rich.console import Console
from sqlalchemy import and_, func
from sqlalchemy.exc import NoResultFound

if sys.platform == "win32":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(errors="replace")
        except Exception:
            pass

console = Console()


def http_get(
    url: str,
    *,
    retries: int = 3,
    timeout: float = 30.0,
    follow_redirects: bool = True,
    **kwargs,
) -> httpx.Response:
    """GET a page, retrying transient failures and raising on a bad final status.

    Scrapers used to parse whatever came back, so an error page looked like a
    vendor with no products. Server errors (5xx), 429 and network errors are
    retried; other 4xx responses raise immediately.
    """
    for attempt in range(1, retries + 1):
        try:
            response = httpx.get(
                url, timeout=timeout, follow_redirects=follow_redirects, **kwargs
            )
            if response.status_code != 429 and response.status_code < 500:
                response.raise_for_status()
                return response
            error = f"HTTP {response.status_code}"
        except httpx.HTTPStatusError:
            raise
        except httpx.TransportError as exc:  # includes timeouts
            error = repr(exc)
        if attempt == retries:
            raise RuntimeError(f"GET {url} failed after {retries} attempts: {error}")
        wait = 2 * attempt
        print(f"  {url} failed ({error}), retrying in {wait}s (attempt {attempt}/{retries})")
        time.sleep(wait)


def delete_sequence(store, name, last_upd):
    if vendor := Vendor.query.filter(Vendor.name == store).first():
        looking_for_name = "%{0}%".format(name)

        vendorid = vendor.id
        row_cnt = Sequence.query.filter(
            and_(
                Sequence.vendor_id == vendorid,
                Sequence.name.ilike(looking_for_name),
                Sequence.time_updated < last_upd,
            )
        ).count()
        print(
            f"Deleting {row_cnt} rows from {store} where name like {name} and last_update is prior to {last_upd}"
        )

        if row_cnt > 0:
            Sequence.query.filter(
                and_(
                    Sequence.vendor_id == vendorid,
                    Sequence.name.ilike(looking_for_name),
                    Sequence.time_updated < last_upd,
                )
            ).delete(synchronize_session="fetch")


def insert_sequence(store, url, name, price="-"):
    vendor = Vendor.query.filter(Vendor.name == store).first()
    sequence = Sequence(
        name=name,
        link=url,
        vendor_id=vendor.id,
        time_updated=datetime.now(),
        price=price,
    )
    print(f"Adding {sequence.name} [{price}]")
    seq = Sequence.query.filter(
        Sequence.link == url and Sequence.vendor_id == vendor.id
    ).first()
    if seq:
        Sequence.query.filter(
            Sequence.link == url and Sequence.vendor_id == vendor.id
        ).delete()
    else:
        seq = Sequence.query.filter(
            Sequence.name == name and Sequence.vendor_id == vendor.id
        ).first()
        Sequence.query.filter(
            Sequence.name == name and Sequence.vendor_id == vendor.id
        ).delete()
    if seq and seq.time_created:
        sequence.time_created = seq.time_created
    else:
        sequence.time_created = datetime.now()
    db.session.add(sequence)
    db.session.commit()


def create_or_update_sequences(sequences: list[Sequence]) -> None:
    for sequence in sequences:
        curr = Sequence.query.filter_by(link=sequence.link).first()
        if not curr:
            console.print(":new:", f"Adding [b]{sequence.name}[/b] at [b]{sequence.price}[/b] to database.")
            db.session.add(sequence)
        elif sequence.price == curr.price:
            console.print(
                f"[b]✓ {sequence.name}[/b] already exists with [b]{sequence.price}[/b].",
                highlight=False,
            )
            curr.time_updated = func.now()
            db.session.add(curr)
        else:
            console.print(
                ":dollar:",
                f"[b]{sequence.name}[/b] price has changed from [b]{curr.price}[/b] to [b]{sequence.price}[/b].",
                highlight=False,
            )
            curr.time_price_changed = func.now()
            curr.price = sequence.price
            db.session.add(curr)

        db.session.commit()


def get_unique_vendor(storename: str) -> Vendor:
    vendor = Vendor.query.filter_by(name=storename).all()
    if not vendor:
        raise NoResultFound(f"{storename} not found in database.")
    elif len(vendor) > 1:
        raise ValueError(f"{storename} found multiple times in database.")

    return vendor[0]
