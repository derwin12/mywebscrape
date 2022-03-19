import re
import requests
from insertData import insSequence

from bs4 import BeautifulSoup

#URL = "https://showstoppersequences-com.3dcartstores.com/product_index.asp"
#page = requests.get(URL)

BASEURL = "https://showstoppersequences-com.3dcartstores.com/"

soup = BeautifulSoup(open("sample-ss.html"), "html.parser")

results = soup.find(id="mainContent")

items = results.find_all("div", class_="product-index-item")

for item in items:
    link_element = item.find("a").attrs['href']
    print("Link:", BASEURL + link_element)

    name_element = item.find("a").getText()
    print("Name:", name_element)

    # TODO Go to link and grab price
    price_element = ""

    storename = "ShowStoppers"
    insSequence(storename, link_element, name_element)