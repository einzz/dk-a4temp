#################################################################################
# A Chat Client application. Used in the course IELEx2001 Computer networks, NTNU
#################################################################################
# GROUP: Elektro group 7: Einar, Christoffer and Simon.
import threading
from socket import *
import time

# --------------------
# Constants
# --------------------
# The states that the application can be in
states = [
    "disconnected",  # Connection to a chat server is not established
    "connected",  # Connected to a chat server, but not authorized (not logged in)
    "authorized"  # Connected and authorized (logged in)
]
TCP_PORT = 1300  # TCP port used for communication
SERVER_HOST = "datakomm.work"  # Set this to either hostname (domain) or IP address of the chat server

# --------------------
# State variables
# --------------------
current_state = "disconnected"  # The current state of the system
# When this variable will be set to false, the application will stop
must_run = True
sync_mode = False
pause_thread = False
# Use this variable to create socket connection to the chat server
# Note: the "type: socket" is a hint to PyCharm about the type of values we will assign to the variable
client_socket = None  # type: socket


def quit_application():
    """ Update the application state so that the main-loop will exit """
    # Make sure we reference the global variable here. Not the best code style,
    # but the easiest to work with without involving object-oriented code
    global must_run
    must_run = False


def send_command(command, arguments):
    """
    Send one command to the chat server.
    :param command: The command to send (login, sync, msg, ...(
    :param arguments: The arguments for the command as a string, or None if no arguments are needed
        (username, message text, etc)
    :return:
    """
    global client_socket
    # Hint: concatenate the command and the arguments
    # Hint: remember to send the newline at the end
    try:
        message_too_send = str(command) + " " + str(arguments) + "\n"
        client_socket.send(message_too_send.encode())
    except:
        print("ERROR: Cant send message!")
        return
    return


def read_one_line(sock):
    """
    Read one line of text from a socket
    :param sock: The socket to read from.
    :return:
    """
    newline_received = False
    message = ""
    while not newline_received:
        character = sock.recv(1).decode()
        if character == '\n':
            newline_received = True
        elif character == '\r':
            pass
        else:
            message += character
    return message


def get_servers_response():
    """
    Wait until a response command is received from the server
    :return: The response of the server, the whole line as a single string
    """

    # Hint: reuse read_one_line (copied from the tutorial-code)
    global client_socket
    server_response = read_one_line(client_socket)
    return server_response


def connect_to_server():
    # Must have these two lines, otherwise the function will not "see" the global variables that we will change here
    global client_socket
    global current_state

    # Hint: create a socket, connect, handle exceptions, then change current_state accordingly
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, TCP_PORT))
    except:
        print("Error connecting to server!")
        current_state = "disconnected"
        return

    current_state = "connected"

    monitor_thread = threading.Thread(target=monitor_chat)
    monitor_thread.start()

    #send_command("async", "")
    #if get_servers_response() == "modeok":
    #    print("SYNC MODE ENGAGED!")
    #else:
    #    print("N'SYNC error!: ", get_servers_response())
    #return

    # Hint: send the sync command according to the protocol
    # Hint: create function send_command(command, arguments) which you will use to send this and all other commands
    # to the server

    # Hint: implement the get_servers_response function first - it should wait for one response command from the server
    # and return the server's response (we expect "modeok" response here). This get_servers_response() function
    # will come in handy later as well - when we will want to check the server's response to login, messages etc


def disconnect_from_server():
    # Hint: close the socket, handle exceptions, update current_state accordingly

    # Must have these two lines, otherwise the function will not "see" the global variables that we will change here
    global client_socket
    global current_state

    try:
        client_socket.close()
    except:
        print("Error! Cant dissconnect! :O")
        return

    current_state = "disconnected"
    return


def login():
    global current_state

    username = input("Input desired username: ")
    send_command("login", username)
    #response = get_servers_response()
    current_state = "authorized"
    """
    if response == "loginok":
        
        print("Login ok")
    else:
        print("Error: ", response)
    """
    return


def send_public_message():
    msg_to_send = input("Input public message: ")
    send_command("msg", msg_to_send)
    """
    response = get_servers_response()
    response_split = response.split()
    if response_split[0] == "msgok":
        print("Message sent to", response_split[1], "users")
    else:
        print(response)
    """
    return


def request_user_list():
    send_command("users\n", None)
    """
    response = get_servers_response()
    response_split = response.split(" ")
    for i in response_split:
        if i == "users":
            print("Users on the server:")
        else:
            print(i)
    """
    return


def send_private_message():
    send_to_username = input("Send to username: ")
    msg_to_send = input("Input private message: ")
    command_to_send = send_to_username + " " + msg_to_send
    send_command("privmsg", command_to_send)
    #response = get_servers_response()
    #if response == "msgok 1\n":
    #    print("Message sent to ", send_to_username)
    #else:
    #    print(response)

    return


def read_inbox():
    send_command("inbox", "")

"""
    response = get_servers_response()
    response_split = response.split(" ", 2)
    number_of_msgs = response_split[1]
    print("You have ", response_split[1], "new messages.")

    for _ in range(int(number_of_msgs)):
        response = get_servers_response()
        response_split = response.split(" ", 2)

        if response_split[0] == "msg":
            print("(Public)", response_split[1], ": ", response_split[2])
        else:
            print("(Private)", response_split[1], ": ", response_split[2])
"""

def get_joke():
    send_command("joke", "")
    pause_thread()

    response = get_servers_response()
    response_split = response.split(" ", 1)
    try:
        print("Joke from server:", response_split[1])
    except:
        print("ERROR: Can't find humor")
    unpause_thread()
    return


