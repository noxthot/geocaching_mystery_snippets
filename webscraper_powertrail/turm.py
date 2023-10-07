import pyperclip
import requests

from bs4 import BeautifulSoup

session = requests.Session()

# Login geocaching.com
login_page_req = session.request(method="GET", url="https://www.geocaching.com/account/signin")
login_page = BeautifulSoup(login_page_req.text, "html.parser")
token_field_name = "__RequestVerificationToken"
token_value = login_page.find("input", attrs={"name": token_field_name})["value"]

myuser = input("Your geocaching.com username: ")
mypsw = input("Your geocaching.com password: ")
allow_clipboard_input = input("Do you want to have the calculated coordinates copied into your clipboard automatically (y/n)?: ")

allow_clipboard = (allow_clipboard_input.lower() in ["y", "j", "yes"])

post = {
    "UsernameOrEmail": myuser,
    "Password": mypsw,
    token_field_name: token_value
}

after_login_page = session.request(method="POST", url="https://www.geocaching.com/account/signin", data=post)

# Ask for website, scrape formula and apply to header coordinates
while True:
    url = input("Cache-URL: ")

    if url == "":
        break

    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    usercontent = soup.find(id="ctl00_ContentBody_ShortDescription")

    found = False

    # find calc rule for new coords
    for p in usercontent.findAll("h2"): # line example: 'N: Header + 357\r\nE: Header + 1498'
        p_str = p.text

        if "N: Header" in p_str: 
            n_rule = p_str.split()[2]
            n_numb = int(p_str.split()[3]) / 1000
        elif "E: Header" in p_str:
            e_rule = p_str.split()[2]
            e_numb = int(p_str.split()[3]) / 1000
        else:
            raise Exception(f"Expected to find N and E Header, but found {p.text}")

        # sanity check
        if p_str.split()[1] != "Header":
            raise Exception("Sanity check failed")

    headersoup = soup.find(id="uxLatLon")  # e.g. 'N 47° 04.900 E 011° 25.960'
    header_split = headersoup.text.split()

    n_coords_pre = f"{header_split[0]} {header_split[1]}"
    n_coords_header = float(header_split[2])

    e_coords_pre = f"{header_split[3]} {header_split[4]}"
    e_coords_header = float(header_split[5])

    if n_rule == "+":
        n_new_coords = n_coords_header + n_numb
    elif n_rule == "-":
        n_new_coords = n_coords_header - n_numb
    else:
        raise Exception(f"n_rule {n_rule} invalid")

    if e_rule == "+":
        e_new_coords = e_coords_header + e_numb
    elif e_rule == "-":
        e_new_coords = e_coords_header - e_numb
    else:
        raise Exception(f"e_rule {e_rule} invalid")

    
    resulting_coords = f"{n_coords_pre} {n_new_coords:.3f} {e_coords_pre} {e_new_coords:.3f}"
    
    if allow_clipboard:
        pyperclip.copy(resulting_coords)

    print(f"{p_str} (rule)")
    print(f"{' '.join(header_split)} (orig)")
    print(resulting_coords)

