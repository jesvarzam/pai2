import socket
import threading
import hashlib, hmac
import signal, sys

HOST = '127.0.0.1'
PORT = 1233

def signal_handler(key, frame):
	print("\n\n[!] Exiting...\n")
	sys.exit(1)

signal = signal.signal(signal.SIGINT, signal_handler)

def threaded_client(connection):
    
    connection.send(str.encode('\n[+] Connection successful'))
    key = recv_key(connection)
    message = connection.recv(2048)
    if not check_nonce(message):
        connection.send(str.encode('\n[!] Repeated nonce. Please try again.'))
        connection.close()
        return
    check_message(connection, message, key)
    connection.close()

def recv_key(connection):
    key = connection.recv(1024)
    return key.decode()

def check_message(connection, message, key):
    from_account = message.decode().split(':')[0].strip()
    to_account = message.decode().split(':')[1].strip()
    amount = message.decode().split(':')[2].strip()
    nonce = message.decode().split(':')[3].strip()
    mac = message.decode().split(':')[4].strip()
    
    check_message = from_account + ":" + to_account + ":" + amount + ":" + nonce
    
    if(hmac.compare_digest(mac, hmac.new(str.encode(key), str.encode(check_message), hashlib.sha256).hexdigest())):
        send_message(connection, from_account, to_account, amount)
    else:
        connection.send(str.encode('\n[!] Invalid message'))

def send_message(connection, from_account, to_account, amount):
    connection.send(str.encode('\n[+] It will be transfered {} from {} to {} in 2-3 working days. Thanks for your patience.\n'.format(
        amount, from_account, to_account)))
    
def check_nonce(message):
    nonce = message.decode().split(':')[3].strip()
    if nonce in NonceTable:
        return False
    return True

if __name__=='__main__':

    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        ServerSocket.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))

    print('\n[+] Waiting for client connection...')
    ServerSocket.listen(5)
    NonceTable = []
    
    while True:
        client, address = ServerSocket.accept()
        client_handler = threading.Thread(
            target=threaded_client,
            args=(client,)  
        )
        client_handler.start()
        print('\n[+] Connection received.')
