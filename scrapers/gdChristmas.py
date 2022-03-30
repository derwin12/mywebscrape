import os
from dotenv import load_dotenv
from getfilelistpy import getfilelist
from googleapiclient.discovery import build
from my_funcs import insert_sequence

storename = 'GoogleDrive'

load_dotenv()  # take environment variables from .env.

API_KEY = os.getenv("API_KEY", "Missing API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID", "Missing FOLDER_ID")
service = build('drive', 'v3', developerKey=API_KEY)

items = []
pageToken = ""

resource = {
    "api_key": API_KEY,
    "id": FOLDER_ID,
    "fields": "files(name,id)",
}


def main() -> None:
    res = getfilelist.GetFileList(resource)

    for key, value in res.items():
        if key == 'fileList':
            for a in sorted(value[0]["files"], key=lambda x: x["name"]):
                if a["name"].endswith("zip"):
                    try:
                        insert_sequence(store=storename, url="https://drive.google.com/uc?id=" +
                                                             a["id"] +
                                                             "&amp;authuser=0&amp;export=download",
                                    name=a["name"].split("--")[0] + " -- " +
                                    a["name"].split("--")[1] + " (" +
                                    a["name"].split("--")[2].split(".")[0] + ")",
                                    price="Free")
                    except:
                        print(f"Insert failed %s" % a["name"])
                        pass


if __name__ == "__main__":
    main()
