import re

import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequences, get_unique_vendor


storename = "Charlees Props"


def get_products_from_page(
    soup: BeautifulSoup, url: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find("table").find_all("tr")[1:]

    sequences = []
    for row in products:
        sequence_name = row.find_all('td')[0].text.strip()

        pattern = r'^(.*?)\([^)]*\)'  # Skip the notes
        match = re.search(pattern, sequence_name)
        if match:
            sequence_name = match.group(1).strip()

        a_element = row.find_all('td')[1].find("a")
        if a_element:
            product_url = a_element['href']
        else:
            continue
        price = "Free"
        print(sequence_name, ", URL", product_url)
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
        print(f"Loading {url.url}")
        response = httpx.get(url.url, timeout=30.0)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, url=url.url, vendor=vendor)

        create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
