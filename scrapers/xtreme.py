import re
from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "xTreme Sequences"
BASEURL = "https://www.xtremesequences.com/index.php?"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("li", class_="cNexusProduct")

    sequences = []
    for product in products:
        sequence_name = product.find("a", class_="").text.strip()
        product_url = urljoin(url, product.find("a")["href"])
        p = product.find("span", class_="cNexusPrice").text
        pattern = re.compile(r"(\d[\d.]+)")
        p_text = pattern.search(p)
        price = p_text[1] if p_text else "Free"
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )
# #elPagination_b1ae5437920375879c1ec73544e75a71_1184440054 > li.ipsPagination_next
    next_page_anchor = soup.find_all("li", class_="ipsPagination_next")
    if next_page_anchor and not soup.find_all("li", class_="ipsPagination_next ipsPagination_inactive"):
        next_page = soup.find("a", attrs={"rel":"next"})
        response = httpx.get(next_page["href"], timeout=30.0)  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(soup=next_soup, url=url, vendor=vendor))

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
