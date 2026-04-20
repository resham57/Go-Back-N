#!/usr/bin/env python3

"""
-----------------------------------------------------------------------------------------------------------
Go-Back-N: UDP Transmitter

Author: Resham Pokhrel
Section: CSCI-5360-001
Assignment: Programming Assignment 3
Date: 04/17/2026

Description:
This program implements the sender side of the Fo-Back-N protocol using UDP.
It reads a file, divides it into chunks, sends packets using a sliding window,
handles cumulative ACKs, retransmits on timeout, and terminates using a FIN packet.
-----------------------------------------------------------------------------------------------------------
"""

import os.path
import socket
import argparse
from pa3.packet import Packet
from pa3.cQueue import CircularQueue

# Configurations
PAYLOAD_SIZE = 50  # Maximum payload size per packet
SEQNUM_SIZE = 10  # Sequence number space size
WINDOW_SIZE = 5
BUFFER_SIZE = 512


# Return all packets currently in the queue (window)
def get_window(queue):
    elements = []
    for i in range(queue.size):
        # Calculate the actual index of packet in the array using modulo
        index = (queue.front + i) % queue.capacity
        elements.append(queue.arr[index])
    return elements


def reliablyTransfer(rx_ip, rx_port, filename):
    # Create UDP socket using IPv4 addressing
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set timeout for ACK waiting
    sock.settimeout(0.2)  # 0.2 second timeout

    # Check if file exists
    if not os.path.isfile(filename):
        print(f"{filename} not found")
        return

    # Initialize the queue
    q = CircularQueue(WINDOW_SIZE)

    index = 0  # Packet counter (for seq# generation)
    file_done = False  # flag indicates file reading completion

    # Open log files to record sent sequence numbers and received ACKs
    tx_seqnum_log = open("TxSeqNum.log", "w")
    tx_ack_log = open("TxAck.log", "w")

    # Open file in binary mode
    with open(filename, 'rb') as f:
        while True:
            # Step 1: fill window and send new packets
            while not q.isFull() and not file_done:

                # read the file as chunk of PAYLOAD_SIZE size
                chunk = f.read(PAYLOAD_SIZE).decode('latin-1')

                # Generates seq#
                seqnum = index % SEQNUM_SIZE

                if chunk:
                    packet = Packet(1, seqnum, len(chunk), chunk)  # Data Packet
                    q.enqueue(packet)  # Adds packet to window buffer

                    sock.sendto(packet.serialize(), (rx_ip, rx_port))  # send packet
                    print(f"{index} sent: flag={packet.flag}, seqnum={seqnum}, length={packet.length}")

                    # Log sent seq#
                    tx_seqnum_log.write(f"{seqnum}\n")
                    index += 1
                else:
                    # End of file reached
                    file_done = True

            # Step 2: receive ACKs
            try:
                message, _ = sock.recvfrom(BUFFER_SIZE)

                # Deserialize ACK packet
                ack = Packet.deserialize(message)
                print(f"Received ack: flag={ack.flag}, seqnum={ack.seqnum}")
                tx_ack_log.write(f"{ack.seqnum}\n")  # Log ACK seq#

                # Get a list of sequence numbers currently in the window
                window_seqnums = [p.seqnum for p in get_window(q)]

                # dequeue all packets upto and including ACK if the ACK is for a packet actually in our window
                if ack.seqnum in window_seqnums:
                    while not q.isEmpty() and q.getFront().seqnum != ack.seqnum:
                        q.dequeue()
                    if not q.isEmpty():
                        q.dequeue()  # dequeue the ACKed packet itself
                else:
                    # Ignores duplicate or old ACKs
                    print(f"Ignored duplicated/old ACK: seqnum={ack.seqnum}")

            except socket.timeout:
                # Step 3: retransmit all packets in window
                print("Timeout! Retransmitting window...")
                tx_seqnum_log.write("Timeout\n")

                # Retransmits all packets in current window
                for pkt in get_window(q):
                    sock.sendto(pkt.serialize(), (rx_ip, rx_port))
                    print(f"Retransmit: seqnum={pkt.seqnum}")
                    tx_seqnum_log.write(f"{pkt.seqnum}\n")

            # Step 4: all data sent and ACKed, send FIN
            if file_done and q.isEmpty():
                # Generates sequence number for FIN packet
                fin_seqnum = index % SEQNUM_SIZE

                # Creates FIN packet
                fin = Packet(2, fin_seqnum, 0, None)

                # Keep sending (timely) FIN until acknowledge
                while True:
                    sock.sendto(fin.serialize(), (rx_ip, rx_port))
                    print(f"FIN sent: seqnum={fin_seqnum}")
                    tx_seqnum_log.write(f"{fin_seqnum}\n")
                    try:
                        message, _ = sock.recvfrom(BUFFER_SIZE)
                        ack = Packet.deserialize(message)

                        # If FIN is acknowledged, terminate
                        if ack.seqnum == fin_seqnum:
                            print("FIN ACKed, transfer complete.")
                            tx_ack_log.write(f"{ack.seqnum}\n")
                            break
                    except socket.timeout:
                        print("Timeout! Retransmitting FIN...")
                        tx_seqnum_log.write("Timeout\n")

                break  # Exit main loop

    # Close log files after sending is complete
    tx_seqnum_log.close()
    tx_ack_log.close()

    # Close the socket connection
    sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Transmitter")
    parser.add_argument("-ip", metavar="IP address", default="127.0.0.1", type=str, help="Receiver IP address")
    parser.add_argument("-p", metavar="Port number", default=12345, type=int, help="Receiver port number")
    parser.add_argument("-f", metavar="File path", default="data/small.txt", type=str, help="Path to the file to send")

    args = parser.parse_args()

    print(args.ip, args.p, args.f)

    reliablyTransfer(args.ip, args.p, args.f)
