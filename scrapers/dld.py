from urllib.parse import urljoin

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor

storename = "Dancing Lights Design"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all('li', attrs={'data-hook': 'product-list-grid-item'})
    sequences = []

    for product in products:
        sequence_name = product.find("p", attrs={'data-hook': 'product-item-name'}).text.strip()
        product_url = urljoin(url, product.find("a")["href"].split("?")[0])
        span_element = product.find('span', attrs={'data-hook': 'product-item-price-to-pay'})
        price = span_element.text

        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    #links = soup.select("a[role=link]")
    #next_page_soup = [
     #   x
      #  for x in links
       # if "wt-is-disabled" not in x.get("class") and "next" in x.text.lower()  # type: ignore
    #]

    #if next_page_soup:
     #   response = httpx.get(next_page_soup[0]["href"], timeout=30.0)  # type: ignore
      #  next_soup = BeautifulSoup(response.text, "html.parser")
       # sequences.extend(get_products_from_page(soup=next_soup, url=url, vendor=vendor))

    return sequences


def main() -> None:
    print(f"Loading {storename}")
    vendor = get_unique_vendor(storename)

    for url in vendor.urls:
        # Using page saved since I was flagged as robot
        response = httpx.get(
            url.url, headers={"User-Agent": "Mozilla/6.0"}, timeout=30.0
        )

        print(f"Loading {url.url}")
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
