import socket
import signal, sys
import hmac, hashlib, uuid, secrets

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

def generate_and_send_key(client):
	key = secrets.token_urlsafe(16)
	client.send(str.encode(key))
	return str.encode(key)


def send_message(client, key):
	while True:
		from_account = input("\nEnter your account number: ")
		to_account = input("\nEnter the account number you want to transfer to: ")
		amount = input("\nEnter the amount you want to transfer: ")
		message = from_account + ":" + to_account + ":" + amount + ":" + uuid.uuid4().hex
		mac = hmac.new(key, str.encode(message), hashlib.sha256).hexdigest()
		message+= ":" + mac
		if message == 'q':
			break
		print(message)
		client.send(str.encode(message))
		response = client.recv(2048)
		return response.decode()

if __name__=='__main__':
	
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(('127.0.0.1', 1233))
	
	# login_response = login(client)
	# login_response = client.recv(2048)
	# login_response = login_response.decode()
	# print(login_response)
	key = generate_and_send_key(client)
	message_response = send_message(client, key)
	print(message_response)
	client.close()
