import pyperclip
import seval

from bs4 import BeautifulSoup

from utils.geocaching_api import get_session


session, allow_clipboard = get_session()

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
    

