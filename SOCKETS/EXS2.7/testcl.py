from socket import *
import time
__author__ = 'jacobshutzman1'
# CLIENT

""" This is the client portion of the socket. It can ask for the following
    services (a menu received from the server): image - screen shot, copyf
    copying a file, foldr - listing files inside a folder, delet - to
    delete a file, pgmrn - to run a program, or quitc - to quit.

    Some services require additional data, so the client is prompted for
    it (i.e 'delet' equires what file to delete), other options do not,
    like quitc.

    The client runs an endless loop of requests, prompting the user for
    input. quitc option closes the client. Appropriate messages are printed
    on the screen for sucess or failure with fullfiling the requests.

"""

SERVER = '127.0.0.1'  # Communicate with a domain name
PORT = 1729
FIRST_MESSAGE_LENGTH = 4
MESSAGE_SIZE = 5
BLKSIZE = 1024
DETAIL_LENGTH = 4
ROW_SIZE = 80
FILE_LIST = 'folder_list.txt'
IMAGE_FILE = 'temp.jpg'


def initial_contact(ip, port):
    """ Sends the first hand-shake to the server and asks for the
        services it provides. Get the menu of options and present it.
    """
    client_socket = socket(AF_INET, SOCK_STREAM)
    # Check if the server is up and running , first.
    try:
        client_socket.connect((ip, port))
    except:
        print 'Server is not up , yet'
        return False, '', ''
    message = "Hi"
    client_socket.send(message)
    # First four bytes contain the message we receive, has the length
    result = client_socket.recv(FIRST_MESSAGE_LENGTH)
    if result:
        message_length = int(result)
        services_offered = client_socket.recv(message_length)
        print services_offered
    return True, result, client_socket


def format_response(response):
    """ The first 4 bytes of the response is its length. so the server
        knows how  many bytes are left for the detailed request.
    """
    m_length = str(len(response))
    m_length = m_length.zfill(DETAIL_LENGTH)
    message_back = m_length + response
    print 'message from cient=', message_back
    return message_back


def recv_timeout(socket, timeout=2):
    """ Use timeout as indication that sending file ended. Set a default
        of 2 seconds. If no more data is received in longer than 2 seconds,
        that means data receiving is done.
    """
    socket.setblocking(0)
    # Set blocking off so 'recv' raises an exception if data isn't flowing
    # (caught with pass).
    total_data = []
    data = ''
    begin = time.time()
    more_data = True
    while more_data:
        # if you got some data, then break after the wait allotment.
        if total_data and time.time()-begin > timeout:
            more_data = False
        # if you got no data at all, wait a little longer
        elif time.time()-begin > timeout*2:
            more_data = False
        try:
            data = socket.recv(BLKSIZE)
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    return ''.join(total_data)


def get_folder_list(client_socket):
    """ Receives the client socket. Writes out a file with the list
        of files from the requested folder at the server, or prints
        an error message if the list could not be obtained.
    """
    data = recv_timeout(client_socket)
    if data:
        if data[:5] != 'Error':
            folder_list_file = open(FILE_LIST, 'w')
            folder_list_file.write(data)
            folder_list_file.close()
            print 'done receving list of files, placed at: ', FILE_LIST
        else:
            print data
    else:
        print 'Unknow error with folder'


def get_image(client_socket, timeout=2):
    """ Receives the client socket. writes out a file with the screen
        image of the server. It does that by receiving chunk after
        chunk from the server and uses the timeout mechanism to signal
        that the image sending has completed.
    """
    client_socket.setblocking(0)
    image_file = open(IMAGE_FILE, 'wb')
    # Set blocking off so 'recv' raises an exception if data isn't flowing
    # (caught with pass).
    total_data = []
    data = ''
    begin = time.time()
    more_data = True
    while more_data:
        # if you got some data, then break after the wait allotment.
        if total_data and time.time()-begin > timeout:
            more_data = False
        # if you got no data at all, wait a little longer
        elif time.time()-begin > timeout*2:
            more_data = False
        try:
            data = client_socket.recv(BLKSIZE)
            if data:
                image_file.write(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    image_file.close()
    print 'client got screen image on file ~/' + IMAGE_FILE


def delete_file(client_socket):
    """ Receives the client socket. prints a message of either
        successful file deletion, or an error message.
    """
    data = recv_timeout(client_socket)
    if not data:
        print 'File could not be deleted'
    else:
        print data


def copy_file(client_socket):
    """ Receives the client socket. prints a message of either
        successful file copied, or an error message.
    """
    data = recv_timeout(client_socket)
    if not data:
        print 'something went seriously wrong with copying the file'
    else:
        print data


def run_program(client_socket):
    data = recv_timeout(client_socket)
    if not data:
        print 'Program requested could not be run'
    else:
        print data


def format_send(message, message_detail, client_socket):
    message_len_detail = format_response(message_detail)
    # code+nnnn+ detail data (nnnn is the length of the detail data)
    full_message = message + message_len_detail
    client_socket.send(full_message)


def send_requests(client_socket):
    """ Reads a message from the user,sends it to the server and prints it
        on the screen.
    """
    last_request = ''
    request = 'Select a service. To repeat the last requested, hit <enter>: '
    more_requests = True
    while more_requests:
        message = raw_input(request)
        if len(message) == 0:
            message = last_request
        else:
            message = message[:MESSAGE_SIZE].lower()
            last_request = message
        if message == 'image':
            client_socket.send(message)
            get_image(client_socket)
            # recv_large_file(client_socket)
        elif message == 'foldr':
            message_detail = raw_input("Enter the full folder's name: ")
            format_send(message, message_detail, client_socket)
            get_folder_list(client_socket)
        elif message == 'delet':
            message_detail = \
                raw_input("Enter the full path of file to be deleted: ")
            format_send(message, message_detail, client_socket)
            delete_file(client_socket)
        elif message == 'copyf':
            message_detail = \
                raw_input("Enter: file1 file2 (copy file1 into file2): ")
            format_send(message, message_detail, client_socket)
            copy_file(client_socket)
        elif message == 'pgmrn':
            message_detail = \
                raw_input("Enter pgm name (if not in PATH, enter full path) ")
            format_send(message, message_detail, client_socket)
            run_program(client_socket)
        elif message == 'quitc':
            client_socket.send(message)
            more_requests = False
        else:
            print 'request is not recognized'
    print "Client has been terminated I'll be baaack !!!"
    client_socket.close()


def mainclient():
    """ Asking the server for the type of services it provides, then
        loop on requests.
    """
    server_on, result, socket = initial_contact(SERVER, PORT)
    if server_on:
        send_requests(socket)


mainclient()