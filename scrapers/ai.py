import httpx
import re
from urllib.parse import urljoin

from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "Animated Illumination"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all(class_="grid__item")

    sequences = []
    pattern = r"[^A-Za-z0-9\-\'\.()&]+"
    for product in products:
        try:
            s = product.find(class_="card__heading h5").text
        except:
            continue
        sequence_name = re.sub(pattern, " ", s).strip()
        product_url = urljoin(url, product.find("a")["href"])

        price_str = product.find(class_="price__sale").text.strip()
        price = f'${price_str.rsplit("$")[-1].split(" ")[0]}'
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
        response = httpx.get(url.url, headers={'User-Agent': 'Mozilla/6.0'}, timeout=30.0)

        print(f"Loading {url.url}")
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
