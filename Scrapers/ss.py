import requests
from urllib.parse import urljoin
from insertData import insSequence

from bs4 import BeautifulSoup

URL = "https://showstoppersequences-com.3dcartstores.com/product_index.asp"
BASEURL = "https://showstoppersequences-com.3dcartstores.com/"

def main() -> None:
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find(id="mainContent")

    products = results.find_all("div", class_="product-index-item")

    for product in products:
        product_url = urljoin(BASEURL, product.find("a")["href"])
        name_element = product.find("a").getText()
        insSequence(store="ShowStoppers", url=product_url, name=name_element)

if __name__ == "__main__":
    main()
