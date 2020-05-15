import socket, threading

# Contains the respective user's thread.
user_threads = dict()
# Contains the connection object for the respective user.
user_connections = dict()

# This dictionary is commented out because it probably won't be needed.
# online_status = dict()


def mainloop(conn, username):
	user_connections[username] = conn
	t = threading.Thread(target=recv, args=(conn, username))
	user_threads[username] = t

	try: 
		t.start()
		t.join()
	finally:
		# Close the thread.
		# user_threads[username].close()
		user_threads.pop(username)
		user_connections.pop(username)


# authorise user and then make a thread for recv() and store it into the user_threads dictionary.

def auth(conn):
    # TODO: Make the authorise code better -- Done, kinda. Need to make the verifications on the server side too.
    username = str(conn.recv(50), 'utf-8')
    
    # Until user gives a valid username which is not already existing, keep waiting
    # for a new username.
    while username in user_connections.keys():
    	conn.send(str.encode('0'))
    	username = str(conn.recv(50), 'utf-8')

    conn.send(str.encode('1'))

    mainloop(conn, username)



# Send the crap user requested. This fn is called by the recv function of the sender, and called for the recipient.
def send(conn, message, sender_username):
    conn.send(str.encode(sender_username + ": " + message))


# Send a message to every active user.
def sendall(sender_conn, message, sender_username):
	for connection in user_connections.values():
		if connection is sender_conn:
			continue
		send(connection, message, sender_username)


# Is threaded for each user, and checks for any message entered.
def recv(conn, username):
	msg = ''
	while True:
		
	    msg = str(conn.recv(5000), 'utf-8')
	    print(msg)
        try:
	        first_word = msg[:msg.index(' ')]
        except ValueError: # No space in message.
            sendall(conn, msg, username)
            continue
            
	    if first_word[0] == '@':    # Message is addressed to a specific person.
	    	recipient = first_word[1:]  # username of receiver of message.

	    	if recipient in user_connections.keys():
                try:
	    		    msg = msg[msg.index(' ') + 1 : ]
                    send(user_connections[recipient], msg, username)
                except ValueError:  # Empty message.
                    send(user_connections[recipient], f"<{username} sent an empty message>", username)
	    	else:
	    		conn.send(str.encode(f"System: {recipient} is offline, or doesn't exist."))
	    else:
	    	sendall(conn, msg, username)




s = socket.socket()

s.bind(('', 9999))

s.listen(20)

while True:
    conn, addr = s.accept()

    t = threading.Thread(target=auth, args=(conn,))
    t.start()
