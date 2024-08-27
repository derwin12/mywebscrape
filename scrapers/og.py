import re

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "OG Sequences"


def get_price_from_product_page(product_url: str) -> str:
    response = httpx.get(product_url, follow_redirects=True, timeout=30.0)
    soup = BeautifulSoup(response.text, "html.parser")

    p_str = soup.find_all(class_="edd_price_option_price")
    if p_str:
        prices = []
        for i in p_str:
            price = re.findall(r".*\$([0-9\.]+).*", i.text)
            prices.append(float(price[0]))
        if not prices:
            prices = [0.0]
        price = min(prices)
    else:
        p_str = soup.find(class_="edd-add-to-cart-label")
        price = float(re.findall(r".*\$([0-9\.]+).*", p_str.text)[0])
    return f"${price:.2f}"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:

    products = soup.find_all("div", class_="elementor-widget-container")

    sequences = []
    for product in products:
        if product.find("a"):
            sequence_name = product.text.replace("*", "").strip()
            product_url = product.find("a")["href"]

            if "ogsequences" not in product_url:
                try:
                    seq_num = re.search(".*p=(\d+).*", product_url)[1]  # type: ignore
                    product_url = (
                    f"http://ogsequences.com/?post_type=download&p={seq_num}&preview=true"
                    )
                except:
                    print("Unable to process ", product_url)
                    continue
        # Price is on a secondary page.
            try:
                price = get_price_from_product_page(product_url)
            except:
                price = "Unknown"
                print("Unable to get price for ", product_url)
            sequences.append(
                Sequence(
                    name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
                )
            )

    next_page = soup.find(class_="next")
    if next_page:
        print(f"Loading {next_page['href']}")  # type: ignore
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
