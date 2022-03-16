import socket
import signal
import sys

def signal_handler(key, frame):
	print("\n\n[!] Exiting...\n")
	sys.exit(1)

signal = signal.signal(signal.SIGINT, signal_handler)

def login(client):
	response = client.recv(2048)
	
	# Input UserName
	name = input(response.decode())	
	client.send(str.encode(name))
	response = client.recv(2048)
	
	# Input Password
	password = input(response.decode())	
	client.send(str.encode(password))
	
	''' Response : Status of Connection :
		1 : Registeration successful 
		2 : Connection Successful
		3 : Login Failed
	'''

def send_message(client):
	while True:
		from_account = input("\nEnter your account number: ")
		to_account = input("\nEnter the account number you want to transfer to: ")
		amount = input("\nEnter the amount you want to transfer: ")
		message = from_account + "," + to_account + "," + amount
		if message == 'q':
			break
		client.send(str.encode(message))
		response = client.recv(2048)
		return response.decode()

if __name__=='__main__':
	
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(('127.0.0.1', 1233))
	
	login_response = login(client)
	login_response = client.recv(2048)
	login_response = login_response.decode()
	print(login_response)
	message_response = send_message(client)
	print(message_response)
	client.close()
