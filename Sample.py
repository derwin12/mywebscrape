value = [{'files': [{'id': '1JuE0K_lNCBwyDXFxPgUyPpdlLxUTewVH', 'name': '12 Days of Christmas--Straight No Chaser--Richard Sonnier.JPG'},
                    {'id': '1UQEPKHXE785a0UyceNCZx-UWa29o6JXe', 'name': '12 Days of Christmas--Straight No Chaser--Richard Sonnier.mp4'},
                    {'id': 'asdfasdfasf', 'name': 'Chipmunks - Christmas Dont Be Late.zip'},
                    {'id': '11cPvArsumi1ElsGrnRPEBHkhBsdXLJzi', 'name': '12 Days of Christmas--Straight No Chaser--Richard Sonnier.zip'}]}]

print(value[0]["files"])

for a in value[0]["files"]:
    #print("id", a["id"])
    #print("name", a["name"])
    if a["name"].endswith("zip"):
        try:
            print("\t\t<song>")
            print("\t\t\t<categoryid>Christmas</categoryid>")
            print("\t\t\t<title>" + a["name"].split("--")[0] + "</title>")
            print("\t\t\t<artist>" + a["name"].split("--")[1] + "</artist>")
            print("\t\t\t<creator>" + a["name"].split("--")[2].split(".")[0] + "</creator>")
            print("\t\t\t<notes>" + "</notes>")
            print("\t\t\t<download>" + "<![CDATA[https://drive.google.com/uc?id=" + a["id"] + "&amp;authuser=0&amp;export=download]]>" + "</download>")
            print("\t\t\t<sequence>" + "Yes" + "</sequence>")
            print("\t\t\t<weblink>" + "<![CDATA[https://drive.google.com/drive/folders/" + '1qSwKT4ooVnflY-_HAogZmibl787PO3Af' + "?fref=gc&amp;dti=628061113896314]]>" + "</weblink>")
            print("\t\t</song>")
        except:
            print("This didnt work...", a["name"])