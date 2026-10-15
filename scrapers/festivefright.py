from urllib.parse import urljoin

from app import Sequence, Vendor
from my_funcs import create_or_update_sequences, get_unique_vendor, http_get

storename = "Festive Fright Sequences"


def get_products(url: str, vendor: Vendor) -> list[Sequence]:
    sequences = []
    page = 1
    while True:
        response = http_get(
            urljoin(url, "/products.json"),
            params={"limit": 250, "page": page},
            timeout=60.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        products = response.json()["products"]
        if not products:
            break

        for product in products:
            sequence_name = product["title"].removeprefix("Sequence:").strip()
            product_url = urljoin(url, f"/products/{product['handle']}")
            amount = float(product["variants"][0]["price"])
            price = f"${amount:.2f}" if amount > 0 else "Free"

            print(product_url, price)
            sequences.append(
                Sequence(
                    name=sequence_name,
                    vendor_id=vendor.id,
                    link=product_url,
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
