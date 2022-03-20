import re

import requests
from bs4 import BeautifulSoup

from my_funcs import insSequence

URL = "https://blinkysequences.com/product-category/sequences/"


def main() -> None:
    page = requests.get(URL)
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

        trim = re.compile(r"[^\d.,]+")

        price_element = trim.sub("", item.find("span", class_="price").getText())
        insSequence(store="BlinkySequences", url=link_element, name=name_element)


if __name__ == "__main__":
    main()
