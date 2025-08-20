import heapq

class PriorityQueue:
    def __init__(self):
        self.heap = []

    def push(self, account, price, nonce):
        # Push a tuple with custom sorting logic
        # (account, nonce, price) ensures sorting by:
        # 1. account lexicographically
        # 2. nonce first (if account is the same)
        # 3. price last (if account is different)
        heapq.heappush(self.heap, (account, nonce, price))

    def pop(self):
        # Return the top element
        account, nonce, price = heapq.heappop(self.heap)
        return account, price, nonce

    def peek(self):
        # Peek at the top element without removing
        account, nonce, price = self.heap[0]
        return account, price, nonce

    def is_empty(self):
        return len(self.heap) == 0


pq = PriorityQueue()

# Insert some test data
pq.push("a", 100, 2)  # Account "a", price 100, nonce 2
pq.push("b", 200, 1)  # Account "b", price 200, nonce 1
pq.push("a", 300, 1)  # Account "a", price 300, nonce 1

while not pq.is_empty():
    print(pq.pop())
