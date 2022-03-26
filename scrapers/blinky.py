import requests
from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor

storename = 'BlinkySequences'


def main() -> None:
    baseurls = BaseUrl.query.join(Vendor).add_columns(Vendor.name.label("vendor_name")) \
        .filter(Vendor.name == storename).order_by(BaseUrl.id).all()
    for baseurl in baseurls:
        page = requests.get(baseurl[0].url)
        soup = BeautifulSoup(page.content, "html.parser")

        results = soup.find(id="content")

        items = results.find_all("li", class_="ast-col-sm-12")

        for item in items:
            link_element = item.find("a", class_="woocommerce-LoopProduct-link").attrs[
                "href"
            ]
            name_element = item.find(
                "h2", class_="woocommerce-loop-product__title"
            ).getText()

            insert_sequence(store=storename, url=link_element, name=name_element)


if __name__ == "__main__":
    print(f"Loading %s..." % storename)
    main()
