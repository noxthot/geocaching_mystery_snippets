# -*- coding: utf-8 -*-
"""
Created on Sat May  2 12:02:17 2020

@author: grego
"""

def convertSpecialChars(word):
    replace_strings = {'0' : 'null',
                       '11': 'elf',
                       '1' : 'eins',
                       '2' : 'zwei',
                       '3' : 'drei',
                       '4' : 'vier',
                       '5' : 'fuenf',
                       '6' : 'sechs',
                       '7' : 'sieben',
                       '8' : 'acht',
                       '9' : 'neun',
                       'ä' : 'ae',
                       'ö' : 'oe',
                       'ü' : 'ue',
                       'ß' : 'ss',
                       ' ' : '',
                       '\n' : '',
                       '\t' : '',
                       '_' : '',
                       '.' : '',
                       '-' : '',
                       "'" : '',
                       '+' : '',
                       '&' : ''}
    
    word = word.lower()
    
    for k in replace_strings:
        word = word.replace(k, replace_strings[k])
        
    return word


with open('input_tomatch2.txt', 'r', encoding="utf-8") as f:
    lines_tomatch = f.readlines()
    
with open('input_dict.txt', 'r', encoding="utf-8") as f:
    lines_dict = f.readlines() 
    
lines_tomatch = [s.replace('\n', '').replace('\t', '') for s in lines_tomatch]
lines_dict = [s.replace('\n', '').replace('\t', '') for s in lines_dict]
lines_dict = list(set(lines_dict)) # remove duplicates   

lines_tomatch_mod = [convertSpecialChars(s) for s in lines_tomatch]
lines_dict_mod = [convertSpecialChars(s) for s in lines_dict]

for idxToMatch, wordToMatch in enumerate(lines_tomatch_mod):
    matchFound = False
    
    for idxDict, wordDictMod in enumerate(lines_dict_mod):
       if sorted(wordToMatch) == sorted(wordDictMod):
       #if (all(x in wordToMatch for x in wordDictMod)):
           print(f'[MATCH] {lines_tomatch[idxToMatch]} -> {wordToMatch} -> {wordDictMod} -> {lines_dict[idxDict]}')
           matchFound = True
           break
           
       
    if not matchFound:
        print(f'[ERROR] {lines_tomatch[idxToMatch]} -> No match found')