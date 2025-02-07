import os

password_file = os.path.join("php_login_bruteforce", "psw.in")

psws = [str(val).zfill(6) for val in range(1000000)]
psws_filtered = [psw for psw in psws if "7" in psw]

with open(password_file, "w") as pswfile:
    for psw in psws_filtered:
        pswfile.write(psw + "\n")

print("fin.")