from datetime import datetime

import os
import requests
import shutil
import time

url_root = "https://www.muggelfrei.at/caches/schlaflos/"

filenames = [f"N{idx}.png" for idx in range(1, 8)] + [
    f"E{idx}.png" for idx in range(1, 9)
]


if __name__ == "__main__":
    while True:
        now = datetime.now()
        current_time = now.strftime("%H_%M")

        try:
            os.mkdir(current_time)
        except Exception:
            pass

        for filename in filenames:
            image_url = url_root + filename

            r = requests.get(image_url, stream=True, verify=False)
            r.raw.decode_content = True

            with open(f"./{current_time}/{filename}", "wb") as f:
                shutil.copyfileobj(r.raw, f)

        time.sleep(30 * 60)  # Delay for 30 minutes
