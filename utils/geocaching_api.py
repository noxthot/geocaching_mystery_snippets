import json
import os
import re
import requests

from bs4 import BeautifulSoup


def _to_decimal(coord_str):
    _, coord_deg, coord_min = coord_str.replace("°", "").replace("'", "").split(" ")

    return round(int(coord_deg) + float(coord_min) / 60, 5)


def get_session():
    session = requests.Session()

    # Login geocaching.com
    login_page_req = session.request(method="GET", url="https://www.geocaching.com/account/signin")
    login_page = BeautifulSoup(login_page_req.text, "html.parser")
    token_field_name = "__RequestVerificationToken"
    token_value = login_page.find("input", attrs={"name": token_field_name})["value"]

    config_path = os.path.join("config.json")

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

    if "Sign out" in after_login_page.text:
        print("Login successful")
    else:
        raise Exception("Login failed")

    return {"session": session, "allow_clipboard": allow_clipboard}


def set_user_coordinate(session, gc_code, lat_str, lon_str):
    lat_dec = _to_decimal(lat_str)
    lon_dec = _to_decimal(lon_str)

    uri_usertoken = f"https://www.geocaching.com/seek/cache_details.aspx?wp={gc_code.upper()}"

    page_usertoken = session.get(uri_usertoken, headers={"Referer" : uri_usertoken})

    res = re.search('userToken = \'(.*)\';', page_usertoken.text)

    if not(res):
        raise("Could not find userToken")

    userToken = res.group(1)

    post_data = {
        "dto": {
            "data": {
                "lat": lat_dec,
                "lng": lon_dec,
            },
            "ut": userToken,
        },
    }

    uri_suc = "https://www.geocaching.com/seek/cache_details.aspx/SetUserCoordinate"
    user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0"

    after_request = session.post(
                                    uri_suc,
                                    allow_redirects=False,
                                    headers={"User-Agent" : user_agent, "Referer" : uri_suc},
                                    json=post_data
    )

    if after_request.status_code == 200:
        print(f"Coordinates updated successfully for {gc_code}")
    else:
        raise Exception(f"Failed to update coordinates for {gc_code}")

    