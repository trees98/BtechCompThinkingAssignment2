import socket
import threading
import time

# Server Info
HOST = "127.0.0.1"
PORT = 15000
INACTIVITY_TIMEOUT = 20
CHECK_INTERVAL = 5

# User dictionary
users = {
    "John":   {"password": "12345", "role": "admin", "subscribed": True, "inbox": [], "active": False, "last_activity": 0, "connection": None},
    "Deer":   {"password": "54321", "role": "editor", "subscribed": True, "inbox": [], "active": False, "last_activity": 0, "connection": None},
    "Bob":    {"password": "54321", "role": "viewer", "subscribed": True, "inbox": [], "active": False, "last_activity": 0, "connection": None},
    "Guest":  {"password": "00000", "role": "viewer", "subscribed": False, "inbox": [], "active": False, "last_activity": 0, "connection": None}
}

lock = threading.Lock()
running = True


# Send message to a user
def send_message(connection, message):
    try:
        connection.sendall((message + "\n").encode()) # Using the socket connection send the message perameter with a new line space for the client.
    except:
        pass


# Login a user
def login_user(connection): # Function that takes one parameter which is the socket connection.
    send_message(connection, "Enter username:") # Calls the send_message function that takes in two peramters, one being the socket connection and the other being the message.
    # In this case the message is "Enter username:".
    username = connection.recv(1024).decode().strip() # create a variable called username and take in the data sent by the client, decode and remove white space.
    # Repeat the same logic for prompting and recieving the password.
    send_message(connection, "\nEnter password:")
    password = connection.recv(1024).decode().strip()

    if username in users and users[username]["password"] == password: # This checks if the username sent from the client and stored on the server
        # in the variable username and if the users matching password in the user dictionary matches the password sent from the client stored in the password variable.
        user = users[username] # Take the entered username from the client and get the info for the user in the users dictionary and store in user.
        user["active"] = True # Set the users status as active or logged in.
        user["last_activity"] = time.time() # Mark the current time to check for inactivity later.
        user["connection"] = connection # Store the users connection.
        send_message(connection, f"\nWelcome {username}! You are logged in as {user['role']} : Have a super number 1 fun and safe time.") # Printing a welcome message for the user sent in username and displaying the role stored in user at ['role']

        #send_message(connection, f"\nuser: {user} and username:{username}") # This is to show how the data is stored after login
        return username, user
        
    else:
        send_message(connection, "Server: Invalid login. Try again.")
        return None, None # return None for both username and user showing a failed login.


# View Inbox
def view_inbox(connection, user): # Takes two parameters, the socket and the user's data.
    if not user["subscribed"]: # if the user is not subscribed
        send_message(connection, "Server: Please subscribe to view messages.") # Subscribed = False then print to the screen "Please subscribe...".
        return # If they are not subscribed then stop the function so the inbox is not displayed.
    if not user["inbox"]: # This checks if the inbox key in the dictionary is empty or false and if it is then send a message saying inbox empty.
        send_message(connection, "Server: Your inbox is empty.")
    else:
        for msg in user["inbox"]: # Itterate through the inbox attached to the user
            send_message(connection, f"- {msg}") # user the send_message function to send the message in the inbox
        user["inbox"].clear() # After viewing the msg's in inbox clear them


# Send Notification
def send_notification(user): # This function takes one parameter which is the users dictionary.
    role = user["role"] # This gets the role from the user.
    # Send a message depening on their role.
    if role == "admin":
        user["inbox"].append("Admin Alert: The system requires an update.") # If the role stored in the users dict is "admin" then add an alert to the inbox of that user.
    elif role == "editor":
        user["inbox"].append(f"Editor Alert: Hello, Please edit the menu as soon as possible!") # If the role stored in the users dict is "editor" then add an alert to the inbox of that user.
    elif role == "viewer":
        user["inbox"].append("Viewer Alert: We will have a new menu coming soon!")# If the role stored in the users dict is "viewer" then add an alert to the inbox of that user.


