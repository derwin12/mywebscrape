import re
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from app import BaseUrl, Vendor
from bs4 import BeautifulSoup
from my_funcs import insert_sequence

storename = "OG Sequences"


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_price_from_product_page(product_url: str) -> str:
    response = httpx.get(product_url, follow_redirects=True)
    soup = BeautifulSoup(response.text, "html.parser")

    prices = soup.find_all("meta", itemprop="price")
    price = max([float(i["content"]) for i in prices])
    return f"${price:.2f}"


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:

    products = soup.find_all("div", class_="elementor-image")

    sequences = []
    for product in products:
        sequence_name = product.text.replace("*", "").strip()
        product_url = urljoin(url, product.find("a")["href"])

        if "ogsequences" not in product_url:
            seq_num = re.search(".*p=(\d+).*", product_url).group(1)  # type: ignore
            product_url = (
                f"http://ogsequences.com/?post_type=download&p={seq_num}&preview=true"
            )

        # Price is on a secondary page.
        price = get_price_from_product_page(product_url)
        sequences.append(Sequence(sequence_name, product_url, price))

    next_page = soup.find(class_="next")
    if next_page:
        response = httpx.get(next_page["href"])  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(get_products_from_page(next_soup, url))

    return sequences


def main() -> None:
    print(f"Loading %s" % storename)
    baseurls = (
        BaseUrl.query.join(Vendor)
        .add_columns(Vendor.name.label("vendor_name"))
        .filter(Vendor.name == storename)
        .order_by(BaseUrl.id)
        .all()
    )
    for baseurl in baseurls:
        print(f"Loading %s" % baseurl[0].url)
        response = httpx.get(baseurl[0].url)
        soup = BeautifulSoup(response.text, "html.parser")
        products = get_products_from_page(soup, baseurl[0].url)

        for product in products:
            insert_sequence(
                store=storename, url=product.url, name=product.name, price=product.price
            )


if __name__ == "__main__":
    main()
