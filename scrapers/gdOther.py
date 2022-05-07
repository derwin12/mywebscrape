from dataclasses import dataclass
import os
from dotenv import load_dotenv
from getfilelistpy import getfilelist
from googleapiclient.discovery import build
from my_funcs import insert_sequence

storename = 'GoogleDrive'


@dataclass
class Sequence:
    name: str
    url: str
    price: str


load_dotenv()  # take environment variables from .env.

API_KEY = os.getenv("API_KEY", "Missing API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID_OTHER", "Missing FOLDER_ID")
service = build('drive', 'v3', developerKey=API_KEY)

items = []
pageToken = ""

FOLDER_IDS = [
    "12fXAtkhD1UQEjRZWPE9U41pa3IWdkZ0n",
    "1Pv7BKMiYU7qAoSFhrRbigYtdG-gm-wXs",
    "1s79C7ZNquiIEgL_A4oxPHiaipXDRlXxC",
    "14Liv1-p1CGj8hbJGEuhpceFUYkzRg0_X",
    "1HN8p8bcqkzCCfiON24gWOls_jXQyc9k5",
    "1nLv78PHAg_dWXaD4TsM9hRUawINhHlDS", # Halloween
    "16yifVMESTYnXmGWXKyNB-dF8FO2qqEF9",  # Needs Review
    "1bH7YAi-aN16oZd9FxfGRc2j9jPr1k0Lp", # XLATW
    "1PwUXWD2SkFjAq5tgEM5I9eKuHkWJddqc",
    "1kcFt-fbIaOvu9eRc7cuTrshLlmRlejBu",
    "15O9WIiTHzv5RSCVDj7fysuH6exoamAf8",
    "1Hd5N_KTcqu1EBnrMYj2fwdDWCTdwW0mH",
    "1qRlqbUigsHTFOV3Ap8_2aFLWBk9J3QlC"
]


def get_products_from_page(folderid: str) -> list[Sequence]:
    sequences = []
    resource = {
            "api_key": API_KEY,
            "id": folderid,
            "fields": "files(name,id)",
    }

    res = getfilelist.GetFileList(resource)

    folder_name = ""
    for key, value in res.items():
        if key == 'searchedFolder':
            folder_name = value["name"]
            print("Loading %s - %s" % (storename, folder_name))
        if key == 'fileList':
            for a in sorted(value[0]["files"], key=lambda x: x["name"]):
                if a["name"].endswith("zip"):
                    if a["name"].find('--', a["name"].find('--')+2) > 0:
                        sequence_name = "[" + folder_name + "] " + \
                            a["name"].split("--")[0] + " -- " + \
                            a["name"].split("--")[1] + " (" + \
                            a["name"].split("--")[2].split(".")[0] + ")"
                    else:
                        sequence_name = "[" + folder_name + "] " + a["name"]
                    product_url = "https://drive.google.com/uc?id=" + a["id"] + \
                                  "&amp;authuser=0&amp;export=download"
                    price = "Free"
                    sequences.append(Sequence(sequence_name, product_url, price))

            return sequences


def main() -> None:
    print(f"Loading %s" % storename)

    for folderid in FOLDER_IDS:
        products = get_products_from_page(folderid)

        for product in products:
            insert_sequence(store=storename, url=product.url, name=product.name, price=product.price)


if __name__ == "__main__":
    main()
