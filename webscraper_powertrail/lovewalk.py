
import json
import os
import pyperclip
import requests
import seval

from bs4 import BeautifulSoup

session = requests.Session()

# Login geocaching.com
login_page_req = session.request(method="GET", url="https://www.geocaching.com/account/signin")
login_page = BeautifulSoup(login_page_req.text, "html.parser")
token_field_name = "__RequestVerificationToken"
token_value = login_page.find("input", attrs={"name": token_field_name})["value"]

config_path = os.path.join(os.path.dirname(__file__), "config.json")

if os.path.exists(config_path):
    print("Loading credentials from config.")
    with open(config_path, "r") as file:
        config = json.load(file)
        myuser = config.get("username", None)
        mypsw = config.get("password", None)
        allow_clipboard = config.get("allow_clipboard", None)
else:
    print("No config provided. Ask user for credentials.")
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

    usercontent = soup.find(id="ctl00_ContentBody_LongDescription")

    found = False

    e_op = None
    e_rule = None
    n_op = None
    n_rule = None
    symbols = []

    start_symbol_search = False

    # find calc rule for new coords
    for p in usercontent.findAll("p"):
        if p.text == ("Dafür müsst ihr kurze schnelle Rechnungen lösen!"):
            start_symbol_search = True
            continue

        if p.text == ("Final Koordinaten"):
            start_symbol_search = False

        if start_symbol_search:
            p_str = p.text

            if "=" in p_str:
                symbols.append(p_str)
        elif p.text.startswith("Header N"):  # Header N 47° +ABA
            p_str = p.text
            print(p_str)

            if "+" in p_str:
                n_op = "+"
            elif "-" in p_str:
                n_op = "-"

            n_rule = p_str.split(n_op)[1].strip()

            # sanity check
            if n_op is None:
                raise Exception("Sanity check failed")
        elif p.text.startswith("Header E"):  # Header E 011° +CDE
            p_str = p.text
            print(p_str)

            if "+" in p_str:
                e_op = "+"
            elif "-" in p_str:
                e_op = "-"

            e_rule = p_str.split(e_op)[1].strip()
            
            break  # Last line to be found


    # sanity checks
    if e_op is None:
        raise Exception("Sanity check failed: e_op")
    
    if n_op is None:
        raise Exception("Sanity check failed: n_op")
    
    if len(symbols) == 0:
        raise Exception("Sanity check failed: symbols empty")
    
    print(f"{'\n'.join(symbols)} (symbols)")

    key_mapping = {}

    for symbol in symbols:
        varname, formula = symbol.split(" = ")
        key_mapping[varname] = str(int(seval.safe_eval(formula)))

    e_numb = int("".join([key_mapping[k] for k in e_rule])) / 1000
    n_numb = int("".join([key_mapping[k] for k in n_rule])) / 1000

    headersoup = soup.find(id="uxLatLon")  # e.g. 'N 47° 04.900 E 011° 25.960'
    header_split = headersoup.text.split()

    n_coords_pre = f"{header_split[0]} {header_split[1]}"
    n_coords_header = float(header_split[2])

    e_coords_pre = f"{header_split[3]} {header_split[4]}"
    e_coords_header = float(header_split[5])

    if n_op == "+":
        n_new_coords = n_coords_header + n_numb
    elif n_op == "-":
        n_new_coords = n_coords_header - n_numb
    else:
        raise Exception(f"n_rule {n_rule} invalid")

    if e_op == "+":
        e_new_coords = e_coords_header + e_numb
    elif e_op == "-":
        e_new_coords = e_coords_header - e_numb
    else:
        raise Exception(f"e_rule {e_rule} invalid")

    resulting_coords = f"{n_coords_pre} {n_new_coords:.3f} {e_coords_pre} {e_new_coords:.3f}"
    
    if allow_clipboard:
        pyperclip.copy(resulting_coords)

    print(symbols)
    print(f"{' '.join(header_split)} (orig)")
    print(resulting_coords)
    

