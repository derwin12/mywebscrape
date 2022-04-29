from dataclasses import dataclass
import re
import undetected_chromedriver as uc

from bs4 import BeautifulSoup

from my_funcs import insert_sequence

from app import BaseUrl, Vendor

from selenium.webdriver.common.by import By
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions


storename = 'Music with Motion'


@dataclass
class Sequence:
    name: str
    url: str
    price: str


def get_products_from_page(soup: BeautifulSoup) -> list[Sequence]:
    products = soup.find_all("div", class_="product-layout")
    sequences = []
    for product in products:
        sequence_name = product.find("h4").text
        product_url = product.find("a")["href"]
        p = product.find("p", class_="price").text
        pattern = r'[^0-9\.\$]+'
        price_text = re.sub(pattern, ' ', p).strip()
        pattern = re.compile("(\$[0-9]+).*(\$[0-9]+)")
        try:
            price = pattern.search(price_text)[22]
        except IndexError:
            price = price_text
        if price == "$0":
            price = "Free"
        sequences.append(Sequence(sequence_name, product_url, price))

    return sequences


def main() -> None:
    print(f"Loading %s" % storename)
    baseurls = BaseUrl.query.join(Vendor).add_columns(Vendor.name.label("vendor_name")) \
        .filter(Vendor.name == storename).order_by(BaseUrl.id).all()
    for baseurl in baseurls:
        print(f"Loading %s" % baseurl[0].url)

        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("start-maximized")
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        caps = options.to_capabilities()

        driver = uc.Chrome(version_main=100, desired_capabilities=caps)
        driver.get(baseurl[0].url)
        try:
            WebDriverWait(driver, 15)\
                .until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "product-details")))
        except TimeoutException:
            print("Unable to load")
            pass
        html = driver.page_source
        driver.close()
        soup = BeautifulSoup(html, "html.parser")
        products = get_products_from_page(soup)

        for product in products:
            print(product)
#            #insert_sequence(store=storename, url=product.url, name=product.name, price=product.price)

        break


if __name__ == "__main__":
    main()
