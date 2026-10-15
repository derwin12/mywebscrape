import html
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "XLights Sequences For Sale"


def get_products(url: str, vendor: Vendor) -> list[Sequence]:
    sequences = []
    page = 1
    total_pages = 1
    while page <= total_pages:
        response = httpx.get(
            urljoin(url, "/wp-json/wc/store/v1/products"),
            params={"per_page": 100, "page": page},
            timeout=60.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        total_pages = int(response.headers.get("x-wp-totalpages", 1))

        for product in response.json():
            prices = product["prices"]
            amount = int(prices["price"] or 0) / 10 ** prices["currency_minor_unit"]
            price = f"${amount:.2f}" if amount > 0 else "Free"

            print(product["permalink"], price)
            sequences.append(
                Sequence(
                    name=html.unescape(product["name"]).strip(),
                    vendor_id=vendor.id,
                    link=product["permalink"],
                    price=price,
                )
            )
        page += 1
    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        print(f"Loading {url.url}")
        create_or_update_sequences(get_products(url.url, vendor))


if __name__ == "__main__":
    main()
