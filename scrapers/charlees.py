import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "Charlees Props"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all("li", class_="grid__item")

    sequences = []
    for product in products:
        s = product.find("h3").text.strip()
        pattern = r"[^A-Za-z0-9\-\'\.()&]+"
        sequence_name = re.sub(pattern, " ", s).strip()
        product_url = urljoin(url, product.find("a")["href"])
        p_str = product.find("div", class_="price__container").text.strip()
        prices = re.findall(r".*\$([0-9\.]+).*", p_str)
        price = prices[0] if len(prices) == 1 else str(min(x for x in prices))
        if "$" not in price:
            price = f"${price}"
        if price == "$0.00":
            price = "Free"
        print(sequence_name, product_url, price)
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
