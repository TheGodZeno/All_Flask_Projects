from PIL import ImageGrab
from socket import *
from glob import *
import os
import shutil
import platform
import subprocess
__author__ = 'jacobshutzman1'
# SERVER
"""
The Server offers its possible services by dislaying a menu with options.
The options can be selected by a client. Some options only require the
code, which is always a 5-letter string (i.e copyf for copying a file).
Other options also require more details, so the main loop of serve_requests
analyzes it, and extracts the right information.
Some data is kept in pre-determined files. Appropriate messages display on
the screen for success or failure with fullfiling the client's requests.
"""


IP = '0.0.0.0'
PORT = 1729
INITIAL_MESSAGE_SIZE = 4
DETAIL_LENGTH = 4
MESSAGE_SIZE = 5
BLKSIZE = 4096
TEXT_SIZE = 80
FIRST = 0
SECOND = 1


def format_response(response):
    """ Receives a message and returns: message-length+message
        The first 4 bytes of the response is its length. so the client
        knows how  many bytes are left for the request.
    """
    m_length = str(len(response))
    m_length = m_length.zfill(INITIAL_MESSAGE_SIZE)
    message_back = m_length + response
    return message_back


def inital_listen():
    """ Run the server and start listening to messages from a client """
    server = socket(AF_INET, SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(1)
    print 'server is listening... on Port:', PORT
    return server


def check_client(server):
    """ wait for client's first message and offer the services that
        are available for clients, as menu options. This function is
        activated once per client.
    """
    client, (ip, port) = server.accept()
    data = client.recv(MESSAGE_SIZE)  # Ask for service (just Hi from client)
    options_menu =\
        ['You may select: image / foldr / delet / copyf / pgmrn / quitc',
            'Your options are: 1. image - for screen-shot.   ',
            '                  2. foldr - for folder content.',
            '                  3. delet - To delete a file.  ',
            '                  4. copyf - To copy a file.    ',
            '                  5. pgmrn - To run a program.  ',
            '                  6. quitc - To quit client.    ']

    first_response = '\n'.join(options_menu)
    first_message_back = format_response(first_response)  # Add length
    client.send(first_message_back)
    data = client.recv(MESSAGE_SIZE)
    return client, data


def send_file(filename, client):
    """ Gets a file to send and a socket. Since the file is an image it
        could be large, so it sends it in BLKSIZE chunks.
    """
    try:
        file_handle = open(filename, 'rb')
    except Exception as e:
        print e.message
    try:
        chunk = file_handle.read(BLKSIZE)
    except:
        print 'read failed'
    print 'sending screen image...'
    while (chunk):
        sent = client.send(chunk)
        assert sent == len(chunk)
        chunk = file_handle.read(BLKSIZE)
    file_handle.close()
    print 'finished sending screen image'


def create_file_list(folder, client):
    """ Gets a string with folder to list its files, and the client socket.
        Sends back all the list of files in the folder, if all's fine.
        Otherwise, sends a message.
     """
    data = ''
    folder = folder.strip()
    if not os.path.isdir(folder):
        data = 'Error: Not a directory'
    else:
        full_path = folder + '/*.*'
        all_files = glob(full_path)
        if len(all_files) == 0:
            data = 'Error: Directory has no files'
        else:
            for file in all_files:
                if len(file) > TEXT_SIZE:
                    line80 = file[len(file)-TEXT_SIZE:]
                else:
                    line80 = file + ' '*(TEXT_SIZE - len(file))
                line80 += '\n'
                sent = client.send(line80)
                assert sent == len(line80)

            print 'list of files for folder sent'
    if data:
        client.send(data)


def delete_file(file_to_delete, client):
    """ Gets a string with file to delete, and the client socket.
        Sends back a message to the client whether the delete was
        successful or not. If all's fine, makes the delete.
     """
    file_to_delete = file_to_delete.strip()
    data = file_to_delete
    if os.path.isfile(file_to_delete):
        try:
            os.remove(file_to_delete)
            data += ' has been removed'
            print 'file: ', file_to_delete, ' has been removed'
        except:
            print 'file: ', file_to_delete, 'could not be deleted'
            data += ' could not be deleted'
    else:
        data += ' not found'
    client.send(data)


def copy_file(copy_from_to, client):
    """ Gets a string with file to copy and the client socket. Sends back
        a message to the client whether copy was successful or not. If all's
        fine, makes the copy, otherwise tries to send a specific note.
     """
    data = 'copied successfully '
    file_from_file_to = copy_from_to.split()
    if len(file_from_file_to) != 2:
        data = 'bad parameter given'
    elif not os.path.isfile(file_from_file_to[FIRST]):
        data = 'file to copy not found ' + file_from_file_to[FIRST]
    elif file_from_file_to[FIRST] == file_from_file_to[SECOND]:
        data = 'Cannot copy a file to itself'
    else:
        try:
            shutil.copy(file_from_file_to[FIRST], file_from_file_to[SECOND])
        except:
            data = 'Unsuccessful copy: '
        data += file_from_file_to[FIRST]+' to '+file_from_file_to[SECOND]
    # print data
    client.send(data)


def run_program(pgm_to_run, client):
    """ Receives an application name to run and a client socket. Checks the
        platform and tries to launch. Sends a message to the client on
        success / failure.
    """
    ret_code = 0
    if platform.system() == 'Windows':  # At least windows 10 yield this.
        # code for running app on windows
        try:
            ret_code = subprocess.call(pgm_to_run)
        except Exception as e:
            print e
    elif platform.system() == 'Darwin':  # Mac OS
        # code for running app on Mac
        # i.e: "Microsoft Office 2011/Microsoft word.app"
        try:
            ret_code = subprocess.call(["/usr/bin/open", "-W", "-n", "-a",
                                        "/Applications/" + pgm_to_run])
        except Exception as e:
            print e
    if ret_code == 0:
        data = 'Program has launched on the server'
    else:
        data = 'Program failed to launch'
    client.send(data)


def analyze_input(client):
    """ Gets the client socket and returns the detail message"""
    detail_length = client.recv(DETAIL_LENGTH)
    detail_length = int(detail_length)
    detail_message = client.recv(detail_length)
    return detail_message


def serve_requests(data, client, server):
    """ Serve requests by the client, as long as they come. This has an
        endless loop for one client. The first 5 bytes of every message
        is a code of action. For actions that require more data, we
        receive 4 bytes of length, and then the data.
    """
    more_requests = True
    while data and more_requests:
        print 'Request received by server: ', data
        if data == 'image':
            screen_snap = ImageGrab.grab()
            screen_snap.save(r'screen.png')
            screen_snap.close()
            print 'screen.png created'
            send_file('screen.png', client)
        elif data == 'foldr':  # More detail is provided (len+folder)
            folder_name = analyze_input(client)
            create_file_list(folder_name, client)
        elif data == 'delet':
            file_to_delete = analyze_input(client)
            delete_file(file_to_delete, client)
        elif data == 'copyf':
            copy_from_to = analyze_input(client)
            copy_file(copy_from_to, client)
        elif data == 'pgmrn':
            pgm_to_run = analyze_input(client)
            run_program(pgm_to_run, client)
        elif data == 'quitc':
            print 'requested to quit client'
            more_requests = False
        data = client.recv(MESSAGE_SIZE)
    print 'closing client'
    client.close()


def mainserver():
    server = inital_listen()
    # start endless loop for as many clients that want services.
    while True:
        client, data = check_client(server)  # New client
        try:
            serve_requests(data, client, server)
        except:
            client.close()
    server.close()

mainserver()