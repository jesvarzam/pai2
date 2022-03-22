import socket
import threading
import hashlib, hmac
import signal, sys, time

HOST = '127.0.0.1'
MITM_PORT = 1233
SERVER_PORT = 1234

def signal_handler(key, frame):
	print("\n\n[!] Exiting...\n")
	sys.exit(1)

signal = signal.signal(signal.SIGINT, signal_handler)

def threaded_client(connection):
    connection.send(str.encode('\n[+] Connection successful'))
    key = recv_key(connection)
    message = connection.recv(2048)
    connection.close()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((HOST, SERVER_PORT))
    server.send(key)
    time.sleep(0.5)
    server.send(message)
    time.sleep(0.5)
    response = server.recv(2048)
    print('hola', response.decode())
    #attack_option = input("\n[+] Do you want to attack this message? (1: Replay attack - 2: MITM attack)")

def recv_key(connection):
    key = connection.recv(1024)
    return key

def send_message(connection, from_account, to_account, amount):
    connection.send(str.encode('\n[+] It will be transfered {} from {} to {} in 2-3 working days. Thanks for your patience.\n'.format(
        amount, from_account, to_account)))

if __name__=='__main__':

    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        ServerSocket.bind((HOST, MITM_PORT))
    except socket.error as e:
        print(str(e))

    print('\n[+] Waiting for client connection...')
    ServerSocket.listen(5)
    
    while True:
        client, address = ServerSocket.accept()
        client_handler = threading.Thread(
            target=threaded_client,
            args=(client,)  
        )
        client_handler.start()
        print('\n[+] Connection received.')
