# A Simple TCP server, used as a warm-up exercise for assignment A3
from socket import *
import threading

def run_server():
    # TODO - implement the logic of the server, according to the protocol.
    # Take a look at the tutorial to understand the basic blocks: creating a listening socket,
    # accepting the next client connection, sending and receiving messages and closing the connection
    print("Starting TCP server...")
    global need_too_run

    welcome_socket = socket(AF_INET, SOCK_STREAM)
    welcome_socket.bind(("", 5678))
    welcome_socket.listen(1)

    connection_socket, client_address = welcome_socket.accept()
    need_too_run = True
    while need_too_run:

        client_thread = threading.Thread(target=make_connection_socket, args=(connection_socket,))
        client_thread.start()



    connection_socket.close()
    welcome_socket.close()

def make_connection_socket(connection_socket):

    global need_too_run
    client_message = connection_socket.recv(1000).decode()
    print("Message from client: ", client_message)
    if client_message == "game over\n":
        need_too_run = False

    if not split_and_add(client_message):
        response = "error"

    else:
        response = split_and_add(client_message)

    connection_socket.send(response.encode())
    print("Sending response: ", response)




def split_and_add(client_message):
    if isinstance(client_message, !int): #wtf
        return False
    else:
        cl_split = client_message.split("+", 2)
        response = str(int(cl_split[0]) + int(cl_split[1]))
        return response



# Main entrypoint of the script
if __name__ == '__main__':
    run_server()
