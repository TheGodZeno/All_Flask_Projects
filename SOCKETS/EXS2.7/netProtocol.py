import socket
HEADERSIZE = 10
RECIEVE_BUFFER = 16

def create_msg_with_header(simple_msg):
    msg_with_header = f'{len(simple_msg):<{HEADERSIZE}}' + simple_msg
    return msg_with_header

def recieve_msg(sock):
    full_msg = ''
    new_msg = True
    while True:
        msg = sock.recv(RECIEVE_BUFFER)
        if len(msg) == 0:
            return None
        if new_msg:
            print(f'LOG->new msg length:{msg[:HEADERSIZE]}')
            msglen = int(msg[:HEADERSIZE])
            new_msg = False
        full_msg += msg.decode("utf-8")

        if len(full_msg) - HEADERSIZE == msglen:
            return full_msg[HEADERSIZE:]

