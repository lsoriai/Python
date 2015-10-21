#!/usr/bin/python
# -*- coding: utf-8 -*-

import calcoohija
import sys

if __name__ == "__main__":
    Fichero = sys.argv[1]
    Archivo = open(Fichero, 'r')
    Lista_Lineas = Archivo.readlines()
    Archivo.close()

    for Linea in Lista_Lineas:
        Lista = Linea.split(",")
        Operacion = Lista[0]
        Resultado = Lista[1]
        for Pos in Lista[2:]:
            calculo = calcoohija.CalculadoraHija(Resultado, Pos, Operacion)
            Resultado = calculo.Operacion1()
        print(Resultado)
