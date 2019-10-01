import socket, threading
from getch import getch
from collections import deque


# input variable
msgArr = deque()
# authorise your existence.
def authorise(conn):
	username = ''
	valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	print("Enter a valid username with no special characters {/, *, (, ), @, ! etc.} and *less than* 50 letters: ", end='')
	while True:
		username = input()
		if not (0 < len(username) < 50):
			print("Invalid length.\nTry again: ", end='')
			continue
		
		

		valid_username = True
		for letter in username:
			if letter not in valid_chars:
				print("Invalid username\nTry again: ", end='')
				valid_username = False
				break

		if not valid_username:
			continue

		
		conn.send(str.encode(username))
		print("Checking if username is valid or not...")
		authorised = str(conn.recv(2), 'utf-8')
		if authorised == '1':
			welcome_msg = "It is! Welcome to your very own chatroom!"
			# Make the welcome a little fancy!
			print(
				"\n" + 
				('-' * (len(welcome_msg) + 2)) + '\n' + 
				' ' + 
				welcome_msg + '\n' + 
				('-' * (len(welcome_msg) + 2))
				)

			break

		else:
			print("Username already taken :( \nTry again: ", end='')


def input_message():
	letter = ''
	global msgArr

	while letter != '\r':
		letter = getch()

		if letter == '\b':
			print('\b \b', flush=True, end='')
			
			try: msgArr.pop()
			except IndexError: pass
			continue

		print(letter, flush=True, end='')
		msgArr.append(letter)

	print()

# Send message.
def send(conn):
	global msgArr

	try:
		while True:
			input_message()
			conn.send(str.encode(''.join(msgArr)))
			msgArr.clear()
	except socket.errors as e:
		conn.close()
		print("Some error caused you to disconnect to the chatroom.\n Pass the error code/message to dev: \n\n", str(e))




# Receive message.
def recv(conn):
	global msgArr
	while True:
		msg = str(conn.recv(5000), 'utf-8')
		if len(msgArr) > 0:
			# Clear the previous message...
			print('\b' * len(msgArr), end='')
			print(' ' * len(msgArr), end='')
			print('\b' * len(msgArr), end='')
			# Done...

			# Print the oncoming message.
			print(msg)

			# Reprint the half-typed message of user.
			print(''.join(msgArr), flush=True, end='')

		else:
			print(msg)	
		



def main():
	server_ip = "192.168.43.228"	# socket.gethostbyname(socket.gethostname())
	port = 9999

	conn = socket.socket()

	try:
		conn.connect((server_ip, port))
		authorise(conn)
	except Exception as err:
		print("Error connecting to chatroom :( \nClose the application and try again.")
		print(err)
		input()
		exit(-1)

	t_send = threading.Thread(target=send, args=(conn,))
	t_recv = threading.Thread(target=recv, args=(conn,))

	t_send.start()
	t_recv.start()


main()
