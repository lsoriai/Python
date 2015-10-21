#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Script de comprobación de entrega de práctica

Para ejecutarlo, desde la shell: 
 $ python check-p6.py login_laboratorio

"""

import os
import random
import sys


# Diccionario con la relación de nombres de usuario
# en los laboratorios (clave) y nombres de usuario en GitHub (valor)
github_dict = {
    "iarranz": "igarag",
    "smarin": "silviamaa",
    "miriammz": "miriammz",
    "rgalan": "raquelgalan",
    "jmarugan": "jfernandezmaru",
    "jcdb": "jcdb",
    "jcdb": "jcdb",
    "maferna": "mghfdez",
    "mtejedor": "mtejedorg",
    "apavo": "apavo",
    "oterino": "aoterinoc",
    "ndiaz": "nathdiaza",
    "crodrigu": "crodriguezgarci",
    "ilope": "ilope236",
    "opedraza": "olallasanchez",
    "calvarez": "calvarezpe",
    "dpascual": "dpascualhe",
    "avera": "Abel-V",
    "amoles": "alvaromv83",
    "aramas": "aramas",
    "jbaos": "JaviBM11",
    "rsierra": "rsierrangulo",
    "imalo": "nmalo5",
    "mireya": "mireepink",
    "albagc": "albagcs",
    "rpablos": "raquelpt",
    "cgarcia": "celiagarcia",
    "lyanezgu": "lyanezgu",
    "omarled": "auronff10",
    "roger": "rogerurrutia",
    "lsoria": "lsoriai",
    "zhiyuan": "ziyua",
    "mcapitan": "mcapitan",
    "juanmis": "Jmita", 
    "molina": "jmartinezmolina",
    "afrutos": "alejandrodefrutos",
}

if len(sys.argv) != 2:
    print
    sys.exit("Usage : $ python check-p6.py login_laboratorio")

if sys.argv[1] not in github_dict:
    print
    print "Usage: $ python check-p6.py login_laboratorio"
    print "donde login_laboratorio es tu login en los laboratorios Linux"
    print
    sys.exit()

repo_git = "http://github.com/" + github_dict[sys.argv[1]] + "/ptavi-p6"

files = ['README.md',
         'LICENSE',
         '.gitignore',
         'client.py',
         'server.py',
         'invite.libpcap',
         'check-p6.py',
         'mp32rtp',
         '.git']

aleatorio = str(int(random.random() * 1000000))

error = 0

print 
print "Clonando el repositorio " + repo_git + "\n"
os.system('git clone ' + repo_git + ' /tmp/' + aleatorio + ' > /dev/null 2>&1')
try:
    student_file_list = os.listdir('/tmp/' + aleatorio)
except OSError:
    error = 1
    print "Error: No se ha podido acceder al repositorio " + repo_git + "."
    print 
    sys.exit()

if len(student_file_list) != len(files):
    error = 1
    print "Error: solamente hay que subir al repositorio los ficheros indicados en las guion de practicas, que son en total " + str(len(student_file_list)) + " (incluyendo .git):"

for filename in files:
    if filename not in student_file_list:
        error = 1
        print "\tError: " + filename + " no encontrado. Tienes que subirlo al repositorio."

if not error:
    print "Parece que la entrega se ha realizado bien."
    print
    print "La salida de pep8 es: (si todo va bien, no ha de mostrar nada)"
    print
    os.system('pep8 --repeat --show-source --statistics /tmp/' + aleatorio + '/client.py /tmp/' + aleatorio + '/server.py')
print
