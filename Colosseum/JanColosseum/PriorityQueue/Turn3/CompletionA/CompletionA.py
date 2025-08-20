import heapq

class CustomPriorityQueue:
    def __init__(self):
        self._heap = []
    
    def push(self, account, price, nonce):
        # Using a tuple where:
        # (account, secondary key depends on account match)
        # price is negated for a max-heap equivalent:
        heapq.heappush(self._heap, (account, nonce if account in {x[0] for x in self._heap} else -price, nonce, account, price))
    
    def pop(self):
        if self._heap:
            # Pop returns the original stored values (account, price, nonce)
            _, _, nonce, account, price = heapq.heappop(self._heap)
            return (account, price, nonce)
        raise IndexError("pop from empty priority queue")
    
    def __len__(self):
        return len(self._heap)
