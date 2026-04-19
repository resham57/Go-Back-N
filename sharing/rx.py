import socket
import argparse
from pa3.packet import Packet


def reliablyReceive(rx_ip, rx_port, filename):
    # Implement the UDP receiver to reliably receive the file
    # You may create other files or methods to further refactor your code,
    # but do not change the signature of the method reliablyReceive
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((rx_ip, rx_port))
    print(f"Receiver is ready to receive at {sock.getsockname()}")

    expected_seqnum = 0
    seqnum_len = 10
    last_ack_seqnum = -1

    rx_seqnum_log = open("RxSeqNum.log", "w")
    rx_ack_log = open("RxAck.log", "w")

    with open(filename, 'wb') as f:
        while True:
            message, sender_address = sock.recvfrom(512)
            packet = Packet.deserialize(message)
            print(f"Received packet: flag={packet.flag}, seqnum={packet.seqnum}, length={packet.length}")
            rx_seqnum_log.write(f"{packet.seqnum}\n")

            if packet.flag == 2:  # FIN packet
                ack = Packet(0, packet.seqnum, 0, None)
                sock.sendto(ack.serialize(), sender_address)
                rx_ack_log.write(f"{packet.seqnum}\n")
                print("FIN received, transfer complete")
                break

            if packet.seqnum == expected_seqnum:  # in-order packet
                f.write(packet.payload.encode('latin-1'))
                last_ack_seqnum = expected_seqnum
                expected_seqnum = (last_ack_seqnum + 1) % seqnum_len
                print(f"ACK sent: seqnum={last_ack_seqnum}")
            else:  # out-of-order packet, resent ACK for last correctly in-ordered packet
                print(f"Out-of-order: expected={expected_seqnum}, got={packet.seqnum}, resending ACK={last_ack_seqnum}")

            ack = Packet(0, last_ack_seqnum, 0, None)
            sock.sendto(ack.serialize(), sender_address)
            rx_ack_log.write(f"{last_ack_seqnum}\n")

    rx_seqnum_log.close()
    rx_ack_log.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Receiver")
    parser.add_argument("-ip", metavar="IP address", default="127.0.0.1", type=str, help="Receiver IP address")
    parser.add_argument("-p", metavar="Port number", default=12345, type=int, help="Receiver port number")
    parser.add_argument("-f", metavar="File path", default="data/destinationFile.txt", type=str,
                        help="Path to the file to send")

    args = parser.parse_args()

    reliablyReceive(args.ip, args.p, args.f)
