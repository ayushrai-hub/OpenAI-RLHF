import heapq

# Define a custom class for items in the priority queue
class Transaction:
    def __init__(self, account, price, nonce):
        self.account = account
        self.price = price
        self.nonce = nonce
    
    def __lt__(self, other):
        # When accounts are different, sort by price
        if self.account != other.account:
            return self.price < other.price
        # When accounts are the same, sort by nonce (lower first)
        return self.nonce < other.nonce
    
    def __repr__(self):
        return f"Transaction(account={self.account}, price={self.price}, nonce={self.nonce})"

# Create a priority queue (min-heap by default)
priority_queue = []

# Insert transactions into the priority queue
heapq.heappush(priority_queue, Transaction("acc1", 10, 2))
heapq.heappush(priority_queue, Transaction("acc2", 5, 1))
heapq.heappush(priority_queue, Transaction("acc1", 15, 1))
heapq.heappush(priority_queue, Transaction("acc2", 7, 2))
heapq.heappush(priority_queue, Transaction("acc1", 5, 3))

# Extract transactions from the priority queue
while priority_queue:
    print(heapq.heappop(priority_queue))
