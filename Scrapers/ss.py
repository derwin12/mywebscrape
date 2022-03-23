import requests
from my_funcs import insSequence

from bs4 import BeautifulSoup

URL = "https://showstoppersequences-com.3dcartstores.com/product_index.asp"
BASEURL = "https://showstoppersequences-com.3dcartstores.com/"


def main() -> None:
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find(id="mainContent")

    items = results.find_all("div", class_="product-index-item")

    for item in items:
        link_element = item.find("a").attrs["href"]
        name_element = item.find("a").getText()
        insSequence(store="ShowStoppers", url=link_element, name=name_element)


if __name__ == "__main__":
    main()
