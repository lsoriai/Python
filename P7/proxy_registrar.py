#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa proxy que hace de intermediario en una sesión sip
"""

import socket
import SocketServer
import sys
import os
import time
import base64
import random
import string
from random import choice
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class XML_PROXY(ContentHandler):
    """
    Extrae la información del fichero Config.xml
    """

    def __init__(self):

        self.Dic = {"server": ["name", "ip", "puerto"],
                    "database": ["path", "passwpath"],
                    "log": ["path"]}
        self.config = {}

    def startElement(self, name, attrs):
        """
        Asigna al diccionario los valores que lee del fichero config.xml
        """
        if name in self.Dic:
            for Atrib in self.Dic[name]:
                self.config[name + '_' + Atrib] = attrs.get(Atrib, "----")
                if name + '_' + Atrib == "server_ip":
                    if len(self.config["server_ip"]) == 0:
                        self.config["server_ip"] = "127.0.0.1"

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


class DATABASE():
    """
    Manejador de usuarios
    """

    def writedatabase(self, dic, USERS):
        """
        Escribe en el fichero usuarios.txt
        """
        databasefile = open(USERS, 'w')
        for user in dic.keys():
            now = str(time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time())))
            name = str(user)
            ip = str(dic[user][0])
            port = str(dic[user][1])
            expire = str(dic[user][2])
            extime = time.strftime('%Y%m%d%H%M%S', time.gmtime(dic[user][3]))
            databasefile = open(USERS, 'a')
            line = now + ' ' + name + ' ' + ip + ' ' + port + ' '
            line += expire + ' ' + str(extime) + '\r\n'
            databasefile.write(line)
            databasefile.close()
        databasefile.close()

    def add_user(self, name, ip, port, expire, dic):
        """
        Añade al diccionario users el nuevo usuario
        """
        if len(dic) == 0:
            key = [ip, port, expire, time.time() + int(expire)]
            dic[name] = key
        else:
            for user in dic.keys():
                if dic[user] == name:
                    key = [ip, port, expire, time.time() + int(expire)]
                    dic[user] = key
                else:
                    key = [ip, port, expire, time.time() + int(expire)]
                    dic[name] = key

    def expire(self, dic, USERS):
        """
        Elimina a los usuarios expirados
        """
        for user in dic.keys():
            now = time.time()
            expiretime = int(dic[user][3])
            if now >= expiretime:
                del dic[user]
        self.writedatabase(dic, USERS)

    def recovery(self, USERS, dic):
        """
        Recupera los datos del paquete de texto
        """
        databasefile = open(USERS, 'r')
        lines = databasefile.readlines()
        for line in lines:
            name = line.split(' ')[1]
            ip = line.split(' ')[2]
            port = line.split(' ')[3]
            expire = line.split(' ')[4]
            expire_time = line.split(' ')[5].replace('\r\n', '')
            dic[name] = [ip, port, expire, expire_time]


class SECURITY:
    """
    Clase que se encarga de los procesos de encriptacion y desencriptacion
    """

    def id_generator(self, n):
        """
        Genera un código aleatorio para el envío de la contraseña
        """
        return ''.join([choice(string.letters + string.digits)
               for i in range(n)])

    def writedatabase(self, codigo, PASSWORD, user):
        """
        Guarda el código usado en la encriptación
        """
        passwordfile = open(PASSWORD, 'r')
        lines = passwordfile.readlines()
        passwordfile = open(PASSWORD, 'w')
        total = ''
        for line in lines:
            line = line.replace('\n', '')
            name = line.split(' ')[0]
            passwd = line.split(' ')[1]
            if name == user:
                total += name + ' ' + passwd + ' ' + codigo + '\n'
            else:
                total += line + '\n'
        passwordfile.write(total)

    def decrypt(self, encrypted, codec):
        """
        Desencripta la contraseña enviada por el UA
        """

        encrypted_array = list(encrypted)
        codec_array = list(codec)
        len_passwd = len(encrypted_array) - len(codec_array)
        password = ''
        i = 1
        while i < 2 * (len_passwd + 1):
            if i % 2 == 1:
                password += encrypted_array[i]
            i = i + 1
        return password

    def confirm(self, user, encrypted, PASSWORD):
        """
        Comprueba la autenticidad del cliente
        """

        passwordfile = open(PASSWORD, 'r')
        lines = passwordfile.readlines()
        for line in lines:
            codec = line.split(' ')[2]
            name = line.split(' ')[0]
            if user == name:
                decrypt_passwd = self.decrypt(encrypted, codec)
                passwd = line.split(' ')[1]
                if decrypt_passwd == passwd:
                    return 'True'
                    break
        return 'False'


class PROXY(SocketServer.DatagramRequestHandler):

    def reenviar(self, ip, port, line, method):
        """
        Reenvia los paquetes entre distintos ususarios
        """
        trama = line.replace('\r\n', ' ')

        #Traza que añade el proxy----------------------------------------------
        rand = random.randint(0, 0xFFFFFF)
        traza_proxy = 'Via: SIP/2.0/UDP ' + ip + ':' + port + ';branch='
        traza_proxy += str(rand) + '\r\n'
        #----------------------------------------------------------------------

        if method == 'INVITE':
            primera = line.split('SIP/2.0')[0]
            segunda = line.split('SIP/2.0')[1]
            line = primera + 'SIP/2.0\r\n' + traza_proxy + segunda

        if method == 'ACK':
            line = line + traza_proxy

        if method == 'BYE':
            line = line + traza_proxy

        traza = 'Sent to: ' + ip + ':' + port + ':' + trama
        logfile = LOG_FILE()
        logfile.write(traza, LOG)
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((ip, int(port)))
        my_socket.send(line)
        return my_socket.recv(1024)

    def handle(self):
        while 1:
            line = self.rfile.read()
            if not line:
                break
            print 'El cliente nos manda: ' + line
            trama = line.replace('\r\n', ' ')
            method = trama.split(' ')[0]
            ip = self.client_address[0]

            #Comentario cabecera proxy
            rand = random.randint(0, 0xFFFFFF)
            traza_proxy = 'Via: SIP/2.0/UDP ' + PROXY_IP + ':' + PROXY_P
            traza_proxy += ';branch=' + str(rand) + '\r\n'
            #------------------------------------------------------------------

            if method == 'REGISTER':
                try:
                    port = trama.split(':')[2].split(' ')[0]
                    name = trama.split(':')[1]
                    expire = str(trama.split(' ')[4])
                except:
                    self.wfile.write('Error: Datos mal introducidos')

                traza = 'Received from ' + ip + ':' + port + ': ' + line
                logfile = LOG_FILE()
                logfile.write(traza, LOG)
                fields = line.split(' ')
                user = fields[1].split(':')[1]
                security = SECURITY()
                if len(fields) == 4:
                    codigo = security.id_generator(40)
                    security.writedatabase(codigo, PASSWORD, user)
                    response = '401 Unauthorized ' + str(codigo)
                    self.wfile.write(response)
                else:
                    permission = security.confirm(user, fields[4], PASSWORD)
                    if permission == 'True':
                        database = DATABASE()
                        database.add_user(name, ip, port, expire, dic_users)
                        database.expire(dic_users, USERS)
                        line = '200 OK\r\n'
                        traza = 'Sent to: ' + ip + ':' + port + ':' + line
                        logfile = LOG_FILE()
                        logfile.write(traza, LOG)
                        self.wfile.write(line)
                    else:
                        self.wfile.write('Incorrect password')

            if method == 'INVITE':
                new_user = trama.split(' ')[1].split(':')[1]
                user = trama.split(' ')[7].split('=')[1]
                ip = trama.split(' ')[8]
                song = trama.split(' ')[11].split('=')[1]
                ip_song = trama.split(' ')[12]
                database = DATABASE()
                database.recovery(USERS, dic_users)
                if len(dic_users) == 0 or user not in dic_users:
                    self.wfile.write('Es necesario estar registrado')
                    break
                if new_user in dic_users:
                    new_user_ip = dic_users[new_user][0]
                    new_user_port = dic_users[new_user][1]
                    response = self.reenviar(new_user_ip, new_user_port, line,
                                             method)
                    response = response + traza_proxy
                    self.wfile.write(response)
                    logfile = LOG_FILE()
                    port = dic_users[user][1]
                    trama = response.replace('\r\n', ' ')
                    traza = 'Sent to: ' + ip + ':' + port + ':' + trama
                    logfile.write(traza, LOG)
                else:
                    line = 'SIP/2.0 404 User Not Found'
                    logfile = LOG_FILE()
                    logfile.write('Error: ' + line, LOG)
                    self.wfile.write(line)

            if method == 'ACK':
                user = trama.split(':')[1].split(' ')[0]
                user_ip = dic_users[user][0]
                user_port = dic_users[user][1]
                self.reenviar(user_ip, user_port, line, method)

            if method == 'BYE':
                user = trama.split(':')[1].split(' ')[0]
                if user in dic_users:
                    user_ip = dic_users[user][0]
                    user_port = dic_users[user][1]
                    response = self.reenviar(user_ip, user_port, line, method)
                    response = response + traza_proxy
                    self.wfile.write(response)
                    logfile = LOG_FILE()
                    port = dic_users[user][1]
                    trama = response.replace('\r\n', ' ')
                    traza = 'Sent to: ' + ip + ':' + port + ':' + trama
                    logfile.write(traza, LOG)
                else:
                    line = 'SIP/2.0 404 User Not Found'
                    logfile = LOG_FILE()
                    logfile.write('Error: ' + line, LOG)
                    self.wfile.write(line)

            if method not in methods:
                line = 'SIP/2.0 405 Method Not Allowed\r\n'
                logfile = LOG_FILE()
                logfile.write('Error: ' + line, LOG)
                self.wfile.write(line)
                break


if __name__ == "__main__":
    methods = ['REGISTER', 'INVITE', 'ACK', 'BYE']
    try:
        CONFIG = sys.argv[1]
        if not os.access(CONFIG, os.F_OK):
            sys.exit('Usage: python proxy_registrar.py config')
    except ValueError:
        sys.exit('Usage: python proxy_registrar.py config')
    except IndexError:
        sys.exit('Usage: python proxy_registrar.py config')

    dic_users = {}
    parser = make_parser()
    Handler = XML_PROXY()
    parser.setContentHandler(Handler)
    parser.parse(open(CONFIG))
    LIST_CONFIG = Handler.get_tags()
    #Extraemos de la lista los datos importantes para empezar a trabajar
    PROXY_NAME = LIST_CONFIG['server_name']
    PROXY_IP = LIST_CONFIG['server_ip']
    PROXY_P = LIST_CONFIG['server_puerto']
    USERS = LIST_CONFIG['database_path']
    LOG = LIST_CONFIG['log_path']
    PASSWORD = LIST_CONFIG['database_passwpath']

    txtfile = open(LOG, 'w')
    Time = time.strftime('%Y%m%d%H%M%S ', time.gmtime(time.time()))
    txtfile.write(str(Time) + 'Starting...\r\n')
    txtfile.close()

    try:
        server = SocketServer.UDPServer((PROXY_IP, int(PROXY_P)), PROXY)
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Programa finalizado'
        logfile = LOG_FILE()
        logfile.write('Finishing...', LOG)
