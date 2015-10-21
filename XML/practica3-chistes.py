#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class ChistesHandler(ContentHandler):
    """
    Clase para manejar chistes malos
    """

    def __init__ (self):
        """
        Constructor. Inicializamos las variables
        """
        self.calificacion = ""
        self.pregunta = ""
        self.inPregunta = 0
        self.respuesta = ""
        self.inRespuesta = 0

    def startElement(self, name, attrs):
        """
        Método que se llama cuando se abre una etiqueta
        """
        if name == 'chiste':
            # De esta manera tomamos los valores de los atributos
            self.calificacion = attrs.get('calificacion',"")
            print("Calificación: ")
            print("============= ")
            print(self.calificacion)
        elif name == 'pregunta':
            self.inPregunta = 1
        elif name == 'respuesta':
            self.inRespuesta = 1

    def endElement(self, name):
        """
        Método que se llama al cerrar una etiqueta
        """
        if name == 'pregunta':
            print(self.pregunta)
            self.pregunta = ""
            self.inPregunta = 0
        if name == 'respuesta':
            print(self.respuesta)
            self.respuesta = ""
            self.inRespuesta = 0
        #if self.inpregunta == 0 and self.inrespuesta == 0:

    def characters(self, char):
        """
        Método para tomar contenido de la etiqueta
        """
        if self.inPregunta:
            self.pregunta = self.pregunta + char
        if self.inRespuesta:
            self.respuesta += char 

if __name__ == "__main__":
    """
    Programa principal
    """
    parser = make_parser()
    cHandler = ChistesHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open('chistes2.xml'))
    print(cHandler.calificacion)
