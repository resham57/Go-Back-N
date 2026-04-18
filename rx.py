import socket
import argparse
from pa3.packet import Packet
from pa3.cQueue import CircularQueue

PAYLOAD_SIZE = 50
SEQNUM_SIZE = 10
WINDOW_SIZE = 5


def receive(rx_ip, rx_port, filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind((rx_ip, rx_port))

    print(f"Receiver is ready to receive at {sock.getsockname()}")

    with open(filename, 'wb') as f:
        while True:
            message, sender_address = sock.recvfrom(512)
            packet = Packet.deserialize(message)

            print(f"Received packet: flag={packet.flag}, seqnum={packet.seqnum}, length={packet.length}")

            # before sending ack, have to add logic to make sure that I am getting correct - in-order packets

            ack = Packet(0, packet.seqnum, 0, None)
            sock.sendto(ack.serialize(), sender_address)

            if packet.flag == 2:  # FIN packet
                print("FIN received, transfer complete")
                break

            if packet.payload is not None:
                f.write(packet.payload.encode('latin-1'))

    sock.sendto("ACK - Data Received".encode(), sender_address)


def reliablyReceive(rx_ip, rx_port, filename):
    # Implement the UDP receiver to reliably receive the file
    # You may create other files or methods to further refactor your code, 
    # but do not change the signature of the method reliablyReceive
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Receiver")
    parser.add_argument("-ip", metavar="IP address", default="127.0.0.1", type=str, help="Receiver IP address")
    parser.add_argument("-p", metavar="Port number", default=12345, type=int, help="Receiver port number")
    parser.add_argument("-f", metavar="File path", default="data/destinationFile.txt", type=str,
                        help="Path to the file to send")

    args = parser.parse_args()

    reliablyReceive(args.ip, args.p, args.f)

    receive(args.ip, args.p, args.f)
