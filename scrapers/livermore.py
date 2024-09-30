import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "Livermore Lights"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all("li", attrs={"data-hook": "product-list-grid-item"})
    sequences = []
    for product in products:
        s = product.find("p", attrs={"data-hook": "product-item-name"}).text.strip()
        pattern = r"[^A-Za-z0-9\-\'\.()&]+"
        sequence_name = re.sub(pattern, " ", s).strip()
        product_url = urljoin(url, product.find("a")["href"])
        price_text = product.find(
            "span", attrs={"data-hook": "product-item-price-to-pay"}
        ).text
        pattern = re.compile(r"(\$\d[\d,.]*)")
        price = pattern.search(price_text)[1]  # type: ignore
        if price == "$0.00":
            price = "Free"
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    if soup.find("i", class_="NOTUSED"):
        np = soup.find("ul", class_="page-numbers")
        if np:
            next_page = np.find_all("a")[-1]  # type: ignore
            if next_page:
                response = httpx.get(next_page["href"], timeout=30.0)  # type: ignore
                next_soup = BeautifulSoup(response.text, "html.parser")
                sequences.extend(
                    get_products_from_page(soup=next_soup, url=url, vendor=vendor)
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
