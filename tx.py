import os.path
import socket
import argparse
from pa3.packet import Packet
from pa3.cQueue import CircularQueue

PAYLOAD_SIZE = 50
SEQNUM_SIZE = 10
WINDOW_SIZE = 5
BUFFER_SIZE = 512


# Return all elements currently in the queue
def get_window(queue):
    elements = []
    for i in range(queue.size):
        # Calculate the actual index in the array using modulo
        index = (queue.front + i) % queue.capacity
        elements.append(queue.arr[index])
    return elements


def reliablyTransfer(rx_ip, rx_port, filename):
    print((rx_ip, rx_port, filename))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)  # confirm the timeout value

    # Check if file exists
    if not os.path.isfile(filename):
        print(f"{filename} not found")
        return

    chunk_size = 50
    seqnum_len = 10  # 0 to 9
    q = CircularQueue(5)
    index = 0
    file_done = False

    tx_seqnum_log = open("TxSeqNum.log", "w")
    tx_ack_log = open("TxAck.log", "w")

    with open(filename, 'rb') as f:
        while True:
            # Step 1: fill window and send new packets
            while not q.isFull() and not file_done:
                chunk = f.read(chunk_size).decode('latin-1')
                seqnum = index % seqnum_len

                if chunk:
                    packet = Packet(1, seqnum, len(chunk), chunk)  # Data Packet
                    q.enqueue(packet)

                    sock.sendto(packet.serialize(), (rx_ip, rx_port))
                    print(f"{index} sent: flag={packet.flag}, seqnum={seqnum}, length={packet.length}")
                    tx_seqnum_log.write(f"{seqnum}\n")
                    index += 1
                else:
                    file_done = True

            # Step 2: receive ACKs
            try:
                message, _ = sock.recvfrom(BUFFER_SIZE)
                ack = Packet.deserialize(message)
                print(f"Received ack: flag={ack.flag}, seqnum={ack.seqnum}")
                tx_ack_log.write(f"{ack.seqnum}\n")

                # Get a list of sequence numbers currently in the window
                window_seqnums = [p.seqnum for p in get_window(q)]

                # dequeue all packets upto and including ACK if the ACK is for a packet actually in our window
                if ack.seqnum in window_seqnums:
                    while not q.isEmpty() and q.getFront().seqnum != ack.seqnum:
                        q.dequeue()
                    if not q.isEmpty():
                        q.dequeue()  # dequeue the ACKed packet itself
                else:
                    print(f"Ignored duplicated/old ACK: seqnum={ack.seqnum}")

            except socket.timeout:
                # Step 3: retransmit all packets in window
                print("Timeout! Retransmitting window...")
                tx_seqnum_log.write("Timeout\n")

                for pkt in get_window(q):
                    sock.sendto(pkt.serialize(), (rx_ip, rx_port))
                    print(f"Retransmit: seqnum={pkt.seqnum}")
                    tx_seqnum_log.write(f"{pkt.seqnum}\n")

            # Step 4: all data sent and ACKed, send FIN
            if file_done and q.isEmpty():
                fin_seqnum = index % seqnum_len
                fin = Packet(2, fin_seqnum, 0, None)

                while True:
                    sock.sendto(fin.serialize(), (rx_ip, rx_port))
                    print(f"FIN sent: seqnum={fin_seqnum}")
                    tx_seqnum_log.write(f"{fin_seqnum}\n")
                    try:
                        message, _ = sock.recvfrom(BUFFER_SIZE)
                        ack = Packet.deserialize(message)
                        if ack.seqnum == fin_seqnum:
                            print("FIN ACKed, transfer complete.")
                            tx_ack_log.write(f"{ack.seqnum}\n")
                            break
                    except socket.timeout:
                        print("Timeout! Retransmitting FIN...")
                        tx_seqnum_log.write("Timeout\n")

                break

    tx_seqnum_log.close()
    tx_ack_log.close()

    # Close the socket connection
    sock.close()

    print("File Sent")
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
