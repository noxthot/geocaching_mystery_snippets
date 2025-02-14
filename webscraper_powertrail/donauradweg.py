# Used for scraping Donauradweg (starting with GC8E3RY)
#%%
from bs4 import BeautifulSoup

from utils.geocaching_api import get_geocaches_from_list, get_session, set_user_coordinate, URLS

#%%
session_dict = get_session()
session = session_dict["session"]


#%%
def solve_one_gc(session, gc_code, dry_run=False):
    page = session.get(f"{URLS["geocache"]}/{gc_code}")
    soup = BeautifulSoup(page.content, "html.parser")

    usercontent = soup.find(id="ctl00_ContentBody_LongDescription")

    comment_line = usercontent.contents[0]
    print("First line:", comment_line)  # Format should be like: N 48° 10.079' E 14° 42.330'
    
    # Extract coordinates from the comment line
    comment_line_stripped = comment_line.replace("'", "").strip()  # Format should be like: N 48° 10.079 E 14° 42.330

    print("Preparing coords line:", comment_line_stripped)
    coords = comment_line_stripped.split()
    lat_str = f"{coords[0]} {coords[1]} {coords[2]}"
    lon_str = f"{coords[3]} {coords[4]} {coords[5]}"

    print("Extracted coords:", lat_str, lon_str)
    
    if "N" not in lat_str:
        raise Exception("Sanity check failed: lat_str")

    if "E" not in lon_str:
        raise Exception("Sanity check failed: lon_str")

    if not dry_run:
        set_user_coordinate(session, gc_code, lat_str, lon_str)


#%%
url = input("List-URL: ")

list_code = url.split("/")[-1]

print("List Code:", list_code)

gc_codes = get_geocaches_from_list(session, list_code)

proceed = input(f"Found {len(gc_codes)} geocaches. Want to proceed (y/n)? ")

if proceed == "y":
    for idx, gc_code in enumerate(gc_codes):
        print(idx, "\t", gc_code)
        solve_one_gc(session, gc_code)
        print()
