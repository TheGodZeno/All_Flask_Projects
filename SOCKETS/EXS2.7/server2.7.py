import socket
import os
import cmd_modules
from netProtocol import create_msg_with_header, recieve_msg

RECIEVE_BUFFER = 1024

CMD_FUNCTIONS_DICT = {'TAKE_SCREENSHOT': cmd_modules.take_snap,
                        'SEND_FILE': cmd_modules.send_file,
                        'COPY': cmd_modules.copyf,
                        'DELETE': cmd_modules.deltef,
                        'DIR': cmd_modules.dir,
                        'EXECUTE': cmd_modules.run_prog,
                        'EXIT': None}

def recieve_client_request(client_socket):
    request = recieve_msg(client_socket)
    cmd_and_params = request.split(' ')
    return cmd_and_params[0], cmd_and_params[1:]


def check_valid_request(cmd, params):
    if cmd not in CMD_FUNCTIONS_DICT:
        return False, 'command not suppored!!'
    elif cmd == 'COPY':
        if len(params) != 2:
            return False, 'Bad parameter given'
        elif not os.path.isfile(params[0]):
            return False, 'File to copy not found' + params[0]
        elif params[0] == params[1]:
            return False, 'Cannot copy a file to itself'
    elif cmd == 'SEND_FILE':
        if len(params) != 1:
            return False, 'Bad parameter given'
        elif not os.path.isfile(params):
            return False, 'Source file is invalid'
    elif cmd == 'DELETE':
        if len(params) != 1:
            return False, 'Delete must get one parm'
        elif not os.path.isfile(params):
            return False, "The file doesn't exist"
    elif cmd == 'TAKE_SCREENSHOT' and params:
        return False, "TAKE_SCREENSHOT doesn't have params"
    elif cmd == 'DIR':
        if not os.path.isdir(params.strip()):
            return False, 'Error: Not a directory'
    elif cmd == 'EXIT':
        return False, 'Bye Bye...'


def handle_client_request(cmd, params):
    return CMD_FUNCTIONS_DICT[cmd](params)


def send_response_to_client(response, client_socket):
    if response != '':
        client_socket.send(create_msg_with_header(response).encode())


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 1729))
    server_socket.listen(3)
    while True:
        print("listing to client to connect to server....")
        client_socket, address = server_socket.accept()
        options_menu =\
        ['You may select: TAKE_SCREENSHOT / DIR / DELETE / COPY / EXECUTE / EXIT',
            'Your options are: 1. TAKE_SCREENSHOT - for screen-shot.   ',
            '                  2. DIR - for folder content.',
            '                  3. DELETE - To delete a file.  ',
            '                  4. COPY - To copy a file.    ',
            '                  5. EXECUTE - To run a program.  ',
            '                  6. EXIT - To quit client.    ']

        first_response = '\n'.join(options_menu)
        send_response_to_client(first_response, client_socket)
        done = False
        while not done:
            cmd,params  = recieve_client_request(client_socket)
            valid, error_msg = check_valid_request(cmd, params)
            if valid:
                response = handle_client_request(cmd, params)
                send_response_to_client(response, client_socket)
            else:
                print(error_msg)
                send_response_to_client(error_msg, client_socket)


            if cmd == 'EXIT':
                client_socket.close()
                done = True


if __name__ == '__main__':
    main()
    


