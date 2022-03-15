import socket
import threading
import hashlib
import signal
import sys

HOST = '127.0.0.1'
PORT = 1233

def signal_handler(key, frame):
	print("\n\n[!] Exiting...\n")
	sys.exit(1)

signal = signal.signal(signal.SIGINT, signal_handler)

def threaded_client(connection):
    connection.send(str.encode('Enter your username: '))
    username = connection.recv(2048)
    username = username.decode()
    connection.send(str.encode('Enter your password: '))
    password = connection.recv(2048)
    password = password.decode()
    password=hashlib.sha256(str.encode(password)).hexdigest()

    check_login(connection, username, password)
    
    transference = connection.recv(2048)
    from_account = transference.decode().split(',')[0].strip()
    to_account = transference.decode().split(',')[1].strip()
    amount = transference.decode().split(',')[2].strip()

    send_message(connection, from_account, to_account, amount)
    connection.close()

def check_login(connection, username, password):
 
    if username not in HashTable:
        HashTable[username]=password
        connection.send(str.encode('[+] Registration successful')) 
        print('Registered: ',username)
        print("{:<8} {:<20}".format('Username','Password'))
        for k, v in HashTable.items():
            label, num = k,v
            print("{:<8} {:<20}".format(label, num))
        print("-------------------------------------------")
        
    else:
        if(HashTable[username] == password):
            connection.send(str.encode('[+] Connection successful'))
            print('[+] Connected: ',username)
        else:
            connection.send(str.encode('[!] Login failed'))
            print('Connection denied: ',username)


def send_message(connection, from_account, to_account, amount):
    connection.send(str.encode('Ok, it will be transfered {} from {} to {} in 2-3 working days. Thanks for your patience'.format(
        amount, from_account, to_account)))

if __name__=='__main__':

    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    ThreadCount = 0
    try:
        ServerSocket.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))

    print('[+] Waiting for client connection...')
    ServerSocket.listen(5)
    HashTable = {}
    
    while True:
        client, address = ServerSocket.accept()
        client_handler = threading.Thread(
            target=threaded_client,
            args=(client,)  
        )
        client_handler.start()
        ThreadCount += 1
        print('Connection request: ' + str(ThreadCount))
