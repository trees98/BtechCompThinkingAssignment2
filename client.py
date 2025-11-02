import socket #import required modules
import threading

HOST = "127.0.0.1"
PORT = 15000

socket_closed = False #track if socket connection is closed or not

#function to recieve messages from server
def receive_messages(client_socket):
    global socket_closed #using global variable to track socket state within functions
    while True: #loop to continue to listen for incoming messages from server
        try:
            data = client_socket.recv(1024).decode() #recieve messages from server (max 1024 bytes) and decode to a string
            if not data: #if no data recieved break the loop
                break
            if data.strip() == "Server: You were logged out due to inactivity.": #if user logged out due to inactivity and server sends this message
                print("\nServer closed connection due to inactivity.") #let client know server closed connection due to inactivity
                socket_closed = True #set the global variable to true
                break #exit the loop
            print(data) #otherwise print the recieved message 
        except:
            break #exit loop if error occurs
    
#main function
def main():
    global socket_closed #use the global socket_closed variable

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket: #create a TCP socket (IPv4) for communication with the server
        try:
            client_socket.connect((HOST, PORT)) #try and connect to server at the specified host and port
            print(f"Connected to server at {HOST}:{PORT}")
        except:
            print("Connection failed. Make sure the server is running.") #if connection fails notify user and exit
            return

        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start() #start a new thread to handle recieving messages from the server

        while True:
            if socket_closed: #if the global socket_closed variable is set to true break the loop and exit program
                break  
            try:
                message = input() #store users input into message variable
            except:
                break #exit loop if error occurs 
            if socket_closed: #check again in case socket is closed after user input
                break
            if message == "2": #if user enters 2 break the loop(logout user) and send it to the server to let it know
                client_socket.sendall(message.encode())
                print("Disconnected.")
                break
            try: #otherwise send option entered by user to the server
                client_socket.sendall(message.encode())
            except:
                break #exit if error occurs 
    #print message when client exits loop
    print("Client exited.")
#call main function to start client program
main()
