#!/usr/bin/env python3

"""
-----------------------------------------------------------------------------------------------------------
Go-Back-N: UDP Receiver

Author: Bishal Bhattarai
Section: CSCI-5360-001
Assignment: Programming Assignment 3
Date: 04/17/2026

Description:
This program implements the receiver side of the Go-Back-N protocol using UDP.
It receives packets, ensures in-order delivery, sends cumulative ACKs, and
handles connection termination using a FIN packet.
-----------------------------------------------------------------------------------------------------------
"""

import socket
import argparse
from pa3.packet import Packet

SEQNUM_SIZE = 10  # Sequence number space size
BUFFER_SIZE = 512


def reliablyReceive(rx_ip, rx_port, filename):
    # Create UDP socket using IPv4 addressing
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Binds the provided IP and port - listens
    sock.bind((rx_ip, rx_port))
    print(f"Receiver is ready to receive at {sock.getsockname()}")

    expected_seqnum = 0  # Initialization of expected sequence number
    last_ack_seqnum = -1  # Last correctly received (in-order) packet's seq # (-1, no packet received yet)

    # Open log files to record received sequence numbers and sent ACKs
    rx_seqnum_log = open("RxSeqNum.log", "w")
    rx_ack_log = open("RxAck.log", "w")

    # Open the output file in binary write mode to store received data
    with open(filename, 'wb') as f:
        try:
            # Main receiving loop - runs indefinitely until timeout after FIN
            while True:
                # Receive a UDP packet and sender's address
                message, sender_address = sock.recvfrom(BUFFER_SIZE)

                # Deserialize raw bytes into a Packet object
                packet = Packet.deserialize(message)
                print(f"Received packet: flag={packet.flag}, seqnum={packet.seqnum}, length={packet.length}")

                # Log received sequence number
                rx_seqnum_log.write(f"{packet.seqnum}\n")

                # Handle FIN (termination)
                if packet.flag == 2:  # FIN packet
                    # Create and send ACK for FIN
                    ack = Packet(0, packet.seqnum, 0, None)
                    sock.sendto(ack.serialize(), sender_address)

                    # Log ACK
                    rx_ack_log.write(f"{packet.seqnum}\n")
                    print("FIN received. Waiting briefly to ensure ACK isn't lost...")

                    # Set a timeout so receiver doesn't exit immediately
                    # If no duplicate FINs arrive in 3 seconds, program will safely exit and closes the connection
                    sock.settimeout(3.0)
                    continue

                # Handle data packets
                if packet.seqnum == expected_seqnum:  # in-order packet
                    # Write payload to file after encoding
                    f.write(packet.payload.encode('latin-1'))

                    # Updates the last ACK seq # and expected seq #
                    last_ack_seqnum = expected_seqnum
                    expected_seqnum = (last_ack_seqnum + 1) % SEQNUM_SIZE
                    print(f"ACK sent: seqnum={last_ack_seqnum}")
                else:  # out-of-order packet, resent ACK for last correctly in-ordered packet
                    print(f"Out-of-order: expected={expected_seqnum}, got={packet.seqnum}, resending ACK={last_ack_seqnum}")

                # Send ACK of last correctly received in-order packet (cumulative ACK)
                ack = Packet(0, last_ack_seqnum, 0, None)
                sock.sendto(ack.serialize(), sender_address)  # Send ACK to transmitter
                rx_ack_log.write(f"{last_ack_seqnum}\n")  # Log ACK

        except socket.timeout:
            # Triggered after FIn if no more packets arrive within timeout
            print("Timeout reached after FIN. Closing receiver cleanly.")
            pass

    # Close log files after receiving is complete
    rx_seqnum_log.close()
    rx_ack_log.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Receiver")
    parser.add_argument("-ip", metavar="IP address", default="127.0.0.1", type=str, help="Receiver IP address")
    parser.add_argument("-p", metavar="Port number", default=12345, type=int, help="Receiver port number")
    parser.add_argument("-f", metavar="File path", default="data/destinationFile.txt", type=str,
                        help="Path to the file to save")

    args = parser.parse_args()

    reliablyReceive(args.ip, args.p, args.f)
