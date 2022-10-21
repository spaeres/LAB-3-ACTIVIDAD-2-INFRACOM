import socket
import os
import errno
import hashlib

NOMBRE_ARCHIVO_100M = 'archivo_100M'
NOMBRE_ARCHIVO_250M = 'archivo_250M'

RUTA_ARCHIVO_100M = './ArchivosRecibidos/archivo_100M'
RUTA_ARCHIVO_250M = './ArchivosRecibidos/archivo_250M'
RUTA_DIR_LOGS = '../Logs/'

# Hacer el archivo hash
nombre = ""


def nombrar_cliente(n_cliente):
    nombre = "cliente" + n_cliente


# Escribir el log(?)
def escribir_directorio():
    try:
        os.mkdir('ArchivosRecibidos')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
def escribir_log(x,y,tipo_archivo,exito, hash):
    nombre_log = "Cliente"+x+"-Prueba-"+y+"("+tipo_archivo+").txt"
    file = open("./ArchivosRecibidos/"+nombre_log,"a")
    file.write("------------Recibido-------------\n")
    if(tipo_archivo=="100MB"):
        file.write("Archivo recibido:   "+NOMBRE_ARCHIVO_100M + " de tamaño 100MB\n")
    elif(tipo_archivo=="250MB"):
        file.write("Archivo recibido:   "+NOMBRE_ARCHIVO_250M + " de tamaño 250MB\n")
    if(exito):
        file.write("El hash recibido es igual al hash del archivo recibido\n")
    else:
        file.write("El hash recibido es diferente al hash del archivo recibido\n")

    file.write("hash esperado: "+hash)
    file.close()


def comparar_hash(archivo_recibido, hash_recibido):
    iguales = False
    md5_hash = hashlib.md5()
    if archivo_recibido == NOMBRE_ARCHIVO_100M:
        a_file = open(RUTA_ARCHIVO_100M, "rb")
    else:
        a_file = open(RUTA_ARCHIVO_250M, "rb")
    content = a_file.read()
    md5_hash.update(content)

    digest = md5_hash.hexdigest()
    if(digest == hash_recibido):
        iguales = True
    return iguales, digest


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port on the server
# given by the caller
host = '192.168.85.128'
port = 29170
hash = ""
server_address = (host, port)
# server_address = (sys.argv[1], 10000)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
escribir_directorio()

try:
    entrada0= input('¿Cuantos clientes desea? (Minimo 1 - maximo 25)\n')
    for i in range(int(entrada0)):
        message = b'Hola, estoy listo para recibir archivos |'
        sock.send(message)
        
        dataInicial = sock.recv(1024)
        print('Recibi tu mensaje: {!r}'.format(dataInicial))

        entrada1 = input('Que archivo quieres? 100 MB o 250 MB? (Por favor escribir unicamente el que desea: Ej: "100MB")\n')
        rutaDeseada = ''
        ruta_archivo = ''
        nombre_archivo = ''
        if (entrada1 == "100MB"):
            nombre_archivo = NOMBRE_ARCHIVO_100M
            ruta_archivo = RUTA_ARCHIVO_100M
            rutaDeseada = b'archivo_100M'
        elif (entrada1 == "250MB"):
            nombre_archivo = NOMBRE_ARCHIVO_250M
            ruta_archivo = RUTA_ARCHIVO_250M
            rutaDeseada = b'archivo_250M'

        sock.send(rutaDeseada)
        # HASH:
        dataHash = sock.recv(1024)
        datosArchivoRestantes = ''
        if dataHash:
            recibido = dataHash.decode('latin1')
            nombre = recibido[0:recibido.index('|')]
            datosArchivoRestantes = recibido[recibido.index('|') + 1:len(recibido)]
        else:
            raise Exception('Deberia recibir el hash')
            
        print('Hash recibido:' + nombre)
        # Archivo:
        f = open(ruta_archivo, 'wb')
        l = sock.recv(1024)
        despedida = ''
        while (l):
            paquete = l.decode('latin1')
            print("Recibiendo archivo...")
            # Ultimo paquete del archivo es el que termina con |:
            if '|' in paquete:
                despedida = paquete[paquete.index('|') + 1:len(paquete)]
                # No se escribe el ultimo paquete!
                break
            f.write(l)
            l = sock.recv(1024)
        f.close()
        print('Recibido: ', despedida)
        print('Verificando integridad del archivo....')
        comparacion = comparar_hash(nombre_archivo, nombre)
        print('Hash verificado correctamente!') if comparacion[0] else print('Hash enviado por el servidor no es correcto:'+nombre+"!="+comparacion[1])
        x=i+1
        escribir_log(str(x),entrada0,entrada1,comparacion[0],comparacion[1])
        print('Recibido despedida server: '+despedida)
finally:
    sock.close()


    