def monitor_chat():
    global async_mode
    global pause_thread
    while True:
        if pause_thread == True:
            time.sleep(1)
        else:
            incoming_msg = get_servers_response()
            print()
            print(incoming_msg)

            incoming_msg_split = incoming_msg.split(" ", 2)
            if incoming_msg_split[0] == "msg":
                print("(Public)", incoming_msg_split[1], ":", incoming_msg_split[2])
            elif incoming_msg_split[0] == "privmsg":
                print("(Private)", incoming_msg_split[1], ":", incoming_msg_split[2])

    """       
            if incoming_msg_split[0] == "users":
                print("Users on the server:")
                again_split = incoming_msg_split[1].split(" ")
                for i in again_split:
                    print(i)
"""


    return

def pause_thread():
    global pause_thread
    pause_thread = True


def unpause_thread():
    global pause_thread
    pause_thread = False



def change_sync_mode():
    global async_mode

    if async_mode:
        send_command("sync", "")
        async_mode = False

    else:
        send_command("async", "")
        async_mode = True

    return


"""
The list of available actions that the user can perform
Each action is a dictionary with the following fields:
description: a textual description of the action
valid_states: a list specifying in which states this action is available
function: a function to call when the user chooses this particular action. The functions must be defined before
            the definition of this variable
"""

available_actions = [
    {
        "description": "Connect to a chat server",
        "valid_states": ["disconnected"],
        "function": connect_to_server
    },
    {
        "description": "Disconnect from the server",
        "valid_states": ["connected", "authorized"],
        "function": disconnect_from_server
    },
    {
        "description": "Authorize (log in)",
        "valid_states": ["connected", "authorized"],

        # Hint: you will probably want to create a new function (call it login(), or authorize()) and
        # reference that function here.
        # Hint: you can ask the user to enter the username with input("Enter username: ") function.
        # Hint: the login function must be above this line, otherwise the available_actions will complain that it can't
        # find the function
        # Hint: you can reuse the send_command() function to send the "login" command
        # Hint: you probably want to change the state of the system: update value of current_state variable
        # Hint: remember to tell the function that you will want to use the global variable "current_state".
        # Hint: if the login was unsuccessful (loginerr returned), show the error message to the user
        "function": login
    },
    {
        "description": "Send a public message",
        "valid_states": ["connected", "authorized"],

        # Hint: ask the user to input the message from the keyboard
        # Hint: you can reuse the send_command() function to send the "msg" command
        # Hint: remember to read the server's response: whether the message was successfully sent or not
        "function": send_public_message
    },
    {
        "description": "Send a private message",
        "valid_states": ["authorized"],

        # Hint: ask the user to input the recipient and message from the keyboard
        # Hint: you can reuse the send_command() function to send the "privmsg" command
        # Hint: remember to read the server's response: whether the message was successfully sent or not
        "function": send_private_message
    },
    {
        "description": "Read messages in the inbox",
        "valid_states": ["connected", "authorized"],

        # Hint: send the inbox command, find out how many messages there are. Then parse messages
        # one by one: find if it is a private or public message, who is the sender. Print this
        # information in a user friendly way
        "function": read_inbox
    },
    {
        "description": "See list of users",
        "valid_states": ["connected", "authorized"],

        # Hint: use the provided chat client tools and analyze traffic with Wireshark to find out how
        # the user list is reported. Then implement a function which gets the user list from the server
        # and prints the list of usernames
        "function": request_user_list
    },
    {
        "description": "Get a joke",
        "valid_states": ["connected", "authorized"],

        # Hint: this part is not described in the protocol. But the command is simple. Try to find
        # out how it works ;)
        "function": get_joke
    },
    {
        "description": "Quit the application",
        "valid_states": ["disconnected", "connected", "authorized"],
        "function": quit_application
    },
    {
        "description": "Swap asynchronous/synchronous mode",
        "valid_states": ["connected", "authorized"],
        "function": change_sync_mode
    },
]


def run_chat_client():
    """ Run the chat client application loop. When this function exists, the application will stop """

    while must_run:
        print_menu()
        action = select_user_action()
        perform_user_action(action)
    print("Thanks for watching. Like and subscribe! 👍")


def print_menu():
    """ Print the menu showing the available options """
    print("==============================================")
    print("What do you want to do now? ")
    print("==============================================")
    print("Available options:")
    i = 1
    for a in available_actions:
        if current_state in a["valid_states"]:
            # Only hint about the action if the current state allows it
            print("  %i) %s" % (i, a["description"]))
        i += 1
    print()


def select_user_action():
    """
    Ask the user to choose and action by entering the index of the action
    :return: The action as an index in available_actions array or None if the input was invalid
    """
    number_of_actions = len(available_actions)
    hint = "Enter the number of your choice (1..%i):" % number_of_actions
    choice = input(hint)
    # Try to convert the input to an integer
    try:
        choice_int = int(choice)
    except ValueError:
        choice_int = -1

    if 1 <= choice_int <= number_of_actions:
        action = choice_int - 1
    else:
        action = None

    return action


def perform_user_action(action_index):
    """
    Perform the desired user action
    :param action_index: The index in available_actions array - the action to take
    :return: Desired state change as a string, None if no state change is needed
    """
    if action_index is not None:
        print()
        action = available_actions[action_index]
        if current_state in action["valid_states"]:
            function_to_run = available_actions[action_index]["function"]
            if function_to_run is not None:
                function_to_run()
            else:
                print("Internal error: NOT IMPLEMENTED (no function assigned for the action)!")
        else:
            print("This function is not allowed in the current system state (%s)" % current_state)
    else:
        print("Invalid input, please choose a valid action")
    print()
    return None


# Entrypoint for the application. In PyCharm you should see a green arrow on the left side.
# By clicking it you run the application.
if __name__ == '__main__':
    menu_thread = threading.Thread(target=run_chat_client)
    menu_thread.start()


