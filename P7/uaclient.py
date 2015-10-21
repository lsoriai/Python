#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Cliente para una sesion SIP
"""

import socket
import sys
import time
import os.path
import os
import base64
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


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
        txtfile = open(log, 'a+')
        reftime = time.strftime('%Y%m%d%H%M%S ', time.gmtime(time.time()))
        line = line.replace("\r\n", " ")
        txtfile.write(str(reftime) + str(line) + '\r\n')
        txtfile.close()


class MY_SOCKET:
    """
    Clase encargada de enviar y recibir paquetes del socket
    """

    def creat_passwd(self, passwd, random):
        """
        Encripta la contraseña con el código enviado desde el proxy
        """
        random_array = list(random)
        passwd_array = list(passwd)
        encrypted_passwd = ''
        for i in random_array:
            if len(passwd_array) > 0:
                encrypted_passwd += i + passwd_array[0]
                del(passwd_array[0])
            else:
                encrypted_passwd += i
        return encrypted_passwd

    def send(self, ip_proxy, p_proxy, method, u_name, u_port, option,
             socket, log, song, song_port, password, random):
        """
        Envia los mensajes asociados a cada metodo
        """

        if method == 'REGISTER':
            line = 'REGISTER sip:' + u_name + ':' + u_port
            line += ' SIP/2.0\r\n' + 'Expires: ' + option

        if method == '401 Unauthorized':
            encrypted_passwd = self.creat_passwd(password, random)
            line = 'REGISTER sip:' + u_name + ':' + u_port
            line += ' SIP/2.0\r\n' + 'Expires: ' + option + ' '
            line += encrypted_passwd

        if method == 'INVITE':
            line = 'INVITE sip:' + OPTION + ' SIP/2.0\r\n'
            line += 'Content-Type: application/sdp\r\n\r\n' + 'v=0\r\n'
            line += 'o=' + u_name + ' ' + ip_proxy + '\r\n'
            line += 's=misesion\r\n' + 't=0\r\n'
            line += 'm=' + song + ' ' + str(song_port) + ' RTP\r\n'

        if method == 'ACK':
            line = 'ACK sip:' + OPTION + ' SIP/2.0\r\n'

        if method == 'BYE':
            line = 'BYE sip:' + OPTION + ' SIP/2.0\r\n'

        print line
        socket.send(line)
        traza = 'Send to ' + ip_proxy + ':' + p_proxy + ': ' + line
        logfile = LOG_FILE()
        logfile.write(traza, log)

    def received(self, line, log, ip, port):
        """
        Recibe los mensajes
        """

        line = line.replace('\r\n', ' ')
        traza = 'Received from ' + ip + ':' + port + ': ' + line
        logfile = LOG_FILE()
        logfile.write(traza, log)
        print 'He recibido: ' + line


if __name__ == "__main__":

    try:
        #Extraemos los datos que nos pasan por la linea de comandos
        CONFIG = sys.argv[1]
        METHOD = sys.argv[2]
        OPTION = sys.argv[3]
        METHODS = ["INVITE", "BYE", "REGISTER"]
        if not os.access(CONFIG, os.F_OK):
            sys.exit('Usage: python proxy_registrar.py config')
    except ValueError:
        sys.exit('Usage: python proxy_registrar.py config')
    except IndexError:
        sys.exit('Usage: python proxy_registrar.py config')

    if METHOD not in METHODS:
        line = 'SIP/2.0 405 Method Not Allowed\r\n'
        logfile = LOG_FILE()
        logfile.write('Error: ' + line, LOG)
        sys.exit('Error: ' + line)

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
    PROXY_IP = LIST_CONFIG['regproxy_ip']
    PROXY_PORT = LIST_CONFIG['regproxy_puerto']
    LOG = LIST_CONFIG['log_path']
    PASS = LIST_CONFIG['account_passwd']

    #Iniciamos el LOG del uaclient --> Starting
    txtfile = open(LOG, 'w')
    reftime = time.strftime('%Y%m%d%H%M%S ', time.gmtime(time.time()))
    txtfile.write(str(reftime) + 'Starting...\r\n')
    txtfile.close()

    #Establacemos el socket para empezar la comunicación
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((PROXY_IP, int(PROXY_PORT)))

    try:
        if METHOD == 'REGISTER':
            s = MY_SOCKET()
            s.send(PROXY_IP, PROXY_PORT, METHOD, U_NAME, U_PORT, OPTION,
                   my_socket, LOG, SONG, AUDIO_PORT, PASS, '')
            data = my_socket.recv(1024)
            s.received(data, LOG, PROXY_IP, PROXY_PORT)
            response = data.split(' ')[0] + ' ' + data.split(' ')[1]
            if response == '401 Unauthorized':
                METHOD = response
                random = data.split(' ')[2]
                s = MY_SOCKET()
                s.send(PROXY_IP, PROXY_PORT, METHOD, U_NAME, U_PORT, OPTION,
                       my_socket, LOG, SONG, AUDIO_PORT, PASS, random)
                data = my_socket.recv(1024)
                s.received(data, LOG, PROXY_IP, PROXY_PORT)

        if METHOD == 'INVITE':
            s = MY_SOCKET()
            s.send(PROXY_IP, PROXY_PORT, METHOD, U_NAME, U_PORT, OPTION,
                   my_socket, LOG, SONG, AUDIO_PORT, PASS, '')
            data = my_socket.recv(1024)
            s.received(data, LOG, PROXY_IP, PROXY_PORT)
            traza = data.replace('\r\n', ' ')
            last = traza.split(' ')[8]
            if last == 'OK':
                #Enviamos el ACK
                s = MY_SOCKET()
                s.send(PROXY_IP, PROXY_PORT, 'ACK', U_NAME, U_PORT, OPTION,
                       my_socket, LOG, SONG, AUDIO_PORT, PASS, '')

        if METHOD == 'BYE':
            s = MY_SOCKET()
            s.send(PROXY_IP, PROXY_PORT, METHOD, U_NAME, U_PORT, OPTION,
                   my_socket, LOG, SONG, AUDIO_PORT, PASS, '')
            data = my_socket.recv(1024)
            s.received(data, LOG, PROXY_IP, PROXY_PORT)

    except socket.error:
        line = 'No server listening at ' + PROXY_IP + ' port: ' + PROXY_PORT
        logfile = LOG_FILE()
        logfile.write('Error: ' + line, LOG)
        sys.exit(line)
