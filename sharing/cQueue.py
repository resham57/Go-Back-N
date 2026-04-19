# Credit: The code is adapted from the implementation of a circular queue in the GeeksforGeeks article:
# https://www.geeksforgeeks.org/dsa/introduction-to-circular-queue/

class CircularQueue:
    def __init__(self, cap):
        # fixed-size array
        self.arr = [0] * cap
        # index of front element
        self.front = 0
        # current number of elements
        self.size = 0
        # maximum capacity
        self.capacity = cap

    # Return True if queue is full else False
    def isFull(self):
        return self.size == self.capacity

    # Return True if queue is empty else False
    def isEmpty(self):
        return self.size == 0

    # Insert an element at the rear
    def enqueue(self, x):
        if self.size == self.capacity:
            print("Queue is full!")
            return
        rear = (self.front + self.size) % self.capacity
        self.arr[rear] = x
        self.size += 1

    # Remove an element from the front
    def dequeue(self):
        if self.size == 0:
            print("Queue is empty!")
            return -1
        res = self.arr[self.front]
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return res

    # Get the front element
    def getFront(self):
        if self.size == 0:
            return -1
        return self.arr[self.front]

    # Get the rear element
    def getRear(self):
        if self.size == 0:
            return -1
        rear = (self.front + self.size - 1) % self.capacity
        return self.arr[rear]


if __name__ == "__main__":
    q = CircularQueue(5)
    q.enqueue(10)
    q.enqueue(20)
    q.enqueue(30)
    print(q.getFront(), q.getRear())
    q.dequeue()
    print(q.getFront(), q.getRear())
    q.enqueue(40)
    print(q.getFront(), q.getRear())
