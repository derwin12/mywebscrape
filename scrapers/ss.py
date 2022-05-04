import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "Showstopper Sequences"


BASEURL = "https://showstoppersequences-com.3dcartstores.com/"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("div", class_="product-item item-template-0 alternative")

    sequences = []
    for product in products:
        sequence_name = product.find("div", class_="name").find("a").text
        # song, artist = sequence_name.split(" - ")
        product_url = urljoin(BASEURL, product.find("a")["href"])
        p_text = product.find("div", class_="price").text.strip()
        pattern = r"[^0-9\.\$]+"
        price_text = re.sub(pattern, " ", p_text).strip()
        pattern = re.compile(r"(\$[0-9]+).*(\$[0-9]+)")
        try:
            price = pattern.search(price_text)[2]  # type: ignore
        except Exception:
            try:
                pattern = re.compile(r".*(\$[0-9]+\.[0-9]+).*")
                price = pattern.search(p_text)[1]  # type: ignore
            except:
                price = "Free"

        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )
    next_page = soup.find("a", text="Next Page")
    if next_page:
        next_page_url = urljoin(url, next_page["href"])  # type: ignore
        print(f"Loading {next_page_url}")
        response = httpx.get(next_page_url, timeout=15)
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(soup=next_soup, url=url, vendor=vendor))

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
