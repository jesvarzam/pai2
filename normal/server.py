import socket
import threading
import hmac, hashlib, uuid, signal,sys, os
import signal, sys, os
from datetime import datetime

HOST = '127.0.0.1'
PORT = 1233
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

def signal_handler(key, frame):
	print("\n\n[!] Exiting...\n")
	sys.exit(1)

signal = signal.signal(signal.SIGINT, signal_handler)

def threaded_client(connection):
    connection.send(str.encode('\n[+] Connection successful'))
    key = connection.recv(1024)
    message = connection.recv(2048)
    if not check_nonce(message):
        write_log(False)
        write_message('[{}] ➝ Invalid message, repeated nonce ➝ '.format(datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")) + message.decode() + '\n\n')
        connection.send(str.encode('\n[!] Invalid message, repeated nonce. Please try again.'))
        connection.close()
        return
    
    alg_cript = message.decode().split(':')[5].strip()
    calculated_hmac = calculate_hmac(key, message, alg_cript)
    check_message(connection, message, calculated_hmac,key)
    connection.close()

def calculate_hmac(key, message, alg_cript):
    from_account = message.decode().split(':')[0].strip()
    to_account = message.decode().split(':')[1].strip()
    amount = message.decode().split(':')[2].strip()
    nonce = message.decode().split(':')[3].strip()
    message = str.encode(from_account + ':' + to_account + ':' + amount + ':' + nonce)
    if alg_cript == "1":
        return hmac.new(key, message, hashlib.sha256).hexdigest()
    elif alg_cript == "2":
        return hmac.new(key, message, hashlib.sha512).hexdigest()
    elif alg_cript == "3":
        return hmac.new(key, message, hashlib.sha3_256).hexdigest()
    elif alg_cript == "4":
        return hmac.new(key, message, hashlib.sha3_512).hexdigest()
    else:
	    print("Invalid algorithm")

def check_message(connection, message, calculated_hmac,key):
    from_account = message.decode().split(':')[0].strip()
    to_account = message.decode().split(':')[1].strip()
    amount = message.decode().split(':')[2].strip()
    mac = message.decode().split(':')[4].strip()
        
    if(mac == calculated_hmac):
        write_log(True)
        write_message('[{}] ➝ Valid message ➝ '.format(datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")) + message.decode() + '\n\n')
        send_message(connection, from_account, to_account, amount, key)

    else:
        write_log(False)
        write_message('[{}] ➝ Invalid message, HMAC is different ➝ '.format(datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")) + message.decode() + '\n\n')
        connection.send(str.encode('\n[!] Invalid message, HMAC is different. Please try again.'))

def send_message(connection, from_account, to_account, amount, key):
    id_transfer=uuid.uuid4().hex
    mac = hmac.new(key, str.encode(id_transfer), hashlib.sha256).hexdigest()
    res=str(id_transfer)+"-"+str(mac)
    connection.send(str.encode('\n[+] It will be transfered {} from {} to {} in 2-3 working days. Thanks for your patience.\nYour transfer id is: {}\n'.format(
        amount, from_account, to_account,res)))
    
def check_nonce(message):
    nonce = message.decode().split(':')[3].strip()
    if nonce in NonceTable:
        return False
    NonceTable.append(nonce)
    return True
    
def write_log(check):
    file = open(CURRENT_PATH+"/../logs/kpi.txt", "r")
    list_of_lines = file.readlines()
    if check:
        list_of_lines[0] = "Valid messages: " + str(int(list_of_lines[0].split(':')[1].strip()) + 1) + "\n"
    else:
        list_of_lines[1] = "Invalid messages: " + str(int(list_of_lines[1].split(':')[1].strip()) + 1) + "\n"
    list_of_lines[2] = "Total messages: " + str(int(list_of_lines[2].split(':')[1].strip()) + 1) + "\n"
    kpi = int(list_of_lines[0].split(':')[1].strip()) / int(list_of_lines[2].split(':')[1].strip()) * 100
    list_of_lines[3] = "KPI: " + str(round(kpi, 2)) + "%"
    file = open(CURRENT_PATH+"/../logs/kpi.txt", "w")
    file.writelines(list_of_lines)
    file.close()

def write_message(message):
    file = open(CURRENT_PATH+"/../logs/messages.txt", "a")
    file.write(message)
    file.close()

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
