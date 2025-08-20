import requests

try:
    import requests
    print("requests", requests.__version__)
except Exception as e:
    print("requests not available:", e)

import requests
import time
from urllib.parse import quote

prompt = "MVP: a mobile app that tracks fitness activities"
encoded_prompt = quote(prompt)

# Define the endpoints
urls = {
    'Pollinations': f'https://image.pollinations.ai/prompt/{encoded_prompt}',
    'RoboHash': f'https://robohash.org/{encoded_prompt}.png',
    'DiceBear': f'https://api.dicebear.com/9.x/pixel-art/svg?seed={encoded_prompt}'
}

times = {}

for name, url in urls.items():
    print(f"Requesting {name} ({url})")
    start = time.perf_counter()
    try:
        resp = requests.get(url, timeout=60)  # 60 sec timeout
        duration = time.perf_counter() - start
        times[name] = duration
        size = len(resp.content)
        print(f"{name}: status {resp.status_code}, time {duration:.2f} s, size {size} bytes")
    except Exception as e:
        print(f"Error for {name}: {e}")

print("Times:", times)



