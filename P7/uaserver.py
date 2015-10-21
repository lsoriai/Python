#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Servidor para una sesion SIP
"""

import SocketServer
import sys
import os
import os.path
import time
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import threading


class XML_CLIENT(ContentHandler):
    """
    Extrae la información del fichero Config.xml
    """

    def __init__(self):

        self.Dic = {"account": ["username", "passwd"],
                    "uaserver": ["ip", "puerto"],
                    "rtpaudio": ["puerto"],
                    "regproxy": ["ip", "puerto"],
                    "log": ["path"],
                    "audio": ["path"]}
        self.config = {}

    def startElement(self, name, attrs):
        """
        Asigna al diccionario los valores que lee del fichero config.xml
        """
        if name in self.Dic:
            for Atrib in self.Dic[name]:
                self.config[name + '_' + Atrib] = attrs.get(Atrib, "----")
                if name + '_' + Atrib == "uaserver_ip":
                    if len(self.config["uaserver_ip"]) == 0:
                        self.config["uaserver_ip"] = "127.0.0.1"

    def get_tags(self):
        """
        Retorna una lista del diccionario
        """
        return self.config


class LOG_FILE:
    """
    Clase encargada de escribir las trazas en LOG del uaclient
    """
    def write(self, line, log):
        txtfile = open(log, 'a')
        now = time.strftime('%Y%m%d%H%M%S ', time.gmtime(time.time()))
        line = line.replace("\r\n", " ")
        txtfile.write(str(now) + str(line) + '\r\n')
        txtfile.close()


class Thread(threading.Thread):
    """
    Se encarga de la reproduccion del audio mediante hilos
    """

    def __init__(self, ip, rtp_port, song):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = rtp_port
        self.song = song

    def run(self):
        """
        Contiene los comandos del terminal para la ejecucion
        """
        Ejecutar_cvlc = 'cvlc rtp://@' + self.ip + ':' + self.port
        Ejecutar_cvlc += ' 2>/dev/null' + '&'
        os.system(Ejecutar_cvlc)

        Ejecutar = './mp32rtp -i ' + self.ip + ' -p ' + str(self.port)
        Ejecutar += ' < ' + self.song
        os.system(Ejecutar)
        print 'Terminado'


class SERVER_SOCKET(SocketServer.DatagramRequestHandler):
    """
    server class
    """
    def handle(self):
        while 1:
            line = self.rfile.read()
            if not line:
                break
            print 'El cliente nos manda ' + line
            trama = line.replace('\r\n', ' ')
            ip_proxy = self.client_address[0]
            p_proxy = self.client_address[1]
            method = trama.split(' ')[0]
            if method == 'INVITE':
                Infor_user['ip'] = trama.split(' ')[12]
                Infor_user['port'] = trama.split(' ')[16]
                logfile = LOG_FILE()
                line = 'SIP/2.0 100 Trying'
                traza = 'Send to ' + str(ip_proxy) + ':' + str(p_proxy)
                traza += ': ' + line
                logfile.write(traza, LOG)
                self.wfile.write(line + '\r\n')
                line = 'SIP/2.0 180 Ringing'
                traza = 'Send to ' + str(ip_proxy) + ':' + str(p_proxy)
                traza += ': ' + line
                logfile.write(traza, LOG)
                self.wfile.write(line + '\r\n')
                line = 'SIP/2.0 200 OK'
                traza = 'Send to ' + str(ip_proxy) + ':' + str(p_proxy)
                traza += ': ' + line
                logfile.write(traza, LOG)
                self.wfile.write(line + '\r\n')

            if method == 'ACK':
                #Avanzado --> hilo de ejecución
                ip = Infor_user['ip']
                rtp_port = Infor_user['port']
                audio = Thread(ip, rtp_port, SONG)
                audio.start()

            if method == 'BYE':
                line = 'SIP/2.0 200 OK'
                traza = 'Send to ' + str(ip_proxy) + ':' + str(p_proxy)
                traza += ': ' + line
                logfile = LOG_FILE()
                logfile.write(traza, LOG)
                self.wfile.write(line + '\r\n')

            if method not in methods:
                line = 'SIP/2.0 405 Method Not Allowed\r\n'
                logfile = LOG_FILE()
                logfile.write('Error: ' + line, LOG)
                self.wfile.write(line)
                break

if __name__ == "__main__":
    Infor_user = {'ip': ' ', 'port': ' '}
    methods = ['INVITE', 'ACK', 'BYE']

    try:
        CONFIG = sys.argv[1]
        if not os.access(CONFIG, os.F_OK):
            sys.exit('Usage: python proxy_registrar.py config')
    except ValueError:
        sys.exit('Usage: python proxy_registrar.py config')
    except IndexError:
        sys.exit('Usage: python proxy_registrar.py config')

    parser = make_parser()
    Handler = XML_CLIENT()
    parser.setContentHandler(Handler)
    parser.parse(open(CONFIG))
    LIST_CONFIG = Handler.get_tags()
    #Extraemos de la lista los datos importantes para empezar a trabajar
    U_NAME = LIST_CONFIG['account_username']
    U_IP = LIST_CONFIG['uaserver_ip']
    U_PORT = LIST_CONFIG['uaserver_puerto']
    AUDIO_PORT = LIST_CONFIG['rtpaudio_puerto']
    SONG = LIST_CONFIG['audio_path']
    LOG = LIST_CONFIG['log_path']

    txtfile = open(LOG, 'w')
    reftime = time.strftime('%Y%m%d%H%M%S ', time.gmtime(time.time()))
    txtfile.write(str(reftime) + 'Starting...\r\n')
    txtfile.close()

    try:
        SERVER = SocketServer.UDPServer((U_IP, int(U_PORT)), SERVER_SOCKET)
        SERVER.serve_forever()
    except KeyboardInterrupt:
        print 'Programa finalizado'
        logfile = LOG_FILE()
        logfile.write('Finishing...', LOG)
