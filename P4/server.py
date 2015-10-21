#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco
en UDP simple
"""

import SocketServer
import sys
import time


class SIPRegisterHandler(SocketServer.DatagramRequestHandler):
    """
    SIPRegisterHandler. Registro de dominios SIP
    """
    def register2file(self):
        """
        Archivo de Registros en formato .txt
        """
        archi = open('registered.txt', 'w')
        for user in dic_user.keys():
            ip = dic_user[user][0]
            t = dic_user[user][1]
            time_exp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t))
            archi.write(user + '\t' + ip + '\t' + str(time_exp) + '\r\n')
        archi.close()

    def handle(self):
        """
        Manejador de registros SIP
        """
        print "El cliente nos manda:"
        while 1:
            line = self.rfile.read()
            print line
            if not line:
                break
            else:
                lista = line.split(' ')
                direc_sip = lista[1].split(':')[1]
                ip = self.client_address[0]
                expires = time.time() + int(lista[3])
                dic_user[direc_sip] = [ip, expires]
                self.register2file()
                for user in dic_user.keys():
                    if time.time() >= dic_user[user][1]:
                        del dic_user[user]
                        self.register2file()
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")

if __name__ == "__main__":
    dic_user = {}
    PORT = int(sys.argv[1])
    SERV = SocketServer.UDPServer(("", PORT), SIPRegisterHandler)
    print "Lanzando servidor UDP de eco..."
    SERV.serve_forever()
