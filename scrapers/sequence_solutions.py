import httpx
from app import Sequence, Vendor
from bs4 import BeautifulSoup
from my_funcs import create_or_update_sequence

storename = "Sequence Solutions"


def get_products_from_page(
    soup: BeautifulSoup, link: str, vendor: Vendor
) -> list[Sequence]:
    products = soup.find_all("div", class_="edd_download item")
    sequences = []
    for product in products:
        sequence_name = product.find("a", itemprop="url").text
        product_url = product.find("a", itemprop="url")["href"]
        price = product.find("span", class_="edd_price").text
        sequences.append(
            Sequence(
                name=sequence_name, vendor_id=vendor.id, link=product_url, price=price
            )
        )

    next_page = soup.find(class_="next")
    if next_page:
        response = httpx.get(next_page["href"])  # type: ignore
        next_soup = BeautifulSoup(response.text, "html.parser")
        sequences.extend(
            get_products_from_page(soup=next_soup, link=link, vendor=vendor)
        )

    return sequences


def main() -> None:
    print(f"Loading %s" % storename)

    vendor = Vendor.query.filter_by(name=storename).all()
    if not vendor:
        raise Exception(f"{storename} not found in database.")
    elif len(vendor) > 1:
        raise Exception(f"{storename} found multiple times in database.")

    vendor = vendor[0]
    baseurls = vendor.urls
    for baseurl in baseurls:
        print(f"Loading %s" % baseurl.url)
        response = httpx.get(baseurl.url)
        soup = BeautifulSoup(response.text, "html.parser")
        sequences = get_products_from_page(soup=soup, link=baseurl.url, vendor=vendor)

        create_or_update_sequence(sequences)


if __name__ == "__main__":
    main()
