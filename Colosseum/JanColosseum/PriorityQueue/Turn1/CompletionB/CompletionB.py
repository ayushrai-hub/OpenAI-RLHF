import heapq

class PriorityQueue:
    def __init__(self):
        self._queue = []
    
    def push(self, account, price, nonce):
        # Pushing tuples into heapq based on your criteria
        heapq.heappush(self._queue, (account, nonce, price))
    
    def pop(self):
        return heapq.heappop(self._queue)

# Usage
pq = PriorityQueue()

# Push items to the priority queue. The order is (account, price, nonce).
pq.push("A", 100, 1)
pq.push("A", 200, 0)
pq.push("B", 50, 2)
pq.push("B", 75, 3)

# Since the heap sorts by account, then nonce for same accounts, we pop in the defined order
result = []
while pq._queue:
    result.append(pq.pop())

print(result)
