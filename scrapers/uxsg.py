import os
import urllib.parse

from app import Sequence, Vendor
from my_funcs import create_or_update_sequences, get_unique_vendor
from openpyxl import load_workbook

storename = "UXSG"
BASEURL = "https://www.facebook.com/groups/228562318717861/search/?q="

#filename = "Unofficial xLights Sharing Group Shared Files List (31 Jan 2022).xlsx"
#filename = "Unofficial xLights Sharing Group Shared Files List (17 May 2022).xlsx"
filename = "Unofficial xLights Sharing Group Shared Files List (14th July 2022).xlsx"
name_column = 6
artist_column = 7
author_column = 9


def main() -> None:
    print("Loading UXSG Spreadsheet")
    vendor = get_unique_vendor(storename)

    if os.name != 'posix':
        dir = os.getcwd() + "\\..\\app\\Data\\"
    else:
        dir = os.getcwd() + "//app//Data//"
    wb = load_workbook(filename=dir + filename, data_only=True)
    sheet_obj = wb["Shares"]
    sequences = []

    for row in range(4, 1500):
        if (
            sheet_obj.cell(column=2, row=row).value
            and "_NA" not in sheet_obj.cell(column=name_column, row=row).value
            and '#VALUE!' not in sheet_obj.cell(column=name_column, row=row).value
        ):
            # exlude the NA ones
            sequence_name = (
                sheet_obj.cell(column=name_column, row=row).value
                + " "
                + "-- "
                + sheet_obj.cell(column=artist_column, row=row)._value
                + " ("
                + sheet_obj.cell(column=author_column, row=row).value
                + ")"
            )
            product_url = BASEURL + urllib.parse.quote(
                sheet_obj.cell(column=name_column, row=row).value.strip()
                + " "
                + sheet_obj.cell(column=artist_column, row=row)._value
                + " "
                + sheet_obj.cell(column=author_column, row=row)._value
            )
            price = "Free"
            sequences.append(
                Sequence(
                    name=sequence_name,
                    vendor_id=vendor.id,
                    link=product_url,
                    price=price,
                )
            )

    create_or_update_sequences(sequences)


if __name__ == "__main__":
    main()
