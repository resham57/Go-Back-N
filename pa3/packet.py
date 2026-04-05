import json

class Packet:
    # constructor for the Packet class, initializes the flag, seqnum, length, and payload attributes
    def __init__(self, flag, seqnum, length, payload):
        self.flag = flag
        self.seqnum = seqnum
        self.length = length
        self.payload = payload

    # converts the Packet object to bytes for transmission
    def serialize(self):
        return json.dumps({
            "flag": self.flag,
            "seqnum": self.seqnum,
            "length": self.length,
            "payload": self.payload
        }).encode('utf-8')
    
    # converts the byte data back to a Packet object
    @classmethod
    def deserialize(cls, data):
        data = json.loads(data.decode('utf-8'))
        return cls(
            flag=data["flag"],
            seqnum=data["seqnum"],
            length=data["length"],
            payload=data["payload"]
        )