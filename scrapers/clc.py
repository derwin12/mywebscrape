from dataclasses import dataclass
from urllib.parse import urljoin
import re

from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

from chromedriver_py import binary_path
import selenium.webdriver.chrome.service as Service


storename = 'Custom Light Creations'
lastval = ""


@dataclass
class Sequence:
    name: str
    url: str


def get_products_from_page(soup: BeautifulSoup, url: str) -> list[Sequence]:
    global lastval
    exitloop = False
    products = soup.find_all("div", attrs={"data-ux": "GridCell",
                                           "class": re.compile('^x-el x-el-div c2-1 c2-2 c2-49 c2-4k c2-4l c2-4m'),
                                           "class": re.compile('c2-6w')})

    sequences = []
    for i, product in enumerate(products):
        sequence_name = product.find("h4").text.strip()
        if i == 0:
            if lastval == sequence_name:
                exitloop = True
                break
            else:
                lastval = sequence_name

        # song, artist = sequence_name.split(" - ")
        product_url = urljoin(url, product.find("a")["href"])
        sequences.append(Sequence(sequence_name, product_url))

    if not exitloop:
        next_page = soup.find(attrs={"data-aid": "PAGINATION_ARROW_FORWARD"})

        if next_page:
            service_object = Service.Service(binary_path)
            print(f"Loading %s" % (urljoin(url, next_page["href"])))
            driver = webdriver.Chrome(service=service_object)
            driver.get(urljoin(url, next_page["href"]))
            try:
                WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.LINK_TEXT, "1")))
            except TimeoutException:
                print("Unable to load")
                raise
            html = driver.page_source
            driver.close()
            next_soup = BeautifulSoup(html, "html.parser")
            sequences.extend(get_products_from_page(next_soup, url))

    return sequences


def document_initialised(driver):
    return driver.execute_script("return")


def main() -> None:
    baseurls = BaseUrl.query.join(Vendor).add_columns(Vendor.name.label("vendor_name")) \
        .filter(Vendor.name == storename).order_by(BaseUrl.id).all()
    for baseurl in baseurls:
        service_object = Service.Service(binary_path)
        driver = webdriver.Chrome(service=service_object)
        driver.get(baseurl[0].url)
        try:
            WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.LINK_TEXT, "1")))
        except TimeoutException:
            print("Unable to load")
            raise
        html = driver.page_source
        driver.close()
        soup = BeautifulSoup(html, "html.parser")
        products = get_products_from_page(soup, baseurl[0].url)

        for product in products:
            insert_sequence(store=storename, url=product.url, name=product.name)


if __name__ == "__main__":
    main()
