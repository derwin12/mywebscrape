import os
from dotenv import load_dotenv
from getfilelistpy import getfilelist
from googleapiclient.discovery import build

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


def main():
    res = getfilelist.GetFileList(resource)  # or r = getfilelist.GetFolderTree(resource)

    for key, value in res.items():
        if key == 'fileList':
            for a in sorted(value[0]["files"], key=lambda x: x["name"]):
                if a["name"].endswith("zip"):
                    try:
                        print("\t\t<song>")
                        print("\t\t\t<hash>Nomusicincluded</hash>")
                        print("\t\t\t<categoryid>Christmas</categoryid>")
                        print("\t\t\t<title>" + a["name"].split("--")[0] + "</title>")
                        print("\t\t\t<artist>" + a["name"].split("--")[1] + "</artist>")
                        print("\t\t\t<creator>" + a["name"].split("--")[2].split(".")[0] + "</creator>")
                        print("\t\t\t<notes>" + "</notes>")
                        print("\t\t\t<download>" + "<![CDATA[https://drive.google.com/uc?id=" + a[
                            "id"] + "&amp;authuser=0&amp;export=download]]>" + "</download>")
                        print("\t\t\t<sequence>" + "Yes" + "</sequence>")
                        print(
                            "\t\t\t<weblink>" + "<![CDATA[https://drive.google.com/drive/folders/" +
                            '1qSwKT4ooVnflY-_HAogZmibl787PO3Af' +
                            "?fref=gc&amp;dti=628061113896314]]>" + "</weblink>")
                        print("\t\t</song>")
                    except:
                        pass


if __name__ == "__main__":
    main()
