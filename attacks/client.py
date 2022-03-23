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

def calculate_hmac(key, message, alg_cript):
	if alg_cript == "1":
		return hmac.new(key, str.encode(message), hashlib.sha256).hexdigest()
	elif alg_cript == "2":
		return hmac.new(key, str.encode(message), hashlib.sha512).hexdigest()
	elif alg_cript == "3":
		return hmac.new(key, str.encode(message), hashlib.sha3_256).hexdigest()
	elif alg_cript == "4":
		return hmac.new(key, str.encode(message), hashlib.sha3_512).hexdigest()
	else:
		print("Invalid algorithm")


def send_message(client, key):
	while True:
		alg_cript = input("\nEnter algorithm to use (1: SHA-256 - 2: SHA-512 - 3: SHA3-256 - 4: SHA3-512): ")
		from_account = input("\nEnter your account number: ")
		to_account = input("\nEnter the account number you want to transfer to: ")
		amount = input("\nEnter the amount you want to transfer: ")
		message = from_account + ":" + to_account + ":" + amount + ":" + uuid.uuid4().hex
		mac = calculate_hmac(key, message, alg_cript)
		message+= ":" + mac + ":" + alg_cript
		client.send(str.encode(message))
		response = client.recv(2048)
		print("\n" + response.decode())
		response_dec=str(response.decode()).split(": ")[1]
		id_transfer=str(response_dec).split("-")[0]
		mac_transfer=str(response_dec).split("-")[1].strip()
		if(hmac.compare_digest(mac_transfer, hmac.new(key, str.encode(id_transfer), hashlib.sha256).hexdigest())):
			print("\n[+] Integrity verified. Transfer successful.")
		else:
			print("\n[!] Integrity failed ➝ MITM attack detected")
		return response.decode()

if __name__=='__main__':
	

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(('127.0.0.1', 1233))
	connection_status = client.recv(1024)
	print(connection_status.decode())
	
	key = generate_and_send_key(client)
	message_response = send_message(client, key)
	client.close()