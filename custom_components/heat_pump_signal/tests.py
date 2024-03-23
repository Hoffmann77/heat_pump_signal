# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 19:50:36 2024

@author: Bobby
"""

class Unit:
    
    Watt = "W"
    
    
    
def test(x):
    
    print(type(x))
    print(x)
    
    
class des:
    
    def __init__(self, unit):
        self.unit = unit
    
    
x = des(Unit.Watt)
print(type(x.unit))