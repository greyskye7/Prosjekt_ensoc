import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 9050
sock = socket.socket(socket.AF_INET,    # Internet protocol
                     socket.SOCK_DGRAM) # User Datagram (UDP)
sock.bind((UDP_IP, UDP_PORT))
while True:
    data, addr = sock.recvfrom(1280) # Max recieve size is 1280 bytes
    
    listen = data.split(',')
    print listen
    for i in listen
    mk = ["1", "2", "3"]
    print mk
    b = listen[1]
    print b
