import sys

print(f"Python Version: {sys.version}")
print(f"Python Implementation: {sys.implementation.name}")
print(f"Platform: {sys.platform}")
print(f"Executable Path: {sys.executable}")
print(f"Python ABI: {sys.abiflags}")
import platform

print(f"System: {platform.system()}")
print(f"Release: {platform.release()}")
print(f"Version: {platform.version()}")
print(f"Machine: {platform.machine()}")
print(f"Processor: {platform.processor()}")
import sys
import platform
import os

# Python details
print(f"Python Version: {sys.version}")
print(f"Python Implementation: {sys.implementation.name}")
print(f"Platform: {sys.platform}")
print(f"Executable Path: {sys.executable}")
print(f"Python ABI: {sys.abiflags}")

# System details
print(f"System: {platform.system()}")
print(f"Release: {platform.release()}")
print(f"Version: {platform.version()}")
print(f"Machine: {platform.machine()}")
print(f"Processor: {platform.processor()}")

# Environment variables
print("\nEnvironment Variables:")
for key, value in os.environ.items():
    print(f'{key}: {value}')
