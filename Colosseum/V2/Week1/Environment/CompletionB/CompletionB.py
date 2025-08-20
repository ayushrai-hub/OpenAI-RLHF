import sys

print(f"Python version: {sys.version}")
print(f"Version info: {sys.version_info}")
print(f"Implementation: {sys.implementation}")


import platform

print(f"Platform: {platform.system()}")
print(f"Platform release: {platform.release()}")
print(f"Platform version: {platform.version()}")
print(f"Architecture: {platform.architecture()}")
print(f"Machine: {platform.machine()}")
print(f"Processor: {platform.processor()}")



import os
import sys
import platform

print("Environment Variables:")
for key, value in os.environ.items():
    print(f"{key}: {value}")

print(f"\nPython version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"CPU count: {os.cpu_count()}")
