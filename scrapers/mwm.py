import re
from urllib.parse import urljoin

import cfscrape
import httpx


from bs4 import BeautifulSoup
from app import Sequence, Vendor

from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "Music with Motion"
BASEURL = 'https://musicwithmotion.com/'
FileDir = "MusicWithMotion"


def get_products_from_page(
        soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("div", class_="product-layout")
    sequences = []

    for product in products:
        sequence_name = product.find("h4").text
        product_url = product.find("a")["href"]
        p = product.find("p", class_="price").text
        # <p class="price">$35.00 <span class="price-tax">Ex Tax:$35.00</span>
        pattern = r"[^0-9\.\$]+"
        pt = re.sub(pattern, " ", p).strip()
        price = pt.split(" ")[0].lstrip(' ')

        if price == "$0":
            price = "Free"

        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    pagination_div = soup.find('div', class_='pagination-wrapper')
    if pagination_div:
        active_li = pagination_div.find('li', class_='active')
        if active_li:
            next_li = active_li.find_next_sibling('li')
            if next_li:
                next_link = next_li.find('a')
                print('Processing next page: ' + next_link['href'])
                response = httpx.get(next_link['href'], timeout=30.0)  # type: ignore
                next_soup = BeautifulSoup(response.text, "html.parser")
                sequences.extend(get_products_from_page(soup=next_soup, url=url, vendor=vendor))

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    # Create a Cloudflare scraper instance
    scraper = cfscrape.create_scraper()

    for url in vendor.urls:
        print(f"Loading {url.url}")
        response = scraper.get(url.url, timeout=30.0)
        soup = BeautifulSoup(response.content, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
