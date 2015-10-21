#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys


class Calculadora():

    def __init__(self, Operador1, Operador2, Operador):
        self.Operador = Operador
        self.a = float(Operador1)
        self.b = float(Operador2)

    def Sumar(self):
        return self.a + self.b

    def Restar(self):
        return self.a - self.b

    def Operacion(self):
        if self.Operador == "suma":
            #Resultado = self.Sumar()
            return self.Sumar()
        elif self.Operador == "resta":
            #Resultado = self.Restar()
            return self.Restar()
        else:
            print("Error a la hora de definir la operación")


if __name__ == "__main__":
    try:
        Operador = sys.argv[2]
        Operador1 = sys.argv[1]
        Operador2 = sys.argv[3]
        calc = Calculadora(Operador1, Operador2, Operador)
        print(calc.Operacion())

    except ValueError:
        print("Error: Non numerical parameters")
