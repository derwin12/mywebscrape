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

    products = soup.find_all("div", class_="edd_download_inner")
    sequences = []
    pattern = r"[^A-Za-z0-9\-\'\.()&]+"
    for product in products:
        s = product.find(class_="edd_download_title").text
        sequence_name = re.sub(pattern, " ", s).strip()
        product_url = urljoin(url, product.find("a")["href"])
        if product.find("div", class_="edd_price_options"):
            p_text = product.find("div", class_="edd_price_options")

            p_text2 = p_text.find("input")["data-price"]
            price = p_text.find("input")["data-price"] if p_text2 else "-"
        else:
            p_text = product.find("a", class_="edd-add-to-cart")
            price = p_text["data-price"] if p_text else "Free"

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
        # Using page saved since I was flagged as robot
        response = httpx.get(url.url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30.0)

        print(f"Loading {url.url}")
        soup = BeautifulSoup(response, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
