import os.path
import socket
import argparse
from pa3.packet import Packet
from pa3.cQueue import CircularQueue

PAYLOAD_SIZE = 50
SEQNUM_SIZE = 10
WINDOW_SIZE = 5


def transfer(rx_ip, rx_port, filename):
    print((rx_ip, rx_port, filename))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.bind() # optional for sender

    # Check if file exists
    if not os.path.isfile(filename):
        print(f"{filename} not found")
        return

    chunk_size = 50
    seqnum_len = 10  # 0 to 9
    index = 0

    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(chunk_size).decode('latin-1')
            seqnum = index % seqnum_len

            if not chunk:
                packet = Packet(2, seqnum, 0, None)  # FIN packet
            else:
                packet = Packet(1, seqnum, len(chunk), chunk)  # Data Packet

            sock.sendto(packet.serialize(), (rx_ip, rx_port))
            print(f"{index} sent: flag={packet.flag}, seqnum={seqnum}, length={packet.length}")

            index += 1

            message, _ = sock.recvfrom(512)

            ack = Packet.deserialize(message)
            print(f"Received ack: flag={ack.flag}, seqnum={ack.seqnum}, length={ack.length}")

            if not chunk:
                break

    print("file sent")

    message, receiver_address = sock.recvfrom(512)  # have to update the receiving length

    # Close the socket connection
    sock.close()

    print(message, receiver_address)


def reliablyTransfer(rx_ip, rx_port, filename):
    # Implement the UDP sender to reliably transfer the file
    # Create log files as well to log the events in the sender side
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Transmitter")
    parser.add_argument("-ip", metavar="IP address", default="127.0.0.1", type=str, help="Receiver IP address")
    parser.add_argument("-p", metavar="Port number", default=12345, type=int, help="Receiver port number")
    parser.add_argument("-f", metavar="File path", default="data/small.txt", type=str, help="Path to the file to send")

    args = parser.parse_args()

    print(args.ip, args.p, args.f)

    reliablyTransfer(args.ip, args.p, args.f)

    transfer(args.ip, args.p, args.f)
