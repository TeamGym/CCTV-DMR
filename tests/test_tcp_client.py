import socket

host = '192.168.'
port = '50003'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
assert sock is not None

sock.connect((host, port))
sock.setblocking(False)

for _ in range(20):
    print('send message from client')
    sock.send('message from client'.encode())

    data = sock.recv(1024, 1000 * 20)
    if data:
        print('data: {}'.format(data.decode('UTF-8')))
    else:
        print('failed to receive data')

    time.sleep(1)

