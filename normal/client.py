import socket
import signal, sys
import hmac, hashlib, uuid, secrets

def signal_handler(key, frame):
	print("\n\n[!] Exiting...\n")
	sys.exit(1)

signal = signal.signal(signal.SIGINT, signal_handler)

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
		client.send(str.encode(message))
		response = client.recv(2048)
		response_dec=str(response.decode()).split(": ")[1]
		id_transfer=str(response_dec).split("-")[0]
		mac_transfer=str(response_dec).split("-")[1].strip()
		if(hmac.compare_digest(mac_transfer, hmac.new(key, str.encode(id_transfer), hashlib.sha256).hexdigest())):
			print("[+] Integrity verify")
		else:
			print("[!] Integrity fail")
		return response.decode()

if __name__=='__main__':
	
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(('127.0.0.1', 1233))
	connection_status = client.recv(1024)
	print(connection_status.decode())
	
	key = generate_and_send_key(client)
	message_response = send_message(client, key)
	print(message_response)
	client.close()