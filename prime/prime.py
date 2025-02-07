# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 20:51:41 2021

@author: grego
"""

import sympy


for nr in range(101, 1000):
    if sympy.isprime(nr):                   # XYZ
        if sympy.isprime(nr % 100):         # YZ
            if sympy.isprime(nr // 10):     # XY
                isPrime = True
                    
                for c in str(nr):
                    isPrime &= sympy.isprime(int(c)) # X, Y, Z
                    
                if isPrime:
                    print(nr)