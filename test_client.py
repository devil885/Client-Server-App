import sys
import socket
import selectors
import types

BUFF_SIZE = 10024 
sel = selectors.DefaultSelector()
#we get the host the port and how many connections we have from the command line
def start_connections(host, port, num_conns):#here we conncect to the server however many time was given
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print(f"starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,#connection id
            recv_total=0,#total bytes received
            output_bytes=b"",
            input_number=None,
            )
        sel.register(sock, events, data=data)

def get_user_input():#here we get the client to input a number
    try:
        user_input = input("Enter a number: ")
        return int(user_input)
    except (ValueError, KeyboardInterrupt):
        return None

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:# handles the data recieved form the server
        recv_data = sock.recv(BUFF_SIZE)
        if recv_data:# we close the client socket once it is received
            print(f"Received data from connection {data.connid}: {recv_data.decode()}")
            data.recv_total += len(recv_data)
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if not data.input_number:
            user_input = get_user_input()
            if user_input is not None:
                data.input_number = user_input
                data.output_bytes = str(user_input).encode()# we convert the input into a byte string

        if data.output_bytes:
            print(f"Sending {data.output_bytes!r} to {data.connid}")
            sent = sock.send(data.output_bytes)
            data.output_bytes = data.output_bytes[sent:]# removes the sent data from this data

try:
    if len(sys.argv) != 4:# checks if the right amount of arguments was given 
        print("Argument should be <host> <port> <number of connections>")
        sys.exit(1)

    host, port, num_conns = sys.argv[1:4]# assigns them their appropriate value
    start_connections(host, int(port), int(num_conns))

    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        if not sel.get_map():# checks if there arent any active connections monitored by the selector
            print("All connections closed. Exiting.")
            break
except KeyboardInterrupt:
    print("Exiting")
finally:
    sel.close()

