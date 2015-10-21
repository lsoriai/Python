#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import SocketServer
import sys
import os


class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        """
        Servidor que envía diferentes tipos de datos
        """
        METHODS = ['ACK', 'INVITE', 'BYE']
        while 1:
            line = self.rfile.read()
            if not line:
                break
            print "El cliente nos manda " + line
            method = line.split(' ')[0]
            if method not in METHODS:
                self.wfile.write("SIP/2.0 405 Method Not Allowed\r\n\r\n")
                break
            if method == 'INVITE':
                mensaje = "SIP/2.0 100 Trying\r\n\r\n"
                mensaje += "SIP/2.0 180 Ringing\r\n\r\n"
                mensaje += "SIP/2.0 200 OK\r\n\r\n"
                self.wfile.write(mensaje)
            elif method == 'ACK':
                ip = line.split('@')[1].split(' ')[0]
                aEjecutar = './mp32rtp -i 127.0.0.1 -p 23032 < ' + sys.argv[3]
                print 'Vamos a ejecutar', aEjecutar
                os.system(aEjecutar)
                print 'Fin de la ejecución'
            elif method == 'BYE':
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
            else:
                self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print sys.argv
        sys.exit('Usage: python server.py IP port audio_file')
    else:
        print 'Listening'
    PORT = int(sys.argv[2])
    serv = SocketServer.UDPServer(("", PORT), EchoHandler)
    serv.serve_forever()
