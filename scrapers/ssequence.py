import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "Show Sequences"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("li", attrs={"class": re.compile("product type-product")})
    sequences = []
    for product in products:
        s = product.find("h3").text.strip()
        pattern = r"[^A-Za-z0-9\-\'\.()&]+"
        sequence_name = re.sub(pattern, " ", s).strip()
        product_url = urljoin(url, product.find("a")["href"])
        p = product.find("span", class_="price").text
        pattern = r"[^0-9\.\$]+"
        price_text = re.sub(pattern, " ", p).strip()
        pattern = re.compile(r"(\$[0-9]+).*(\$[0-9]+)")
        try:
            price = pattern.search(price_text)[2]  # type: ignore
        except Exception:
            price = price_text
        if price == "$0":
            price = "Free"
            print("price", price)
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    next_tag = soup.find(class_="NOTUSED")
    if next_tag:
        np = next_tag.find("a")
        if np:
            next_page = urljoin(url, np["href"])  # type: ignore
            print(f"Loading {next_page}")
            response = httpx.get(next_page)  # type: ignore
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
        response = httpx.get(url.url)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
