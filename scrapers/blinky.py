import httpx
import re
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "BlinkySequences"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all(class_="product")
    sequences = []
    for product in products:
        sequence_name_text = product.find("h2", class_="woocommerce-loop-product__title")
        if not sequence_name_text:
            continue

        sequence_name = sequence_name_text.text.strip()
        product_url = product.find("a")["href"]

        price_string = product.find(class_="woocommerce-Price-amount")
        if price_string:
            price = price_string.text.strip()
        else:
            price = "Free"

        if price == "$0.00":
            price = "Free"

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
        response = httpx.get(url.url, timeout=30.0)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
