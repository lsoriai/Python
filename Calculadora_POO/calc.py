#!/usr/bin/phyton
# -*- coding: utf-8 -*-


import sys


def Sumar(a, b):
    return (a + b)


def Restar(a, b):
    return (a - b)


try:
    if sys.argv[2] == "suma":
        Resultado = Sumar(float(sys.argv[1]), float(sys.argv[3]))
        print Resultado
    elif sys.argv[2] == "resta":
        Resultado = Restar(float(sys.argv[1]), float(sys.argv[3]))
        print Resultado
    else:
        print("Error a la hora de definir la operación")

except:
    print("Error: Non numerical parameters")
