#!/usr/bin/phyton
# -*- coding: utf-8 -*-

import sys
import calcoo


#Es la clase CalculadoraHija que hereda de calcoo.Calculadora
class CalculadoraHija(calcoo.Calculadora):

    def __init__(self, Operador1, Operador2, Operador):
        self.Operador = Operador
        self.a = float(Operador1)
        self.b = float(Operador2)

    def Multiplicar(self):
        return self.a * self.b

    def Dividir(self):
        try:
            result = self.a / self.b
        except ZeroDivisionError:
            print("Division by zero is not allowed")
            sys.exit()
        else:
            return self.a / self.b

    def Operacion1(self):
        if self.Operador == "multiplica":
            Resultado = self.Multiplicar()
            return Resultado
        elif self.Operador == "divide":
            Resultado = self.Dividir()
            return Resultado
        else:
            return self.Operacion()

if __name__ == "__main__":
    try:
        Operador = sys.argv[2]
        Operador1 = float(sys.argv[1])
        Operador2 = float(sys.argv[3])
        CalcHija = CalculadoraHija(Operador1, Operador2, Operador)
        print(CalcHija.Operacion1())

    except:
        print("Error: Non numerical parameters")
