# %%
import string


# %%
# Input settings
INPUT_TEXT = """
NYHABSPLYL KB OHZA HBJO KPLZLU JVKL 
NLRUHJRA BT KPLZLU TFZALYPL GB SVLZLU
IPSKL UBU ILP KLU LPUGLSULU UVYK BUK
VZA RVVYKPUHALU KLY CPLY TFZAYPLZ KPL
LPUZALSSPNLU XBLYZBTTLU BUK YLJOUL
KPL MPUHS RVVYKPUHALU TPA BUALU
ZALOLUKLY MVYTLS HBZ TFZALYPL LPUZ
UVYK PZA H VZA PZA I TFZALYPL GDLP UVYK
PZA J VZA PZA K TFZALYPL KYLP UVYK PZA L
VZA PZA M TFZALYPL CPLY UVYK PZA N VZA
PZA O
"""

SHIFT = None  # Define letter shift. Use None to output all or a number if you want to be specific


# %%
# Interna
alphabet = string.ascii_uppercase
input_text_uppercase = INPUT_TEXT.upper()


# %%
def decrypt_caesar(input_text, shift):
    translated = ""

    for symbol in input_text:
        if symbol in alphabet:
            num = alphabet.find(symbol) - shift

            if num < 0:
                num += len(alphabet)

            translated += alphabet[num]
        else:
            translated += symbol

    return translated


def decrypt_and_print(input_text, shift):
    print(f"Shifted by {shift}:")
    print("-------")
    print(decrypt_caesar(input_text, shift))
    print("-------")


# %%
if SHIFT is None:
    for idx in range(len(alphabet)):
        decrypt_and_print(input_text_uppercase, idx)
else:
    decrypt_and_print(input_text_uppercase, SHIFT)

# %%
