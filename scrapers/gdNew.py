from dataclasses import dataclass
import urllib.parse
import os

from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from chromedriver_py import binary_path
import selenium.webdriver.chrome.service as Service


SHARED_LINK = "https://drive.google.com/drive/folders/0B2ozCEidtWh3ZURlVWFvenRiSVk" + \
              "?resourcekey=0-t4zYmi-whU6yaxp08BQfSw&usp=sharing"
storename = 'GoogleDrive'
lastval = ""


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    files = soup.find_all("div", role="gridcell")
    sequences = []

    for file in files:
        file_name_div = file.find("div", attrs={"data-tooltip-unhoverable": "true"})
        file_name = file_name_div["aria-label"]

        url_link = file.find("img")
        if url_link:
            if file_name.endswith("zip") or file_name.endswith("piz"):
                sequence_name = file_name
                product_url = url + "&" + \
                    urllib.parse.quote(file_name.split(".")[0])
                price = "Free"
                sequences.append(Sequence(sequence_name, product_url, price))

    return sequences


def document_initialised(driver):
    return driver.execute_script("return")


def main() -> None:
    print(f"Loading %s" % storename)

    print(f"Loading %s" % SHARED_LINK)
    if os.name != "posix":
        service_object = Service.Service(binary_path)
        driver = webdriver.Chrome(service=service_object)
    else:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get(SHARED_LINK)

    j = 1
    for i in range(400):
        try:
            element = driver.find_element(By.XPATH, f"//c-wiz[{j}]")
        except NoSuchElementException:
            break
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        j = j + 1

    html = driver.page_source
    driver.close()

    soup = BeautifulSoup(html, "html.parser")
    products = get_products_from_page(soup, SHARED_LINK)

    for product in products:
        insert_sequence(store=storename, url=product.url, name=product.name, price=product.price)


if __name__ == "__main__":
    main()
