import socket
import argparse
from pa3.packet import Packet
from pa3.cQueue import CircularQueue

PAYLOAD_SIZE = 50
SEQNUM_SIZE = 10
WINDOW_SIZE = 5


def reliablyReceive(rx_ip, rx_port, filename):
    # Implement the UDP receiver to reliably receive the file
    # You may create other files or methods to further refactor your code, 
    # but do not change the signature of the method reliablyReceive
    pass
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Receiver")
    parser.add_argument("-ip", metavar="IP address", default="127.0.0.1", type=str, help="Receiver IP address")
    parser.add_argument("-p", metavar="Port number", default=12345, type=int, help="Receiver port number")
    parser.add_argument("-f", metavar="File path", default="data/destinationFile.txt", type=str, help="Path to the file to send")

    args = parser.parse_args()
    
    reliablyReceive(args.ip, args.p, args.f)