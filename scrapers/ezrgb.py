import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "EZRGB"

NAME_CLEANER = r"[^A-Za-z0-9\-\'\.()&]+"


def get_products(url: str, vendor: Vendor) -> list[Sequence]:
    response = httpx.get(
        urljoin(url, "/api/getSequenceList"),
        timeout=60.0,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    sequences = []
    for product in response.json():
        name = re.sub(NAME_CLEANER, " ", product["sequenceTitle"]).strip()
        sequence_name = re.sub(r"\(.*?\)", "", name).strip()
        product_url = urljoin(url, product["sequenceUrl"])

        amount = float(product["price"] or 0)
        price = f"${amount:.2f}" if amount > 0 else "Free"

        print(product_url, price)
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )
    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        create_or_update_sequences(get_products(url.url, vendor))


if __name__ == "__main__":
    main()
