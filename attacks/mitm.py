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
    key = connection.recv(1024)    
    message = connection.recv(2048)
    message_dec=message.decode()
    print("[↓] Captured message [↓]")
    print(message_dec + "\n")
    print("[↓] Message breakdown [↓]")
    print("From: " + str(message_dec).split(":")[0])
    print("To: " + str(message_dec).split(":")[1])
    print("Amount: " + str(message_dec).split(":")[2] +"\n")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((HOST, SERVER_PORT))
    server.send(key)
    time.sleep(0.1)
    server.send(message)
    time.sleep(0.1)
    response = server.recv(2048)
    print("[↓] Server Response [↓] ")
    print(response.decode())
    connection.send(response)
    #attack_option = input("\n[+] Do you want to attack this message? (1: Replay attack - 2: MITM attack)")

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
        print('\n[+] Connection received.\n')
