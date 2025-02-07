# Used for scraping FBPT M486 BikePT Die Antwort der Doppeladlerin (starting with GC73NEP)
from bs4 import BeautifulSoup

from utils.geocaching_api import get_session, set_user_coordinate


session_dict = get_session()
session = session_dict["session"]
allow_clipboard = session_dict["allow_clipboard"]

# Ask for website, scrape formula and apply to header coordinates
while True:
    url = input("Cache-URL: ")

    if url == "":
        break

    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    usercontent = soup.find(id="ctl00_ContentBody_LongDescription")

    lines = []

    # find calc rule for new coords
    for p in usercontent.findAll("p"):
        if p.text.startswith("Start-Koordinaten"):
            lines = p.text.split()
            break

    if len(lines) != 9:  # e.g. looks like this: ['Start-Koordinaten', 'N47°', '33.940', '+', '617', 'E012°', '05.600', '-', '96']
        raise Exception("Sanity check failed: lines")

    n_base, n_op, n_numb_str = lines[2], lines[3], lines[4]
    e_base, e_op, e_numb_str = lines[6], lines[7], lines[8]

    e_numb = int(e_numb_str) / 1000
    n_numb = int(n_numb_str) / 1000

    headersoup = soup.find(id="uxLatLon")  # e.g. 'N 47° 04.900 E 011° 25.960'
    header_split = headersoup.text.split()

    n_coords_pre = f"{header_split[0]} {header_split[1]}"
    n_coords_header = float(header_split[2])

    e_coords_pre = f"{header_split[3]} {header_split[4]}"
    e_coords_header = float(header_split[5])

    if n_coords_header != float(n_base):
        raise Exception("Sanity check failed: n_coords_header")

    if e_coords_header != float(e_base):
        raise Exception("Sanity check failed: e_coords_header")
    
    if n_op == "+":
        n_new_coords = n_coords_header + n_numb
    elif n_op == "-":
        n_new_coords = n_coords_header - n_numb
    else:
        raise Exception(f"n_op {n_op} invalid")

    if e_op == "+":
        e_new_coords = e_coords_header + e_numb
    elif e_op == "-":
        e_new_coords = e_coords_header - e_numb
    else:
        raise Exception(f"e_op {e_op} invalid")

    lat_str = f"{n_coords_pre} {n_new_coords:.3f}"
    lon_str = f"{e_coords_pre} {e_new_coords:.3f}"

    gc_code = url.split("/")[-1]

    set_user_coordinate(session_dict["session"], gc_code, lat_str, lon_str)

    print(lines)
    print(f"{' '.join(header_split)} (orig)")
    print(lat_str, lon_str)
    

