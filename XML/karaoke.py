#!/usr/bin/python
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from smallsmilhandler import SmallSmilHandler
import sys
import os


class KaraokeLocal():

    def __init__(self, fichero):
        parser = make_parser()
        Handler = SmallSmilHandler()
        parser.setContentHandler(Handler)
        parser.parse(open(fichero))
        self.Lista_Datos = Handler.get_tags()

    def __str__(self):
        Cadena = ""
        for Dic in self.Lista_Datos:
            Cadena += str('\n' + Dic["name"] + '\t')
            for Clave in Dic:
                if Clave != "name" and Dic[Clave] != "SIN DATOS":
                    Cadena += str(Clave + "= " + '"' + Dic[Clave] + '"' + '\t')
        return Cadena

    def do_local(self):
        Cadena = ""
        for Dic in self.Lista_Datos:
            Cadena += str('\n' + Dic["name"] + '\t')
            for Clave in Dic:
                if Clave != "name" and Dic[Clave] != "SIN DATOS":
                    if Clave == "src":
                        os.system("wget -q " + Dic[Clave])
                        Dic[Clave] = Dic[Clave].split("/")[-1]
                    Cadena += str(Clave + "= " + '"' + Dic[Clave] + '"' + '\t')
        return Cadena

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage:python karaoke.py src_file.smil")
    fichero = sys.argv[1]
    Karaoke = KaraokeLocal(fichero)
    print Karaoke
    Karaoke.do_local()
    print Karaoke
