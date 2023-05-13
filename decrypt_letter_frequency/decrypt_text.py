# %%
import os
import string

import pandas as pd

from collections import Counter


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

INPUT_LANGUAGE = "DE"  # available: DE, EN, FR, ES, IT, SE, PT


# %%
# Internal constants
colname_letter = "letter"


# %%
# Check configuration
if INPUT_LANGUAGE not in {"DE", "EN", "ES", "FR", "IT", "PT", "SE"}:
    raise Exception(f"INPUT_LANGUAGE {INPUT_LANGUAGE} not supported")


# %%
# Load language letter frequencies
df_lang_letter_frequencies = pd.read_csv(os.path.join("letter_frequencies.csv"))
lang_letters_desc_sorted_by_frequency = df_lang_letter_frequencies[[colname_letter, INPUT_LANGUAGE]].sort_values(INPUT_LANGUAGE, ascending=False)[colname_letter].values


# %%
# Generate source text letter frequencies
input_text_upper = INPUT_TEXT.upper()
count_frequency = Counter(input_text_upper)

text_letters_desc_sorted_by_frequency = [tup[0] for tup in count_frequency.most_common() if tup[0] in string.ascii_uppercase]


# %%
# Decrypt text based on frequencies
letter_mapping = dict({source : dest for source, dest in zip(text_letters_desc_sorted_by_frequency, lang_letters_desc_sorted_by_frequency)})
decrypted_text = []

for l in input_text_upper:
    if l in letter_mapping:
        decrypted_text.append(letter_mapping[l])
    else:
        decrypted_text.append(l)


# %%
# Output result
print("".join(decrypted_text))
# %%