# Logout User
def logout_user(username, user): # Takes two parameters, the username logged in and the dictionary information attached stored as user.
    with lock: # this makes it so only one thread or connection can log out so there is no data conflicts.
        user["active"] = False # Change the active status to false
        user["connection"] = None # Remove the connection information stored in user.
    print(f"{username} logged out.", flush=True) # Show the client they have logged out with their coresponding username.
    

# Background Checker
def background_checker(): # This function is always running in the backround to check activity.
    while running: # This makes it run if the program is running.
        with lock: # Prevents multiple threads from changing users data.
            now = time.time() # Grabs the current time in seconds since the program started.
            for name, user in users.items(): # Loop through all the users in the dictionary.
                if user["active"] and now - user["last_activity"] > INACTIVITY_TIMEOUT: # Checks if 'active' in the user dictionary is true and if they have been inactive for longer than INACTIVITY_TIMEOUT.
                    send_message(user["connection"], "Server: You were logged out due to inactivity.") # Send a message with the users connection and say they were logged out.
                    logout_user(name, user) # Call the logout function to log that user out.
                elif user["active"] and user["subscribed"]: #if there active and have a subscription then go ahead and send them a message.
                    send_notification(user) # call the notification sender for that user.
        time.sleep(CHECK_INTERVAL) # Pauses the while loop for a set amount of time so it is not constantly checking.


# User Menu
def user_menu(connection, username, user):
    while user["active"]: # always list the menu until the user is not active
        # Send the menu to the client
        send_message(connection, "\n-*-*-Menu-*-*-")
        send_message(connection, "1. View Inbox")
        send_message(connection, "2. Logout")

        # Take in the clients response to the menu.
        try:
            choice = connection.recv(1024).decode().strip()
        except:
            break
        # If they select 1 to view the inbox then call the view_inbox function.
        if choice == "1":
            view_inbox(connection, user)
            user["last_activity"] = time.time()
            #Add logic to reset to the timer for inactivity time.time() = (user[last_activity])
        #If they select 2 to logout then call the logout_user function then break out of the menu loop.
        elif choice == "2":
            send_message(connection, "Server: Goodbye!")
            logout_user(username, user)
            break
        # If they enter anything else then ask them to try again.
        else:
            send_message(connection, "Server: Invalid option. Try again.")


# Handle Each Connection
def handle_client(connection, address): # Takes in the socket connection and the IP & Port.
    #send_message(connection, f"I see you are located at {address}")
    send_message(connection, "Server: Welcome to the notification system!") # Greet the client with a message and prompt to login.
    username, user = login_user(connection) # Call the login function which returns the username and user. username being what they entered at login and user being the attached information from the dictionary.
    if user:
        user_menu(connection, username, user) # Call menu function to show the client their options and if they logout then move to connection.close()
    connection.close() # If user is not returned from login then close the connection.


# Main server function
def main():
    try:
        threading.Thread(target=background_checker, daemon=True).start() # Start the backround checker in a seperate thread. daemon=True will close the thread when the program stops.

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server: # Creaete a socket with IPv4 and TCP and call it server.
            server.settimeout(1)
            server.bind((HOST, PORT)) # Bind the socket to the servers IP and Port stored as a constant.

            server.listen() # Listen for incoming connections.
            print(f"Server running on {HOST}:{PORT}") # Show the server is running and on what port with what IP.

            while True: # Loop to continue accepting clients.
                try:
                    connection, address = server.accept() # Wait for a connection then when someone connects then return the socket info.
                    threading.Thread(target=handle_client, args=(connection, address), daemon=True).start() # Make a new thread to handle this client so when a new client connects it has its own thread.
                except socket.timeout:
                    continue
    except KeyboardInterrupt:
        print("\nServer shutting down via Ctrl+C")
    finally:
        server.close()
        print("Socket Closed")
main()

