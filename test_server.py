import sys
import socket
import selectors
import types
from test_scraper import scrape

sel = selectors.DefaultSelector()
BUFF_SIZE = 10024 
file_path="hiji.txt"


def accept_wrapper(sock): 
    #Accepts a new connection, sets it to non-blocking mode, and registers it with the selector
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data= types.SimpleNamespace(addr=addr, input_bytes=b"", output_bytes=b"")
    events=selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn,events, data=data)

def service_connection(key, mask):
    #Handles read and write events for a given connection
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(BUFF_SIZE)
        if recv_data:
            data.output_bytes += recv_data 
        else:#if we don't receive data it means the client socket is closed
            print(f"Connection closed by {data.addr}")
            sel.unregister(sock)
            sock.close()
            
     
            

    if mask & selectors.EVENT_WRITE:
        if data.output_bytes:
            print(f"Sending data to {data.addr}")
            rows = int(recv_data.decode())
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = [next(file).strip() for _ in range(rows)]
                answer = '\n'.join(lines)
            sent = sock.send(answer.encode('utf-8'))
            data.output_bytes = data.output_bytes[sent:]#removes the data send from the output_bytes string
            
           
host,port = sys.argv[1], int(sys.argv[2]) 
lis_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lis_sock.bind((host,port)) 
scrape() 
print(f"Listening rn {(host, port)}")
lis_sock.listen()
lis_sock.setblocking(False)
sel.register(lis_sock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)# blocks until there are sockets ready for input or output
        #and returns a list of tuples containing a key and a mask for each socket
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key,mask)
except KeyboardInterrupt: 
    print("Exiting")
finally:
    sel.close()