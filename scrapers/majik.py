import re
from urllib.parse import urljoin

from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor, http_get

storename = "Majik Show"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    sequences = []
    for product in soup.find_all("article", class_="store-card"):
        sequence_name = product.find("h3").text.strip()
        product_url = urljoin(url, product.find("a", class_="store-card-link")["href"])

        price_element = product.find(class_="store-price")
        match = re.search(r"\$\d+\.\d{2}", price_element.text) if price_element else None
        price = match.group() if match else "Free"
        if price == "$0.00":
            price = "Free"

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
        response = http_get(
            url.url,
            timeout=60.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        soup = BeautifulSoup(response.text, "html.parser")
        create_or_update_sequences(
            get_products_from_page(soup=soup, url=url.url, vendor=vendor)
        )


if __name__ == "__main__":
    main()
