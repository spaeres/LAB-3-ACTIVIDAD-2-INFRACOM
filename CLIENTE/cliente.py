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


def escribir_log(x, y, tipo_archivo, exito, hash):
    nombre_log = "Cliente" + x + "-Prueba-" + y + "(" + tipo_archivo + ").txt"
    file = open("./ArchivosRecibidos/" + nombre_log, "a")
    file.write("------------Recibido-------------\n")
    if (tipo_archivo == "100MB"):
        file.write("Archivo recibido:   " + NOMBRE_ARCHIVO_100M + " de tamaño 100MB\n")
    elif (tipo_archivo == "250MB"):
        file.write("Archivo recibido:   " + NOMBRE_ARCHIVO_250M + " de tamaño 250MB\n")
    if (exito):
        file.write("El hash recibido es igual al hash del archivo recibido\n")
    else:
        file.write("El hash recibido es diferente al hash del archivo recibido\n")

    file.write("hash esperado: " + hash)
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
    if (digest == hash_recibido):
        iguales = True
    return iguales, digest


def verificar_transferencia_exitosa(numero_bytes_recibidos, numero_bytes_esperados):
    return numero_bytes_recibidos == numero_bytes_esperados


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Connect the socket to the port on the server
# given by the caller
host = '192.168.20.34'
port = 29170
hash = ""
server_address = (host, port)
# server_address = (sys.argv[1], 10000)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
escribir_directorio()

try:
    entrada0 = input('¿Cuantos clientes desea? (Minimo 1 - maximo 25)\n')
    for i in range(int(entrada0)):
        message = b'Hola, estoy listo para recibir archivos |' + bytes(sock.getsockname()[0], 'ascii') + b"|" + bytes(str(sock.getsockname()[1]), 'ascii')
        sock.send(message)
        dataInicial = sock.recv(1024)
        print('Recibi tu mensaje: {!r}'.format(dataInicial))

        entrada1 = input('Que archivo quieres? 100 MB o 250 MB? (Por favor escribir unicamente el que desea: Ej: "100MB")\n')
        rutaDeseada = ''
        ruta_archivo = ''
        nombre_archivo = ''
        if entrada1 == "100MB":
            nombre_archivo = NOMBRE_ARCHIVO_100M
            ruta_archivo = RUTA_ARCHIVO_100M
            rutaDeseada = b'archivo_100M'
        elif entrada1 == "250MB":
            nombre_archivo = NOMBRE_ARCHIVO_250M
            ruta_archivo = RUTA_ARCHIVO_250M
            rutaDeseada = b'archivo_250M'

        sock.send(rutaDeseada)
        # Archivo:
        f = open(ruta_archivo, 'wb')
        l = sock.recv(10024)
        despedida = ''
        while (l):
            paquete = l.decode('ascii')
            print("Recibiendo archivo...")
            # Ultimo paquete del archivo es el que termina con |:
            if '|' in paquete:
                despedida = paquete[paquete.index('|') + 1:len(paquete)]
                # No se escribe el ultimo paquete!
                break
            f.write(l)
            l = sock.recv(10024)
        archivo_nueva_ruta = f.name
        f.close()
        print('Recibido: ', despedida)
        print('Verificando transferencia exitosa....')
        tamanno_archivo_recibido = os.path.getsize(archivo_nueva_ruta)
        tammano_archivo_esperado = int(despedida.split("|")[1])
        print('Transferencia Exitosa: '+str(verificar_transferencia_exitosa(tamanno_archivo_recibido, tammano_archivo_esperado)))
        print('Bytes recibidos: '+str(tamanno_archivo_recibido))
        print('Bytes esperados: ' + str(tammano_archivo_esperado))
        x = i + 1
        #escribir_log(str(x), entrada0, entrada1, comparacion[0], comparacion[1])

        print('Recibido despedida server: ' + despedida)
except Exception as e:
    print("Error: " + e.__str__())
    exitoso = False
    sock.close()
