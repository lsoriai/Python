#!/usr/bin/python
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class SmallSmilHandler(ContentHandler):

    def __init__(self):

        self.Dic = {"root-layout": ["width", "height", "background-color"],
                    "region": ["id", "top", "bottom", "left", "right"],
                    "img": ["src", "region", "begin", "dur"],
                    "audio": ["src", "begin", "dur"],
                    "textstream": ["src", "region"]}
        self.Lista_Datos = []

    def startElement(self, name, attrs):

        if name in self.Dic:
            d = {}
            d["name"] = name
            for Atrib in self.Dic[name]:
                d[Atrib] = attrs.get(Atrib, "SIN DATOS")
            self.Lista_Datos.append(d)

    def get_tags(self):
        return self.Lista_Datos

if __name__ == "__main__":

    parser = make_parser()
    Handler = SmallSmilHandler()
    parser.setContentHandler(Handler)
    parser.parse(open('karaoke.smil'))
    print Handler.get_tags()
